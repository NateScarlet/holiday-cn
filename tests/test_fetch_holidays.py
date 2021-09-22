"""Test module `fetch_holidays`.  """
import json

import pytest

from fetch_holidays import (
    CustomJSONEncoder,
    DescriptionParser,
    get_paper,
    get_paper_urls,
    get_rules,
)

from .filetools import _file_path


def test_get_paper_urls():
    assert get_paper_urls(2019) == [
        "http://www.gov.cn/zhengce/content/2018-12/06/content_5346276.htm",
        "http://www.gov.cn/zhengce/content/2019-03/22/content_5375877.htm",
    ]


def test_get_rules():
    assert list(
        get_rules(
            get_paper(
                "http://www.gov.cn/zhengce/content/2019-03/22/content_5375877.htm"
            )
        )
    ) == [("劳动节", "2019年5月1日至4日放假调休，共4天。4月28日（星期日）、5月5日（星期日）上班。")]


def _normalize(iterable):
    return sorted(
        json.loads(json.dumps(list(iterable), cls=CustomJSONEncoder)),
        key=lambda x: x["date"],
    )


def _description_parsing_cases():
    with open(
        _file_path("description_parsing_cases.json"),
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


@pytest.mark.parametrize("case", _description_parsing_cases())
def test_parse_description(case):

    year, description, expected = case["year"], case["description"], case["expected"]
    assert _normalize(DescriptionParser(description, year).parse()) == _normalize(
        expected
    ), case
