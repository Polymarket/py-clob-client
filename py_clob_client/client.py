import logging

from .headers import create_level_1_headers, create_level_2_headers
from .signer import Signer

from .endpoints import CREATE_API_KEY, GET_API_KEYS, TIME
from .clob_types import ApiCreds, RequestArgs
from .exceptions import PolyException
from .http_helpers.helpers import get, post
from .constants import CREDENTIAL_CREATION_WARNING, L0, L1, L1_AUTH_UNAVAILABLE, L2, L2_AUTH_UNAVAILABLE


class ClobClient:
    """
    Clob Client
    """

    def __init__(self, host, chain_id: int = None, key:str = None, creds:ApiCreds = None):
        """
        Initializes the clob client
        The client can be started in 3 modes:
        1) Level 0: Requires only the clob host url
                    Allows access to open CLOB endpoints
        
        2) Level 1: Requires the host, chain_id and a private key.
                    Allows access to L1 authenticated endpoints + all unauthenticated endpoints

        3) Level 2: Requires the host, chain_id, a private key, and Credentials.
                    Allows access to all endpoints
        """
        self.host = host
        self.signer = Signer(key, chain_id) if key else None
        self.creds = creds
        self.mode = self._get_client_mode()
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def get_ok(self):
        """
        Health check: Confirms that the server is up
        Does not need authentication
        """
        return get("{}/".format(self.host))
    

    def get_server_time(self):
        """
        Returns the current timestamp on the server
        Does not need authentication
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

    def create_limit_order(self):
        """
        Creates and signs a limit order
        Level 2 Auth required
        """
        self.assert_level_2_auth()

        pass


    def assert_level_1_auth(self):
        """
        Level 1 Poly Auth
        """
        if self.mode < L1:
            raise PolyException(L1_AUTH_UNAVAILABLE)


    def assert_level_2_auth(self):
        """
        Level 2 Poly Auth
        """
        if self.mode < L2:
            raise PolyException(L2_AUTH_UNAVAILABLE)

    def _get_client_mode(self):
        if self.signer is not None and self.creds is not None:
            return L2
        if self.signer is not None:
            return L1
        return L0
            


