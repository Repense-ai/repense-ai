class BaseSecrets(object):
    """abstract object that implements a .run() method"""

    def __init__(self):
        pass

    def get_secret(self, **kwargs):
        pass