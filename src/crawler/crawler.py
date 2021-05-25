from pyspark.sql.functions import explode, udf, lit, sum, col, array
from pyspark.sql.types import IntegerType, Row, StringType, StructType, StructField, LongType, ArrayType
from scraper import Scraper, NoStatusCode200
from parsers import \
    CharactersCountParser, \
    ImagesCountParser, \
    UniqueLinksCountParser, \
    UniqueLinksParser, \
    UrlLengthParser, \
    WordsCountParser


def parse(parser, args):
    url, html = args
    return parser.parse(url, html)


class Crawler():
    def __init__(self, spark, storage=None):
        self.__spark = spark
        self.__storage = storage

    appearances_table = 'appearances'
    features_table = 'features'
    features_cols = [
        'characters_count',
        'images_count',
        'links_count',
        'url_length',
        'words_count',
    ]

    @udf(returnType=StringType())
    def __udf_scrap(url):
        try:
            scraper = Scraper()
            return scraper.execute(url)
        except NoStatusCode200:
            return None

    @udf(returnType=IntegerType())
    def __udf_characters_count(args):
        return parse(CharactersCountParser(), args)

    @udf(returnType=IntegerType())
    def __udf_images_count(args):
        return parse(ImagesCountParser(), args)

    @udf(returnType=ArrayType(StringType()))
    def __udf_unique_links(args):
        return parse(UniqueLinksParser(), args)

    @udf(returnType=IntegerType())
    def __udf_unique_links_count(args):
        return parse(UniqueLinksCountParser(), args)

    @udf(returnType=IntegerType())
    def __udf_url_length(args):
        return parse(UrlLengthParser(), args)

    @udf(returnType=IntegerType())
    def __udf_words_count(args):
        return parse(WordsCountParser(), args)

    urls_schema = StructType([
        StructField('url', StringType(), True),
    ])

    appearances_schema = StructType([
        StructField('url', StringType(), True),
        StructField('appearances', LongType(), True),
    ])

    features_schema = StructType([
        StructField('url', StringType(), True),
        StructField('html', StringType(), True),
        StructField('links', ArrayType(StringType()), True),
        StructField('characters_count', IntegerType(), True),
        StructField('images_count', IntegerType(), True),
        StructField('links_count', IntegerType(), True),
        StructField('url_length', IntegerType(), True),
        StructField('words_count', IntegerType(), True),
    ])

    def __df_tocrawl(self, urls):
        return self.__spark.createDataFrame(
            data=list(map(Row, map(lambda u: u.rstrip('/'), urls))),
            schema=Crawler.urls_schema
        )

    def __df_crawled(self):
        return self.__spark.createDataFrame(
            data=self.__spark.sparkContext.emptyRDD(),
            schema=Crawler.urls_schema
        )

    def __df_appearances(self):
        return self.__spark.createDataFrame(
            data=self.__spark.sparkContext.emptyRDD(),
            schema=Crawler.appearances_schema
        )

    def __df_features(self):
        return self.__spark.createDataFrame(
            data=self.__spark.sparkContext.emptyRDD(),
            schema=Crawler.features_schema
        )

    def execute(self, urls, depth=1):
        """ Inspired by BST breadth first search algorithm """
        # Setup
        df_crawled = self.__df_crawled()
        df_tocrawl = self.__df_tocrawl(urls)
        df_appearances = self.__df_appearances()
        df_features = self.__df_features()

        # Iterations
        for i in range(0, depth):
            # Scrap
            df_scrap = df_tocrawl \
                .select(
                    'url',
                    Crawler.__udf_scrap('url').alias('html')
                ) \
                .where(col('html').isNotNull()) \
                .select(
                    'url',
                    'html',
                    Crawler.__udf_unique_links(array('url', 'html')).alias('links'),
                    Crawler.__udf_characters_count(array('url', 'html')).alias('characters_count'),
                    Crawler.__udf_images_count(array('url', 'html')).alias('images_count'),
                    Crawler.__udf_unique_links_count(array('url', 'html')).alias('links_count'),
                    Crawler.__udf_url_length(array('url', 'html')).alias('url_length'),
                    Crawler.__udf_words_count(array('url', 'html')).alias('words_count')
                )

            df_features = df_features.union(df_scrap)

            df_explode = df_scrap \
                .select(
                    explode('links').alias('url'),
                    lit(1).cast(IntegerType()).alias('appearances')
                )

            # Aggregate and count partial results
            df_appearances = df_appearances.union(df_explode) \
                .groupby('url') \
                .agg(sum('appearances').alias('appearances'))

            # Update crawled list
            df_crawled = df_crawled.union(df_tocrawl)

            # Update list to be crawled
            if i != depth - 1:  # skip on last iteration
                df_tocrawl = df_explode \
                    .select('url') \
                    .drop_duplicates() \
                    .subtract(df_crawled)

        if self.__storage:
            self.__storage.set(
                table=Crawler.appearances_table,
                df=df_appearances,
            )
            self.__storage.set(
                table=Crawler.features_table,
                df=df_features,
            )

        return df_appearances, df_features

    def get_features(self, url):
        scraper = Scraper()
        html = scraper.execute(url)

        args = (url, html)
        data = [(
            url.rstrip('/'),
            html,
            parse(UniqueLinksParser(), args),
            parse(CharactersCountParser(), args),
            parse(ImagesCountParser(), args),
            parse(UniqueLinksCountParser(), args),
            parse(UrlLengthParser(), args),
            parse(WordsCountParser(), args),
        )]
        return self.__spark.createDataFrame(
            data=data,
            schema=Crawler.features_schema
        )
