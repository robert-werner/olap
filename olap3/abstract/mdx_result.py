from abc import abstractmethod, ABCMeta


class MDXResult(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def getSlice(properties=None, **kwargs):
        """
        getSlice(properties=None [,Axis<Number>=n|Axis<Number>=[i1,i2,..,ix]])

        Return the resulting cells from a MDX statement.
        The result is presented as an array of arrays of arrays of...
        depending on amount of axes in the MDX.
        You can carve out slices you need by listing the indices of the axes
        you are interested in.

        Examples:

        result.getSlice() # return all
        result.getSlice(Axis0=3) # carve out the 4th column
        result.getSlice(Axis0=3, SlicerAxis=0) # same as above, SlicerAxis is ignored
        result.getSlice(Axis1=[1,2]) # return the data sliced at the 2nd and 3rd row
        result.getSlice(Axis0=3, Axis1=[1,2]) # return the data sliced at the 2nd and
                                                3rd row in addition to the 4th column

        If you do not want the whole cell returned but just a single property of it
        (like the Value) name that property in the property parameter:

        # from all the cells just get me the Value property
        result.getSlice(properties="Value")
        # from all the cells just get me the Value property
        result.getSlice(properties=["Value", "FmtValue"])

        """

    @staticmethod
    @abstractmethod
    def getAxisTuple(axis):
        """Returns the tuple on axis with name <axis>, usually 'Axis0', 'Axis1', 'SlicerAxis'.
        If axis is a number return tuples on the <axis>-th axis."""
