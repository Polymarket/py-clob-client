import logging

from py_clob_client.headers import create_level_1_headers
from .signer import Signer
from .signing.eip712 import sign_clob_auth_message

from .endpoints import CREATE_API_KEY, TIME
from .clob_types import ApiCreds
from .exceptions import PolyException
from .http_helpers.helpers import get, post
from .constants import CREDENTIAL_CREATION_WARNING, L1_AUTH_UNAVAILABLE, L2_AUTH_UNAVAILABLE


class ClobClient:
    """
    Clob Client
    """

    def __init__(self, host, key:str = None, creds:ApiCreds = None):
        self.host = host
        self.signer = Signer(key) if key else None
        self.creds = creds
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_ok(self):
        """
        Health check: Confirms that the server is up
        """
        return get("{}/".format(self.host))
    

    def get_server_time(self):
        """
        Returns the current timestamp on the server
        """
        return get("{}{}".format(self.host, TIME))

    def create_api_key(self):
        """
        Creates a new CLOB API key for the given 
        """
        self.assert_level_1_auth()
        
        endpoint = "{}{}".format(self.host, CREATE_API_KEY)
        headers= create_level_1_headers(self.signer)
        creds = post(endpoint, headers=headers)
        self.logger.info(CREDENTIAL_CREATION_WARNING)
        return creds

    def assert_level_1_auth(self):
        """
        Level 1 Poly Auth
        """
        if self.signer is None:
            raise PolyException(L1_AUTH_UNAVAILABLE)

    def assert_level_2_auth(self):
        """
        """
        if self.creds is None:
            raise PolyException(L2_AUTH_UNAVAILABLE)



