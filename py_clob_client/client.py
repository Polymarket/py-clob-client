import logging
from .signer import Signer
from .signing.eip712 import sign_clob_auth_message

from .endpoints import CREATE_API_KEY, TIME
from .clob_types import ApiCreds
from .exceptions import PolyException
from .http_helpers.helpers import get, post
from .constants import L1_AUTH_UNAVAILABLE, L2_AUTH_UNAVAILABLE


class ClobClient:
    """
    Clob Client
    """

    def __init__(self, host, key:str = None, creds:ApiCreds = None):
        self.host = host
        self.signer = Signer(key)
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
        self.level_1_auth()
        
        endpoint = "{}{}".format(self.host, CREATE_API_KEY)
        sign_clob_auth_message(self.signer)
        # headers = create_level_1_headers()
        # return post(endpoint, headers=headers)

    def assert_level_1_auth(self):
        """
        Level 1 Poly Auth
        """
        if self.key is None:
            raise PolyException(L1_AUTH_UNAVAILABLE)

    def assert_level_2_auth(self):
        """
        """
        if self.creds is None:
            raise PolyException(L2_AUTH_UNAVAILABLE)



