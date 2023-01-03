class ConnectionException(Exception):
    pass


class OlapException(Exception):
    def __init__(self, message, detail):
        super(OlapException, self).__init__(message)
        self.detail = detail


class XMLAException(OlapException):
    pass


class SchemaElementNotFound(Exception):
    def __init__(self, restrictions, properties):
        super(SchemaElementNotFound, self).__init__()
        self.restrictions = restrictions
        self.properties = properties
