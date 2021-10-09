#!/usr/bin/env python3
"""Script for updating data. """

import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timedelta, tzinfo
from tempfile import mkstemp
from zipfile import ZipFile

from tqdm import tqdm

from fetch_holidays import CustomJSONEncoder, fetch_holiday
from generate_ics import generate_ics


class ChinaTimezone(tzinfo):
    """Timezone of china."""

    def tzname(self, dt):
        return "UTC+8"

    def utcoffset(self, dt):
        return timedelta(hours=8)

    def dst(self, dt):
        return timedelta()


__dirname__ = os.path.abspath(os.path.dirname(__file__))


def _file_path(*other):

    return os.path.join(__dirname__, *other)


def update_data(year: int) -> str:
    """Update and store data for a year.

    Args:
        year (int): Year

    Returns:
        str: Stored data path
    """

    filename = _file_path(f"{year}.json")
    with open(filename, "w", encoding="utf-8", newline="\n") as f:
        data = fetch_holiday(year)

        json.dump(
            dict(
                (
                    (
                        "$schema",
                        "https://raw.githubusercontent.com/NateScarlet/holiday-cn/master/schema.json",
                    ),
                    (
                        "$id",
                        f"https://raw.githubusercontent.com/NateScarlet/holiday-cn/master/{year}.json",
                    ),
                    *data.items(),
                )
            ),
            f,
            indent=4,
            ensure_ascii=False,
            cls=CustomJSONEncoder,
        )

        generate_ics(data, filename=f"{year}.ics")
    return filename


def update_holiday_ics(fr_year, to_year):
    big_days = []
    for year in range(fr_year, to_year + 1):
        filename = _file_path(f"{year}.json")
        if not os.path.isfile(filename):
            continue
        with open(filename, "r", encoding="utf8") as inf:
            data = json.loads(inf.read())
            big_days.extend(data.get("days"))

    generate_ics(
        {"days": sorted(big_days, key=lambda x: x["date"])},
        filename="holiday-cn.ics",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--all",
        action="store_true",
        help="Update all years since 2007, default is this year and next year",
    )
    parser.add_argument(
        "--release",
        action="store_true",
        help="create new release if repository data is not up to date",
    )
    args = parser.parse_args()

    now = datetime.now(ChinaTimezone())
    is_release = args.release

    filenames = []
    progress = tqdm(range(2007 if args.all else now.year, now.year + 2))
    for i in progress:
        progress.set_description(f"Updating {i} data")
        filename = update_data(i)
        filenames.append(filename)
    print("")

    update_holiday_ics(now.year - 4, now.year + 1)

    subprocess.run(["hub", "add", *filenames], check=True)
    diff = subprocess.run(
        ["hub", "diff", "--stat", "--cached", "*.json", "*.ics"],
        check=True,
        stdout=subprocess.PIPE,
        encoding="utf-8",
    ).stdout
    if not diff:
        print("Already up to date.")
        return

    if not is_release:
        print("Updated repository data, skip release since not specified `--release`")
        return

    subprocess.run(["hub", "commit", "-m", "Update holiday data [skip ci]"], check=True)
    subprocess.run(["hub", "push"], check=True)

    tag = now.strftime("%Y.%m.%d")
    temp_note_fd, temp_note_name = mkstemp()
    with open(temp_note_fd, "w", encoding="utf-8") as f:
        f.write(tag + "\n\n```diff\n" + diff + "\n```\n")
    os.makedirs(_file_path("dist"), exist_ok=True)
    zip_path = _file_path("dist", f"holiday-cn-{tag}.zip")
    pack_data(zip_path)

    subprocess.run(
        [
            "hub",
            "release",
            "create",
            "-F",
            temp_note_name,
            "-a",
            f"{zip_path}#JSON数据",
            tag,
        ],
        check=True,
    )
    os.unlink(temp_note_name)


def pack_data(file):
    """Pack data json in zip file."""

    zip_file = ZipFile(file, "w")
    for i in os.listdir(__dirname__):
        if not re.match(r"\d+\.json", i):
            continue
        zip_file.write(_file_path(i), i)


if __name__ == "__main__":
    main()
