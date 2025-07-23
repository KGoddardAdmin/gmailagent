#!/usr/bin/env python3
"""Troubleshoot Gmail API filtering issues"""

import json
from gmail_mcp.auth import GmailAuth
from gmail_mcp.gmail_client import GmailClient
from googleapiclient.errors import HttpError


def troubleshoot_filtering():
    print("🔍 Gmail API Filter Troubleshooting")
    print("=" * 50)
    
    try:
        # Initialize authentication and client
        auth = GmailAuth()
        client = GmailClient(auth)
        
        # Check authentication scopes
        print("\n1️⃣ Checking OAuth Scopes:")
        print("-" * 30)
        if hasattr(auth.creds, 'scopes'):
            for scope in auth.creds.scopes:
                print(f"✓ {scope}")
        else:
            print("❌ Cannot read scopes from credentials")
        
        # Test basic list without query
        print("\n2️⃣ Testing basic list_messages (no query):")
        print("-" * 30)
        try:
            result = client.list_messages(max_results=1)
            print(f"✅ Success! Found {result.get('resultSizeEstimate', 0)} messages")
        except HttpError as e:
            print(f"❌ Failed: {e.reason}")
            print(f"   Details: {e.error_details}")
        
        # Test with simple query
        print("\n3️⃣ Testing with simple query (is:unread):")
        print("-" * 30)
        try:
            result = client.list_messages(query="is:unread", max_results=1)
            print(f"✅ Success! Query parameter works")
        except HttpError as e:
            print(f"❌ Failed: {e.reason}")
            if "Metadata scope does not support 'q' parameter" in str(e):
                print("\n⚠️  ISSUE IDENTIFIED: Metadata scope limitation!")
                print("   The current OAuth scope doesn't support search queries.")
                print("   This happens when using 'gmail.metadata' scope instead of full access.")
        
        # Test with email search
        print("\n4️⃣ Testing email search query:")
        print("-" * 30)
        try:
            result = client.list_messages(query="from:test@example.com", max_results=1)
            print(f"✅ Success! Email search works")
        except HttpError as e:
            print(f"❌ Failed: {e.reason}")
        
        # Check API endpoint being used
        print("\n5️⃣ Checking API configuration:")
        print("-" * 30)
        service = client.service
        print(f"API Version: {service._baseUrl}")
        print(f"Service Name: {service._serviceName}")
        
        # Test different message formats
        print("\n6️⃣ Testing message format access:")
        print("-" * 30)
        try:
            # Get a message ID first
            msgs = client.list_messages(max_results=1)
            if msgs.get('messages'):
                msg_id = msgs['messages'][0]['id']
                
                # Test MINIMAL format
                try:
                    msg = client.get_message(msg_id, format='minimal')
                    print("✅ MINIMAL format: Success")
                except HttpError as e:
                    print(f"❌ MINIMAL format: {e.reason}")
                
                # Test FULL format
                try:
                    msg = client.get_message(msg_id, format='full')
                    print("✅ FULL format: Success")
                except HttpError as e:
                    print(f"❌ FULL format: {e.reason}")
                    if "Metadata scope doesn't allow format FULL" in str(e):
                        print("   ⚠️  Limited to metadata only - cannot read message content!")
        except Exception as e:
            print(f"❌ Could not test formats: {str(e)}")
        
        # Diagnose the issue
        print("\n🔧 DIAGNOSIS:")
        print("=" * 50)
        
        # Check if we have the metadata limitation
        test_errors = []
        try:
            client.list_messages(query="test", max_results=1)
        except HttpError as e:
            test_errors.append(str(e))
        
        if any("Metadata scope" in err for err in test_errors):
            print("❌ PROBLEM: Your OAuth token has limited scopes!")
            print("\nThe current implementation seems to be using a restricted scope that:")
            print("- ❌ Cannot use search queries (q parameter)")
            print("- ❌ Cannot read full message content")
            print("- ✅ Can list messages")
            print("- ✅ Can delete messages (with proper scope)")
            print("\nSOLUTION:")
            print("1. The token might be from a different authentication session")
            print("2. The Gmail API might be in 'restricted' mode")
            print("3. Need to revoke current token and re-authenticate")
        else:
            print("✅ Query filtering should work with current authentication")
        
        # Check token details
        print("\n7️⃣ Token Information:")
        print("-" * 30)
        token_path = auth.token_path
        if token_path.exists():
            print(f"Token location: {token_path}")
            with open(token_path, 'r') as f:
                token_data = json.load(f)
            print(f"Token type: {token_data.get('token_type', 'Unknown')}")
            if 'scopes' in token_data:
                print("Token scopes:")
                for scope in token_data.get('scopes', []):
                    print(f"  - {scope}")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    troubleshoot_filtering()