from zeep import Plugin

from olap.xmla.connection import schema_soap_env, schema_xmla
from olap.xmla.utils import etree_tostring


class LogRequest(Plugin):
    def __init__(self, enabled=True):
        self.enabled = enabled

    def egress(self, envelope, http_headers, operation, binding_options):
        if self.enabled:
            print(etree_tostring(envelope))

    def ingress(self, envelope, http_headers, operation):
        if self.enabled:
            print(etree_tostring(envelope))

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False


class SessionPlugin(Plugin):
    def __init__(self, xmlaconn):
        self.xmlaconn = xmlaconn

    def ingress(self, envelope, http_headers, operation):
        if self.xmlaconn.getListenOnSessionId():
            nsmap = {'se': schema_soap_env,
                     'xmla': schema_xmla}
            s = envelope.xpath("/se:Envelope/se:Header/xmla:Session", namespaces=nsmap)[0]
            sid = s.attrib.get("SessionId")
            self.xmlaconn.setSessionId(sid)