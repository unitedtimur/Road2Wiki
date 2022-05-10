from typing import Optional, Match
from bs4 import BeautifulSoup
from ratelimiter import RateLimiter

import argparse
import validators
import re
import urllib.parse
import copy
import queue
import numpy as np
import requests


# Function checks if is url is wiki url
def is_wiki_url(url: str) -> Optional[Match[str]]:
    return re.search('(https://).*(wiki).*(/wiki/)', url)


# Returns the lang prefix from url
def get_lang_prefix(url: str) -> str:
    return re.search(r'(https://)(.*?)(.wiki)', url).group(2)


# Return urls from url by content
def get_urls_from_url(page_content):
    beautiful_oup = BeautifulSoup(page_content, 'html.parser')
    f_page_content = beautiful_oup.find(id="bodyContent")

    if f_page_content:
        return np.array([urllib.parse.unquote_plus(url['href']) for url in f_page_content.find_all('a', href=True)])

    return np.empty()


# Returns full url in wiki format
def get_full_wiki_url(url: str, lang_prefix: str):
    if 'https' not in url:
        return 'https://' + lang_prefix + '.wikipedia.org' + url
    elif 'http' not in url:
        return 'http://' + lang_prefix + '.wikipedia.org' + url
    return url


# Find path from url A to url B
def find_wiki_path(start: str, finish: str, rate_limit: int, depth: int, lang_prefix: str) -> object:
    f_urls = queue.Queue()
    tmp_urls = queue.Queue()
    tmp_depth = 0
    urls = {start: ''}
    start = urllib.parse.unquote_plus(start)
    finish = urllib.parse.unquote_plus(finish)
    tmp_urls.put(start)

    while not tmp_urls.empty():
        f_urls.queue = copy.copy(tmp_urls.queue)
        tmp_urls.queue.clear()
        tmp_depth = tmp_depth + 1
        print(f'Depth now %s' % tmp_depth)

        process = 0

        while not f_urls.empty():
            f_url = f_urls.get()
            process = process + 1
            print('Processing url %s in %s' % (f_url, process))

            @RateLimiter(max_calls=rate_limit, period=60)
            def get_content_by_url(link):
                try:
                    response = requests.get(link)
                    if response.reason == 'OK':
                        return response.content
                    return ''
                except Exception as e:
                    print(e)
                    return ''
            content = get_content_by_url(f_url)

            if content:
                for n_url in get_urls_from_url(content):
                    n_url = get_full_wiki_url(n_url, lang_prefix)

                    if is_wiki_url(n_url):
                        if n_url == finish:
                            path = [finish, f_url]
                            url = urls[f_url]

                            while url:
                                path.append(url)
                                url = urls[url]

                            return path[::-1]

                        if (n_url not in urls) and tmp_depth != depth:
                            urls[n_url] = f_url
                            tmp_urls.put(n_url)

        print("\n")

    return []


# Main function
def main() -> None:
    arg_parser = argparse.ArgumentParser(
        description='Road2Wiki for searching path from A to B with rate limit and depth')
    arg_parser.add_argument('--start', type=str, required=True, help='Start page')
    arg_parser.add_argument('--finish', type=str, required=True, help='Last page')
    arg_parser.add_argument('--rate_limit', type=int, default=10, help='Number of restrictions per minute')
    arg_parser.add_argument('--depth', type=int, default=5, help='Depth for searching last page')
    args = arg_parser.parse_args()

    if not validators.url(args.start) or not validators.url(args.finish) or not is_wiki_url(args.start) \
            or not is_wiki_url(args.finish):
        print("Valid/s not valid")
        exit(1)

    start_prefix = get_lang_prefix(args.start)
    finish_prefix = get_lang_prefix(args.finish)

    if start_prefix != finish_prefix:
        print("Prefix is not equal")
        exit(2)

    path = find_wiki_path(args.start, args.finish, args.rate_limit, args.depth, start_prefix)

    if len(path) == 0:
        print("No path")
        exit(3)

    print("\nPath founded")

    result = str()

    for i in range(0, len(path)):
        result = result + path[i]

        if i != len(path) - 1:
            result = result + str(" => ")

    print(result)

    exit(0)


if __name__ == '__main__':
    main()
