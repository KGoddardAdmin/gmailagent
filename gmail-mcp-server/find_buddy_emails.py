#!/usr/bin/env python3
"""Find communications with buddy@loser.com by checking recent messages"""

import json
from datetime import datetime
from gmail_mcp.auth import GmailAuth
from gmail_mcp.gmail_client import GmailClient


def find_buddy_emails():
    print("🔍 Searching for communications with buddy@loser.com...")
    print("=" * 50)
    
    try:
        # Initialize authentication and client
        auth = GmailAuth()
        client = GmailClient(auth)
        
        print("\n📧 Fetching recent messages to search...")
        
        # Get recent messages
        all_messages = []
        page_token = None
        pages_to_check = 5  # Check 5 pages (500 messages)
        
        for page in range(pages_to_check):
            print(f"Checking page {page + 1}...")
            result = client.list_messages(
                max_results=100,
                page_token=page_token
            )
            
            messages = result.get('messages', [])
            if messages:
                all_messages.extend(messages)
            
            page_token = result.get('nextPageToken')
            if not page_token:
                break
        
        print(f"\n🔍 Checking {len(all_messages)} messages for buddy@loser.com...")
        
        buddy_messages = []
        from_buddy = []
        to_buddy = []
        
        # Check each message
        for i, msg in enumerate(all_messages):
            if i % 50 == 0:
                print(f"  Processed {i}/{len(all_messages)} messages...")
            
            try:
                # Get message content
                message_data = client.get_message_content(msg['id'])
                headers = message_data.get('headers', {})
                
                from_addr = headers.get('from', '').lower()
                to_addr = headers.get('to', '').lower()
                cc_addr = headers.get('cc', '').lower()
                
                # Check if buddy@loser.com is involved
                if 'buddy@loser.com' in from_addr:
                    from_buddy.append((msg['id'], message_data))
                    buddy_messages.append((msg['id'], message_data, 'FROM'))
                elif 'buddy@loser.com' in to_addr or 'buddy@loser.com' in cc_addr:
                    to_buddy.append((msg['id'], message_data))
                    buddy_messages.append((msg['id'], message_data, 'TO'))
                    
            except Exception as e:
                # Skip messages that can't be read
                pass
        
        print(f"\n✅ Search complete!")
        
        # Display results
        print(f"\n📊 Results Summary:")
        print("=" * 50)
        print(f"Total messages with buddy@loser.com: {len(buddy_messages)}")
        print(f"  - FROM buddy@loser.com: {len(from_buddy)}")
        print(f"  - TO buddy@loser.com: {len(to_buddy)}")
        
        if buddy_messages:
            print(f"\n📧 Message Details:")
            print("-" * 50)
            
            # Sort by date (most recent first)
            for msg_id, msg_data, direction in buddy_messages[:20]:  # Show up to 20
                headers = msg_data.get('headers', {})
                
                subject = headers.get('subject', 'No subject')
                from_addr = headers.get('from', 'Unknown')
                to_addr = headers.get('to', 'Unknown')
                date = headers.get('date', 'Unknown date')
                snippet = msg_data.get('snippet', '')
                
                print(f"\n[{direction}] Message ID: {msg_id}")
                print(f"  Date: {date}")
                print(f"  From: {from_addr}")
                print(f"  To: {to_addr}")
                print(f"  Subject: {subject}")
                if snippet:
                    print(f"  Preview: {snippet[:150]}...")
            
            if len(buddy_messages) > 20:
                print(f"\n... and {len(buddy_messages) - 20} more messages")
                
            # Get thread information
            thread_ids = set()
            for msg_id, msg_data, _ in buddy_messages:
                thread_id = msg_data.get('threadId')
                if thread_id:
                    thread_ids.add(thread_id)
            
            print(f"\n📑 Conversation threads: {len(thread_ids)}")
            
        else:
            print("\n❌ No communications found with buddy@loser.com in recent messages")
            print("   (Checked the most recent 500 messages)")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    find_buddy_emails()