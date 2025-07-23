#!/usr/bin/env python3
"""Find communications with brian@loser.com"""

import json
from datetime import datetime
from gmail_mcp.auth import GmailAuth
from gmail_mcp.gmail_client import GmailClient


def find_brian_emails():
    print("🔍 Searching for communications with brian@loser.com...")
    print("=" * 50)
    
    try:
        # Initialize authentication and client
        auth = GmailAuth()
        client = GmailClient(auth)
        
        print("\n📧 Fetching recent messages to search...")
        
        # Get recent messages including sent items
        all_messages = []
        page_token = None
        pages_to_check = 5  # Check 5 pages (500 messages)
        
        # First check regular messages
        for page in range(pages_to_check):
            print(f"Checking inbox page {page + 1}...")
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
        
        # Also check sent messages
        print("\nChecking sent messages...")
        sent_result = client.list_messages(
            label_ids=['SENT'],
            max_results=100
        )
        sent_messages = sent_result.get('messages', [])
        if sent_messages:
            all_messages.extend(sent_messages)
            print(f"Added {len(sent_messages)} sent messages to search")
        
        print(f"\n🔍 Checking {len(all_messages)} total messages for brian@loser.com...")
        
        brian_messages = []
        from_brian = []
        to_brian = []
        
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
                
                # Check if brian@loser.com is involved
                if 'brian@loser.com' in from_addr:
                    from_brian.append((msg['id'], message_data))
                    brian_messages.append((msg['id'], message_data, 'FROM'))
                elif 'brian@loser.com' in to_addr or 'brian@loser.com' in cc_addr:
                    to_brian.append((msg['id'], message_data))
                    brian_messages.append((msg['id'], message_data, 'TO'))
                    
            except Exception as e:
                # Skip messages that can't be read
                pass
        
        print(f"\n✅ Search complete!")
        
        # Display results
        print(f"\n📊 Results Summary:")
        print("=" * 50)
        print(f"Total messages with brian@loser.com: {len(brian_messages)}")
        print(f"  - FROM brian@loser.com: {len(from_brian)}")
        print(f"  - TO brian@loser.com: {len(to_brian)}")
        
        if brian_messages:
            print(f"\n📧 Message Details:")
            print("-" * 50)
            
            # Sort by date (most recent first)
            for msg_id, msg_data, direction in brian_messages[:20]:  # Show up to 20
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
                
                # Check if this is the thank you email we sent
                if "thank you" in subject.lower() and direction == "TO":
                    print(f"  📌 This appears to be the thank you email sent via MCP!")
            
            if len(brian_messages) > 20:
                print(f"\n... and {len(brian_messages) - 20} more messages")
                
            # Get thread information
            thread_ids = set()
            for msg_id, msg_data, _ in brian_messages:
                thread_id = msg_data.get('threadId')
                if thread_id:
                    thread_ids.add(thread_id)
            
            print(f"\n📑 Conversation threads: {len(thread_ids)}")
            
            # Check if we got a reply to our thank you email
            print(f"\n🔍 Checking for replies to your thank you email...")
            thank_you_thread = None
            for msg_id, msg_data, direction in brian_messages:
                if "thank you" in msg_data.get('headers', {}).get('subject', '').lower() and direction == "TO":
                    thank_you_thread = msg_data.get('threadId')
                    break
            
            if thank_you_thread:
                replies = [m for m in brian_messages if m[1].get('threadId') == thank_you_thread and m[2] == "FROM"]
                if replies:
                    print(f"✅ Found {len(replies)} reply/replies to your thank you email!")
                else:
                    print("⏳ No reply yet to your thank you email")
            
        else:
            print("\n❌ No communications found with brian@loser.com")
            print("   Note: This is unexpected since we sent a thank you email earlier!")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    find_brian_emails()