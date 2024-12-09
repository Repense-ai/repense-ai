import io
import base64

from PIL import Image


def display_base64_image(base64_str: str) -> None:

    image_data = base64.b64decode(base64_str)

    image = Image.open(io.BytesIO(image_data))
    image.show()

def display_bytes_image(image_bytes: bytes) -> None:

    image = Image.open(io.BytesIO(image_bytes))
    image.show()