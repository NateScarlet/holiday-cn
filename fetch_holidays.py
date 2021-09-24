#!/usr/bin/env python3
"""Fetch holidays from gov.cn  """

import argparse
import json
import re
from datetime import date, timedelta
from itertools import chain
from typing import Iterator, List, Optional, Tuple

import bs4
import requests

SEARCH_URL = "http://sousuo.gov.cn/s.htm"
PAPER_EXCLUDE = [
    "http://www.gov.cn/zhengce/content/2014-09/29/content_9102.htm",
    "http://www.gov.cn/zhengce/content/2015-02/09/content_9466.htm",
]
PAPER_INCLUDE = {
    2015: ["http://www.gov.cn/zhengce/content/2015-05/13/content_9742.htm"]
}

PRE_PARSED_PAPERS = {
    "http://www.gov.cn/zhengce/content/2015-05/13/content_9742.htm": [
        {
            "name": "抗日战争暨世界反法西斯战争胜利70周年纪念日",
            "date": date(2015, 9, 3),
            "isOffDay": True,
        },
        {
            "name": "抗日战争暨世界反法西斯战争胜利70周年纪念日",
            "date": date(2015, 9, 4),
            "isOffDay": True,
        },
        {
            "name": "抗日战争暨世界反法西斯战争胜利70周年纪念日",
            "date": date(2015, 9, 5),
            "isOffDay": True,
        },
        {
            "name": "抗日战争暨世界反法西斯战争胜利70周年纪念日",
            "date": date(2015, 9, 6),
            "isOffDay": False,
        },
    ]
}


def _raise_for_status_200(resp: requests.Response):
    resp.raise_for_status()
    if resp.status_code != 200:
        raise requests.HTTPError(
            "request failed: %d: %s" % (resp.status_code, resp.request.url),
            response=resp,
        )


def get_paper_urls(year: int) -> List[str]:
    """Find year related paper urls.

    Args:
        year (int): eg. 2018

    Returns:
        List[str]: Urls， newlest first.
    """

    resp = requests.get(
        SEARCH_URL,
        params={
            "t": "paper",
            "advance": "true",
            "title": year,
            "q": "假期",
            "pcodeJiguan": "国办发明电",
            "puborg": "国务院办公厅",
        },
    )
    _raise_for_status_200(resp)
    ret = re.findall(
        r'<li class="res-list".*?<a href="(.+?)".*?</li>', resp.text, flags=re.S
    )
    ret = [i for i in ret if i not in PAPER_EXCLUDE]
    ret += PAPER_INCLUDE.get(year, [])
    ret.sort()
    if not ret and date.today().year >= year:
        raise RuntimeError("could not found papers for %d" % year)
    return ret


def get_paper(url: str) -> str:
    """Extract paper text from url.

    Args:
        url (str): Paper url.

    Returns:
        str: Extracted paper text.
    """

    assert re.match(
        r"http://www.gov.cn/zhengce/content/\d{4}-\d{2}/\d{2}/content_\d+.htm", url
    ), "Site changed, need human verify"

    response = requests.get(url)
    _raise_for_status_200(response)
    response.encoding = "utf-8"
    soup = bs4.BeautifulSoup(response.text, features="html.parser")
    container = soup.find("td", class_="b12c")
    assert container, f"Can not get paper container from url: {url}"
    ret = container.get_text().replace("\u3000\u3000", "\n")
    assert ret, f"Can not get paper content from url: {url}"
    return ret


def get_rules(paper: str) -> Iterator[Tuple[str, str]]:
    """Extract rules from paper.

    Args:
        paper (str): Paper text

    Raises:
        NotImplementedError: When find no rules.

    Returns:
        Iterator[Tuple[str, str]]: (name, description)
    """

    lines: list = paper.splitlines()
    lines = sorted(set(lines), key=lines.index)
    count = 0
    for i in chain(get_normal_rules(lines), get_patch_rules(lines)):
        count += 1
        yield i
    if not count:
        raise NotImplementedError(lines)


