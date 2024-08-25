import os
import mysql.connector
from mysql.connector import Error
import pandas as pd
import logging
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class DBManager:
    def __init__(self, namespace: str, table_name: str):
        try:

            self.connection = mysql.connector.connect(
                host=os.getenv("DB_ENDPOINT"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                port=os.getenv("DB_PORT"),
            )
            self.cursor = self.connection.cursor(
                buffered=True
            )  # Use buffered cursor to automatically fetch results
            self.namespace = namespace
            self.table_name = table_name
            logging.info("Database connection established.")
        except Error as e:
            logging.error(f"Error connecting to database: {e}")

    def execute_query(self, query: str, values: tuple | None = None):
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            logging.info(f"Query: {query} - executed successfully.")
            if self.cursor.with_rows:
                return self.cursor.fetchall()  # Fetch results if there are any
        except Error as e:
            logging.error(f"Error executing query: {query} - Error: {e}")
            self.connection.rollback()

    def insert_record(self, log_dict: dict[str, Any]):
        table = f"{self.namespace}.{self.table_name}"
        fields = ", ".join(log_dict.keys())
        placeholders = ", ".join(["%s"] * len(log_dict))
        query = f"INSERT INTO {table} ({fields}) VALUES ({placeholders})"
        values = tuple(log_dict.values())
        self.execute_query(query, values)

    def get_records(self, condition: str):
        query = f"SELECT * FROM {self.namespace}.{self.table_name} WHERE {condition}"
        return self.execute_query(query)

    def update_record(self, log_dict: dict[str, Any], record_id: int):
        table = table = f"{self.namespace}.{self.table_name}"
        fields = ", ".join(f"{k} = %s" for k in log_dict.keys())
        query = f"""UPDATE {table} SET {fields} WHERE id = %s"""
        values = tuple(log_dict.values()) + (record_id,)
        self.execute_query(query, values)

    def delete_records(self, condition: str):
        query = f"DELETE FROM {self.namespace}.{self.table_name} WHERE {condition}"
        self.execute_query(query)

    def delete_table(self):
        query = f"DROP TABLE IF EXISTS {self.namespace}.{self.table_name}"
        self.execute_query(query)

    def close(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            logging.info("Database connection closed.")

    def create_table(self, schema: str):
        self.create_schema()
        query = (
            f"CREATE TABLE IF NOT EXISTS {self.namespace}.{self.table_name} ({schema})"
        )
        self.execute_query(query)

    def create_schema(self):
        query = f"CREATE DATABASE IF NOT EXISTS {self.namespace}"
        self.execute_query(query)

    def select_records(
        self, condition: str | None = None, return_dataframe: bool = False
    ):
        query = f"SELECT * FROM {self.namespace}.{self.table_name}"
        if condition:
            query += f" WHERE {condition}"
        records = self.execute_query(query)
        if return_dataframe:
            try:
                df = pd.DataFrame(
                    records, columns=[i[0] for i in self.cursor.description]
                )
                return df
            except TypeError:
                return pd.DataFrame()
        else:
            return records

    def list_tables(self):
        query = f"SHOW TABLES from {self.namespace}"
        tables = self.execute_query(query)
        return [table[0] for table in tables]
