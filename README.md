# Link Reference Prediction

## About

This project builds a service for predicting the number of references of a website on a subset of the internet.

It has a REST API with the following functions:
 - return an array of features of an website
 - return a prediction of the number of appearances of a link of a site based on a trained model

The code has a scrapper and parsers to get the links and features of given urls. A crawler is build using that scrapper to recursively travel through the urls. It utilizes spark framework to achieve reliable distributed computing.

The [Spark MLlib](http://spark.apache.org/docs/latest/ml-guide.html) is used to train the model for the prediction.

## Assumptions

- URL parameters and the rightmost slash ("/") of the URL's are not considered as part of URL for the sets of URL's in this code, the same applies for querystrings and anchors;
- Only non-empty link HTML tags are considered links, for example, `<a href="#"><a />` is discarted;
- More than one link of the same site in a page is considered as only one appearance of that site;
- Links referencing paths and starting with `/` will be concatenated on the base URL to form a new URL;
- URL's need to start with `http`;
- The counting will only occur in a subset of the internet that was crawled, so the prediction will represent the number of appearances in that subset;

## Requirements

`Docker` and `Makefile` are required to run this project.

## Running

A docker image built by the Dockerfile can be used to run the project. A Makefile is available to make things easier.

First you should edit the `.env` file, where you can setup which urls will be crawled, the training parameters and the spark configuration.

After the setup is ready:
```bash
make crawl
```
 `make crawl` to execute the crawler which will populate our storage with the `appearances` and `features` of the configured urls.

```
make train
```
Next step is the training which can be executed with `make train`, which will train and storage a `model`.

```
make run
```
For the last, `make run` can be executed to start the API, which will run port http://localhost:5000.

```
make test
```
There also some unit tests that can be run.

### API

The following endpoints area available:
- `/features?url={url}`: to list the features of a given url
- `/prediction?url={url}`: to predict the appearances of a given url
- `/storage-count`: for debuging

### About issues and improvements

- The developed API utilizes a Spark Session which delays the responses, maybe it can be removed and a better model deploy strategy can be used.
- The storage which the API consumes suffers from the same issue above. It also does not handle concurrency well and it's using parquet with spark read/writes.
- The developed concurrent crawling probably can tuned to perform better, and depending of the depth requested the spark resources need to be adjusted.
- The tests does not cover all the code.
