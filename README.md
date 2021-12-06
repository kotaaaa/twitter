# Twitter text analysis

## Overview 
- Collect tweet with twitter API, analyse the distribution, statistics, build classfication model and predict category (Posivtive / Negative).

## Directory Configuration
```
Crawling: Collect tweets scripts
 ├ crawl-tweets-withword.py: crawl tweets with specific query.
 ├ crawl_followers.py: fetch user's followers
 └ crawl_user_timeline.py: crawl users timeline's tweet.
Model: train RF model, predict classification
 ├ rf_input_tweet.py: Prints which class the input document belongs to.
 ├ rf_get_tweets_label.py: Store the result of determining whether each tweet has pos or neg polarity 
 |                         for the group of tweets in csv.
 └ rf_show_FI.py: Prints the Feature Importance for each feature in the training model.
View: Input html interface for demo
 └ input.html: Html to show this as DEMO.
```

## Tech
- FW: sklearn, pandas, numpy
- DB: mysql
- Model: Random Forest
- Train data: About 1,000 tweets collected from Twitter API.
  - Positive: About 5,000 tweets collected by "嬉し(Happy)". 
  - Negative: About 5,000 tweets collected by "悲し(Sad)".  
