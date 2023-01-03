import asyncio

import httpx
import six
import zeep
from async_class import AsyncClass
from six import u
from zeep import Transport, Plugin, Client
from zeep.exceptions import Fault

import olap3
from olap3.abstract.connection import Connection
from olap3.abstract.provider import Provider
from olap3.abstract.schema_elements import OLAPSchemaElement
from olap3.abstract.xmla import schemaElementTypes
from olap3.clients import AsyncClient
from olap3.exceptions import SchemaElementNotFound, XMLAException
from olap3.formatreader import TupleFormatReader, TupleFormatReaderTabular
from olap3.plugins import SessionPlugin, LogRequest
from olap3.resources import defaultwsdl
from olap3.transports import AsyncTransport
from olap3.utils import schemaNameToMethodName, ns_name, as_etree, fromETree, aslist, dictify

xmla1_1_rowsets = ["DISCOVER_DATASOURCES",
                   "DISCOVER_PROPERTIES",
                   "DISCOVER_SCHEMA_ROWSETS",
                   "DISCOVER_ENUMERATORS",
                   "DISCOVER_LITERALS",
                   "DISCOVER_KEYWORDS",
                   "DBSCHEMA_CATALOGS",
                   "DBSCHEMA_COLUMNS",
                   "DBSCHEMA_TABLES",
                   "DBSCHEMA_TABLES_INFO",
                   "DBSCHEMA_PROVIDER_TYPES",
                   "MDSCHEMA_ACTIONS",
                   "MDSCHEMA_CUBES",
                   "MDSCHEMA_DIMENSIONS",
                   "MDSCHEMA_FUNCTIONS",
                   "MDSCHEMA_HIERARCHIES",
                   "MDSCHEMA_MEASURES",
                   "MDSCHEMA_MEMBERS",
                   "MDSCHEMA_PROPERTIES",
                   "MDSCHEMA_SETS"
                   ]

schema_xmla = "urn:schemas-microsoft-com:xml-analysis"
schema_xmla_rowset = "urn:schemas-microsoft-com:xml-analysis:rowset"
schema_xmla_mddataset = "urn:schemas-microsoft-com:xml-analysis:mddataset"
schema_soap_env = "http://schemas.xmlsoap.org/soap/envelope/"
schema_xml = "http://www.w3.org/2001/XMLSchema"


class XMLAClass(OLAPSchemaElement):

    def __init__(self, unique_name_property, properties, schemaElementName, conn):
        self._properties = properties
        self._conn = conn
        self.unique_name_property = unique_name_property
        self.schemaElementName = schemaElementName

    def getElementProperties(self):
        return self._properties

    def getUniqueName(self):
        if hasattr(self, self.unique_name_property):
            return u("") + getattr(self, self.unique_name_property)

    def objectFactory(self, classname, unp, schemaElementName, props):
        _class = globals()[classname]
        return [_class(unp, prop, schemaElementName, self._conn) for prop in props]

    def getSchemaElements(self, schemaElementName, unique_name,
                          aslist=False, more_restrictions=None,
                          more_properties=None,
                          generate_instance=True):
        schemaElementType = schemaElementTypes[schemaElementName]
        r = restrictions = {}

        for otherRestrict in schemaElementType["RESTRICT_ON"]:
            other_restrict_et = schemaElementTypes[otherRestrict]
            restriction_name = other_restrict_et["RESTRICTION_NAME"]
            try:
                r[restriction_name] = getattr(self, restriction_name)
            except AttributeError:
                # print("failed getting value of attribute {}".format(rn))
                if more_restrictions and restriction_name in more_restrictions:
                    r[restriction_name] = more_restrictions[restriction_name]
                else:
                    raise

        if unique_name:
            r[schemaElementType["RESTRICTION_NAME"]] = unique_name

        if more_restrictions:
            r.update(more_restrictions)

        catalog_restriction_name = schemaElementTypes["CATALOG"]["RESTRICTION_NAME"]
        try:
            properties = {"Catalog": getattr(self, catalog_restriction_name)}
        except:
            properties = {}

        if more_properties:
            properties.update(more_properties)

        if catalog_restriction_name in r and len(r) > 1:
            properties["Catalog"] = r.pop(catalog_restriction_name)

        func = getattr(self._conn, schemaElementType["XMLA_FUNC"])
        props = func(r, properties)

        if props is None or len(props) == 0:
            raise SchemaElementNotFound(r, properties)

        if generate_instance:
            result = self.objectFactory(schemaElementType["ELEMENT_CLASS"],
                                        schemaElementType["PROPERTY_NAME"],
                                        schemaElementName,
                                        props)
        else:
            result = props

        if not aslist:
            result = result[0]
        return result

    def query(self, mdx_stmt):
        return self._conn.Execute(mdx_stmt, Catalog=self.CATALOG_NAME)

    def __getattr__(self, name):
        if name in self._properties:
            return self._properties[name]


