import os
from pyspark.ml.pipeline import PipelineModel

STORAGE_URL = os.environ['STORAGE_URL']
MODEL_PATH = 'model'


class Storage:
    def __init__(self, spark=None):
        self.__spark = spark

    def get(self, table):
        return self.__spark.read \
            .parquet(f'{STORAGE_URL}/{table}')

    def set(self, table, df):
        df.write \
            .mode('overwrite') \
            .parquet(f'{STORAGE_URL}/{table}')

    def append(self, table, df):
        df.write \
            .mode('append') \
            .parquet(f'{STORAGE_URL}/{table}')

    def getModel(self):
        return PipelineModel.load(f'{STORAGE_URL}/{MODEL_PATH}')

    def setModel(self, model):
        model.write() \
            .overwrite() \
            .save(f'{STORAGE_URL}/{MODEL_PATH}')
