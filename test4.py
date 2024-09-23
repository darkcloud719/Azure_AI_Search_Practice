import psycopg2

connection = psycopg2.connect(
    dbname="test",
    user='postgres',
    password='0719',
    host='localhost',
    port='5432'
)

def create_table():

    with connection.cursor() as cursor:
        create_table_query = '''
        CREATE TABLE employees2(
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            hire_date DATE
        );
        '''

        cursor.execute(create_table_query)
        connection.commit()

def insear_data():

    with connection.cursor() as cursor:
        insert_query = '''
        INSEAR INTO employees(name, position, hire_date)
        VALUES(%s, %s, %s);
        '''
        data = ('John Doe','Developer','2021-07-19')
        cursor.execute(insert_query, data)
        connection.commit()

def search_data():

    with connection.cursor() as cursor:
        select_query = 'SELECT * FROM employees;'
        cursor.execute(select_query)

        records = cursor.fetchall()
        for record in records:
            print(record)

def update_data():

    with connection.cursor() as cursor:
        update_query = '''
        UPDATE employees
        SET position = %s
        WHERE name = %s;
        '''
        data = ('Senior Developer','John Doe')
        cursor.execute(update_query, data)
        connection.commit()

def delete_data():

    with connection.cursor() as cursor:
        delete_data = '''
        DELETE FROM employees
        WHERE name = %s;
        '''
        data = ('John Doe')
        connection.commit()



if __name__ == "__main__":
    # search_data()
    create_table()
    connection.close()