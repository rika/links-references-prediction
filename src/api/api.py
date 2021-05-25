import os
import json
from flask import Flask, request, abort
from pyspark.sql.session import SparkSession
from crawler import Crawler
from scraper import NoStatusCode200
from storage import Storage

APP_NAME = os.environ['APP_NAME']
SPARK_MASTER = os.environ['SPARK_MASTER']

app = Flask(__name__)
app.config['DEBUG'] = True


def getSparkSession():
    return SparkSession.builder \
        .master(SPARK_MASTER) \
        .appName(f'{APP_NAME}-api') \
        .getOrCreate()


@app.route('/storage-count', methods=['GET'])
def get_storage():
    storage = Storage(getSparkSession())
    appearances = storage.get('appearances').count()
    features = storage.get('features').count()

    return json.dumps({
        'appearances': appearances,
        'features': features,

    })


def _get_features_df(spark, storage, url):
    df_features = storage.get('features').where(f'url = "{url}"')
    count = df_features.count()

    if count == 0:
        crawler = Crawler(spark)
        df_features = crawler.get_features(url)
        storage.append(Crawler.features_table, df_features)

    df_features.show()
    return df_features.select(*Crawler.features_cols)


@app.route('/features', methods=['GET'])
def get_features():
    try:
        url = request.args.get('url')
        if not url:
            abort(400, 'Error: `url` querystring parameter missing')

        url = url.rstrip('/')

        spark = getSparkSession()
        storage = Storage(spark)
        features = _get_features_df(spark, storage, url).collect()[0]

        return json.dumps({
            'url': url,
            'features': features
        })
    except NoStatusCode200:
        abort(400, 'Error: url did not return status code 200')


@app.route('/prediction', methods=['GET'])
def get_prediction():
    try:
        url = request.args.get('url')
        if not url:
            abort(400, 'Error: `url` querystring parameter missing')

        spark = getSparkSession()
        storage = Storage(spark)

        df_appearances = storage.get('appearances').where(f'url = "{url}"')

        if df_appearances.count() > 0:
            prediction = df_appearances.select('appearances').collect()[0]
        else:
            model = storage.getModel()
            df_features = _get_features_df(spark, storage, url)

            data = df_features.select(*Crawler.features_cols)
            prediction = model.transform(data) \
                .select('prediction') \
                .collect()[0]

        return json.dumps({
            'prediction': prediction
        })
    except NoStatusCode200:
        abort(400, 'Error: url did not return status code 200')


if __name__ == '__main__':
    app.run()