class AsyncXMLAClass(AsyncClass):

    async def __ainit__(self, unique_name_property, properties, schemaElementName, conn):
        self._properties = properties
        self._conn = conn
        self.unique_name_property = unique_name_property
        self.schemaElementName = schemaElementName

    async def getElementProperties(self):
        return self._properties

    async def getUniqueName(self):
        if hasattr(self, self.unique_name_property):
            return u("") + getattr(self, self.unique_name_property)

    async def objectFactory(self, classname, unp, schemaElementName, props, conn):
        _class = globals()[classname]
        return [await _class(unp, prop, schemaElementName, conn) for prop in props]

    async def getSchemaElements(self, schemaElementName, unique_name,
                                aslist=False, more_restrictions=None,
                                more_properties=None,
                                generate_instance=True):
        schemaElementType = schemaElementTypes[schemaElementName]
        r = restrictions = {}

        for otherRestrict in schemaElementType["RESTRICT_ON"]:
            other_restrict_et = schemaElementTypes[otherRestrict]
            restriction_name = other_restrict_et["RESTRICTION_NAME"]
            try:
                r[restriction_name] = getattr(self, restriction_name)
            except AttributeError:
                # print("failed getting value of attribute {}".format(rn))
                if more_restrictions and restriction_name in more_restrictions:
                    r[restriction_name] = more_restrictions[restriction_name]
                else:
                    raise

        if unique_name:
            r[schemaElementType["RESTRICTION_NAME"]] = unique_name

        if more_restrictions:
            r.update(more_restrictions)

        properties = {}

        catalog_restriction_name = schemaElementTypes["CATALOG"]["RESTRICTION_NAME"]
        if hasattr(self, catalog_restriction_name):
            if getattr(self, catalog_restriction_name):
                properties = {"Catalog": getattr(self, catalog_restriction_name)}

        if more_properties:
            properties.update(more_properties)

        if catalog_restriction_name in r and len(r) > 1:
            properties["Catalog"] = r.pop(catalog_restriction_name)
        func = getattr(self._conn, schemaElementType["XMLA_FUNC"])
        props = await func(r, properties)

        if props is None or len(props) == 0:
            raise SchemaElementNotFound(r, properties)

        if generate_instance:
            result = await self.objectFactory("Async" + schemaElementType["ELEMENT_CLASS"],
                                              schemaElementType["PROPERTY_NAME"],
                                              schemaElementName,
                                              props,
                                              self._conn)
        else:
            result = props

        if not aslist:
            result = result[0]
        return result

    async def query(self, mdx_stmt):
        return await self._conn.Execute(mdx_stmt, Catalog=self.CATALOG_NAME)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]


class AsyncXMLACube(AsyncXMLAClass):

    async def getHierarchies(self):
        return await self.getHierarchy()

    async def getHierarchy(self, unique_name=None):
        return await self.getSchemaElements("HIERARCHY", unique_name,
                                            aslist=unique_name == None)

    async def getMeasures(self):
        return await self.getMeasure()

    async def getMeasure(self, unique_name=None):
        return await self.getSchemaElements("MEASURE", unique_name,
                                            aslist=unique_name == None)

    async def getSets(self):
        return await self.getSet()

    async def getSet(self, unique_name=None):
        return await self.getSchemaElements("SET", unique_name,
                                            aslist=unique_name == None)

    async def getDimensions(self):
        return await self.getDimension()

    async def getDimension(self, unique_name=None):
        return await self.getSchemaElements("DIMENSION", unique_name,
                                            aslist=unique_name == None)


