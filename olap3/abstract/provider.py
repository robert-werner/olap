from abc import ABCMeta, abstractmethod


class Provider(metaclass=ABCMeta):
    """
    This covers all provider specifics.
    """

    @staticmethod
    @abstractmethod
    def connect(**connect_params):
        """
        Connect to OLAP Server and return an IConnection instance or
        throws an exception.
        What parameters are needed is left to the actual olap provider.
        """