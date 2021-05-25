import os
from argparse import ArgumentParser
from pyspark.sql import SparkSession
from crawler import Crawler
from storage import Storage

APP_NAME = os.environ['APP_NAME']
SPARK_MASTER = os.environ['SPARK_MASTER']
DESCRIPTION = """
Crawl recursively a list of urls to find how many different references of
external pages were found. A maximum depth N must be passed as argument,
which represents how many iterations the crawler will make.
"""


def build_parser():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        '-u',
        '--urls',
        required=True,
        type=lambda u: [url.rstrip('/') for url in u.split(',')],
        help='List of urls separated by comma (ex: URLS=https://foo.com,https://bar.com)'
    )
    parser.add_argument(
        '-d',
        '--depth',
        required=True,
        type=int,
        help='Recursive crawling depth'
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    spark = SparkSession.builder \
        .master(SPARK_MASTER) \
        .appName(f'{APP_NAME}-crawler') \
        .getOrCreate()

    crawler = Crawler(
        spark=spark,
        storage=Storage(spark)
    )
    crawler.execute(
        urls=args.urls,
        depth=args.depth
    )

    spark.stop()


if __name__ == "__main__":
    main()
