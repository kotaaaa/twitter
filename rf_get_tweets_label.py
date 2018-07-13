# coding: utf-8
import mysql.connector
import MeCab
import pandas as pd
import numpy as np
from collections import Counter
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier

'''データベースの設定ファイルを読み込むxxx'''
def get_db_name():
    local_db = {}
    with open('table_tweet.conf','r') as f:
        local_db['host'] = f.readline().strip()
        local_db['user'] = f.readline().strip()
        local_db['passwd'] = f.readline().strip()
        local_db['db_name'] = f.readline().strip()

    return local_db

'''データベース内のテーブル名を読み込む'''
#Worldcup
#Happy
#Sad
def get_table_name():
    table_names = []
    with open('table_names_tweet.txt','r') as f:
        for line in f.readlines():
            table_names.append( line.strip() )

    return table_names

'''データベースからツイートを取得する'''
def get_text(db_info, table_name):
    connector = mysql.connector.connect(
        auth_plugin='mysql_native_password',
        host = db_info["host"],
        user = db_info["user"],
        passwd = db_info["passwd"],
        db = db_info["db_name"],
        # charset = "utf8mb4"
        )
    cursor = connector.cursor()
    sql = """
    SELECT TEXT FROM %s;
    """ %(table_name)
    cursor.execute(sql)
    text = cursor.fetchall()
    # 出力
    joined_text = ''
    tweets=[]
    for i in text:
        joined_text += i[0]
        tweets.append(i[0])
    cursor.close()
    connector.close()
    return tweets

'''形態素解析する'''
def parse_text(texts):
    mecab = MeCab.Tagger("-Owakati")#Mecabのインスタンスを作成する．
    Wakachi_texts = mecab.parse(texts)#形態素解析を掛ける．
    Wakachi_texts=Wakachi_texts.strip()#改行文字を除去する．
    return Wakachi_texts

'''counterのオブジェクトを作成'''
def word_count(vocab):
    word_counter = Counter(vocab)
    return word_counter

'''ツイートの邪魔な文字列を削除する'''
def format_text(text):
    '''
    MeCabに入れる前のツイートの整形方法例
    '''
    text=re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", text)
    text=re.sub(u' [ぁ-ん]{1} ', "", text)
    text=re.sub(u' [ぁ-ん]{2} ', "", text)
    text=re.sub('RT|#|、|。|「|」|【|】|・|…|★|☆|→|↓|←|↑|⇒|⇔|`|"|♡|-|〜|\\|①|●|×', "", text)
    text=re.sub(r'[!-~]', "", text)#半角記号,数字,英字
    text=re.sub(r'[︰-＠]', "", text)#全角記号
    text=re.sub('\n', "", text)#改行文字
    return text

'''全ツイートを一つの配列に'''
def get_all_tweet():

    local_db = get_db_name()
    table_names = get_table_name()
    All_processed_tweet = np.array([])

    for i in range(0,len(table_names)):

        tweets = get_text(local_db, table_names[i])
        Processed_tweet=[]

        for tweet in tweets:
            tweet = format_text(tweet)#ツイートの前処理を実行
            tweet = parse_text(tweet)#形態素解析する
            Processed_tweet.append(tweet)
        print(table_names[i],'のツイート数 ',len(Processed_tweet))
        All_processed_tweet = np.append(All_processed_tweet,np.array(Processed_tweet))

    return All_processed_tweet

'''CountVectorizerオブジェクトを作る．'''
def get_CountVec(tweet):
    c_vec = CountVectorizer(min_df=3)     # CountVectorizerオブジェクトの生成
    c_vec.fit(tweet)       # 対象ツイート全体の単語の集合をセットする
    return c_vec

'''単語の出現頻度をベクトル化する．'''
def make_tweet_bag(c_vec,tweet):
    c_terms = c_vec.get_feature_names()   # ベクトル変換後の各成分に対応する単語をベクトル表示
    c_tran  = c_vec.transform(tweet)  # ツイートをベクトル表現に変換する
    df = pd.DataFrame(c_tran.toarray())#pandasデータフレームに格納する
    df.columns = c_terms
    # print(df.columns)
    # print('特徴量の次元数(単語数)>>> ',len(c_terms))
    return df

'''教師ラベルを作成する'''
def set_target(df):
    df['Target']=1
    df['Target'][0:14997]=0
    df['Target'][14997:20147]=1#Happyクラス:1
    df['Target'][20147:]=2#Sadクラス:2
    return df

'''ランダムフォレストモデルを訓練する'''
def rf_train(df):
    clf = RandomForestClassifier(n_estimators=100, random_state=0)
    clf.fit(df.ix[14997:,:-1], df['Target'][14997:])
    return clf

'''ツイートをベクトル化する'''
def get_tweet_vec(c_vec,tweet):
    c_tran = c_vec.transform(tweet)
    tweet_vec = c_tran.toarray()#pandasデータフレームに格納する
    return tweet_vec

'''ツイートを分類する'''
def rf_classify(clf,tweet):
    category = clf.predict(tweet)
    return category

'''FIが上位の素性を抽出する．'''
def sort_fi(clf,df):
    print(clf.feature_importances_)
    print(type(clf.feature_importances_))
    print(len(clf.feature_importances_))
    max_is = np.argsort(clf.feature_importances_)[::-1]#降順にソートする．その時のインデックスを取得する．
    print(max_is)
    print(np.argmax(clf.feature_importances_))
    for i in max_is[:30]:
        print('Max of index,Feature_Importance:Feature >> ', i,',',clf.feature_importances_[i],':',df.columns[i])

def input_tweet():
    in_text = input('感情分類するテキストを入力:')
    # print('入力されたテキスト>>>',in_text)
    return in_text

def trim_tweet():
    in_text = input_tweet()
    in_text = format_text(in_text)#ツイートの前処理を実行
    in_text = parse_text(in_text)#形態素解析する
    print('trim後のツイート>>>',in_text)
    return in_text

def main():

    All_tweet = get_all_tweet()
    print('全ツイート数 ',All_tweet.shape)
    c_vec = get_CountVec(All_tweet)
    feature = make_tweet_bag(c_vec, All_tweet)
    feature_with_label = set_target(feature)
    clf = rf_train(feature_with_label)
    tweet_vec = np.array(feature_with_label.ix[:14996,:-1])
    cat = rf_classify(clf,tweet_vec)
    feature_with_label['Predict']=0
    feature_with_label['Predict'][:14997]=cat
    result = feature_with_label[['Predict','Target']]
    result['Tweet'] = All_tweet
    result.to_csv('result_love_mindf3_short.csv',encoding='utf-8')

if __name__ == "__main__":
    main()
