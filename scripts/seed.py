import sqlite3
import requests
import json
import argparse


DATABASE_NAME = 'data.db'
TABLE_NAME = 'users'

def create_table():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    create_table = f'CREATE TABLE IF NOT EXISTS {TABLE_NAME} (\
        id INTEGER PRIMARY KEY, login text, type text, avatar_url text, url text)'
    cursor.execute(create_table)

    connection.commit()
    connection.close()
    
def insert_users(users):
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    query = f'INSERT INTO {TABLE_NAME} VALUES(?, ?, ?, ?, ?)'
    try:
        cursor.executemany(query, (users))
    except:
        print('Error inserting data')

    connection.commit()
    connection.close()

def select_users():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    query = f'SELECT * FROM {TABLE_NAME}'
    result = cursor.execute(query)
    users = []

    for row in result:
        users.append({
            'id' : row[0],
            'login' : row[1],
            'type' : row[2],
            'avatar_url' : row[3],
            'url' : row[4],
        })

    connection.close()

    return users

def get_github_users(total_users, per_page):
    github_users_url = 'https://api.github.com/users'
    users = []
    last_id = 0
    
    while len(users) < total_users:
        users_response = requests.get(github_users_url + f"?&since={last_id}&per_page={per_page}").json()
        parsed_users = [(user['id'], user['login'], user['type'], user['avatar_url'], user['url']) for user in users_response]
        users.extend(parsed_users)
        last_id = users[-1][0]

    return users

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--total', '-t', help="specify total users to request", type=int)
    parser.add_argument('--per-page', '-p', help="number of users per page", type=int, default=50)
    args = parser.parse_args()

    if not args.total:
        print(parser.format_help())
        exit()

    create_table()
    get_users = get_github_users(args.total, args.per_page)
    insert_users(get_users)

    users_in_db = select_users()
    print(json.dumps(users_in_db, indent=2))
    print(f'Total users in DB: {len(users_in_db)}')
