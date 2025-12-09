"""
RFQ Full Flow Example

This script demonstrates the complete RFQ (Request for Quote) flow between two parties.
For a single manual test, edit the REQUEST_PARAMS and QUOTE_PARAMS at the top.

Usage: python rfq_full_flow.py

TROUBLESHOOTING "invalid request" errors:
1. Ensure the tokenID exists in your environment (staging vs production)
2. Check that the market is active and has liquidity
3. Verify your API keys have RFQ permissions enabled
4. Run `python get_markets.py` to get valid token IDs
5. Make sure you're using the correct CLOB_API_URL for your environment

If you get "invalid request" on all steps, the token ID is likely invalid for your environment.
"""

import os
import time

from dotenv import load_dotenv

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
from py_clob_client.rfq import RfqUserOrder, RfqUserQuote, AcceptQuoteParams, ApproveOrderParams
from py_clob_client.order_builder.constants import BUY
from py_clob_client.constants import AMOY

load_dotenv()

# ============================================
# RFQ REQUEST PARAMETERS (REQUESTER) - EDIT THESE
# ============================================
TOKEN_ID = "34097058504275310827233323421517291090691602969494795225921954353603704046623"

REQUEST_ORDER = RfqUserOrder(
    token_id=TOKEN_ID,
    price=0.50,       # Price per token (e.g., 0.50 = 50 cents)
    side=BUY,         # BUY or SELL
    size=100.0,       # Number of tokens
)

# ============================================
# RFQ QUOTE PARAMETERS (QUOTER) - EDIT THESE
# ============================================
QUOTE_PRICE = 0.50  # Quoted price per token

# ============================================
# EXPIRATION CONFIGURATION
# ============================================
EXPIRATION_SECONDS = 3600  # 1 hour


def main():
    # ============================================
    # Setup: Initialize both requester and quoter clients
    # ============================================
    host = os.getenv("CLOB_API_URL", "https://clob-staging.polymarket.com/")
    chain_id = os.getenv("CHAIN_ID", AMOY)

    # Requester (creates the request and accepts the quote)
    requester_key = os.getenv("REQUESTER_PK")
    requester_creds = ApiCreds(
        api_key=os.getenv("REQUESTER_API_KEY"),
        api_secret=os.getenv("REQUESTER_SECRET"),
        api_passphrase=os.getenv("REQUESTER_PASS_PHRASE"),
    )
    requester_client = ClobClient(host, key=requester_key, chain_id=chain_id, creds=requester_creds)

    # Quoter (creates the quote and approves the order)
    quoter_key = os.getenv("QUOTER_PK")
    quoter_creds = ApiCreds(
        api_key=os.getenv("QUOTER_API_KEY"),
        api_secret=os.getenv("QUOTER_SECRET"),
        api_passphrase=os.getenv("QUOTER_PASS_PHRASE"),
    )
    quoter_client = ClobClient(host, key=quoter_key, chain_id=chain_id, creds=quoter_creds)

    print("=" * 60)
    print("RFQ Full Flow")
    print("=" * 60)
    print(f"Host: {host}")
    print(f"Chain ID: {chain_id}")
    print("=" * 60)
    
    # ============================================
    # Step 1: Requester creates RFQ request
    # ============================================
    print("\n[Step 1] Requester creating RFQ request...")
    print(f"  Token ID: {REQUEST_ORDER.token_id}")
    print(f"  Side: {REQUEST_ORDER.side}")
    print(f"  Size: {REQUEST_ORDER.size}")
    print(f"  Price: {REQUEST_ORDER.price}")

    rfq_request_response = requester_client.rfq.create_rfq_request(REQUEST_ORDER)

    # Check for errors
    if rfq_request_response.get("error"):
        print(f"Failed to create request. Error: {rfq_request_response['error']}")
        raise Exception(f"Request creation failed: {rfq_request_response['error']}")

    request_id = rfq_request_response.get("requestId")
    if not request_id:
        print(f"Failed to create request. Response: {rfq_request_response}")
        raise Exception("Request creation failed - no requestId returned")

    print("Request created successfully!")
    print(f"  Request ID: {request_id}")
    print(f"  Full response: {rfq_request_response}")
    
    # ============================================
    # Step 2: Quoter creates quote for the request
    # ============================================
    print("\n[Step 2] Quoter creating quote for request...")
    print(f"  Request ID: {request_id}")
    print(f"  Price: {QUOTE_PRICE}")

    user_quote = RfqUserQuote(
        request_id=request_id,
        price=QUOTE_PRICE,
    )
    rfq_quote_response = quoter_client.rfq.create_rfq_quote(user_quote)

    # Check for errors
    if rfq_quote_response.get("error"):
        print(f"Failed to create quote. Error: {rfq_quote_response['error']}")
        raise Exception(f"Quote creation failed: {rfq_quote_response['error']}")

    quote_id = rfq_quote_response.get("quoteId")
    if not quote_id:
        print(f"Failed to create quote. Response: {rfq_quote_response}")
        raise Exception("Quote creation failed - no quoteId returned")

    print("Quote created successfully!")
    print(f"  Quote ID: {quote_id}")
    print(f"  Request ID: {request_id}")
    print(f"  Full response: {rfq_quote_response}")
    
    # ============================================
    # Step 3: Requester accepts the quote
    # ============================================
    print("\n[Step 3] Requester accepting quote...")

    expiration = int(time.time()) + EXPIRATION_SECONDS

    accept_params = AcceptQuoteParams(
        request_id=request_id,
        quote_id=quote_id,
        expiration=expiration,
    )
    accept_result = requester_client.rfq.accept_rfq_quote(accept_params)

    print(accept_result)
    print("Quote accepted successfully!")
    print(f"  Request ID: {request_id}")
    print(f"  Quote ID: {quote_id}")
    
    # ============================================
    # Step 4: Quoter approves the order
    # ============================================
    print("\n[Step 4] Quoter approving order...")

    approve_params = ApproveOrderParams(
        request_id=request_id,
        quote_id=quote_id,
        expiration=expiration,
    )
    approve_result = quoter_client.rfq.approve_rfq_order(approve_params)

    print(approve_result)
    print("Order approved successfully!")
    print(f"  Request ID: {request_id}")
    print(f"  Quote ID: {quote_id}")
    
    # ============================================
    # Summary
    # ============================================
    print("\n" + "=" * 60)
    print("RFQ FLOW COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Request ID: {request_id}")
    print(f"Quote ID:   {quote_id}")
    print("=" * 60)


main()