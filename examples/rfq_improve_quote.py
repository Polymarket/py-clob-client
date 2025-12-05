"""
Example: Improve an RFQ quote (Maker side)

This script demonstrates how a maker can improve their existing quote
by offering a better amount.
"""

import os

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.rfq import ImproveRfqQuoteParams, GetRfqQuotesParams
from dotenv import load_dotenv


load_dotenv()


def main():
    host = os.getenv("CLOB_API_URL", "https://clob.polymarket.com")
    key = os.getenv("PK")
    creds = ApiCreds(
        api_key=os.getenv("CLOB_API_KEY"),
        api_secret=os.getenv("CLOB_SECRET"),
        api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
    )
    chain_id = int(os.getenv("CHAIN_ID", "137"))
    client = ClobClient(host, key=key, chain_id=chain_id, creds=creds)

    quote_id = os.getenv("RFQ_QUOTE_ID")
    new_amount_out = os.getenv("RFQ_NEW_AMOUNT_OUT")

    if not quote_id:
        print("RFQ_QUOTE_ID not provided. Please set this environment variable.")
        return

    # Get the current quote to show what we're improving
    print(f"Fetching current quote: {quote_id}")
    params = GetRfqQuotesParams(quote_ids=[quote_id])
    response = client.rfq.get_rfq_quotes(params)

    if response.get("data") and len(response["data"]) > 0:
        quote = response["data"][0]
        current_amount_out = quote.get("sizeOut", quote.get("size_out", quote.get("amountOut")))
        print(f"Current amount_out: {current_amount_out}")
    else:
        print("Quote not found")
        return

    if not new_amount_out:
        # Improve by 5% (for demonstration)
        if current_amount_out:
            new_amount_out = str(int(float(current_amount_out) * 1.05))
            print(f"No RFQ_NEW_AMOUNT_OUT provided, improving by 5%")
        else:
            print("Cannot determine improvement amount. Please set RFQ_NEW_AMOUNT_OUT.")
            return

    print(f"\nImproving quote {quote_id}")
    print(f"  New amount_out: {new_amount_out}")

    improve_params = ImproveRfqQuoteParams(
        quote_id=quote_id,
        amount_out=new_amount_out,
    )

    try:
        response = client.rfq.improve_rfq_quote(improve_params)
        print(f"\nResponse: {response}")

        if response == "OK":
            print("\nQuote improved successfully!")
        else:
            print(f"\nImprove returned: {response}")
    except Exception as e:
        print(f"\nError improving quote: {e}")

    print("\nDone!")


if __name__ == "__main__":
    main()
