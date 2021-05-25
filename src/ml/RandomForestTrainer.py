from pyspark.ml import Pipeline
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.evaluation import RegressionEvaluator


class RandomForestTrainer:
    def __init__(self, spark, storage=None):
        self.__spark = spark
        self.__storage = storage

    def execute(
        self,
        appearances_table,
        features_table,
        features_cols,
        num_trees,
        max_depth,
        split_seed
    ):
        storage = self.__storage

        features_df = self.__storage.get(appearances_table)
        appearances_df = self.__storage.get(features_table)

        # Join features with appearances
        data = features_df.join(
            appearances_df,
            on=['url'],
            how='inner'
        ).select(
            'appearances',
            *features_cols
        )

        (trainingData, testData) = data.randomSplit([0.7, 0.3], split_seed)

        assembler =\
            VectorAssembler(
                inputCols=features_cols,
                outputCol="features"
            )

        rf = RandomForestRegressor(
            labelCol="appearances",
            featuresCol="features",
            numTrees=num_trees,
            maxDepth=max_depth
        )

        # # Chain assembler and forest in a Pipeline
        pipeline = Pipeline(stages=[assembler, rf])

        # # Run pipeline which trains teh model. This also runs the assembler.
        model = pipeline.fit(trainingData)

        # # Make predictions.
        predictions = model.transform(testData)

        # # Evaluate prediction
        evaluator = RegressionEvaluator(
            labelCol="appearances",
            predictionCol="prediction",
            metricName="rmse"
        )
        rmse = evaluator.evaluate(predictions)

        if storage:
            storage.setModel(model)

        print(
            "===================================================\n" +
            "Root Mean Squared Error (RMSE) on test data = %g\n" % rmse +
            "==================================================="
        )

        return model
