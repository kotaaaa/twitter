# -*-coding:utf-8-*-
import mysql.connector

table_names = []

def main():
    local_db = {}
    with open('table.conf','r') as f:
        local_db['host'] = f.readline().strip()
        local_db['user'] = f.readline().strip()
        local_db['passwd'] = f.readline().strip()
        local_db['db_name'] = f.readline().strip()

    with open('table_names.txt','r') as f:
        for line in f.readlines():
            table_names.append( line.strip() )

    for i in range(0,len(table_names)):
        create_search_table(local_db, table_names[i])

def create_search_table(db_info, table_name):
    connector = mysql.connector.connect(
        auth_plugin='mysql_native_password',
        host = db_info["host"],
        user = db_info["user"],
        passwd = db_info["passwd"],
        db = db_info["db_name"],

        )
    cursor = connector.cursor()
    sql = """
    CREATE TABLE IF NOT EXISTS
        %s(
            id BIGINT PRIMARY KEY AUTO_INCREMENT,
            tweet_id BIGINT unique not null,
            datetime DATETIME,
            user_id BIGINT,
            user_name VARCHAR(50),
            text TEXT
        )
    ;
    """ %(table_name)
    cursor.execute(sql)
    connector.commit()
    cursor.close()
    connector.close()

if __name__ == "__main__":
    main()
