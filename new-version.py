#!/usr/bin/env python3

# pylint: disable=invalid-name,missing-module-docstring

import argparse
import fileinput
import logging
import pathlib
import re
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

def check_file(input_file: pathlib.Path):
    """
    Check if the given file exists, exit if it does not.
    """
    if not input_file.is_file():
        die(f"{input_file} does not exist")

def format_date(the_date: datetime) -> str:
    """
    Returns a formatted date string.
    """
    day_endings = {
        1: 'st',
        2: 'nd',
        3: 'rd',
        21: 'st',
        22: 'nd',
        23: 'rd',
        31: 'st'
    }

    return the_date.strftime("%-d{ORD} %B %Y").replace(
        "{ORD}", day_endings.get(the_date.day, "th")
    )

def die(msg: str) -> None:
    """
    Log error message and exit.
    """
    logging.error(msg)
    sys.exit(1)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Checks for new Slurm version and updates repo files as required",
        add_help=True
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Turn on debug messages",
        dest="verbose",
        action="store_true"
    )
    args = parser.parse_args()

    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG

    logging.basicConfig(format='%(message)s', level=log_level)

    current_dir = pathlib.Path(__file__).parents[0]
    version_file = current_dir / "current_version"
    check_file(version_file)

    with open(version_file, mode="r", encoding="utf-8") as f:
        current_version = f.readline().strip()

    url = "https://schedmd.com/downloads.php"
    logging.debug("loading %s", url)
    reqs = requests.get(url, timeout=20)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    download_re = re.compile(
        r"^https://download.schedmd.com/slurm/slurm-([0-9]+\.[0-9]+\.[0-9]+).tar.bz2$"
    )
    latest_version = None

    for link in soup.find_all('a'):
        link = link.get("href")
        match = download_re.match(link)
        if match:
            latest_version = match.group(1)

    if latest_version is None:
        die("could not determine Slurm version")

    logging.info("latest version is: %s", latest_version)
    logging.info("version used by this repo: %s", current_version)

    if current_version == latest_version:
        logging.info("nothing to do")
        sys.exit(0)

    major_version = latest_version.split('.', 1)[0]

    changelog_file = current_dir / "CHANGELOG.md"
    conf_file = current_dir / f"slurm.{major_version}.conf"
    docker_file = current_dir / "Dockerfile"
    readme_file = current_dir / "README.md"
    for f in [changelog_file, conf_file, docker_file, readme_file]:
        check_file(f)

    logging.info("patching %s", docker_file)
    with fileinput.FileInput(str(docker_file), True) as f:
        search_str = f"ARG SLURM_VER={current_version}\n"
        for line in f:
            if line == search_str:
                print(f"ARG SLURM_VER={latest_version}", end="\n")
            else:
                print(f"{line}", end="")

    logging.info("patching %s", readme_file)
    with fileinput.FileInput(str(readme_file), True) as f:
        for line in f:
            line = line.replace(current_version, latest_version)
            print(f"{line}", end="")

    logging.info("adding changelog entry")
    # check if entry already exists
    changelog_lines = ""
    first_entry_found = False
    with open(changelog_file, mode="r", encoding="utf-8") as f:
        search_re = re.compile(latest_version)
        while True:
            line = f.readline()
            if not line:
                break
            match = search_re.search(line)
            if match:
                die(f"changelog already has an entry for SLURM {latest_version}")
            if line.startswith("## "):
                first_entry_found = True
            if first_entry_found:
                changelog_lines += line

    date_str = format_date(datetime.now())
    with open(changelog_file, mode="w", encoding="utf-8") as f:
        f.write("# Change log\n\n")
        f.write(f"## {date_str}\n\n")
        f.write(f"* Added support for Slurm {latest_version}\n\n")
        f.write(changelog_lines)

    logging.info("updating current_version file")
    with open(version_file, mode="w", encoding="utf-8") as f:
        f.write(latest_version)

    logging.info("done")
    sys.exit(0)
