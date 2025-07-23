#!/usr/bin/env python3
"""Delete all spam emails from Gmail using the Gmail MCP client"""

import asyncio
import sys
from gmail_mcp.auth import GmailAuth
from gmail_mcp.gmail_client import GmailClient


async def delete_all_spam():
    print("🔍 Initializing Gmail client...")
    
    try:
        # Initialize authentication and client
        auth = GmailAuth()
        client = GmailClient(auth)
        
        print("📧 Fetching spam messages...")
        
        all_spam_ids = []
        page_token = None
        total_pages = 0
        
        # Fetch all spam messages using pagination
        while True:
            total_pages += 1
            print(f"📄 Fetching page {total_pages}...")
            
            # List messages with SPAM label
            result = client.list_messages(
                label_ids=['SPAM'],
                max_results=100,  # Max allowed per request
                page_token=page_token,
                include_spam_trash=True  # Must be True to see spam
            )
            
            messages = result.get('messages', [])
            if messages:
                spam_ids = [msg['id'] for msg in messages]
                all_spam_ids.extend(spam_ids)
                print(f"  Found {len(spam_ids)} spam messages on this page")
            
            # Check if there are more pages
            page_token = result.get('nextPageToken')
            if not page_token:
                break
        
        if not all_spam_ids:
            print("✅ No spam messages found! Your spam folder is already empty.")
            return
        
        print(f"\n🗑️  Total spam messages found: {len(all_spam_ids)}")
        
        # Confirm before deletion
        response = input("\n⚠️  Are you sure you want to permanently delete all spam? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Deletion cancelled.")
            return
        
        print("\n🚮 Deleting spam messages...")
        
        # Delete in batches (Gmail API supports up to 1000 per batch)
        batch_size = 50  # Conservative batch size
        total_deleted = 0
        
        for i in range(0, len(all_spam_ids), batch_size):
            batch = all_spam_ids[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(all_spam_ids) + batch_size - 1) // batch_size
            
            print(f"  Deleting batch {batch_num}/{total_batches} ({len(batch)} messages)...")
            
            try:
                client.batch_delete_messages(batch)
                total_deleted += len(batch)
                print(f"  ✓ Batch {batch_num} deleted successfully")
            except Exception as e:
                print(f"  ✗ Error deleting batch {batch_num}: {str(e)}")
                # Continue with next batch even if one fails
        
        print(f"\n✅ Successfully deleted {total_deleted} spam messages!")
        
        if total_deleted < len(all_spam_ids):
            print(f"⚠️  {len(all_spam_ids) - total_deleted} messages could not be deleted")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    print("🧹 Gmail Spam Cleaner")
    print("=" * 50)
    asyncio.run(delete_all_spam())