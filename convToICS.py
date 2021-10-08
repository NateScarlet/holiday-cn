import datetime
import json
import uuid
from icalendar import Event, Calendar, Timezone, TimezoneStandard


def create_timezone():
    tz = Timezone()
    tz.add('TZID', 'Asia/Shanghai')

    tz_standard = TimezoneStandard()
    tz_standard.add('DTSTART', datetime.datetime(1970, 1, 1))
    tz_standard.add('TZOFFSETFROM', datetime.timedelta(hours=8))
    tz_standard.add('TZOFFSETTO', datetime.timedelta(hours=8))

    tz.add_component(tz_standard)
    return tz


def create_event(event_name, start, end):
    # 创建事件/日程
    event = Event()
    event.add('SUMMARY', event_name)

    dt_now = datetime.datetime.now()
    event.add('DTSTART', start)
    event.add('DTEND', end)
    # 创建时间
    event.add('DTSTAMP', dt_now)

    # UID保证唯一
    event['UID'] = str(uuid.uuid1()) + '/NateScarlet/holiday-cn'

    return event


def ranger(lst):
    if len(lst) == 0:
        return None, None

    if len(lst) == 1:
        return lst[0], lst[0]

    fr, to = lst[0], lst[0]
    for cur in lst[1:]:
        cur_date = datetime.datetime(*map(int, cur.get('date').split('-')))
        if (cur_date - datetime.datetime(*map(int, to.get('date').split('-')))).days == 1 \
                and cur.get('isOffDay') == to.get('isOffDay'):
            to = cur
        else:
            yield fr, to
            fr, to = cur, cur
    yield fr, to


def main(year):
    with open(f'{year}.json', 'r') as inf:
        data = json.loads(inf.read())

    cal = Calendar()
    cal.add('VERSION', '2.0')
    cal.add('METHOD', 'PUBLISH')
    cal.add('CLASS', 'PUBLIC')

    cal.add_component(create_timezone())

    for fr, to in ranger(data.get('days', [])):
        start = datetime.datetime(*map(int, fr.get('date').split('-')))
        end = datetime.datetime(*map(int, to.get('date').split('-')))
        end = end + datetime.timedelta(days=1)

        name = fr.get('name')
        if not fr.get('isOffDay'):
            name = "上班(补" + name + "假期)"
        else:
            name += "假期"
        cal.add_component(create_event(name, start, end))

    with open(f'{year}.ics', 'wb') as ics:
        ics.write(cal.to_ical())

