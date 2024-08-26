from repenseai.database.db_manager import DBManager, DBConnection
from repenseai.database.db_secrets import DBSecrets

class DBUsage():
    def __init__(self, db_name: str, db_schema: str, db_table: str):
        self.db_secrets = DBSecrets()
        self.db_connection = DBConnection(self.db_secrets.get_db_secrets())
        self.db_manager = DBManager(self.db_connection, db_name, db_table)

        self.db_schema = db_schema
        self.db_table = db_table
        self.db_name = db_name

    def insert_usage_record(self, record: dict[str, Any]):
        try:
            tables = self.db_manager.list_tables()
        except Exception:
            tables = []

        if self.db_table not in tables:
            self.db_manager.create_table(self.db_schema)

        self.db_manager.insert_record(record)

    def select_usage_records(self, condition: str | None = None, return_dataframe: bool = True):
        dataframe = self.db_manager.select_records(condition, return_dataframe)
        return dataframe

    def check_limits(self, username: str, variable: str, limit: int):
        if username == "Admin":
            return False

        try:
            tables = self.db_manager.list_tables()
        except Exception:
            tables = []

        if self.db_table not in tables:
            return False

        condition = f"username = '{username}'"
        dataframe = self.db_manager.select_records(condition, return_dataframe=True)

        if dataframe.empty:
            return False

        total_pages = dataframe[variable].sum()

        if total_pages >= limit:
            return True

        return False

    def delete_user_records(self, username: str):
        condition = f"username = '{username}'"
        try:
            self.db_manager.delete_records(condition)
        except Exception as e:
            raise Exception(f"Error deleting user records: {e}")

    def clean_test_records(self, test_users: list[str]):
        for user in test_users:
            self.delete_user_records(user)