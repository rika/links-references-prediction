# Link Reference Prediction

## About

This project builds a service for predicting the number of references of a website on a subset of the internet.

It has a REST API with the following functions:
 - return an array of features of an website
 - return a prediction of the number of appearances of a link of a site based on a trained model

The code has a scrapper to get the links and model features on a specific url. A crawler is build using that scrapper to recursively travel through the urls. It utilizes spark framework to achieve reliable distributed computing.

## Assumptions
- URL parameters and the rightmost slash ("/") of the URL's are not considered as part of URL for the sets of URL's in this code;
- Only non-empty link HTML tags are considered links, for example, <a href="#"><a/> is discarted;
- More than one link of the same site in a page is considered as only one appearance of that site;
- Links referencing paths and starting with `/` will be concatenated on the base URL to form a new URL;
- URL's need to start with `http`;
- The counting will only occur in a subset of the internet that was crawled, so the prediction will represent the number of appearances in that subset;
