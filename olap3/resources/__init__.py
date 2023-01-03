from pkg_resources import ResourceManager

rm = ResourceManager()
defaultwsdl = "file://" + rm.resource_filename(__name__, "vs.wsdl")
