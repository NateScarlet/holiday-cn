
import json
import sys

from fetch_holidays import parse_holiday_description


def _generate_tests():
    with open('description_parsing_cases.json', 'r', encoding='utf-8', ) as f:
        cases = json.load(f)

    def create_test(case):
        def _test():
            year, description, expected = case['year'], case['description'], case['expected']
            assert parse_holiday_description(
                year, description) == expected, case
        return _test

    for index, case in enumerate(cases, 1):
        setattr(sys.modules[__name__],
                f'test_parse_holiday_description_{index}', create_test(case))


_generate_tests()