def get_normal_rules(lines: Iterator[str]) -> Iterator[Tuple[str, str]]:
    """Get normal holiday rule for a year

    Args:
        lines (Iterator[str]): paper content

    Returns:
        Iterator[Tuple[str, str]]: (name, description)
    """
    for i in lines:
        match = re.match(r"[一二三四五六七八九十]、(.+?)：(.+)", i)
        if match:
            yield match.groups()


def get_patch_rules(lines: Iterator[str]) -> Iterator[Tuple[str, str]]:
    """Get holiday patch rule for existed holiday

    Args:
        lines (Iterator[str]): paper content

    Returns:
        Iterator[Tuple[str, str]]: (name, description)
    """
    name = None
    for i in lines:
        match = re.match(r".*\d+年([^和、]{2,})(?:假期|放假).*安排", i)
        if match:
            name = match.group(1)
        if not name:
            continue
        match = re.match(r"^[一二三四五六七八九十]、(.+)$", i)
        if not match:
            continue
        description = match.group(1)
        if re.match(r".*\d+月\d+日.*", description):
            yield name, description


def _cast_int(value):
    return int(value) if value else None


class DescriptionParser:
    """Parser for holiday shift description."""

    def __init__(self, description: str, year: int):
        self.description = description
        self.year = year
        self.date_history = list()

    def parse(self) -> Iterator[dict]:
        """Generator for description parsing result.

        Args:
            year (int): Context year
        """

        del self.date_history[:]
        for i in re.split("[，。；]", self.description):
            for j in SentenceParser(self, i).parse():
                yield j

        if not self.date_history:
            raise NotImplementedError(self.description)

    def get_date(self, year: Optional[int], month: Optional[int], day: int) -> date:
        """Get date in context.

        Args:
            year (Optional[int]): year
            month (int): month
            day (int): day

        Returns:
            date: Date result
        """

        assert day, "No day specified"

        # Special case: month inherit
        if month is None:
            month = self.date_history[-1].month

        # Special case: 12 month may mean previous year
        if (
            year is None
            and month == 12
            and self.date_history
            and max(self.date_history) < date(year=self.year, month=2, day=1)
        ):
            year = self.year - 1

        year = year or self.year
        return date(year=year, month=month, day=day)