class AsyncXMLACatalog(AsyncXMLAClass):

    async def getCubes(self):
        return await self.getCube()

    async def getCube(self, unique_name=None):
        return await self.getSchemaElements("CUBE", unique_name,
                                            aslist=unique_name == None)

    async def getDimensions(self, unique_name=None):
        return await self.getSchemaElements("CATALOG_DIMENSION", unique_name, aslist=True)

    async def getDimension(self, unique_name):
        return await self.getSchemaElements("CATALOG_DIMENSION", unique_name,
                                            aslist=unique_name == None)

    async def getHierarchies(self, unique_name=None):
        return await self.getSchemaElements("CATALOG_HIERARCHY", unique_name, aslist=True)

    async def getHierarchy(self, unique_name=None):
        return await self.getSchemaElements("CATALOG_HIERARCHY", unique_name,
                                            aslist=unique_name == None)

    async def getSets(self, unique_name=None):
        return await self.getSchemaElements("CATALOG_SET", unique_name, aslist=True)

    async def getSet(self, unique_name=None):
        return await self.getSchemaElements("CATALOG_SET", unique_name,
                                            aslist=unique_name == None)

    async def getMeasures(self, unique_name=None):
        return await self.getSchemaElements("CATALOG_MEASURE", unique_name, aslist=True)

    async def getMeasure(self, unique_name):
        return await self.getSchemaElements("CATALOG_MEASURE", unique_name,
                                            aslist=unique_name == None)


class XMLAConnection(Connection):

    @classmethod
    def addMethod(cls, funcname, func):
        return setattr(cls, funcname, func)

    @classmethod
    def setupMembers(cls):
        def getFunc(schemaName):
            return lambda this, *args, **kw: cls.Discover(this,
                                                          schemaName,
                                                          *args, **kw)

        for schemaName in xmla1_1_rowsets:
            mname = schemaNameToMethodName(schemaName)
            cls.addMethod(mname, getFunc(schemaName))

    def __init__(self, url, location, sslverify, **kwargs):
        if "session" in kwargs:
            session = kwargs["session"]
            del kwargs["session"]
            transport = Transport(session=session)
        else:
            transport = Transport()

        if "auth" in kwargs:
            transport.session.auth = kwargs["auth"]
            del kwargs["auth"]

        transport.session.verify = sslverify
        self.sessionplugin = SessionPlugin(self)
        plugins = [self.sessionplugin]

        if "log" in kwargs:
            log = kwargs.get("log")
            if isinstance(log, Plugin):
                plugins.append(log)
            elif log == True:
                plugins.append(LogRequest())
            del kwargs["log"]

        self.client = Client(url,
                             transport=transport,
                             plugins=plugins)

        self.service = self.client.create_service(ns_name(schema_xmla, "MsXmlAnalysisSoap"), location)
        self.client.set_ns_prefix(None, schema_xmla)
        # optional, call might fail
        self.getMDSchemaLevels = lambda *args, **kw: self.Discover("MDSCHEMA_LEVELS",
                                                                   *args, **kw)
        self.setListenOnSessionId(False)
        self.setSessionId(None)
        self._soapheaders = None

    def getListenOnSessionId(self):
        return self.listenOnSessionId

    def setListenOnSessionId(self, trueOrFalse):
        self.listenOnSessionId = trueOrFalse

    def setSessionId(self, sessionId):
        self.sessionId = sessionId

    def Discover(self, what, restrictions=None, properties=None):
        rl = as_etree(restrictions, "RestrictionList")
        pl = as_etree(properties, "PropertyList")
        try:
            doc = self.service.Discover(RequestType=what, Restrictions=rl, Properties=pl,
                                        _soapheaders=self._soapheaders)
            root = fromETree(doc.body["return"]["_value_1"], ns=schema_xmla_rowset)
            res = getattr(root, "row", [])
            if res:
                res = aslist(res)
        except Fault as fault:
            raise XMLAException(fault.message, dictify(fromETree(fault.detail, ns=None)))
        return res

    def Execute(self, command, dimformat="Multidimensional",
                axisFormat="TupleFormat", **kwargs):
        if isinstance(command, six.stringtypes):
            command = as_etree({"Statement": command})
        props = {"Format": dimformat, "AxisFormat": axisFormat}
        props.update(kwargs)

        plist = as_etree({"PropertyList": props})
        ns = schema_xmla_mddataset if dimformat == "Multidimensional" else schema_xmla_rowset
        reader = TupleFormatReader if dimformat == "Multidimensional" else TupleFormatReaderTabular
        try:

            res = self.service.Execute(Command=command, Properties=plist, _soapheaders=self._soapheaders)
            root = res.body["return"]["_value_1"]
            cols = None if dimformat == "Multidimensional" else fromETree(root, ns=schema_xml, name="schema")
            rows = fromETree(root, ns=ns)
            return reader(rows, cols)
        except Fault as fault:
            raise XMLAException(fault.message, dictify(fromETree(fault.detail, ns=None)))

    def BeginSession(self):
        bs = self.client.get_element(ns_name(schema_xmla, "BeginSession"))(mustUnderstand=1)
        self.setListenOnSessionId(True)
        cmd = as_etree("Statement")

        self.service.Execute(Command=cmd, _soapheaders={"BeginSession": bs})
        self.setListenOnSessionId(False)

        sess = self.client.get_element(ns_name(schema_xmla, "Session"))(SessionId=self.sessionId, mustUnderstand=1)
        self._soapheaders = {"Session": sess}

    def EndSession(self):
        if self.sessionId is not None:
            es = self.client.get_element(ns_name(schema_xmla, "EndSession"))(SessionId=self.sessionId, mustUnderstand=1)
            cmd = as_etree("Statement")
            self.service.Execute(Command=cmd, _soapheaders={"EndSession": es})
            self.setSessionId(None)
            self._soapheaders = None


