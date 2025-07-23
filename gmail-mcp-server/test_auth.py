#!/usr/bin/env python3
"""Test script to initialize Gmail authentication"""

from gmail_mcp.auth import GmailAuth

def main():
    print("Initializing Gmail authentication...")
    print("A browser window should open for you to authorize access.")
    print("Please follow the prompts in your browser.")
    
    try:
        auth = GmailAuth()
        service = auth.get_service()
        
        # Test by getting profile
        profile = service.users().getProfile(userId='me').execute()
        print(f"\nAuthentication successful!")
        print(f"Authenticated as: {profile.get('emailAddress')}")
        print(f"Total messages: {profile.get('messagesTotal')}")
        print(f"Total threads: {profile.get('threadsTotal')}")
        
    except Exception as e:
        print(f"\nError during authentication: {e}")
        print("Please make sure you have the credentials file at ~/.gmail-mcp/credentials.json")

if __name__ == "__main__":
    main()