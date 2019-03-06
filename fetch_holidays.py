#!/usr/bin/env python3
"""Fetch holidays from gov.cn  """

import argparse
import re

import bs4
import requests

SEARCH_URL = ('http://sousuo.gov.cn/s.htm'
              '?t=paper&advance=true&sort=&title={year}+%E8%8A%82%E5%81%87%E6%97%A5'
              '&puborg=%E5%9B%BD%E5%8A%A1%E9%99%A2%E5%8A%9E%E5%85%AC%E5%8E%85'
              '&pcodeJiguan=%E5%9B%BD%E5%8A%9E%E5%8F%91%E6%98%8E%E7%94%B5')


def get_paper_urls(year):
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


def parse_holiday_description(year, description):
    pass


def parse_paper(url):
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('year')
    args = parser.parse_args()

    papers = get_paper_urls(args.year)

    for i in papers:
        paper = get_paper(i)
        [print(i) for i in get_rules(paper)]


if __name__ == '__main__':
    main()
