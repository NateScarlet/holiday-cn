import datetime
from typing import Any, Iterator, Sequence, Text, Tuple
from icalendar import Event, Calendar, Timezone, TimezoneStandard


def _create_timezone():
    tz = Timezone()
    tz.add("TZID", "Asia/Shanghai")

    tz_standard = TimezoneStandard()
    tz_standard.add("DTSTART", datetime.datetime(1970, 1, 1))
    tz_standard.add("TZOFFSETFROM", datetime.timedelta(hours=8))
    tz_standard.add("TZOFFSETTO", datetime.timedelta(hours=8))

    tz.add_component(tz_standard)
    return tz


def _create_event(event_name, start, end):
    # 创建事件/日程
    event = Event()
    event.add("SUMMARY", event_name)

    event.add("DTSTART", start)
    event.add("DTEND", end)
    # 创建时间
    event.add("DTSTAMP", start)

    # UID保证唯一
    event["UID"] = f"{start}/{end}/NateScarlet/holiday-cn"

    return event


def _cast_date(v: Any) -> datetime.date:
    if isinstance(v, datetime.date):
        return v
    if isinstance(v, str):
        return datetime.date.fromisoformat(v)
    raise NotImplementedError("can not convert to date: %s" % v)


def _iter_date_ranges(days: Sequence[dict]) -> Iterator[Tuple[dict, dict]]:
    if len(days) == 0:
        return

    if len(days) == 1:
        yield days[0], days[0]
        return

    fr, to = days[0], days[0]
    for cur in days[1:]:
        if (_cast_date(cur["date"]) - _cast_date(to["date"])).days == 1 and cur[
            "isOffDay"
        ] == to["isOffDay"]:
            to = cur
        else:
            yield fr, to
            fr, to = cur, cur
    yield fr, to


def generate_ics(days: Sequence[dict], filename: Text) -> None:
    """Generate ics from days."""
    cal = Calendar()
    cal.add("X-WR-CALNAME", "中国法定节假日")
    cal.add("X-WR-CALDESC", "中国法定节假日数据，自动每日抓取国务院公告。")
    cal.add("VERSION", "2.0")
    cal.add("METHOD", "PUBLISH")
    cal.add("CLASS", "PUBLIC")

    cal.add_component(_create_timezone())

    days = sorted(days, key=lambda x: x["date"])

    for fr, to in _iter_date_ranges(days):
        start = _cast_date(fr["date"])
        end = _cast_date(to["date"]) + datetime.timedelta(days=1)

        name = fr["name"] + "假期"
        if not fr["isOffDay"]:
            name = "上班(补" + name + ")"
        cal.add_component(_create_event(name, start, end))

    with open(filename, "wb") as f:
        f.write(cal.to_ical())
