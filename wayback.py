#!/usr/bin/python3
import concurrent.futures
import configparser
import datetime

import json
import os
import re
import subprocess
import sys
import time
import requests
from urllib.parse import urlsplit, urlunsplit, parse_qs, urlparse, unquote
from pathlib import Path, PurePosixPath
from argparse import ArgumentParser
from os.path import basename

RESULTS_DIRECTORY = './wayback_results'

def create_working_folder(domain: str) -> str:
    """
    Creates the working folder

    :param domain: the domain for which this tool is being run
    :return: the path to the working directory
    """
    path = os.getcwd()
    now = datetime.datetime.now()

    if not os.path.exists(f"{path}/{RESULTS_DIRECTORY}/"):
        os.mkdir(f"{path}/{RESULTS_DIRECTORY}/")

    folder = f"{path}/{RESULTS_DIRECTORY}/{domain}_" + now.strftime("%Y-%m-%d_%H%M%S")

    try:
        os.mkdir(folder)
    except OSError:
        print("Creation of the directory %s failed" % path)

    return folder

def get_wayback_file(working_folder: str) -> str:
    return f"{working_folder}/wayback_urls.txt"


def search_wayback(working_folder: str, domain: str) -> None:
    """
    Searches wayback for URLs associated with the target domain and sub domains

    :param working_folder: the working folder
    :param domain: the domain context
    """
    response = requests.get(f"http://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=json&collapse=urlkey")
    json_data = json.loads(response.text)
    count = 0
    url_array = []
    for (key, value) in enumerate(json_data):
        if count > 0:
            if value[2].endswith(".jpg") \
                    or value[2].endswith(".jpeg") \
                    or value[2].endswith(".png") \
                    or value[2].endswith(".svg") \
                    or value[2].endswith(".css") \
                    or value[2].endswith(".woff2") \
                    or value[2].endswith(".woff") \
                    or value[2].endswith(".ttf") \
                    or value[2].endswith(".eot") \
                    or value[2].endswith(".gif"):
                continue
            url_array.append((value[1], value[4], value[2]))

        count += 1

    url_array.sort(key=lambda x: x[0])

    with open(get_wayback_file(working_folder), "a") as wayback_file:
        for value in url_array:
            wayback_file.writelines(f"{value[0]} - {value[1]} - {value[2]}\n")


def main():
    """
    Main program
    """
    parser = ArgumentParser()
    parser.add_argument("-d", "--domain", dest="domain", help="Domain to target")

    args = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        exit(1)

    folder = create_working_folder(args.domain)

    print(f"*** Working directory - {folder} ***")

    print("*** Searching wayback for URLs ***")
    search_wayback(folder, args.domain)


if __name__ == "__main__":
    main()
