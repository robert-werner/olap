from abc import ABCMeta, abstractmethod


class Connection(metaclass=ABCMeta):
    """
    Talk to the backend through this.
    """

    ...
