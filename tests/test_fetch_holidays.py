"""Test module `fetch_holidays`.  """
import json
import os
import sys

from fetch_holidays import CustomJSONEncoder, DescriptionParser

__dirname__ = os.path.abspath(os.path.dirname(__file__))


def _file_path(*other):

    return os.path.join(__dirname__, *other)


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