class SentenceParser:
    """Parser for holiday shift description sentence."""

    special_cases = {
        "延长2020年春节假期至2月2日（农历正月初九": [
            {"date": date(2020, 1, 31), "isOffDay": True},
            {"date": date(2020, 2, 1), "isOffDay": True},
            {"date": date(2020, 2, 2), "isOffDay": True},
        ],
    }

    def __init__(self, parent: DescriptionParser, sentence):
        self.parent = parent
        self.sentence = sentence

    def extract_dates(self, text: str) -> Iterator[date]:
        """Extract date from text.

        Args:
            text (str): Text to extract

        Returns:
            Iterator[date]: Extracted dates.
        """

        count = 0
        text = text.replace("(", "（").replace(")", "）")
        for i in chain(
            *(method(self, text) for method in self.date_extraction_methods)
        ):
            count += 1
            is_seen = i in self.parent.date_history
            self.parent.date_history.append(i)
            if is_seen:
                continue
            yield i

        if not count:
            raise NotImplementedError(text)

    def _extract_dates_1(self, value: str) -> Iterator[date]:
        match = re.findall(r"(?:(\d+)年)?(?:(\d+)月)?(\d+)日", value)
        for groups in match:
            groups = [_cast_int(i) for i in groups]
            assert len(groups) == 3, groups
            yield self.parent.get_date(year=groups[0], month=groups[1], day=groups[2])

    def _extract_dates_2(self, value: str) -> Iterator[date]:
        match = re.findall(
            r"(?:(\d+)年)?(?:(\d+)月)?(\d+)日(?:至|-|—)(?:(\d+)年)?(?:(\d+)月)?(\d+)日", value
        )
        for groups in match:
            groups = [_cast_int(i) for i in groups]
            assert len(groups) == 6, groups
            start = self.parent.get_date(year=groups[0], month=groups[1], day=groups[2])
            end = self.parent.get_date(year=groups[3], month=groups[4], day=groups[5])
            for i in range((end - start).days + 1):
                yield start + timedelta(days=i)

    def _extract_dates_3(self, value: str) -> Iterator[date]:
        match = re.findall(
            r"(?:(\d+)年)?(?:(\d+)月)?(\d+)日(?:（[^）]+）)?"
            r"(?:、(?:(\d+)年)?(?:(\d+)月)?(\d+)日(?:（[^）]+）)?)+",
            value,
        )
        for groups in match:
            groups = [_cast_int(i) for i in groups]
            assert not (len(groups) % 3), groups
            for i in range(0, len(groups), 3):
                yield self.parent.get_date(
                    year=groups[i], month=groups[i + 1], day=groups[i + 2]
                )

    date_extraction_methods = [_extract_dates_1, _extract_dates_2, _extract_dates_3]

    def parse(self) -> Iterator[dict]:
        """Parse days with memory

        Args:
            memory (set): Date memory

        Returns:
            Iterator[dict]: Days without name field.
        """
        for method in self.parsing_methods:
            for i in method(self):
                yield i

    def _parse_rest_1(self):
        match = re.match(r"(.+)(放假|补休|调休|公休)+(?:\d+天)?$", self.sentence)
        if match:
            for i in self.extract_dates(match.group(1)):
                yield {"date": i, "isOffDay": True}

    def _parse_work_1(self):
        match = re.match("(.+)上班$", self.sentence)
        if match:
            for i in self.extract_dates(match.group(1)):
                yield {"date": i, "isOffDay": False}

    def _parse_shift_1(self):
        match = re.match("(.+)调至(.+)", self.sentence)
        if match:
            for i in self.extract_dates(match.group(1)):
                yield {"date": i, "isOffDay": False}
            for i in self.extract_dates(match.group(2)):
                yield {"date": i, "isOffDay": True}

    def _parse_special(self):
        for i in self.special_cases.get(self.sentence, []):
            yield i

    parsing_methods = [
        _parse_rest_1,
        _parse_work_1,
        _parse_shift_1,
        _parse_special,
    ]


def parse_paper(year: int, url: str) -> Iterator[dict]:
    """Parse one paper

    Args:
        year (int): Year
        url (str): Paper url

    Returns:
        Iterator[dict]: Days
    """
    if url in PRE_PARSED_PAPERS:
        yield from PRE_PARSED_PAPERS[url]
        return
    paper = get_paper(url)
    rules = get_rules(paper)
    ret = (
        {"name": name, **i}
        for name, description in rules
        for i in DescriptionParser(description, year).parse()
    )
    try:
        for i in ret:
            yield i
    except NotImplementedError as ex:
        raise RuntimeError("Can not parse paper", url) from ex


def fetch_holiday(year: int):
    """Fetch holiday data."""

    papers = get_paper_urls(year)

    days = dict()

    for k in (j for i in papers for j in parse_paper(year, i)):
        days[k["date"]] = k

    return {
        "year": year,
        "papers": papers,
        "days": sorted(days.values(), key=lambda x: x["date"]),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("year", type=int)
    args = parser.parse_args()
    year = args.year

    print(
        json.dumps(
            fetch_holiday(year), indent=4, ensure_ascii=False, cls=CustomJSONEncoder
        )
    )


class CustomJSONEncoder(json.JSONEncoder):
    """Custom json encoder."""

    def default(self, o):
        # pylint:disable=method-hidden
        if isinstance(o, date):
            return o.isoformat()

        return super().default(o)


if __name__ == "__main__":
    main()
