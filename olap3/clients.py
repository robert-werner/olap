import typing

from async_class import AsyncClass
from zeep import Client, Settings
from zeep.proxy import AsyncServiceProxy

from olap3.documents import AsyncDocument
from olap3.transports import AsyncTransport


class AsyncClient(AsyncClass, Client):
    _default_transport = AsyncTransport

    def __init__(self,
                 wsdl,
                 wsse=None,
                 transport=None,
                 service_name=None,
                 port_name=None,
                 plugins=None,
                 settings=None):
        ...

    async def __ainit__(
            self,
            wsdl,
            wsse=None,
            transport=None,
            service_name=None,
            port_name=None,
            plugins=None,
            settings=None,
    ):
        if not wsdl:
            raise ValueError("No URL given for the wsdl")

        self.settings = settings or Settings()
        self.transport = (
            transport if transport is not None else self._default_transport()
        )
        if isinstance(wsdl, AsyncDocument):
            self.wsdl = wsdl
        else:
            self.wsdl = await AsyncDocument(wsdl, self.transport, settings=self.settings)
        self.wsse = wsse
        self.plugins = plugins if plugins is not None else []

        self._default_service = None
        self._default_service_name = service_name
        self._default_port_name = port_name
        self._default_soapheaders = None

    def bind(
            self,
            service_name: typing.Optional[str] = None,
            port_name: typing.Optional[str] = None,
    ):
        """Create a new ServiceProxy for the given service_name and port_name.

        The default ServiceProxy instance (`self.service`) always referes to
        the first service/port in the wsdl Document.  Use this when a specific
        port is required.

        """
        if not self.wsdl.services:
            return

        service = self._get_service(service_name)
        port = self._get_port(service, port_name)
        return AsyncServiceProxy(self, port.binding, **port.binding_options)

    async def create_service_async(self, binding_name, address):
        """Create a new ServiceProxy for the given binding name and address.

        :param binding_name: The QName of the binding
        :param address: The address of the endpoint

        """
        try:
            binding = self.wsdl.bindings[binding_name]
        except KeyError:
            raise ValueError(
                "No binding found with the given QName. Available bindings "
                "are: %s" % (", ".join(self.wsdl.bindings.keys()))
            )
        return AsyncServiceProxy(self, binding, address=address)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type=None, exc_value=None, traceback=None) -> None:
        await self.transport.aclose()
