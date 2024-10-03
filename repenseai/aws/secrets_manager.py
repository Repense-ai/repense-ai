import json

import boto3
from botocore.exceptions import ClientError

from repenseai.utils.logs import logger


class SecretsManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SecretsManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, secret_name: str, region_name: str):
        if not self._initialized:
            self._secrets = {}

            self.secret_name = secret_name
            self.region_name = region_name

            self.client = boto3.client(
                service_name="secretsmanager", region_name=self.region_name
            )

            self._initialized = True

    def get_secret(self, secret_key: str) -> str:
        if self._secrets.get(secret_key):
            return self._secrets.get(secret_key)

        try:
            get_secret_value_response = self.client.get_secret_value(
                SecretId=self.secret_name
            )
            secrets = json.loads(get_secret_value_response["SecretString"])
        except ClientError as e:
            logger(f"Error getting secret: {e}")
            return None

        secret = secrets.get(secret_key)

        if secret_key not in self._secrets:
            self._secrets[secret_key] = secret

        return secret
