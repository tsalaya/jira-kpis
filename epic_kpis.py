#!/usr/bin/env python3

import argparse

import httplib2
from bs4 import BeautifulSoup as _bs


def get_epic_ux_rejections(epic_key, headers, from_status, to_status):
    from time import time
    # get current time in milliseconds
    milliseconds = int(time() * 1000)

    url = f"https://jira.teko.vn/browse/{epic_key}?page=com.atlassian.jira.plugin.system.issuetabpanels:changehistory-tabpanel&_={milliseconds}"

    headers['Referer'] = f'https://jira.teko.vn/browse/{epic_key}'

    h = httplib2.Http()
    (resp_headers, content) = h.request(
        url, "GET", headers=headers)

    _rejections = {}

    try:
        soup = _bs(content, 'html.parser')
        tds = soup.find_all('td', class_="activity-old-val")
    except ValueError as e:
        print(f"Invalid HTML: {e}")

    found_rows = [td for td in tds if (
            from_status.lower() in td.text.lower() and to_status.lower() in td.find_next_sibling('td').text.lower())]

    _rejections[epic_key] = len(found_rows)

    return _rejections


def build_headers():
    f = open("req_headers.txt", "r")
    req_headers = f.readlines()

    # remove the GET / ...
    del req_headers[0]

    header_dict = {}
    for r in req_headers:
        items = r.split(':')
        header_dict[items[0]] = items[1]

    header_dict['cache-control'] = 'no-cache'

    return header_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("epics")
    parser.add_argument("from_status")
    parser.add_argument("to_status")
    
    args = parser.parse_args()
    
    epics = args.epics
    _from_status = args.from_status
    _to_status = args.to_status

    # epic_keys = "TG-96,VHB-1669".split(",")
    epic_keys = epics.split(",")
    results = {}
    for k in epic_keys:
        rejections = get_epic_ux_rejections(k, headers=build_headers(), from_status=_from_status, to_status=_to_status)
        results[k] = rejections[k]

    print(results)
