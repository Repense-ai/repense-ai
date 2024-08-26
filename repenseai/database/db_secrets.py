from repenseai.aws.secrets_manager import SecretsManager

class DBSecrets():
    def __init__(self, secret_name: str, region_name: str):
        secret_manager = SecretsManager(secret_name=secret_name, region_name=region_name)

        self.host = os.getenv("DB_ENDPOINT") or secret_manager.get_secret("DB_ENDPOINT")
        self.user = os.getenv("DB_USER") or secret_manager.get_secret("DB_USER")
        self.password = os.getenv("DB_PASSWORD") or secret_manager.get_secret("DB_PASSWORD")
        self.port = os.getenv("DB_PORT") or secret_manager.get_secret("DB_PORT")

        self.admin_password = os.getenv("ADMIN_PASSWORD") or secret_manager.get_secret("ADMIN_PASSWORD")
        self.test_password = os.getenv("TEST_PASSWORD") or secret_manager.get_secret("TEST_PASSWORD")

    def get_admin_password(self):
        return self.admin_password

    def get_test_password(self):
        return self.test_password
    
    def get_db_secrets(self):
        return {
            "host": self.host,
            "user": self.user,
            "password": self.password,
            "port": self.port
        }