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
    with open('database_followers.conf','r') as f:
        local_db['host'] = f.readline().strip()
        local_db['user'] = f.readline().strip()
        local_db['passwd'] = f.readline().strip()
        local_db['db_name'] = f.readline().strip()
        local_db['table_name'] = f.readline().strip()
        local_db['user_id'] = f.readline().strip()

    with open('key_followers.conf','r') as f:
        oath_key_dict['consumer_key'] = f.readline().strip()
        oath_key_dict['consumer_secret'] = f.readline().strip()
        oath_key_dict['access_token'] = f.readline().strip()
        oath_key_dict['access_token_secret'] = f.readline().strip()

    # crawler()
    scheduler = BlockingScheduler()
    # scheduler.add_job(crawler,'cron',second='*/20',hour='*')
    scheduler.add_job(crawler,'cron',minute='*/1',hour='*')
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except:
        KeyboardInterrupt,SystemExit#:
        scheduler.shutdown()

def crawler():
    with open('current_cursor.conf','r') as f:
        current_cursor = f.readline().strip()

    tweets = followers_search(local_db['user_id'], oath_key_dict, current_cursor)
    current_cursor = tweets['next_cursor_str']

    with open('current_cursor.conf','w') as f:
        f.write(current_cursor)

    for i in range(len(tweets['users'])):
        print(i)
        user_id = tweets['users'][i]['id_str']
        user_name = tweets['users'][i]['name']
        screen_name = tweets['users'][i]['screen_name']
        location = tweets['users'][i]['location']
        description = tweets['users'][i]['description']
        if '\'' in description:
            description = description.replace('\'','\'\'')
        if '\"' in description:
            description = description.replace('\"','\"\"')

        if 'status' in tweets['users'][i].keys():
            latest_tweet_text = tweets['users'][i]['status']['text']
            latest_tweet_created_at = tweets['users'][i]['status']['created_at']
            time_s = time.mktime(time.strptime(latest_tweet_created_at,"%a %b %d %H:%M:%S +0000 %Y"))
            dt = datetime.fromtimestamp(time_s)
            dt = dt + timedelta(hours=9)

        else:
            latest_tweet_text = '0'
            latest_tweet_created_at = '0'
            dt = '0000-00-00 00:00:0'

        search_query = {
        "user_id": user_id,
        "user_name": user_name,
        "screen_name": screen_name,
        "location": location,
        "description": description,
        "latest_tweet_text": latest_tweet_text,
        "latest_tweet_created_at": dt
        }
        insert_into_twitter_search(local_db, search_query)
    # exit()
    print(current_cursor)

def create_oath_session(oath_key_dict):
    oath = OAuth1Session(
    oath_key_dict["consumer_key"],
    oath_key_dict["consumer_secret"],
    oath_key_dict["access_token"],
    oath_key_dict["access_token_secret"]
    )
    return oath

def followers_search(person, oath_key_dict, pointer):
    # url = "https://api.twitter.com/1.1/search/tweets.json"
    url = "https://api.twitter.com/1.1/followers/list.json"
    params = {
        "user_id": person,
        "count": "200",
        # "lang": "ja",
        # "result_type": "recent",
        # "count": "100"
        "cursor": pointer
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
        NULL, '%s', '%s', '%s', '%s', '%s', '%s', '%s'
    )
    ;

    """ %(
        local_db["table_name"],
        search_query["user_id"],
        search_query["user_name"],
        search_query["screen_name"],
        search_query["location"],
        search_query["description"],
        search_query["latest_tweet_text"],
        search_query["latest_tweet_created_at"]
        )
    cursor.execute(sql)
    connector.commit()
    cursor.close()
    connector.close()

if __name__ == "__main__":
    main()
