import requests

from py_clob_client.clob_types import FilterParams

from ..exceptions import PolyApiException

GET = "GET"
POST = "POST"
DELETE = "DELETE"
PUT = "PUT"


def request(endpoint: str, method: str, headers=None, data=None):
    try:
        resp = requests.request(
            method=method, url=endpoint, headers=headers, json=data if data else None
        )
        if resp.status_code != 200:
            raise PolyApiException(resp)
        return resp.json()
    except requests.RequestException:
        raise PolyApiException(error_msg="Request exception!")


def post(endpoint, headers=None, data=None):
    return request(endpoint, POST, headers, data)


def get(endpoint, headers=None, data=None):
    return request(endpoint, GET, headers, data)


def delete(endpoint, headers=None, data=None):
    return request(endpoint, DELETE, headers, data)


def build_query_params(url: str, param: str, val: str) -> str:
    url_with_params = url
    last = url_with_params[-1]
    # if last character in url string == "?", append the param directly: api.com?param=value
    if last == "?":
        url_with_params = "{}{}={}".format(url_with_params, param, val)
    else:
        # else add "&", then append the param
        url_with_params = "{}&{}={}".format(url_with_params, param, val)
    return url_with_params


def add_query_params(base_url: str, params: FilterParams = None) -> str:
    """
    Adds query parameters to a url
    """
    url = base_url
    if params:
        url = url + "?"
        if params.market:
            url = build_query_params(url, "market", params.market)
        if params.limit:
            url = build_query_params(url, "limit", params.limit)
        if params.after:
            url = build_query_params(url, "after", params.after)
        if params.before:
            url = build_query_params(url, "before", params.before)
        if params.maker:
            url = build_query_params(url, "maker", params.maker)
        if params.taker:
            url = build_query_params(url, "taker", params.taker)
        if params.id:
            url = build_query_params(url, "id", params.id)
        if params.owner:
            url = build_query_params(url, "owner", params.owner)
    return url
