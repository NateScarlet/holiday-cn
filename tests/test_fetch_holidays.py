"""Test module `fetch_holidays`.  """
import json
import sys

from fetch_holidays import CustomJSONEncoder, DescriptionParser, get_paper_urls, get_rules, get_paper

from .filetools import _file_path


def test_get_paper_urls():
    assert get_paper_urls(2019) == [
        'http://www.gov.cn/zhengce/content/2019-03/22/content_5375877.htm',
        'http://www.gov.cn/zhengce/content/2018-12/06/content_5346276.htm'
    ]


def test_get_patch_rules():
    assert(list(get_rules(get_paper('http://www.gov.cn/zhengce/content/2019-03/22/content_5375877.htm')))
           == [('劳动节', '2019年5月1日至4日放假调休，共4天。4月28日（星期日）、5月5日（星期日）上班。')])


def _normalize(iterable):
    return sorted(json.loads(json.dumps(list(iterable), cls=CustomJSONEncoder)),
                  key=lambda x: x['date'])


def _generate_tests():
    with open(_file_path('description_parsing_cases.json'), 'r', encoding='utf-8', ) as f:
        cases = json.load(f)

    def create_test(case):
        def _test():
            year, description, expected = case['year'], case['description'], case['expected']
            assert _normalize(DescriptionParser(
                description, year).parse()) == _normalize(expected), case
        return _test

    for index, case in enumerate(cases, 1):
        setattr(sys.modules[__name__],
                f'test_description_parser_{index}', create_test(case))


_generate_tests()
