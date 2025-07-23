#!/usr/bin/env python3
"""Search for all communications with buddy@loser.com"""

import json
from datetime import datetime
from gmail_mcp.auth import GmailAuth
from gmail_mcp.gmail_client import GmailClient


def search_buddy_emails():
    print("🔍 Searching for communications with buddy@loser.com...")
    print("=" * 50)
    
    try:
        # Initialize authentication and client
        auth = GmailAuth()
        client = GmailClient(auth)
        
        # Search queries
        searches = [
            ("from:buddy@loser.com", "Emails FROM buddy@loser.com"),
            ("to:buddy@loser.com", "Emails TO buddy@loser.com"),
            ("from:buddy@loser.com OR to:buddy@loser.com", "All communications with buddy@loser.com")
        ]
        
        all_messages = []
        
        for query, description in searches:
            print(f"\n📧 {description}:")
            print("-" * 40)
            
            # Get all messages for this search
            messages_found = []
            page_token = None
            
            while True:
                result = client.list_messages(
                    query=query,
                    max_results=100,
                    page_token=page_token
                )
                
                messages = result.get('messages', [])
                if messages:
                    messages_found.extend(messages)
                
                page_token = result.get('nextPageToken')
                if not page_token:
                    break
            
            print(f"Found {len(messages_found)} messages")
            
            # Get details for recent messages (up to 10)
            if messages_found:
                print(f"\nRecent messages (showing up to 10):")
                for i, msg in enumerate(messages_found[:10]):
                    try:
                        # Get message content
                        message_data = client.get_message_content(msg['id'])
                        headers = message_data.get('headers', {})
                        
                        # Extract key information
                        subject = headers.get('subject', 'No subject')
                        from_addr = headers.get('from', 'Unknown')
                        to_addr = headers.get('to', 'Unknown')
                        date = headers.get('date', 'Unknown date')
                        
                        print(f"\n  {i+1}. Message ID: {msg['id']}")
                        print(f"     Date: {date}")
                        print(f"     From: {from_addr}")
                        print(f"     To: {to_addr}")
                        print(f"     Subject: {subject}")
                        
                        # Show snippet
                        snippet = message_data.get('snippet', '')
                        if snippet:
                            print(f"     Preview: {snippet[:100]}...")
                        
                    except Exception as e:
                        print(f"     Error reading message: {str(e)}")
                
                if len(messages_found) > 10:
                    print(f"\n  ... and {len(messages_found) - 10} more messages")
            
            # Store all messages for summary
            if "All communications" in description:
                all_messages = messages_found
        
        # Analyze threads
        if all_messages:
            print(f"\n\n📊 Communication Summary:")
            print("=" * 50)
            print(f"Total messages: {len(all_messages)}")
            
            # Get unique thread IDs
            thread_ids = set()
            for msg in all_messages:
                try:
                    msg_data = client.get_message(msg['id'], format='minimal')
                    thread_ids.add(msg_data.get('threadId'))
                except:
                    pass
            
            print(f"Total conversation threads: {len(thread_ids)}")
            
            # Check for recent activity
            print("\n🕐 Recent Activity:")
            recent_count = 0
            for msg in all_messages[:20]:  # Check last 20 messages
                try:
                    msg_data = client.get_message(msg['id'], format='minimal')
                    internal_date = int(msg_data.get('internalDate', 0)) / 1000
                    msg_date = datetime.fromtimestamp(internal_date)
                    days_ago = (datetime.now() - msg_date).days
                    
                    if days_ago < 30:
                        recent_count += 1
                    
                    if days_ago < 7:
                        print(f"  - Message from {days_ago} days ago")
                except:
                    pass
            
            print(f"\nMessages in last 30 days: {recent_count}")
            
        else:
            print("\n❌ No communications found with buddy@loser.com")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    search_buddy_emails()