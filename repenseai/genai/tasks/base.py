# TODO:
# improve templating so that context keywords are optional
# instead of raising errors when missing


class BaseTask(object):
    """abstract object that implements a .predict() method"""

    def __init__(self):
        pass

    def predict(self, **kwargs):
        pass
