import datetime
from icalendar import Event, Calendar, Timezone, TimezoneStandard


def create_timezone():
    tz = Timezone()
    tz.add("TZID", "Asia/Shanghai")

    tz_standard = TimezoneStandard()
    tz_standard.add("DTSTART", datetime.datetime(1970, 1, 1))
    tz_standard.add("TZOFFSETFROM", datetime.timedelta(hours=8))
    tz_standard.add("TZOFFSETTO", datetime.timedelta(hours=8))

    tz.add_component(tz_standard)
    return tz


def create_event(event_name, start, end):
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


def ranger(lst):
    if len(lst) == 0:
        return []

    if len(lst) == 1:
        return [(lst[0], lst[0])]

    fr, to = lst[0], lst[0]
    for cur in lst[1:]:
        if (cur.get("date") - to.get("date")).days == 1 and cur.get(
            "isOffDay"
        ) == to.get("isOffDay"):
            to = cur
        else:
            yield fr, to
            fr, to = cur, cur
    yield fr, to


def generate_ics(data, filename):
    """
    将爬取的节假日JSON数据转换为ICS

    Args:
        filename: str
        data: from `fetch_holiday`
    """
    cal = Calendar()
    cal.add("VERSION", "2.0")
    cal.add("METHOD", "PUBLISH")
    cal.add("CLASS", "PUBLIC")

    cal.add_component(create_timezone())

    days = data.get("days", [])
    for day in days:
        if isinstance(day.get("date"), str):
            day["date"] = datetime.date(*map(int, day["date"].split("-")))

    for fr, to in ranger(days):
        start = fr.get("date")
        end = to.get("date") + datetime.timedelta(days=1)

        name = fr.get("name") + "假期"
        if not fr.get("isOffDay"):
            name = "上班(补" + name + ")"
        cal.add_component(create_event(name, start, end))

    with open(f"{filename}.ics", "wb") as ics:
        ics.write(cal.to_ical())
