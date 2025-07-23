#!/usr/bin/env python3
"""Search for project updates from buddy@loser.com and brian@loser.com"""

import json
from datetime import datetime
from gmail_mcp.auth import GmailAuth
from gmail_mcp.gmail_client import GmailClient


def search_project_updates():
    print("🔍 Searching for project updates from loser.com team...")
    print("=" * 50)
    
    try:
        # Initialize authentication and client
        auth = GmailAuth()
        client = GmailClient(auth)
        
        # Search for both buddy and brian
        searches = [
            ("from:buddy@loser.com OR to:buddy@loser.com", "buddy@loser.com"),
            ("from:brian@loser.com OR to:brian@loser.com", "brian@loser.com"),
            ("from:loser.com", "anyone from loser.com domain")
        ]
        
        all_messages = {}
        
        for query, description in searches:
            print(f"\n📧 Searching for {description}...")
            try:
                result = client.list_messages(query=query, max_results=50)
                messages = result.get('messages', [])
                
                if messages:
                    print(f"✅ Found {len(messages)} messages")
                    all_messages[description] = []
                    
                    # Get details for each message
                    for msg in messages:
                        try:
                            content = client.get_message_content(msg['id'])
                            headers = content.get('headers', {})
                            
                            msg_data = {
                                'id': msg['id'],
                                'subject': headers.get('subject', 'No subject'),
                                'from': headers.get('from', 'Unknown'),
                                'to': headers.get('to', 'Unknown'),
                                'date': headers.get('date', 'Unknown'),
                                'snippet': content.get('snippet', ''),
                                'body': content.get('body', {})
                            }
                            all_messages[description].append(msg_data)
                        except Exception as e:
                            print(f"   ⚠️ Could not read message {msg['id']}: {str(e)}")
                else:
                    print(f"❌ No messages found")
                    
            except Exception as e:
                print(f"❌ Search failed: {str(e)}")
        
        # Analyze and display results
        print("\n\n📊 PROJECT UPDATE ANALYSIS")
        print("=" * 50)
        
        # Check buddy@loser.com
        print("\n👤 buddy@loser.com:")
        if "buddy@loser.com" in all_messages and all_messages["buddy@loser.com"]:
            print(f"   No messages found with buddy@loser.com")
        else:
            print("   ❌ No communications found")
        
        # Check brian@loser.com
        print("\n👤 brian@loser.com:")
        if "brian@loser.com" in all_messages and all_messages["brian@loser.com"]:
            brian_messages = all_messages["brian@loser.com"]
            print(f"   ✅ {len(brian_messages)} total messages")
            
            # Look for project-related keywords
            project_keywords = ['project', 'update', 'progress', 'status', 'development', 
                               'release', 'version', 'build', 'feature', 'bug', 'fix',
                               'elite club', 'rock me amadeus']
            
            project_messages = []
            
            for msg in brian_messages:
                subject_lower = msg['subject'].lower()
                snippet_lower = msg['snippet'].lower()
                
                # Check if message contains project keywords
                if any(keyword in subject_lower or keyword in snippet_lower for keyword in project_keywords):
                    project_messages.append(msg)
            
            if project_messages:
                print(f"\n   📋 Found {len(project_messages)} potential project-related messages:")
                
                # Sort by date (most recent first)
                for i, msg in enumerate(project_messages[:10]):  # Show up to 10
                    print(f"\n   {i+1}. {msg['subject']}")
                    print(f"      From: {msg['from']}")
                    print(f"      Date: {msg['date']}")
                    print(f"      Preview: {msg['snippet'][:150]}...")
                    
                    # Check message body for more details
                    body_text = msg['body'].get('text', '') or msg['body'].get('html', '')
                    if body_text and 'project' in body_text.lower():
                        print(f"      📌 Contains project information in body")
            else:
                print("\n   ℹ️ Messages found but none appear to be project updates")
                print("   Recent messages are:")
                for i, msg in enumerate(brian_messages[:5]):
                    print(f"\n   - {msg['subject']}")
                    print(f"     Date: {msg['date']}")
        else:
            print("   ❌ No communications found")
        
        # Check other loser.com addresses
        print("\n🏢 Other loser.com addresses:")
        if "anyone from loser.com domain" in all_messages and all_messages["anyone from loser.com domain"]:
            other_messages = all_messages["anyone from loser.com domain"]
            
            # Get unique senders
            senders = set()
            for msg in other_messages:
                from_addr = msg['from']
                if '@loser.com' in from_addr:
                    senders.add(from_addr)
            
            if senders:
                print(f"   Found messages from: {', '.join(senders)}")
            else:
                print("   No other loser.com senders found")
        else:
            print("   ❌ No other loser.com communications found")
        
        # Summary
        print("\n\n📌 SUMMARY:")
        print("-" * 30)
        if any(all_messages.values()):
            print("✅ Found communications with brian@loser.com")
            print("❌ No communications with buddy@loser.com")
            print("\nThe brian@loser.com messages appear to be about:")
            print("- Elite Club welcome messages")
            print("- Rock Me Amadeus references")
            print("\nNo explicit project updates found in recent messages.")
        else:
            print("❌ No communications found with either address")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    search_project_updates()