# -*- coding:utf-8 -*-
from datetime import datetime,timedelta
from requests_oauthlib import OAuth1Session
from apscheduler.schedulers.blocking import BlockingScheduler
import json
import os
import mysql.connector
import time


local_db = {}
oath_key_dict = {}

def main():
    with open('database.conf','r') as f:
        local_db['host'] = f.readline().strip()
        local_db['user'] = f.readline().strip()
        local_db['passwd'] = f.readline().strip()
        local_db['db_name'] = f.readline().strip()
        local_db['table_name'] = f.readline().strip()
        local_db['search_word'] = f.readline().strip()

    with open('key.conf','r') as f:
        oath_key_dict['consumer_key'] = f.readline().strip()
        oath_key_dict['consumer_secret'] = f.readline().strip()
        oath_key_dict['access_token'] = f.readline().strip()
        oath_key_dict['access_token_secret'] = f.readline().strip()

    scheduler = BlockingScheduler()
    scheduler.add_job(crawler,'cron',second='*/20',hour='*')
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except:
        KeyboardInterrupt,SystemExit#:
        scheduler.shutdown()

def crawler():
    tweets = tweet_search(local_db['search_word'], oath_key_dict)
    for tweet in tweets["statuses"]:
        tweet_id = tweet[u'id_str']
        text = tweet['text']
        created_at = tweet[u'created_at']
        user_id = tweet[u'user'][u'id_str']
        user_name = tweet[u'user'][u'name']
        time_s = time.mktime(time.strptime(created_at,"%a %b %d %H:%M:%S +0000 %Y"))
        dt = datetime.fromtimestamp(time_s)
        dt = dt + timedelta(hours=9)
        search_query = {
        "tweet_id": tweet_id,
        "datetime": dt,
        "user_id": user_id,
        "user_name": user_name,
        "text": text
        }
        insert_into_twitter_search(local_db, search_query)

def create_oath_session(oath_key_dict):
    oath = OAuth1Session(
    oath_key_dict["consumer_key"],
    oath_key_dict["consumer_secret"],
    oath_key_dict["access_token"],
    oath_key_dict["access_token_secret"]
    )
    return oath

def tweet_search(search_word, oath_key_dict):
    url = "https://api.twitter.com/1.1/search/tweets.json"
    params = {
        "q": search_word,
        "lang": "ja",
        "result_type": "recent",
        "count": "100"
        }
    oath = create_oath_session(oath_key_dict)
    responce = oath.get(url, params = params)
    if responce.status_code != 200:
        print("Error code: %d" %(responce.status_code))
        return None
    tweets = json.loads(responce.text)
    return tweets

def insert_into_twitter_search(db_info, search_query):
    connector = mysql.connector.connect(
        auth_plugin='mysql_native_password',
        host = db_info["host"],
        user = db_info["user"],
        passwd = db_info["passwd"],
        db = db_info["db_name"],
        charset = "utf8mb4"
        )
    cursor = connector.cursor()
    sql = """
    INSERT INTO
        %s
    VALUES(
        NULL, '%s', '%s', '%s', '%s', '%s'
    )
    ;

    """ %(
        local_db["table_name"],
        search_query["tweet_id"],
        search_query["datetime"],
        search_query["user_id"],
        search_query["user_name"],
        search_query["text"]
        )
    cursor.execute(sql)
    connector.commit()
    cursor.close()
    connector.close()

if __name__ == "__main__":
    main()
