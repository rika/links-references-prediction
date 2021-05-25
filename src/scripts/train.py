import os
from argparse import ArgumentParser
from pyspark.sql import SparkSession
from storage import Storage
from crawler import Crawler
from ml import RandomForestTrainer

APP_NAME = os.environ['APP_NAME']
SPARK_MASTER = os.environ['SPARK_MASTER']
DESCRIPTION = """
Train a prediction model utilizing a Random Forest regression algorithm.
"""


def build_parser():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        '-n',
        '--num-trees',
        required=True,
        type=int,
        help='Random Forest number of trees param'
    )
    parser.add_argument(
        '-d',
        '--max-depth',
        required=True,
        type=int,
        help='Random Forest max depth param'
    )
    parser.add_argument(
        '-s',
        '--split-seed',
        required=False,
        type=int,
        help='Random Split seed'
    )
    return parser


def main():
    parser = build_parser()
    args_dict = vars(parser.parse_args())

    spark = SparkSession.builder \
        .master(SPARK_MASTER) \
        .appName(f'{APP_NAME}-trainer') \
        .getOrCreate()

    storage = Storage(spark)
    trainer = RandomForestTrainer(spark, storage)
    trainer.execute(
        appearances_table=Crawler.appearances_table,
        features_table=Crawler.features_table,
        features_cols=Crawler.features_cols,
        **args_dict
    )

    spark.stop()


if __name__ == "__main__":
    main()
