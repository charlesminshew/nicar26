"""
GA Ethics Commission API Probe
===============================
Tests the GetTransactionDetails endpoint to understand:
1. Whether fromDate/toDate filtering actually works
2. How pagination behaves (pageNumber/pageSize in response)
3. Maximum viable pageSize before timeout/rejection

Run: python ga_ethics_api_probe.py

Endpoint: https://api-recordsearch.ethics.ga.gov/api/PublicTransactionDetails/GetTransactionDetails
"""

import requests
import json
import time
import sys

API_URL = "https://api-recordsearch.ethics.ga.gov/api/PublicTransactionDetails/GetTransactionDetails"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

BASE_PAYLOAD = {
    "pageNumber": 1,
    "pageSize": 10,
    "sortBy": "Transaction Date",
    "sortType": "desc",
    "transactionTypeCode": "TCON",
    "filerName": "",
    "sourceName": "",
    "transactionAmountMax": None,
    "sourceTypeCode": "",
    "committeeType": "",
    "electionID": "",
    "reportName": "",
    "toDate": None,
    "fromDate": None,
    "byState": "",
    "electionType": "",
    "electionYear": "",
    "filerRegistrationGuid": None,
}


def make_request(label, overrides=None, timeout=30):
    """Make a request with optional payload overrides and print diagnostics."""
    payload = {**BASE_PAYLOAD, **(overrides or {})}

    print(f"\n{'='*70}")
    print(f"TEST: {label}")
    print(f"{'='*70}")
    print(f"  pageNumber: {payload['pageNumber']}")
    print(f"  pageSize:   {payload['pageSize']}")
    print(f"  fromDate:   {payload['fromDate']}")
    print(f"  toDate:     {payload['toDate']}")

    try:
        start = time.time()
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=timeout)
        elapsed = time.time() - start

        print(f"  HTTP status:  {resp.status_code}")
        print(f"  Response time: {elapsed:.2f}s")

        if resp.status_code != 200:
            print(f"  Response body (first 500 chars): {resp.text[:500]}")
            return None

        data = resp.json()

        if not data.get("succeeded"):
            print(f"  API error: {data.get('error')}")
            return None

        items = data["data"]["items"]
        total_items = data["data"]["totalItems"]
        resp_page_num = data["data"]["pageNumber"]
        resp_page_size = data["data"]["pageSize"]

        print(f"\n  RESPONSE METADATA:")
        print(f"    totalItems (from API): {total_items:,}")
        print(f"    pageNumber (from API): {resp_page_num}")
        print(f"    pageSize (from API):   {resp_page_size}")
        print(f"    items returned:        {len(items)}")

        if items:
            dates = [item["transactionDate"] for item in items]
            amounts = [item["transactionAmount"] for item in items]
            print(f"\n  DATA SNAPSHOT:")
            print(f"    Date range in results: {min(dates)} to {max(dates)}")
            print(f"    Amount range:          ${min(amounts):,.2f} to ${max(amounts):,.2f}")
            print(f"    First record date:     {items[0]['transactionDate']}")
            print(f"    Last record date:      {items[-1]['transactionDate']}")

        return {
            "total_items": total_items,
            "resp_page_num": resp_page_num,
            "resp_page_size": resp_page_size,
            "items_returned": len(items),
            "items": items,
            "elapsed": elapsed,
        }

    except requests.exceptions.Timeout:
        print(f"  TIMEOUT after {timeout}s")
        return None
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def main():
    print("GA Ethics Commission API Probe")
    print("=" * 70)

    # ---------------------------------------------------------------
    # TEST 1: Baseline — no date filter, pageSize=10
    # ---------------------------------------------------------------
    r1 = make_request(
        "Baseline (no date filter, pageSize=10)",
    )

    # ---------------------------------------------------------------
    # TEST 2: Date filter — December 2025 only, pageSize=10
    # ---------------------------------------------------------------
    r2 = make_request(
        "Date filter: Dec 2025 (pageSize=10)",
        {"fromDate": "2025-12-01", "toDate": "2025-12-31"},
    )

    # ---------------------------------------------------------------
    # TEST 3: Compare totalItems — did filtering change the count?
    # ---------------------------------------------------------------
    if r1 and r2:
        print(f"\n{'='*70}")
        print("ANALYSIS: Does date filtering work?")
        print(f"{'='*70}")
        if r2["total_items"] < r1["total_items"]:
            print(f"  YES — totalItems dropped from {r1['total_items']:,} to {r2['total_items']:,}")
            print(f"  The API appears to respect fromDate/toDate.")
        elif r2["total_items"] == r1["total_items"]:
            print(f"  UNCLEAR — totalItems is {r1['total_items']:,} in both cases.")
            print(f"  Checking if returned records are actually filtered...")
            dates_r2 = [item["transactionDate"] for item in r2["items"]]
            outside_range = [d for d in dates_r2 if d < "2025-12-01" or d > "2025-12-31"]
            if outside_range:
                print(f"  NO — found dates outside Dec 2025: {outside_range}")
                print(f"  Date params appear to be IGNORED by the API.")
            else:
                print(f"  Maybe — all returned records are within Dec 2025, but totalItems didn't change.")
                print(f"  Could be coincidence (most recent records are Dec 2025 anyway).")
        else:
            print(f"  WEIRD — totalItems went UP from {r1['total_items']:,} to {r2['total_items']:,}")

    # ---------------------------------------------------------------
    # TEST 4: Pagination — page 2 with same params
    # ---------------------------------------------------------------
    r3 = make_request(
        "Pagination: page 2 of Dec 2025 (pageSize=10)",
        {"pageNumber": 2, "fromDate": "2025-12-01", "toDate": "2025-12-31"},
    )

    if r2 and r3:
        print(f"\n{'='*70}")
        print("ANALYSIS: Does pagination work?")
        print(f"{'='*70}")
        ids_p1 = {item["transactionId"] for item in r2["items"]}
        ids_p2 = {item["transactionId"] for item in r3["items"]}
        overlap = ids_p1 & ids_p2
        if not overlap and r3["items_returned"] > 0:
            print(f"  YES — page 1 and page 2 have no overlapping transactionIds.")
        elif overlap:
            print(f"  NO — {len(overlap)} overlapping transactionIds found: {overlap}")
        else:
            print(f"  UNCLEAR — page 2 returned 0 items.")

    # ---------------------------------------------------------------
    # TEST 5: Larger pageSize (100)
    # ---------------------------------------------------------------
    r4 = make_request(
        "Larger pageSize: 100 (Dec 2025)",
        {"pageSize": 100, "fromDate": "2025-12-01", "toDate": "2025-12-31"},
    )

    # ---------------------------------------------------------------
    # TEST 6: Even larger pageSize (500)
    # ---------------------------------------------------------------
    r5 = make_request(
        "Larger pageSize: 500 (Dec 2025)",
        {"pageSize": 500, "fromDate": "2025-12-01", "toDate": "2025-12-31"},
        timeout=60,
    )

    # ---------------------------------------------------------------
    # TEST 7: Narrow date range to sanity-check filtering
    #         Use a single day (Dec 15) — if totalItems changes, filtering works
    # ---------------------------------------------------------------
    r6 = make_request(
        "Narrow date: single day Dec 15, 2025",
        {"fromDate": "2025-12-15", "toDate": "2025-12-15"},
    )

    # ---------------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------------
    print(f"\n\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    results = [
        ("Baseline (no filter)", r1),
        ("Dec 2025 filter", r2),
        ("Dec 2025 page 2", r3),
        ("Dec 2025 pageSize=100", r4),
        ("Dec 2025 pageSize=500", r5),
        ("Single day Dec 15", r6),
    ]
    print(f"  {'Test':<30} {'totalItems':>12} {'returned':>10} {'time':>8}")
    print(f"  {'-'*30} {'-'*12} {'-'*10} {'-'*8}")
    for label, r in results:
        if r:
            print(f"  {label:<30} {r['total_items']:>12,} {r['items_returned']:>10} {r['elapsed']:>7.2f}s")
        else:
            print(f"  {label:<30} {'FAILED':>12}")

    print(f"\nDone. Review the results above to determine scraping strategy.")


if __name__ == "__main__":
    main()
