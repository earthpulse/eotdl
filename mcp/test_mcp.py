#!/usr/bin/env python3
"""
Direct MCP Server Testing Script

This script demonstrates how to test the MCP server directly without LangChain.
"""

import requests
import json
import sys

def test_mcp_server(base_url="http://localhost:8000"):
    """
    Test the MCP server directly
    """
    print(f"Testing MCP server at {base_url}")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        "What satellite datasets are available for land use classification?",
        "Find information about Sentinel-2 data processing",
        "What are the best datasets for monitoring deforestation?",
        "How can I access climate data for agricultural monitoring?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 30)
        
        try:
            # Call the rag_search tool
            response = requests.post(
                f"{base_url}/tools/rag_search",
                json={"query": query},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result.get('result', 'No result')[:200]}...")
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure the MCP server is running")
        except requests.exceptions.Timeout:
            print("❌ Timeout: Server took too long to respond")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_server_health(base_url="http://localhost:8000"):
    """
    Test if the server is running and healthy
    """
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is healthy")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server health check failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Check if server is running
    if not test_server_health():
        print("\nMake sure to start the MCP server first:")
        print("cd /Users/juan/Desktop/eotdl/mcp")
        print("python server.py")
        sys.exit(1)
    
    # Run tests
    test_mcp_server()
