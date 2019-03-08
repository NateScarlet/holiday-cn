#!/usr/bin/env python3
import json
import os
import subprocess
from datetime import datetime, timedelta, tzinfo

from fetch_holidays import CustomJSONEncoder, fetch_holiday


class ChinaTimezone(tzinfo):
    """Timezone of china.  """

    def tzname(self, dt):
        return 'UTC+8'

    def utcoffset(self, dt):
        return timedelta(hours=8)

    def dst(self, dt):
        return timedelta()


__dirname__ = os.path.abspath(os.path.dirname(__file__))


def _file_path(*other):

    return os.path.join(__dirname__, *other)


def update_data(year):
    filename = _file_path(f'{year}.json')
    with open(filename, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(fetch_holiday(year), f,
                  indent=4,
                  ensure_ascii=False,
                  cls=CustomJSONEncoder)
    return filename


def main():
    now = datetime.now(ChinaTimezone())

    filenames = []
    filenames.append(update_data(now.year))
    filenames.append(update_data(now.year + 1))

    subprocess.run(['git', 'add', *filenames], check=True)
    diff = subprocess.run(['git', 'diff', '--stat', '--cached'],
                          check=True,
                          stdout=subprocess.PIPE,
                          encoding='utf-8').stdout
    if not diff:
        print('Already up to date.')
        return

    subprocess.run(
        ['git', 'commit', '-m', 'Update data [skip ci]\n\n' + diff], check=True)
    subprocess.run(['git', 'tag', now.strftime('%Y.%m.%d')], check=True)
    subprocess.run(['git', 'push'], check=True)
    subprocess.run(['git', 'push', '--tags'], check=True)


if __name__ == '__main__':
    main()
