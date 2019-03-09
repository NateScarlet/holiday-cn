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

SEARCH_URL = ('http://sousuo.gov.cn/s.htm'
              '?t=paper&advance=true&sort=&title={year}+%E8%8A%82%E5%81%87%E6%97%A5'
              '&puborg=%E5%9B%BD%E5%8A%A1%E9%99%A2%E5%8A%9E%E5%85%AC%E5%8E%85'
              '&pcodeJiguan=%E5%9B%BD%E5%8A%9E%E5%8F%91%E6%98%8E%E7%94%B5')


def get_paper_urls(year: int) -> List[str]:
    """Find year related paper urls.

    Args:
        year (int): eg. 2018

    Returns:
        List[str]: Urls
    """

    url = SEARCH_URL.format(year=year)
    body = requests.get(url).text
    ret = re.findall(
        r'<li class="res-list".*?<a href="(.+?)".*?</li>', body, flags=re.S)

    return ret


def get_paper(url: str) -> str:
    """Extract paper text from url.

    Args:
        url (str): Paper url.

    Returns:
        str: Extracted paper text.
    """

    assert re.match(r'http://www.gov.cn/zhengce/content/\d{4}-\d{2}/\d{2}/content_\d+.htm',
                    url), 'Site changed, need human verify'

    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = bs4.BeautifulSoup(response.text, features='html.parser')
    container = soup.find('td', class_='b12c')
    assert container, f'Can not get paper container from url: {url}'
    ret = container.get_text().replace('\u3000\u3000', '\n')
    assert ret, f'Can not get paper context from url: {url}'
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
    count = 0
    for i in sorted(set(lines), key=lines.index):
        match = re.match(r'[一二三四五六七八九十]、(.+?)：(.+)', i)
        if match:
            count += 1
            yield match.groups()

    if not count:
        raise NotImplementedError(lines)


def _cast_int(value):
    return int(value) if value else None


class DescriptionParser:
    """Parser for holiday shift description.  """

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
        for i in re.split('[，。；]', self.description):
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

        assert day, 'No day specified'

        # Special case: month inherit
        if month is None:
            month = self.date_history[-1].month

        # Special case: 12 month may mean previous year
        if (year is None
                and month == 12
                and self.date_history
                and max(self.date_history) < date(year=self.year, month=2, day=1)):
            year = self.year - 1

        year = year or self.year
        return date(year=year, month=month, day=day)


class SentenceParser:
    """Parser for holiday shift description sentence. """

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
        text = text.replace('(', '（').replace(')', '）')
        for i in chain(*(method(self, text) for method in self.date_extraction_methods)):
            count += 1
            is_seen = i in self.parent.date_history
            self.parent.date_history.append(i)
            if is_seen:
                continue
            yield i

        if not count:
            raise NotImplementedError(text)

    def _extract_dates_1(self, value: str) -> Iterator[date]:
        match = re.findall(r'(?:(\d+)年)?(?:(\d+)月)?(\d+)日', value)
        for groups in match:
            groups = [_cast_int(i) for i in groups]
            assert len(groups) == 3, groups
            yield self.parent.get_date(year=groups[0], month=groups[1], day=groups[2])

    def _extract_dates_2(self, value: str)-> Iterator[date]:
        match = re.findall(
            r'(?:(\d+)年)?(?:(\d+)月)?(\d+)日(?:至|-|—)(?:(\d+)年)?(?:(\d+)月)?(\d+)日', value)
        for groups in match:
            groups = [_cast_int(i) for i in groups]
            assert len(groups) == 6, groups
            start = self.parent.get_date(year=groups[0],
                                         month=groups[1], day=groups[2])
            end = self.parent.get_date(year=groups[3],
                                       month=groups[4], day=groups[5])
            for i in range((end - start).days + 1):
                yield start + timedelta(days=i)

    def _extract_dates_3(self, value: str)-> Iterator[date]:
        match = re.findall(
            r'(?:(\d+)年)?(?:(\d+)月)?(\d+)日(?:（[^）]+）)?'
            r'(?:、(?:(\d+)年)?(?:(\d+)月)?(\d+)日(?:（[^）]+）)?)+',
            value)
        for groups in match:
            groups = [_cast_int(i) for i in groups]
            assert not (len(groups) % 3), groups
            for i in range(0, len(groups), 3):
                yield self.parent.get_date(year=groups[i], month=groups[i+1], day=groups[i+2])

    date_extraction_methods = [
        _extract_dates_1,
        _extract_dates_2,
        _extract_dates_3
    ]

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
        match = re.match(r'(.+)(放假|补休|调休|公休)+(?:\d+天)?$', self.sentence)
        if match:
            for i in self.extract_dates(match.group(1)):
                yield {
                    'date': i,
                    'isOffDay': True
                }

    def _parse_work_1(self):
        match = re.match('(.+)上班$', self.sentence)
        if match:
            for i in self.extract_dates(match.group(1)):
                yield {
                    'date': i,
                    'isOffDay': False
                }

    def _parse_shift_1(self):
        match = re.match('(.+)调至(.+)', self.sentence)
        if match:
            for i in self.extract_dates(match.group(1)):
                yield {
                    'date': i,
                    'isOffDay': False
                }
            for i in self.extract_dates(match.group(2)):
                yield {
                    'date': i,
                    'isOffDay': True
                }

    parsing_methods = [
        _parse_rest_1,
        _parse_work_1,
        _parse_shift_1,
    ]


def fetch_holiday(year: int):
    """Fetch holiday data.  """

    papers = get_paper_urls(year)

    days = []
    for i in papers:
        paper = get_paper(i)
        rules = get_rules(paper)
        for name, description in rules:
            days.extend({
                'name': name,
                **j
            } for j in DescriptionParser(description, year).parse())
    return {
        'year': year,
        'papers': papers,
        'days': sorted(days, key=lambda x: x['date'])
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('year', type=int)
    args = parser.parse_args()
    year = args.year

    print(json.dumps(fetch_holiday(year),
                     indent=4,
                     ensure_ascii=False,
                     cls=CustomJSONEncoder))


class CustomJSONEncoder(json.JSONEncoder):
    """Custom json encoder. """

    def default(self, o):
        # pylint:disable=method-hidden
        if isinstance(o, date):
            return o.isoformat()

        return super().default(o)


if __name__ == '__main__':
    main()
