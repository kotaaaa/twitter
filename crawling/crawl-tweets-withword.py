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
    with open('database_tweet.conf','r') as f:
        local_db['host'] = f.readline().strip()
        local_db['user'] = f.readline().strip()
        local_db['passwd'] = f.readline().strip()
        local_db['db_name'] = f.readline().strip()
        local_db['table_name'] = f.readline().strip()
        local_db['search_word'] = f.readline().strip()

    with open('key_tweet.conf','r') as f:
        oath_key_dict['consumer_key'] = f.readline().strip()
        oath_key_dict['consumer_secret'] = f.readline().strip()
        oath_key_dict['access_token'] = f.readline().strip()
        oath_key_dict['access_token_secret'] = f.readline().strip()

    # crawler()
    scheduler = BlockingScheduler()
    # scheduler.add_job(crawler,'cron',second='*/20',hour='*')
    # scheduler.add_job(crawler,'cron',minute='*/1',hour='*')
    scheduler.add_job(crawler,'cron',second='*/2',hour='*') #2秒に一回リクエストを送信
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except:
        KeyboardInterrupt,SystemExit#:
        scheduler.shutdown()

def Rem_Quotation(target):
    if '\'' in target:#user_name内に'が入っている時，それを削除する
        target = target.replace('\'','\'\'')
    if '\"' in target:
        target = target.replace('\"','\"\"')
    return target

def crawler():
    with open('last_tweet_id.conf','r') as f:
        last_tweet_id = f.readline().strip()

    tweets = tweet_search(local_db['search_word'], oath_key_dict, last_tweet_id) #last_tweet_id以降のtweetを取得する．
    for c,tweet in enumerate(tweets["statuses"],1):
        tweet_id = tweet[u'id_str']
        text = tweet['text']
        text = Rem_Quotation(text)
        created_at = tweet[u'created_at']
        user_id = tweet[u'user'][u'id_str']
        user_name = tweet[u'user'][u'name']
        user_name = Rem_Quotation(user_name)

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

        last_tweet_id = tweet_id
        with open('last_tweet_id.conf','w') as f:
            f.write(last_tweet_id)#DB格納エラーが出たときのため，次のtweet_idに遷移できるように，更新しておく
        if c == len(tweets["statuses"]): #max_idはその自身のIDを含んでしまうので，最後のツイートはDBに格納しない．
            break
        insert_into_twitter_search(local_db, search_query)

def create_oath_session(oath_key_dict):
    oath = OAuth1Session(
    oath_key_dict["consumer_key"],
    oath_key_dict["consumer_secret"],
    oath_key_dict["access_token"],
    oath_key_dict["access_token_secret"]
    )
    return oath

def tweet_search(search_word, oath_key_dict, pointer):
    print('pointer',pointer)
    url = "https://api.twitter.com/1.1/search/tweets.json"
    params = {
        "q": search_word,
        "lang": "ja",
        # "result_type": "recent",
        "count": "100",
        "max_id": pointer #max_idはその自身のIDを含んでしまうらしい．
        # "until": "2019-03-10"
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
