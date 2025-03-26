import json

import boto3
from botocore.exceptions import ClientError

from repenseai.secrets.base import BaseSecrets

from repenseai.utils.logs import logger


class AWSSecrets(BaseSecrets):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AWSSecrets, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        secret_name: str,
        region_name: str,
        profile_name: str = None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_session_token=None,
    ):
        if not self._initialized:
            self._secrets = {}

            self.secret_name = secret_name
            self.region_name = region_name

            if profile_name:

                session = boto3.Session(profile_name=profile_name)

                self.client = session.client(
                    service_name="secretsmanager",
                    region_name=self.region_name,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    aws_session_token=aws_session_token,
                )

            else:
                self.client = boto3.client(
                    service_name="secretsmanager",
                    region_name=self.region_name,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    aws_session_token=aws_session_token,
                )

            self._initialized = True

    def get_secret(self, secret_key: str) -> str:
        if self._secrets.get(secret_key):
            return self._secrets.get(secret_key)

        try:
            response = self.client.get_secret_value(SecretId=self.secret_name)

            secrets = json.loads(response["SecretString"])
        except ClientError as e:
            logger(f"Error getting secret: {e}")
            return None

        secret = secrets.get(secret_key)

        if secret_key not in self._secrets:
            self._secrets[secret_key] = secret

        return secret
