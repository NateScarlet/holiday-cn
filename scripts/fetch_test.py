"""Test module `fetch_holidays`.  """
import json

import pytest

from fetch import (
    CustomJSONEncoder,
    DescriptionParser,
    get_paper,
    get_paper_urls,
    get_rules,
)

from filetools import workspace_path


def test_get_paper_urls():
    assert get_paper_urls(2019) == [
        "http://www.gov.cn/zhengce/zhengceku/2018-12/06/content_5346276.htm",
        "http://www.gov.cn/zhengce/zhengceku/2019-03/22/content_5375877.htm",
    ]


def test_get_rules():
    assert list(
        get_rules(
            get_paper(
                "http://www.gov.cn/zhengce/zhengceku/2019-03/22/content_5375877.htm"
            )
        )
    ) == [("劳动节", "2019年5月1日至4日放假调休，共4天。4月28日（星期日）、5月5日（星期日）上班。")]


def test_get_rules_2023():
    got = list(
        get_rules(
            get_paper(
                "http://www.gov.cn/zhengce/zhengceku/2022-12/08/content_5730844.htm"
            )
        )
    )
    assert got == [
        ("元旦", "2022年12月31日至2023年1月2日放假调休，共3天。"),
        ("春节", "1月21日至27日放假调休，共7天。1月28日（星期六）、1月29日（星期日）上班。"),
        ("清明节", "4月5日放假，共1天。"),
        ("劳动节", "4月29日至5月3日放假调休，共5天。4月23日（星期日）、5月6日（星期六）上班。"),
        ("端午节", "6月22日至24日放假调休，共3天。6月25日（星期日）上班。"),
        ("中秋节、国庆节", "9月29日至10月6日放假调休，共8天。10月7日（星期六）、10月8日（星期日）上班。"),
    ]


def _normalize(iterable):
    return sorted(
        json.loads(json.dumps(list(iterable), cls=CustomJSONEncoder)),
        key=lambda x: x["date"],
    )


def _description_parsing_cases():
    with open(
        workspace_path("scripts", "description_parsing_cases.json"),
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
