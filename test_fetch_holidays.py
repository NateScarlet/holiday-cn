
import json
import sys

from fetch_holidays import CustomJSONEncoder, parse_holiday_description


def _normalize(iterable):
    return sorted(json.loads(json.dumps(list(iterable), cls=CustomJSONEncoder)), key=lambda x: x['date'])


def _generate_tests():
    with open('description_parsing_cases.json', 'r', encoding='utf-8', ) as f:
        cases = json.load(f)

    def create_test(case):
        def _test():
            year, description, expected = case['year'], case['description'], case['expected']
            assert _normalize(parse_holiday_description(
                description, year)) == _normalize(expected), case
        return _test

    for index, case in enumerate(cases, 1):
        setattr(sys.modules[__name__],
                f'test_parse_holiday_description_{index}', create_test(case))


_generate_tests()
