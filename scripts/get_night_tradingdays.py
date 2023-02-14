"""Test module `fetch_holidays`.  """
from collections import defaultdict
from datetime import datetime
from fetch import *


def get_last_weekday(day=date.today):
    now=day
    if now.isoweekday()==1:
      day_step=3
    else:
      day_step=1
    last_weekday = now - timedelta(days=day_step)
    return last_weekday

def process_holidays(holiday_cn_days):
    processed_holidays = {}
    for holiday in holiday_cn_days:
        if holiday['isOffDay']:
            if holiday['name'] in processed_holidays:
                processed_holidays[holiday['name']]['date'].append(holiday['date'])
            else:
                processed_holidays[holiday['name']] = {'name': holiday['name'], 'date': [holiday['date']]}
    return list(processed_holidays.values())

def get_night_tradingdays(year):
    festival_days_and_last_weekday = []
    holiday_cn = fetch_holiday(year)
    holiday_cn_days_grouping = process_holidays(holiday_cn['days'])
    for festival in holiday_cn_days_grouping:
        festival_days = festival['date']
        last_weekday = get_last_weekday(festival_days[0])
        festival_days_and_last_weekday.append(last_weekday)
        festival_days_and_last_weekday.extend(festival_days)
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    night_working_dates = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5 and current_date not in festival_days_and_last_weekday:
            night_working_dates.append(current_date)
        current_date += timedelta(days=1)
    night_working_dates_formatted = [date.strftime("%Y-%m-%d") for date in night_working_dates]
    return night_working_dates_formatted

def generate_night_tradingdays_mapping(year, names=['A','B','C','D','E']):
    nigth_tradingdays = get_night_tradingdays(year)
    result = {}
    for i in range(0, len(nigth_tradingdays), 5):
        temp = dict(zip(nigth_tradingdays[i:i+5], names))
        result.update(temp)
        names = names[1:] + [names[0]]
    return result


if __name__ == '__main__':
    year = 2023
    names = ['A', 'B', 'C', 'D', 'E']

    temp = generate_night_tradingdays_mapping(year=year, names=names)
    print(temp)
