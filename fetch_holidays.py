#!/usr/bin/env python3
"""Fetch holidays from gov.cn  """

import argparse
import json
import re
from datetime import date, timedelta
from typing import List

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
    assert all(
        re.match(
            r'http://www.gov.cn/zhengce/content/\d{4}-\d{2}/\d{2}/content_\d+.htm', i)
        for i in ret), 'Site changed, need human verify'

    return ret


def get_paper(url):
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = bs4.BeautifulSoup(response.text, features='html.parser')
    container = soup.find('td', class_='b12c')
    assert container, f'Can not get paper container from url: {url}'
    ret = container.get_text()
    assert ret, f'Can not get paper context from url: {url}'
    return ret


def get_rules(paper: str):
    lines: list = paper.splitlines()
    for i in sorted(set(lines), key=lines.index):
        match = re.match(r'[一二三四五六七八九十]、(.+?)：(.+)', i)
        if match:
            yield match.groups()


def _cast_int(value):
    return int(value) if value else None


class SentenceParser:
    """Parser for rule sentence. """

    def __init__(self, sentence, year):
        self.sentence = sentence
        self.year = year

    def extract_dates(self, value) -> List[date]:
        memory = set()
        for method in self.date_extraction_methods:
            for i in method(self, value):
                if i not in memory:
                    memory.add(i)
                    yield i

    def _extract_dates_1(self, value):
        match = re.match(r'(?:(\d+)年)?(?:(\d+)月)(\d+)日', value)
        if match:
            groups = [_cast_int(i) for i in match.groups()]
            assert len(groups) == 3, groups
            yield date(year=groups[0] or self.year,
                       month=groups[1], day=groups[2])

    def _extract_dates_2(self, value):
        match = re.match(
            r'(?:(\d+)年)?(?:(\d+)月)(\d+)日(?:至|-)(?:(\d+)年)?(?:(\d+)月)?(\d+)日', value)
        if match:
            groups = [_cast_int(i) for i in match.groups()]
            assert len(groups) == 6, groups
            start = date(year=groups[0] or self.year,
                         month=groups[1], day=groups[2])
            end = date(year=groups[3] or self.year,
                       month=groups[4] or groups[1], day=groups[5])
            for i in range((end - start).days + 1):
                yield start + timedelta(days=i)

    def _extract_dates_3(self, value):
        match = re.match(
            r'(?:(\d+)年)?(?:(\d+)月)(\d+)日(?:（[^）]+）)?(?:、(?:(\d+)年)?(?:(\d+)月)?(\d+)日(?:（[^）]+）)?)+', value)
        if match:
            groups = [_cast_int(i) for i in match.groups()]
            assert not (len(groups) % 3), groups
            year = self.year
            month = None
            day = None
            for i in range(0, len(groups), 3):
                year = groups[i] or year
                month = groups[i+1] or month
                day = groups[i+2]
                assert year
                assert month
                assert day
                yield date(year=year, month=month, day=day)

    date_extraction_methods = [
        _extract_dates_1,
        _extract_dates_2,
        _extract_dates_3
    ]

    def parse(self):
        date_memory = set()
        for method in self.parsing_methods:

            for i in method(self):
                if i['date'] in date_memory:
                    continue
                date_memory.add(i['date'])
                yield i

    def _parse_rest_1(self):
        match = re.match('(.+)放假(调休)?$', self.sentence)
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

    def _parse_work_2(self):
        match = re.match('(.+)公休日调至(.+)', self.sentence)
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
        _parse_work_2,
    ]


def parse_holiday_description(description: str, year: int):
    for i in re.split('，|。', description):
        for j in SentenceParser(i, year).parse():
            yield j


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('year', type=int)
    args = parser.parse_args()
    year = args.year
    papers = get_paper_urls(year)

    ret = []
    for i in papers:
        paper = get_paper(i)
        rules = get_rules(paper)
        for name, description in rules:
            ret.extend({
                'name': name,
                **j
            } for j in parse_holiday_description(description, year))

    print(json.dumps(ret, indent=4, ensure_ascii=False, cls=CustomJSONEncoder))


class CustomJSONEncoder(json.JSONEncoder):
    """Custom json encoder. """

    def default(self, o):
        # pylint:disable=method-hidden
        if isinstance(o, date):
            return o.isoformat()

        return super().default(o)


if __name__ == '__main__':
    main()
