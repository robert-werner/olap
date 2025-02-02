olap3
=========
This package is meant for accessing XMLA datasources (Pentaho and etc.) - see http://en.wikipedia.org/wiki/XML_for_Analysis

Derived from old and unsupported [may-day/olap](https://github.com/may-day/olap.git)

Now you may install olap3 just with `python setup.py install` (in GitHub repository folder) or with `pip install olap3` without the hassle of installing [xmla](https://pypi.org/project/xmla/) separately

Example
-

_You may use olap3 as drop-in replacement of olap package, no changes of existing code are needed._

Here is an example how to use it:

```python

    import olap.xmla.xmla as xmla
    p = xmla.XMLAProvider()
    # mondrian
    c = p.connect(location="http://localhost:8080/mondrian/xmla")

    # or ssas - note that this needs setup on an iis
    # also you'll probably need to authenticate using kerberos
    # from requests_kerberos import HTTPKerberosAuth
    # c = p.connect(location="https://my-as-server/olap/msmdpump.dll", 
    #               sslverify="/path/to/my/as-servers-ca-cert.pem", auth=HTTPKerberosAuth())

    # getting info about provided data
    print(c.getDatasources())
    print(c.getMDSchemaCubes())
    # for ssas a catalog is needed, so the call would be like
    # get a catalogname from a call to c.getDBSchemaCatalogs()
    # c.getMDSchemaCubes(properties={"Catalog":"a catalogname"})

    # execute a MDX (working against the foodmart sample catalog of mondrian)
    cmd= """
    select {[Measures].ALLMEMBERS} * {[Time].[1997].[Q2].children} on columns, 
    [Gender].[Gender].ALLMEMBERS on rows 
    from [Sales]
    """

    res = c.Execute(cmd, Catalog="FoodMart")
    #return only the Value property from the cells
    res.getSlice(properties="Value")
    # or two props
    res.getSlice(properties=["Value", "FmtValue"]) 

    # to return some subcube from the result you can
    # return all
    res.getSlice()
    # just the 4th column
    res.getSlice(Axis0=3) 
    # same as above, SlicerAxis is ignored
    res.getSlice(Axis0=3, SlicerAxis=0) 
    # return the data sliced at the 2nd and 3rd row
    res.getSlice(Axis1=[1,2]) 
    # return the data sliced at the 2nd and 3rd row and at the 4th column
    res.getSlice(Axis0=3, Axis1=[1,2]) 
```

Using the procedural interface:
```python

    import olap.xmla.xmla as xmla

    p = xmla.XMLAProvider()
    c = p.connect(location="http://localhost:8080/mondrian/xmla")
    s = c.getOLAPSource()

    # import olap.interfaces as oi
    # oi.IOLAPSource.providedBy(s) == True

    s.getCatalogs()
    s.getCatalog("FoodMart").getCubes()
    s.getCatalog("FoodMart").getCube("HR").getDimensions()
    s.getCatalog("FoodMart").getCube("HR").getDimension("[Department]").\
    getMembers()
    s.getCatalog("FoodMart").getCube("HR").getDimension("[Department]").\
    getMember("[Department].[14]")

    cmd= """
    select {[Measures].ALLMEMBERS} * {[Time].[1997].[Q2].children} on columns, 
    [Gender].[Gender].ALLMEMBERS on rows 
    from [Sales]
    """
    res=s.getCatalog("FoodMart").query(cmd)
    res.getSlice()
```

Note
-

The contained vs.wsdl originates from the following package:
http://www.microsoft.com/en-us/download/confirmation.aspx?id=9388 and
was subsequently modified (which parameters go in the soap header) to
work with the zeep.
