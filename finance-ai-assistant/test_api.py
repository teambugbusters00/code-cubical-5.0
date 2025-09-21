#!/usr/bin/env python3
"""
Simple test script to verify the Finance AI Assistant API is working
"""

import requests
import json
from datetime import datetime

def test_api():
    """Test basic API endpoints"""
    base_url = "http://localhost:8000"

    print("Testing Finance AI Assistant API")
    print("=" * 50)

    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("PASS - Health check")
            print(f"   Response: {response.json()}")
        else:
            print(f"FAIL - Health check ({response.status_code})")
    except Exception as e:
        print(f"ERROR - Health check: {e}")

    print()

    # Test 2: Root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("PASS - Root endpoint")
            print(f"   Response: {response.json()}")
        else:
            print(f"FAIL - Root endpoint ({response.status_code})")
    except Exception as e:
        print(f"ERROR - Root endpoint: {e}")

    print()

    # Test 3: Stock quote (with fallback data)
    try:
        response = requests.get(f"{base_url}/api/stocks/AAPL/quote")
        if response.status_code == 200:
            print("PASS - Stock quote (AAPL)")
            data = response.json()
            print(f"   Symbol: {data.get('symbol')}")
            print(f"   Price: ${data.get('current_price')}")
            print(f"   Source: {data.get('source', 'unknown')}")
        else:
            print(f"FAIL - Stock quote (AAPL) ({response.status_code})")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"ERROR - Stock quote (AAPL): {e}")

    print()

    # Test 4: Stock info
    try:
        response = requests.get(f"{base_url}/api/stocks/AAPL/info")
        if response.status_code == 200:
            print("PASS - Stock info (AAPL)")
            data = response.json()
            print(f"   Name: {data.get('name')}")
            print(f"   Sector: {data.get('sector')}")
        else:
            print(f"FAIL - Stock info (AAPL) ({response.status_code})")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"ERROR - Stock info (AAPL): {e}")

    print()

    # Test 5: Market indices
    try:
        response = requests.get(f"{base_url}/api/market/indices")
        if response.status_code == 200:
            print("PASS - Market indices")
            data = response.json()
            print(f"   Found {len(data)} indices")
            for symbol, info in data.items():
                print(f"   {symbol}: ${info.get('current_price')}")
        else:
            print(f"FAIL - Market indices ({response.status_code})")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"ERROR - Market indices: {e}")

    print()

    # Test 6: Test prediction endpoint
    try:
        response = requests.get(f"{base_url}/api/stocks/AAPL/predict-test?days=3")
        if response.status_code == 200:
            print("PASS - Test prediction")
            data = response.json()
            print(f"   Symbol: {data.get('symbol')}")
            print(f"   Predictions: {len(data.get('predictions', []))} days")
            print(f"   Model: {data.get('model')}")
        else:
            print(f"FAIL - Test prediction ({response.status_code})")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"ERROR - Test prediction: {e}")

    print()

    # Test 7: News endpoint
    try:
        response = requests.get(f"{base_url}/api/stocks/AAPL/news?limit=2")
        if response.status_code == 200:
            print("PASS - News endpoint")
            data = response.json()
            print(f"   Found {len(data)} news items")
            if data:
                print(f"   First news: {data[0].get('title', 'No title')[:50]}...")
        else:
            print(f"FAIL - News endpoint ({response.status_code})")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"ERROR - News endpoint: {e}")

    print()
    print("API Testing Complete!")
    print("=" * 50)

    # Summary
    print("\nSummary:")
    print("If all tests show 'PASS', your API is working correctly!")
    print("The API uses fallback data when external services are unavailable.")
    print("\nNext Steps:")
    print("1. Open http://localhost:8000/docs for interactive API documentation")
    print("2. Start the Streamlit frontend: streamlit run ui/streamlit_app.py")
    print("3. Access the web interface at http://localhost:8501")

if __name__ == "__main__":
    test_api()