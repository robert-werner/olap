import operator
import os
import typing

from async_class import AsyncClass
from lxml import etree
from zeep import Settings
from zeep.loader import is_relative_path, load_external_async
from zeep.wsdl.wsdl import Definition
from zeep.xsd import Schema


class AsyncDocument(AsyncClass):
    """A WSDL Document exists out of one or more definitions.

    There is always one 'root' definition which should be passed as the
    location to the Document.  This definition can import other definitions.
    These imports are non-transitive, only the definitions defined in the
    imported document are available in the parent definition.  This Document is
    mostly just a simple interface to the root definition.

    After all definitions are loaded the definitions are resolved. This
    resolves references which were not yet available during the initial
    parsing phase.


    :param location: Location of this WSDL
    :type location: string
    :param transport: The transport object to be used
    :type transport: zeep.transports.Transport
    :param base: The base location of this document
    :type base: str
    :param strict: Indicates if strict mode is enabled
    :type strict: bool

    """

    async def __ainit__(
            self, location, transport: typing.Type["AsyncTransport"], base=None, settings=None
    ):
        """Initialize a WSDL document.

        The root definition properties are exposed as entry points.

        """
        self.settings = settings or Settings()

        if isinstance(location, str):
            if is_relative_path(location):
                location = os.path.abspath(location)
            self.location = location
        else:
            self.location = base

        self.transport = transport

        # Dict with all definition objects within this WSDL
        self._definitions = (
            {}
        )  # type: typing.Dict[typing.Tuple[str, str], "Definition"]
        self.types = Schema(
            node=None,
            transport=self.transport,
            location=self.location,
            settings=self.settings,
        )
        await self.load(location)

    async def load(self, location):
        document = await self._get_xml_document(location)
        root_definitions = Definition(self, document, self.location)
        root_definitions.resolve_imports()

        # Make the wsdl definitions public
        self.messages = root_definitions.messages
        self.port_types = root_definitions.port_types
        self.bindings = root_definitions.bindings
        self.services = root_definitions.services

    def __repr__(self):
        return "<WSDL(location=%r)>" % self.location

    def dump(self):
        print("")
        print("Prefixes:")
        for prefix, namespace in self.types.prefix_map.items():
            print(" " * 4, "%s: %s" % (prefix, namespace))

        print("")
        print("Global elements:")
        for elm_obj in sorted(self.types.elements, key=lambda k: k.qname):
            value = elm_obj.signature(schema=self.types)
            print(" " * 4, value)

        print("")
        print("Global types:")
        for type_obj in sorted(self.types.types, key=lambda k: k.qname or ""):
            value = type_obj.signature(schema=self.types)
            print(" " * 4, value)

        print("")
        print("Bindings:")
        for binding_obj in sorted(self.bindings.values(), key=lambda k: str(k)):
            print(" " * 4, str(binding_obj))

        print("")
        for service in self.services.values():
            print(str(service))
            for port in service.ports.values():
                print(" " * 4, str(port))
                print(" " * 8, "Operations:")

                operations = sorted(
                    port.binding._operations.values(), key=operator.attrgetter("name")
                )

                for operation in operations:
                    print("%s%s" % (" " * 12, str(operation)))
                print("")

    async def _get_xml_document(self, location: typing.IO) -> etree._Element:
        """Load the XML content from the given location and return an
        lxml.Element object.

        :param location: The URL of the document to load
        :type location: string

        """
        return await load_external_async(
            location, self.transport, self.location, settings=self.settings
        )

    def _add_definition(self, definition: "Definition"):
        key = (definition.target_namespace, definition.location)
        self._definitions[key] = definition
