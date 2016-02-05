import logging
logger = logging.getLogger(__name__)


from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.parse import urljoin
from xml.etree import ElementTree


class CASProvider(object):
    def __init__(self, request, next_url):
        self.request = request
        self.next_url = next_url

    def verify_cas_20(self, ticket):
        """Verifies the CAS 2.0+ XML-based authentication ticket.
        Returns the username on success and None on failure.
        """
        service = self._get_service_url()
        params = {"ticket": ticket, "service": service}
        config = self.request.registry.settings
        cas_server = config.get("pyramid_cas.cas_server")
        url = urljoin(cas_server, "serviceValidate") + "?" + urlencode(params)
        logger.debug("serviceValidate: %s", url)
        page = urlopen(url)
        try:
            response = page.read()
            logger.debug("serviceValidate response: %s", response)
            tree = ElementTree.fromstring(response)
            if tree[0].tag.endswith("authenticationSuccess"):
                return tree[0][0].text  # username
            else:
                return None
        finally:
            page.close()

    def _get_service_url(self):
        service = self.request.host_url + self.request.path
        service += ("&" if "?" in service else "?")
        service += urlencode({"next": self.next_url})
        # service = http://my.app/login?next=http://my.app/somepage
        return service

    def _get_cas_url(self, action, service):
        """
        Generates a CAS URL for a given action.
        @param string action:   "login" | "logout"
        """
        params = {"service": service}
        config = self.request.registry.settings
        cas_server = config.get("pyramid_cas.cas_server")
        url = urljoin(cas_server, action) + "?" + urlencode(params)
        return url

    def get_login_url(self):
        "Generates the CAS login URL"
        service = self._get_service_url()
        url = self._get_cas_url("login", service)
        logger.debug("login: %s", url)
        return url

    def get_logout_url(self):
        "Generates the CAS logout URL"
        # Redirect direcly to next_url after logout
        url = self._get_cas_url("logout", self.next_url)
        logger.debug("logout: %s", url)
        return url
