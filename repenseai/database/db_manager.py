import mysql.connector
from mysql.connector import Error
import pandas as pd
import logging
from typing import Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class DBConnection:
    def __init__(self, host: str, user: str, password: str, port: str):
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                port=port,
            )
            self.cursor = self.connection.cursor(buffered=True)
            logging.info("Database connection established.")
        except Error as e:
            logging.error(f"Error connecting to database: {e}")
            raise

    def execute_query(self, query: str, values: tuple | None = None):
        try:
            self.cursor.execute(query, values)
            self.connection.commit()

            logging.info(f"Query: {query} - executed successfully.")
            
            if self.cursor.with_rows:
                return self.cursor.fetchall()
        except Error as e:
            logging.error(f"Error executing query: {query} - Error: {e}")
            self.connection.rollback()
        finally:
            self.close()    

    def close(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            logging.info("Database connection closed.")

class DBManager:
    def __init__(self, db_connection: DBConnection, namespace: str, table_name: str):
        self.db = db_connection

        self.namespace = namespace
        self.table_name = table_name

        self.table = f"{self.namespace}.{self.table_name}"

    def insert_record(self, log_dict: dict[str, Any]):
        fields = ", ".join(log_dict.keys())
        placeholders = ", ".join(["%s"] * len(log_dict))
        query = f"INSERT INTO {self.table} ({fields}) VALUES ({placeholders})"
        values = tuple(log_dict.values())
        self.db.execute_query(query, values)

    def get_records(self, condition: str):
        query = f"SELECT * FROM {self.table} WHERE {condition}"
        return self.db.execute_query(query)

    def update_record(self, log_dict: dict[str, Any], record_id: int):
        fields = ", ".join(f"{k} = %s" for k in log_dict.keys())
        query = f"UPDATE {self.table} SET {fields} WHERE id = %s"
        values = tuple(log_dict.values()) + (record_id,)
        self.db.execute_query(query, values)

    def delete_records(self, condition: str):
        query = f"DELETE FROM {self.table} WHERE {condition}"
        self.db.execute_query(query)

    def delete_table(self):
        query = f"DROP TABLE IF EXISTS {self.table}"
        self.db.execute_query(query)

    def create_table(self, schema: str):
        self.create_schema()
        query = f"CREATE TABLE IF NOT EXISTS {self.table} ({schema})"
        self.db.execute_query(query)

    def create_schema(self):
        query = f"CREATE DATABASE IF NOT EXISTS {self.namespace}"
        self.db.execute_query(query)

    def select_records(self, condition: str | None = None, return_dataframe: bool = False):
        query = f"SELECT * FROM {self.table}"
        if condition:
            query += f" WHERE {condition}"
        records = self.db.execute_query(query)
        if return_dataframe:
            try:
                df = pd.DataFrame(records, columns=[i[0] for i in self.db.cursor.description])
                return df
            except TypeError:
                return pd.DataFrame()
        else:
            return records

    def list_tables(self) -> List[str]:
        query = f"SHOW TABLES from {self.namespace}"
        tables = self.db.execute_query(query)
        return [table[0] for table in tables]

# Example usage:
# db_connection = DBConnection(host="localhost", user="user", password="password", port="3306")
# table_handler = TableHandler(db_connection, namespace="mydb", schema="public", table_name="users")
# ... use table_handler methods ...
# db_connection.close()