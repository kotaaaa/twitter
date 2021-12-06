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
    with open('database_user_timeline.conf','r') as f:
        local_db['host'] = f.readline().strip()
        local_db['user'] = f.readline().strip()
        local_db['passwd'] = f.readline().strip()
        local_db['db_name'] = f.readline().strip()
        local_db['table_name'] = f.readline().strip()
        local_db['username_table'] = f.readline().strip()

    with open('key_user_timeline.conf','r') as f:
        oath_key_dict['consumer_key'] = f.readline().strip()
        oath_key_dict['consumer_secret'] = f.readline().strip()
        oath_key_dict['access_token'] = f.readline().strip()
        oath_key_dict['access_token_secret'] = f.readline().strip()

    scheduler = BlockingScheduler()
    scheduler.add_job(crawler,'cron',second='*/1',hour='*')
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except:
        KeyboardInterrupt,SystemExit#:
        scheduler.shutdown()

def crawler():
    with open('primary_id.conf','r') as f:
        primary_id = f.readline().strip()

    screen_name = select_user(local_db, primary_id)
    # current_cursor = tweets['next_cursor_str']
    primary_id = str(int(primary_id)+1)
    with open('primary_id.conf','w') as f:
        f.write(primary_id)

    # screen_name = '126junky'
    tweets = timeline_search(screen_name, oath_key_dict)
    print(len(tweets))
    for i in range(len(tweets)):
        print(i)
        created_at = tweets[i]['created_at']
        time_s = time.mktime(time.strptime(created_at,"%a %b %d %H:%M:%S +0000 %Y"))
        dt = datetime.fromtimestamp(time_s)
        # dt = dt + timedelta(hours=9)
        dt = dt - timedelta(hours=7)

        place = tweets[i]['place']
        tweet_id = tweets[i]['id_str']
        text = tweets[i]['text']

        retweet_flg = 0
        if 'retweeted_status' in tweets[i].keys():
            retweet_flg = 1

        search_query = {
        "screen_name": screen_name,
        "created_at": dt,
        "place": place,
        "tweet_id": tweet_id,
        "text": text,
        "retweet_flg": retweet_flg,
        }
        print(search_query)
        insert_into_twitter_search(local_db, search_query)
    # exit()

def create_oath_session(oath_key_dict):
    oath = OAuth1Session(
    oath_key_dict["consumer_key"],
    oath_key_dict["consumer_secret"],
    oath_key_dict["access_token"],
    oath_key_dict["access_token_secret"]
    )
    return oath

def timeline_search(person, oath_key_dict):
    # url = "https://api.twitter.com/1.1/search/tweets.json"
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    params = {
        # "user_id": person,
        "screen_name": person,
        "count": "200",
        # "lang": "ja",
        # "result_type": "recent",
        # "count": "100"
        # "cursor": pointer,
        # "exclude_replies": True,
        # "include_rts": False
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
    cursor = connector.cursor()#buffered=True)
    sql = """
    INSERT INTO
        %s
    VALUES(
        NULL, '%s', '%s', '%s', '%s', '%s', '%s'
    )
    ;

    """ %(
        local_db["table_name"],
        search_query["screen_name"],
        search_query["created_at"],
        search_query["place"],
        search_query["tweet_id"],
        search_query["text"],
        search_query["retweet_flg"]
        # search_query["reply_flg"]
        )

    cursor.execute(sql)
    connector.commit()
    cursor.close()
    connector.close()


def select_user(db_info,id):
    connector = mysql.connector.connect(
        auth_plugin='mysql_native_password',
        host = db_info["host"],
        user = db_info["user"],
        passwd = db_info["passwd"],
        db = db_info["db_name"],
        charset = "utf8mb4"
        )
    cursor = connector.cursor(buffered=True)
    sql = """
    SELECT
        screen_name
    FROM
        %s
    WHERE
        id = %s
    ;

    """ %(
        db_info["username_table"],
        id
        )
    print(sql)
    cursor.execute(sql)
    # print(cursor.fetchall())#190315 なぜかここのprintを出力しないと，エラーになる．
    Us = cursor.fetchall()
    print(len(Us))
    print(Us[0][0])
    if len(Us) == 0:
        # print()
        u = 0 # 仮に
    else:
    # print(cursor.fetchall()[0])#[0] is None)
    # print(cursor.fetchall())
        # u = cursor.fetchall()[0][0]
        u = Us[0][0]
    print(u)
    connector.commit()
    cursor.close()
    connector.close()
    return u


if __name__ == "__main__":
    main()
