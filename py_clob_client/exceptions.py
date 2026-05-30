# optimized_exceptions.py

from typing import Optional, Union
import json
import httpx

class PolyException(Exception):
    """Base exception class for all Poly-related errors."""
    def __init__(self, msg: str):
        # Pass the message to the base Exception class
        super().__init__(msg)
        self.msg = msg

class PolyApiException(PolyException):
    """
    Exception raised for API-related errors, capturing HTTP status and response body.
    """
    def __init__(self, 
                 resp: Optional[httpx.Response] = None, 
                 error_msg: Optional[Union[str, dict]] = None):
        
        # Validation: Ensure at least one piece of information is provided.
        if resp is None and error_msg is None:
            raise ValueError("PolyApiException requires either an httpx.Response object or an error message.")

        if resp is not None:
            self.status_code: Optional[int] = resp.status_code
            self.error_msg: Union[str, dict] = self._get_message(resp)
        else:
            self.status_code = None
            self.error_msg = error_msg
        
        # Call base class constructor with a summary message
        super().__init__(f"API Error (Status: {self.status_code}): {self.error_msg}")


    def _get_message(self, resp: httpx.Response) -> Union[str, dict]:
        """
        Attempts to parse the response body as JSON. Falls back to raw text if parsing fails.
        """
        try:
            # httpx.Response.json() attempts to decode the body and raises a ValueError on failure.
            return resp.json()
        except ValueError:
            # If JSON decoding fails, return the raw text content.
            return resp.text
        # No need for a general 'except Exception', specific error handling is better.

    def __repr__(self) -> str:
        """
        Provides a detailed, unambiguous representation of the exception.
        """
        return (f"{self.__class__.__name__}("
                f"status_code={self.status_code!r}, "
                f"error_message={self.error_msg!r})")

    # __str__ method is omitted as Python's default behavior uses __repr__ 
    # if __str__ is not defined, which is often sufficient for error messages.
