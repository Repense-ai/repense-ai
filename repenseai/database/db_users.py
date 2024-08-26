from repenseai.database.db_manager import DBManager, DBConnection
from repenseai.database.db_secrets import DBSecrets

from datetime import datetime
from repenseai.utils.hasher import Hasher

class DBUsers():
    def __init__(self, db_name: str, db_schema: str, db_table: str):
        self.db_secrets = DBSecrets()
        self.db_connection = DBConnection(self.db_secrets.get_db_secrets())
        self.db_manager = DBManager(self.db_connection, db_name, db_table)

        self.db_schema = db_schema
        self.db_table = db_table
        self.db_name = db_name

    def insert_user_login(self, login: dict[str, Any]):
        password = login["password"]
        hashed_password = Hasher([password]).generate()

        login["password"] = hashed_password[0]
        login["created_at"] = datetime.now()

        try:
            tables = self.db_manager.list_tables()
        except Exception:
            tables = []

        if self.db_table not in tables:
            self.db_manager.create_table(self.db_schema)

        self.db_manager.insert_record(login)

    def create_admin_login(self, admin_password: str):
        if not admin_password:
            raise Exception("Admin password is not set")

        login = {
            "name": "Admin",
            "password": self.db_secrets.get_admin_password(),
            "email": "admin@snc-ai.com",
            "admin": True,
        }

        self.insert_user_login(login)

    def create_test_login(self, test_password: str):
        if not test_password:
            raise Exception("Test password is not set")

        login = {
            "name": "Test",
            "password": self.db_secrets.get_test_password(),
            "email": "test@snc-ai.com",
            "admin": False,
        }

        self.insert_user_login(login)

    def check_streamlit_login(self):
        with self.get_connection():
            credentials = {"usernames": {}}
            records = self.db_manager.select_records()

            for record in records:
                name = record[1]
                email = record[2]
                db_pass = record[3]
                admin = record[4]

                temp_dict = {
                    email: {"name": name, "password": db_pass, "admin": admin},
                }

                credentials["usernames"].update(temp_dict)

            return credentials

    def delete_user_login(self, email: str):
        
        condition = f"email = '{email}'"

        try:
            self.db_manager.delete_records(condition)
        except Exception as e:
            raise Exception(f"Error deleting user: {e}")