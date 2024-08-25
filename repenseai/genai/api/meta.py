import os
import requests
import json

# from repenseai.utils.logs import logger


def get_api_key():
    if "META_API_KEY" not in os.environ.keys():
        from dotenv import load_dotenv

        load_dotenv()
    if os.getenv("META_API_KEY") is not None:
        return os.getenv("META_API_KEY")
    else:
        return os.getenv("REQUESTER_TOKEN")


class MetaAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def send_message(self, number: str, message: str) -> None:

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-type": "application/json",
        }

        data = {
            "messaging_product": "whatsapp",
            "preview_url": False,
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "body": message,
            },
        }

        # n_id = "206628859194870" # meu numero
        n_id = "195556453642803"  # teste

        _ = requests.post(
            f"https://graph.facebook.com/v18.0/{n_id}/messages",
            headers=headers,
            data=json.dumps(data),
        )

        # logger(response.json())
