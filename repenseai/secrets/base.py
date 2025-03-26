class BaseSecrets(object):
    """abstract object that implements a .get_secret() method"""

    def __init__(self):
        pass

    def get_secret(self, **kwargs):
        pass
