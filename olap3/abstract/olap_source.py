from abc import ABCMeta, abstractmethod


class OLAPSource(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def getCatalogs():
        """Returns a list of ICatalogs in the Datasource."""

    @staticmethod
    @abstractmethod
    def getCatalog(unique_name):
        """Returns a ICatalog in the Datasource with the given unique name."""
