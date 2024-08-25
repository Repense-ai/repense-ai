import io


class NamedBytesIO(io.BytesIO):
    def __init__(self, buffer, name):
        super().__init__(buffer)

        self.name = name


def get_memory_buffer(binary):
    audio_bytesio = NamedBytesIO(binary, "audio.ogg")
    audio_buffer = io.BufferedReader(audio_bytesio)

    return audio_buffer
