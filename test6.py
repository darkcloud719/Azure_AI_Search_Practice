from flask import Flask, Response, request
import json
import psycopg2
import psycopg2.extras

connection = psycopg2.connect(
    host="localhost",
    database="mydb",
    user="nick",
    password="0719",
    port=5432
)

app = Flask(__name__)

def create_table():
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        age INTEGER NOT NULL    
    )
    '''

    with connection.cursor() as cursor:
        cursor.execute(create_table_query)
        connection.commit()
        print("Table created successfully")

@app.route('/users', methods=['GET'])
def get_users():
    select_query = "SELECT * FROM users"

    with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute(select_query)
        records = cursor.fetchall()

    users = [dict(row) for row in records]
    response = Response(json.dumps(users), status=200, mimetype="application/json")
    return response

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')

    insert_query = f"INSERT INTO users (name, age) VALUES (%s, %s)"
    with connection.cursor() as cursor:
        cursor.execute(insert_query, (name, age))
        connection.commit()

    response_data = {"message":f"User {name} created successfully"}
    response = Response(json.dumps(response_data), status=201, mimetype="application/json")
    return response


if __name__ == "__main__":
    create_table()
    app.run(host="0.0.0.0", port=5000)