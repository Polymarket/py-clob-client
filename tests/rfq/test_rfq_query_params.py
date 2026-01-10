from unittest import TestCase
from urllib.parse import urlencode

from py_clob_client.rfq import GetRfqRequestsParams, GetRfqQuotesParams
from py_clob_client.rfq.rfq_helpers import (
    parse_rfq_requests_params,
    parse_rfq_quotes_params,
)


class TestRfqQueryParams(TestCase):
    def test_get_rfq_requests_request_ids_are_repeated_query_params(self):
        id1 = "019b69d4-2eb6-7ef9-8595-d149c97de10b"
        id2 = "019b69c3-d49e-7abf-88d0-cb3fd79fb721"
        params = GetRfqRequestsParams(request_ids=[id1, id2])

        parsed = parse_rfq_requests_params(params)
        qs = urlencode(parsed, doseq=True)

        self.assertEqual(qs, f"requestIds={id1}&requestIds={id2}")

    def test_get_rfq_quotes_quote_ids_are_repeated_query_params(self):
        q1 = "019b69d4-2eb6-7ef9-8595-d149c97de10b"
        q2 = "019b69c3-d49e-7abf-88d0-cb3fd79fb721"
        params = GetRfqQuotesParams(quote_ids=[q1, q2])

        parsed = parse_rfq_quotes_params(params)
        qs = urlencode(parsed, doseq=True)

        self.assertEqual(qs, f"quoteIds={q1}&quoteIds={q2}")
