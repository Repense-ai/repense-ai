class BaseSecrets(object):
    """abstract object that implements a .predict() method"""

    def __init__(self):
        pass

    def get_secret(self, **kwargs):
        pass