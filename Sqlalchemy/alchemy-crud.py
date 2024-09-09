# docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=P@ssw0rd0719" -p 1433:1433 --name huaidb -d mcr.microsoft.com/mssql/server:2022-latest

import logging, os, sqlalchemy, pymssql
import pandas as pd
from enum import Enum
from sqlalchemy import create_engine, inspect, Column, Integer, String, text, ForeignKey, MetaData, Table
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from urllib.parse import quote_plus

Base = declarative_base()

mssql_db="test"
mssql_ip="localhost"
mssql_account="sa"
mssql_pw="P@ssw0rd0719"

encoded_password = quote_plus(mssql_pw)

connection_string = f"mssql+pymssql://{mssql_account}:{encoded_password}@{mssql_ip}:1433/{mssql_db}"

engine = create_engine(connection_string)

metadata = MetaData()

users_table = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
)

products_table = Table(
    'products',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('price', Integer)
)

orders_table = Table(
    'orders',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer),
    Column('product_id', Integer)
)

def _create_tables():
    try:
        metadata.create_all(engine)
    except Exception as ex:
        logging.error(f"Error creating tables: {ex}")

def _delete_tables():
    try:
        metadata.drop_all(engine)
    except Exception as ex:
        logging.error(f"Error deleting tables: {ex}")

def _read_data():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        select_users = users_table.select().where(users_table.c.name == "John Doe")
        result = session.execute(select_users)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        print("Users DataFrame:")
        print(df)

        select_products = products_table.select()
        result = session.execute(select_products)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        print("Products DataFrame:")
        print(df)

        select_orders = orders_table.select()
        result = session.execute(select_orders)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        print("Orders DataFrame:")
        print(df)

    except Exception as ex:
        logging.error(f"Error reading data: {ex}")
    finally:
        session.close()

def _insert_data():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        insert_user = users_table.insert().values(name="John Doe")
        session.execute(insert_user)

        insert_product = products_table.insert().values(name="Laptop", price=1000)
        session.execute(insert_product)

        insert_order = orders_table.insert().values(user_id=1, product_id=1)
        session.execute(insert_order)

        session.commit()
        print("Data inserted successfully")
    except Exception as ex:
        session.rollback()
        logging.error(f"Error inserting data: {ex}")
    finally:
        session.close()

def _update_data():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        update_user = users_table.update().where(users_table.c.id == 6).values(name="Nick Doe")
        session.execute(update_user)
        session.commit()
        print("User updated successfully")
    except Exception as ex:
        session.rollback()
        logging.error(f"Error updating data: {ex}")
    finally:
        session.close()

def _delete_data():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        delete_user = users_table.delete().where(users_table.c.id == 6)
        session.execute(delete_user)
        session.commit()
        print("User deleted successfully")
    except Exception as ex:
        session.rollback()
        logging.error(f"Error deleting data: {ex}")
    finally:
        session.close()

def _clear_table_data():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        delete_all_users = users_table.delete()
        session.execute(delete_all_users)
        session.commit()
        print("All user data deleted successfully")
    except Exception as ex:
        session.rollback()
        logging.error(f"Error deleting all user data: {ex}")
    finally:
        session.close()


if __name__ == "__main__":
    _read_data()