class AsyncXMLAConnection(AsyncClass, Connection):

    @classmethod
    async def addMethod(cls, funcname, func):
        return setattr(cls, funcname, func)

    @classmethod
    async def setupMembers(cls):
        async def getFunc(schemaName):
            return lambda this, *args, **kw: (await cls.Discover(this, schemaName, *args, **kw) for _ in
                                              '_').__anext__()

        for schemaName in xmla1_1_rowsets:
            mname = schemaNameToMethodName(schemaName)
            await cls.addMethod(mname, await getFunc(schemaName))

    async def __ainit__(self, url, location, sslverify, **kwargs):
        if "transport" in kwargs:
            self.transport = kwargs["transport"]
            del kwargs["transport"]
        else:
            self.transport = await AsyncTransport()

        self.sessionplugin = SessionPlugin(self)
        plugins = [self.sessionplugin]

        if "log" in kwargs:
            log = kwargs.get("log")
            if isinstance(log, Plugin):
                plugins.append(log)
            elif log == True:
                plugins.append(LogRequest())
            del kwargs["log"]

        if "client" in kwargs:
            self.client = kwargs["client"]
            del kwargs["client"]
        else:
            self.client = await AsyncClient(url,
                                            transport=self.transport,
                                            plugins=plugins)

        self.service = await self.client.create_service_async(ns_name(schema_xmla, "MsXmlAnalysisSoap"), location)
        self.client.set_ns_prefix(None, schema_xmla)
        # optional, call might fail
        self.getMDSchemaLevels = lambda *args, **kw: (await self.Discover("MDSCHEMA_LEVELS", *args, **kw) for _ in
                                                      '_').__anext__()
        self.setListenOnSessionId(False)
        self.setSessionId(None)
        self._soapheaders = None

    def getListenOnSessionId(self):
        return self.listenOnSessionId

    def setListenOnSessionId(self, trueOrFalse):
        self.listenOnSessionId = trueOrFalse

    def setSessionId(self, sessionId):
        self.sessionId = sessionId

    async def Discover(self, what, restrictions=None, properties=None):
        rl = as_etree(restrictions, "RestrictionList")
        pl = as_etree(properties, "PropertyList")
        try:
            doc = await self.service.Discover(RequestType=what, Restrictions=rl, Properties=pl,
                                              _soapheaders=self._soapheaders)
            root = fromETree(doc.body["return"]["_value_1"], ns=schema_xmla_rowset)
            res = getattr(root, "row", [])
            if res:
                res = aslist(res)
        except Fault as fault:
            raise XMLAException(fault.message, dictify(fromETree(fault.detail, ns=None)))
        return res

    async def Execute(self, command, dimformat="Multidimensional",
                      axisFormat="TupleFormat", **kwargs):
        if isinstance(command, six.stringtypes):
            command = as_etree({"Statement": command})
        props = {"Format": dimformat, "AxisFormat": axisFormat}
        props.update(kwargs)

        plist = as_etree({"PropertyList": props})
        ns = schema_xmla_mddataset if dimformat == "Multidimensional" else schema_xmla_rowset
        reader = TupleFormatReader if dimformat == "Multidimensional" else TupleFormatReaderTabular
        try:

            res = self.service.Execute(Command=command, Properties=plist, _soapheaders=self._soapheaders)
            root = res.body["return"]["_value_1"]
            cols = None if dimformat == "Multidimensional" else fromETree(root, ns=schema_xml, name="schema")
            rows = fromETree(root, ns=ns)
            return reader(rows, cols)
        except Fault as fault:
            raise XMLAException(fault.message, dictify(fromETree(fault.detail, ns=None)))

    async def BeginSession(self):
        bs = self.client.get_element(ns_name(schema_xmla, "BeginSession"))(mustUnderstand=1)
        self.setListenOnSessionId(True)
        cmd = as_etree("Statement")

        self.service.Execute(Command=cmd, _soapheaders={"BeginSession": bs})
        self.setListenOnSessionId(False)

        sess = await self.client.get_element(ns_name(schema_xmla, "Session"))(SessionId=self.sessionId,
                                                                              mustUnderstand=1)
        self._soapheaders = {"Session": sess}

    async def EndSession(self):
        if self.sessionId is not None:
            es = await self.client.get_element(ns_name(schema_xmla, "EndSession"))(SessionId=self.sessionId,
                                                                                   mustUnderstand=1)
            cmd = as_etree("Statement")
            self.service.Execute(Command=cmd, _soapheaders={"EndSession": es})
            self.setSessionId(None)
            self._soapheaders = None


