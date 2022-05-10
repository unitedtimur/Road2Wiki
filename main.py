import argparse
import validators

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Road2Wiki for searching path from A to B with rate limit and depth')
    argparser.add_argument('--start', type=str, required=True, help='Start page')
    argparser.add_argument('--finish', type=str, required=True, help='Last page')
    argparser.add_argument('--rate_limit', type=int, default=10, help='Number of restrictions per minute')
    argparser.add_argument('--depth', type=int, default=5, help='Depth for searching last page')
    args = argparser.parse_args()

    if not validators.url(args.start) or not validators.url(args.finish):
        print("Not valid link or links")
        exit(1)


