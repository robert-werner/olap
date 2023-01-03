import logging
import os
from urllib.parse import urlparse

import aiofiles
import httpx
from async_class import AsyncClass
from httpx import Response
from zeep.exceptions import TransportError
from zeep.utils import get_version
from zeep.wsdl.utils import etree_to_string

from olap3 import httpx_file


class AsyncTransport(AsyncClass):
    """Asynchronous Transport class using httpx.

    Note that loading the wsdl is still a sync process since and only the
    operations can be called via async.

    """

    async def __ainit__(
            self,
            client=None,
            wsdl_client=None,
            cache=None,
            timeout=300,
            operation_timeout=None,
            verify_ssl=True,
            proxy=None,
    ):

        self._close_session = False
        self.cache = cache
        self.wsdl_client = wsdl_client or httpx_file.AsyncClient(
            verify=verify_ssl,
            proxies=proxy,
            timeout=timeout,
        )
        self.client = client or httpx.AsyncClient(
            verify=verify_ssl,
            proxies=proxy,
            timeout=operation_timeout,
        )
        self.logger = logging.getLogger(__name__)

        self.wsdl_client.headers = {
            "User-Agent": "Zeep/%s (www.python-zeep.org)" % (get_version())
        }
        self.client.headers = {
            "User-Agent": "Zeep/%s (www.python-zeep.org)" % (get_version())
        }

    async def aclose(self):
        await self.client.aclose()

    async def load(self, url):
        """Load the content from the given URL"""
        if not url:
            raise ValueError("No url given to load")

        scheme = urlparse(url).scheme
        if scheme in ("http", "https", "file"):

            if self.cache:
                response = await self.cache.get(url)
                if response:
                    return bytes(response)

            content = await self._load_remote_data(url)

            if self.cache:
                self.cache.add(url, content)

            return content
        else:
            with aiofiles.open(os.path.expanduser(url), "rb") as fh:
                return fh.read()


    async def _load_remote_data(self, url):
        response = await self.wsdl_client.get(url)
        result = response.read()

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise TransportError(status_code=response.status_code)
        return result

    async def post(self, address, message, headers):
        self.logger.debug("HTTP Post to %s:\n%s", address, message)
        response = await self.client.post(
            address,
            content=message,
            headers=headers,
        )
        self.logger.debug(
            "HTTP Response from %s (status: %d):\n%s",
            address,
            response.status_code,
            response.read(),
        )
        return response

    async def post_xml(self, address, envelope, headers):
        message = etree_to_string(envelope)
        response = await self.post(address, message, headers)
        return await self.new_response(response)

    async def get(self, address, params, headers):
        response = await self.client.get(
            address,
            params=params,
            headers=headers,
        )
        return await self.new_response(response)

    async def new_response(self, response):
        """Convert an aiohttp.Response object to a requests.Response object"""
        body = response.read()
        return Response(status_code=response.status_code, headers=response.headers, content=body)
