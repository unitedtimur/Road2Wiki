import argparse
from typing import Optional, Match

import validators
import re


# Function checks if is url is wiki url
def is_wiki_url(url: str) -> Optional[Match[str]]:
    return re.search('(https://).*(wiki).*(/wiki/)', url)


# Returns the lang prefix from url
def get_lang_prefix(url: str) -> str:
    return re.search(r'(https://)(.*?)(.wiki)', url).group(2)


# Find path from url A to url B
def find_wiki_path(start: str, finish: str, rate_limit: int, depth: int):
    pass


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

    print(find_wiki_path(args.start, args.finish, args.rate_limit, args.depth))

    exit(0)


if __name__ == '__main__':
    main()
