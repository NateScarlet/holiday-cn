#!/usr/bin/env python3
# coding=utf-8

import sys
import calendar
from dominate.tags import *
from get_night_tradingdays import *


style_applied = '''
        body{
            font-family: verdana,arial,sans-serif;
            font-size: 20px;
        }
        table.gridtable {
            color: #333333;
            border-width: 1px;
            border-color: #666666;
            border-collapse: collapse;
            font-size: 20px;
        }
        table.gridtable th {
            border-width: 1px;
            padding: 8px;
            border-style: solid;
            border-color: #666666;
            background-color: #DDEBF7;
            width: 120px;
            height: 80px;
        }
        table.gridtable td {
            border-width: 1px;
            padding: 8px;
            border-style: solid;
            border-color: #666666;
            background-color: #ffffff;
            text-align: center;
            height: 80px;
        }
        table.gridtable td.failed {
            color: #ED5F5F;
        }
        table.gridtable td.passrate {
            font-weight: bold;
            color: green;
        }
        li {
            margin-top: 5px;
        }
        div{
            margin-top: 10px;
        }
    '''


def set_table_head(title_name):
    with tr():
        th(title_name, colspan="7")
    with tr():
        th("周一")
        th("周二")
        th("周三")
        th("周四")
        th("周五")
        th("周六")
        th("周日")

def fill_table_data(day_name):
    #return tr(td(dn, __pretty=False) for dn in day_name)
    with tr() as data_tr:
        for dn in day_name:
            if dn == 0:
                td()
                continue
            if isinstance(dn, tuple) and len(dn) == 2:
                td(dn[0], br(), dn[1])
            elif isinstance(dn, tuple) and len(dn) == 3:
                td(dn[0], br(), dn[1], cls='passrate')
            else:
                td(dn)
    return data_tr

def generate_result_table_monthly(year, month, tradingdays_mapping, not_working_dates):
    ym = f"{year}-{month:02d}"
    ym_cn = f"{year}年{month}月"
    month_calendar = calendar.monthcalendar(year, month)
    tradingday_list = list(tradingdays_mapping.keys())
    
    result_div = div(id=ym)
    with result_div.add(table(cls='gridtable')).add(tbody()):
        set_table_head(ym_cn)
        for week_cal in month_calendar:
            for i in range(7):
                date_cal = f"{year}-{month:02d}-{week_cal[i]:02d}"
                if date_cal in tradingday_list:
                    if date_cal in not_working_dates:
                        week_cal[i] = (week_cal[i], tradingdays_mapping.get(date_cal), 'green')
                    else:
                        week_cal[i] = (week_cal[i], tradingdays_mapping.get(date_cal))
            fill_table_data(week_cal)
    result_div += br()
    result_div += br()
    return result_div

def generate_html_calendar(year, names, mapping, dates):
    # html init
    html_root = html(lang="zh")
    # html head
    with html_root.add(head()):
        meta(content="text/html; charset=utf-8", http_equiv="Content-Type")
        style(style_applied, type='text/css')
    # html body
    with html_root.add(body()):
        for i in range(12):
            i += 1
            generate_result_table_monthly(year, i, mapping, dates)
    return html_root


if __name__ == "__main__":
    names = ['Aa', 'Bb', 'Cc', 'Dd', 'Ee']
    year = sys.argv[1]
    if not year:
        year = 2023
    else:
        year = int(year)
    # night tradingdays
    night_tradingdays_mapping, not_working_dates = generate_night_tradingdays_mapping(year=year, names=names)
    # html txt
    html_txt = generate_html_calendar(year, names, night_tradingdays_mapping, not_working_dates)

    # save as html file
    with open(f'../{year}.html', 'w') as f:
        f.write(html_txt.render())

