from abc import ABCMeta, abstractmethod


class OLAPSchemaElement(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def getElementProperties():
        """Return a dictionary of this element's properties."""


class Catalog(OLAPSchemaElement):

    @staticmethod
    @abstractmethod
    def getCubes():
        """Returns a list of ICube in the catalog."""

    @staticmethod
    @abstractmethod
    def getCube(unique_name):
        """Returns a ICube in the catalog with the given unique name."""

    @staticmethod
    @abstractmethod
    def getDimensions(unique_name=None):
        """Returns a list of IDimension in the catalog optionally
        matching the given name."""

    @staticmethod
    @abstractmethod
    def getDimension(unique_name):
        """Returns a IDimension in the Catalog with the given unique name."""

    @staticmethod
    @abstractmethod
    def getHierarchies(unique_name=None):
        """Returns a list of IHierarchy in the catalog optionally
        matching the given name."""

    @staticmethod
    @abstractmethod
    def getHierarchy(unique_name):
        """Returns a IHierarchy in the catalog with the given unique name."""

    @staticmethod
    @abstractmethod
    def getSets(unique_name=None):
        """Returns a list of ISet in the catalog optionally
        matching the given name."""

    @staticmethod
    @abstractmethod
    def getSet(unique_name):
        """Returns a ISet in the catalog with the given unique name."""

    @staticmethod
    @abstractmethod
    def getMeasures(unique_name=None):
        """Returns a list of IMeasure in the catalog optionally
        matching the given name."""

    @staticmethod
    @abstractmethod
    def getMeasure(unique_name):
        """Returns a IMeasure in the catalog with the given unique name."""

    @staticmethod
    @abstractmethod
    def query(mdx_stmt):
        """Return a IMDXResult resulting from executing the mdx statement."""

    @staticmethod
    @abstractmethod
    def getRelationships(unique_name=None):
        """Returns a list of IRelationships in the catalog optionally
        matching the given name."""


class Cube(OLAPSchemaElement):

    @staticmethod
    @abstractmethod
    def getHierarchies():
        """Returns a list of IHierarchy related to the cube."""

    @staticmethod
    @abstractmethod
    def getHierarchy(unique_name):
        """Returns a IHierarchy in the cube with the given unique name."""

    @staticmethod
    @abstractmethod
    def getMeasures():
        """Returns a list of IMeasure in this cube."""

    @staticmethod
    @abstractmethod
    def getMeasure(unique_name):
        """Returns a IMeasure in the cube with the given unique name."""

    @staticmethod
    @abstractmethod
    def getSets():
        """Returns a list of ISet in this cube."""

    @staticmethod
    @abstractmethod
    def getSet(unique_name):
        """Returns a ISet with the given unique name in the cube."""

    @staticmethod
    @abstractmethod
    def getDimensions():
        """Returns a list of IDimension in the cube"""

    @staticmethod
    @abstractmethod
    def getDimension(unique_name):
        """Returns a IDimension in the cube with the given unique name."""


class Dimension(OLAPSchemaElement):

    @staticmethod
    @abstractmethod
    def getHierarchies():
        """Returns a list of IHierarchy related to the cube."""

    @staticmethod
    @abstractmethod
    def getHierarchy(unique_name):
        """Returns a IHierarchy in the cube with the given unique name."""

    @staticmethod
    @abstractmethod
    def getMembers():
        """Returns a list of IMember in the dimension."""

    @staticmethod
    @abstractmethod
    def getMember(unique_name):
        """Returns a IMember of the given name in the dimension."""


class Hierarchy(OLAPSchemaElement):

    @staticmethod
    @abstractmethod
    def getLevels():
        """Returns a list of ILevel in the hierarchy."""

    @staticmethod
    @abstractmethod
    def getLevel(unique_name):
        """Returns a ILevel in the hierarchy with the given unique name."""

    @staticmethod
    @abstractmethod
    def getMembers():
        """Returns a list of IMember in the hierarchy."""

    @staticmethod
    @abstractmethod
    def getMember(unique_name):
        """Returns a IMember of the given name in the hierarchy."""


class Level(OLAPSchemaElement):

    @staticmethod
    @abstractmethod
    def getMembers():
        """Returns a list of IMember from this level."""

    @staticmethod
    @abstractmethod
    def getProperties():
        """Returns a list of IProperty in the level."""

    @staticmethod
    @abstractmethod
    def getProperty(unique_name):
        """Returns a IProperty with the given unique name in the level."""


class Member(OLAPSchemaElement):

    @staticmethod
    @abstractmethod
    def getParent():
        """Return this member's parent member unique or None if this is the root
        already."""

    @staticmethod
    @abstractmethod
    def getChildren():
        """Return this member's children in a list."""

    @staticmethod
    @abstractmethod
    def hasChildren():
        """Returns True if this mmeber has children False otherwise."""

    @staticmethod
    @abstractmethod
    def getSiblings():
        """Return this member's siblings in a list."""

    @staticmethod
    @abstractmethod
    def hasSiblings():
        """Returns True if this mmeber has siblings False otherwise."""

    @staticmethod
    @abstractmethod
    def getAncestors():
        """Return the member's line of ancestors in a list (self not included)."""


class Measure(OLAPSchemaElement):

    @staticmethod
    @abstractmethod
    def getElementProperties():
        """Return a dictionary of this element's properties."""


class Property(OLAPSchemaElement):

    @staticmethod
    @abstractmethod
    def getElementProperties():
        """Return a dictionary of this element's properties."""


class Set(OLAPSchemaElement):

    @staticmethod
    @abstractmethod
    def getElementProperties():
        """Return a dictionary of this element's properties."""


class Relationship(OLAPSchemaElement):

    @staticmethod
    @abstractmethod
    def getElementProperties():
        """Return a dictionary of this element's properties."""
