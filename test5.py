from flask import Flask, Response, request, jsonify
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
    with connection.cursor() as cursor:
        cursor.execute(select_query)
        records = cursor.fetchall()

    users = []
    for row in records:
        users.append({
            "id":row[0],
            "name":row[1],
            "age":row[2]
        })
    return jsonify(users), 200

@app.route('/users/new', methods=['GET'])
def get_users_all():
    select_query = "SELECT * FROM users"

    with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
        cursor.execute(select_query)
        records = cursor.fetchall()

    # print(dict(records[0]))
    print(type(records[0]))
    print(type(dict(records[0])))

    print(records[0]['name'])
    print(records[0])

    users = [dict(row) for row in records]
    response = Response(json.dumps(users), status=200, mimetype="application/json")
    return response




@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')
    
    insert_query = "INSERT INTO users (name, age) VALUES (%s,%s)"
    with connection.cursor() as cursor:
        cursor.execute(insert_query, (name, age))
        connection.commit()

    response_data = {"message":f"User {name} added."}
    response = Response(json.dumps(response_data), status=201, mimetype="application/json")
    return response
    
    # response_data = {"message":f"User {name} added."}
    # return jsonify(response_data), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user_age(user_id):
    data = request.get_json()
    new_age = data.get('age')

    update_query = "UPDATE users SET age = %s WHERE id = %s"
    with connection.cursor() as cursor:
        cursor.execute(update_query, (new_age, user_id))
        connection.commit()

    response_data = {"message":f"User with id {user_id} updated to age {new_age}."}
    response = Response(json.dumps(response_data), status=200, mimetype="application/json")
    return response 

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    delete_query = "DELETE FROM users WHERE id = %s"
    with connection.cursor() as cursor:
        cursor.execute(delete_query, (user_id,))
        connection.commit()
    
    response_data = {"message":f"User with id {user_id} deleted."}
    response = Response(json.dumps(response_data), status=200, mimetype="application/json")
    return response

if __name__ == "__main__":
    create_table()
    app.run(debug=True)