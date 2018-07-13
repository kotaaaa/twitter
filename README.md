# twitter

入力した文書に対してそのツイートがポジティブなのかネガティブのどちらの極性を持つのかを判定するシステムを作りました．

使っているデータベース:mysql
モデル:ランダムフォレスト
訓練データ:ツイッターから集めてきたツイート約10000件
正例:「嬉し」で集めてきた約5000件のツイート．
負例:「悲し」で集めてきた約5000件のツイート．

ここで訓練したモデルに対して，

rf_input_tweet.py>>>入力した文書がどちらのクラスに所属するかを出力する．
rf_get_tweets_label.py>>>csvでまとまったtweet群に対して，それぞれがpos,negどちらの極性を持つのか判定した結果を格納する．
rf_show_FI.py>>>訓練モデルにおいて，各素性のFeature Importanceを出力する．

というプログラムになっています．