class XMLAProvider(Provider):

    def connect(self, url=defaultwsdl, location=None, sslverify=True, **kwargs):
        return XMLASource(url, location, sslverify, **kwargs)


class AsyncXMLAProvider(AsyncClass, Provider):

    async def connect(self, url=defaultwsdl, location=None, sslverify=True, **kwargs):
        async_xmla_source = await AsyncXMLASource(url, location, sslverify, **kwargs)
        return async_xmla_source


class XMLASource(XMLAConnection, XMLAClass):

    def __init__(self, urlwsdl=defaultwsdl,
                 location=None,
                 sslverify=True, **kwargs):
        self.urlwsdl = urlwsdl
        self.location = location
        self.sslverify = sslverify

        XMLAClass.__init__(self, None, {}, None, self)
        XMLAConnection.__init__(self, urlwsdl, location, sslverify, **kwargs)

    # IConnection interface
    def getOLAPSource(self):
        return self

    # IOLAPSource interface
    def getCatalogs(self):
        """Returns a list of catalogs in the Datasource."""
        return self.getCatalog(None)

    def getCatalog(self, unique_name):
        return self.getSchemaElements("CATALOG", unique_name,
                                      aslist=unique_name == None)


class AsyncXMLASource(AsyncXMLAConnection, AsyncXMLAClass):

    async def __ainit__(self, urlwsdl=defaultwsdl,
                        location=None,
                        sslverify=True, **kwargs):
        self.urlwsdl = urlwsdl
        self.location = location
        self.sslverify = sslverify

        await AsyncXMLAClass.__ainit__(self, None, {}, None, self)
        await AsyncXMLAConnection.__ainit__(self, urlwsdl, location, sslverify, **kwargs)

    async def getOLAPSource(self):
        return self

    async def getCatalogs(self):
        """Returns a list of catalogs in the Datasource."""
        return await self.getCatalog()

    async def getCatalog(self, unique_name=None):
        return await self.getSchemaElements("CATALOG", unique_name,
                                            aslist=unique_name == None)


async def provider():
    await AsyncXMLAConnection().setupMembers()

    p = await AsyncXMLAProvider()
    c = await p.connect(location="http://localhost:25880/pentaho/Xmla?userid=Admin&password=root")
    ds = await c.getOLAPSource()
    cs = await ds.getCatalog("AisKPI")
    cus = await cs.getCube("GosPay")
    print(cus.query())


asyncio.get_event_loop().run_until_complete(provider())
