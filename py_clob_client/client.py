import logging

from py_clob_client.headers import create_level_1_headers, create_level_2_headers
from .signer import Signer
from .signing.eip712 import sign_clob_auth_message

from .endpoints import CREATE_API_KEY, GET_API_KEYS, TIME
from .clob_types import ApiCreds, RequestArgs
from .exceptions import PolyException
from .http_helpers.helpers import get, post
from .constants import CREDENTIAL_CREATION_WARNING, L1_AUTH_UNAVAILABLE, L2_AUTH_UNAVAILABLE


class ClobClient:
    """
    Clob Client
    """

    def __init__(self, host, key:str = None, creds:ApiCreds = None, from_address=None):
        self.host = host
        self.signer = Signer(key) if key else None
        self.creds = creds
        self.logger = logging.getLogger(self.__class__.__name__)
        self.from_address = from_address
    
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

    def get_api_keys(self):
        """
        Gets the available API keys for this address
        Level 2 Auth required
        """
        self.assert_level_2_auth()
        
        request_args = RequestArgs(method="GET", request_path=GET_API_KEYS)
        headers = create_level_2_headers(self.signer, self.creds, request_args)
        return get("{}{}".format(self.host, GET_API_KEYS), headers=headers)


    def assert_level_1_auth(self):
        """
        Level 1 Poly Auth
        """
        if self.signer is None:
            raise PolyException(L1_AUTH_UNAVAILABLE)


    def assert_level_2_auth(self):
        """
        Level 2 Poly Auth
        """
        if self.signer is None or self.creds is None:
            raise PolyException(L2_AUTH_UNAVAILABLE)



