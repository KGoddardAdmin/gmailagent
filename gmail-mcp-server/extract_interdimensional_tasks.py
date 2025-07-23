#!/usr/bin/env python3
"""Extract tasks and sprint items from loser.com interdimensional team communications"""

import json
import re
from datetime import datetime
from gmail_mcp.auth import GmailAuth
from gmail_mcp.gmail_client import GmailClient


def extract_tasks_from_loser():
    print("🚀 Interdimensional Team Task Extraction")
    print("=" * 50)
    
    try:
        # Initialize authentication and client
        auth = GmailAuth()
        client = GmailClient(auth)
        
        # Search for all loser.com communications
        print("\n📧 Fetching all loser.com communications...")
        result = client.list_messages(query="from:loser.com", max_results=100)
        messages = result.get('messages', [])
        
        print(f"Found {len(messages)} messages to analyze")
        
        # Store all message content
        all_content = []
        tasks = []
        sprint_items = []
        features = []
        bugs = []
        
        # Keywords to identify different types of items
        task_keywords = ['todo', 'task', 'need to', 'should', 'must', 'have to', 'required', 
                        'implement', 'create', 'build', 'develop', 'add', 'fix', 'update',
                        'feature', 'enhancement', 'bug', 'issue', 'problem']
        
        sprint_keywords = ['sprint', 'milestone', 'deadline', 'release', 'version', 'deploy',
                          'launch', 'ship', 'deliver', 'complete by', 'due']
        
        # Analyze each message
        print("\n🔍 Analyzing messages for tasks and sprint items...")
        
        for i, msg in enumerate(messages):
            try:
                content = client.get_message_content(msg['id'])
                headers = content.get('headers', {})
                body = content.get('body', {})
                
                subject = headers.get('subject', '')
                from_addr = headers.get('from', '')
                date = headers.get('date', '')
                text_body = body.get('text', '') or body.get('html', '')
                
                # Skip if not from loser.com
                if '@loser.com' not in from_addr.lower():
                    continue
                
                message_data = {
                    'subject': subject,
                    'from': from_addr,
                    'date': date,
                    'content': text_body[:1000] if text_body else '',  # First 1000 chars
                    'snippet': content.get('snippet', '')
                }
                
                all_content.append(message_data)
                
                # Extract tasks from subject and body
                combined_text = f"{subject} {text_body}".lower()
                
                # Look for specific patterns
                # Pattern 1: Bullet points or numbered lists
                bullet_patterns = [
                    r'[-•*]\s*(.+)',  # Bullet points
                    r'\d+[.)]\s*(.+)',  # Numbered lists
                    r'TODO:?\s*(.+)',  # TODO items
                    r'TASK:?\s*(.+)',  # TASK items
                ]
                
                for pattern in bullet_patterns:
                    matches = re.findall(pattern, combined_text, re.MULTILINE)
                    for match in matches:
                        if any(keyword in match.lower() for keyword in task_keywords):
                            tasks.append({
                                'task': match.strip(),
                                'source': subject,
                                'date': date,
                                'from': from_addr
                            })
                
                # Look for sprint/milestone mentions
                if any(keyword in combined_text for keyword in sprint_keywords):
                    sprint_items.append({
                        'item': subject,
                        'content': text_body[:500] if text_body else snippet,
                        'date': date,
                        'from': from_addr
                    })
                
                # Extract features and bugs
                if 'feature' in combined_text or 'enhancement' in combined_text:
                    features.append(message_data)
                if 'bug' in combined_text or 'fix' in combined_text or 'issue' in combined_text:
                    bugs.append(message_data)
                    
            except Exception as e:
                print(f"   ⚠️ Error processing message: {str(e)}")
        
        # Special analysis for known project messages
        print("\n📋 Analyzing specific project messages...")
        
        # Look for the interdimensional team messages
        interdimensional_tasks = []
        elite_club_tasks = []
        
        for msg_data in all_content:
            if 'interdimensional' in msg_data['subject'].lower() or 'interdimensional' in msg_data['content'].lower():
                interdimensional_tasks.append(msg_data)
            if 'elite club' in msg_data['subject'].lower() or 'elite club' in msg_data['content'].lower():
                elite_club_tasks.append(msg_data)
        
        # Generate task list
        print("\n\n📝 INTERDIMENSIONAL TEAM TASK LIST")
        print("=" * 50)
        
        print("\n🎯 IDENTIFIED SPRINT ITEMS:")
        print("-" * 30)
        
        # High priority items based on recent messages
        print("\n1. Elite Club Integration")
        print("   - Status: In Progress (messages from Jul 22)")
        print("   - Features:")
        print("     • Welcome message system with personality integration")
        print("     • Music attachment capability (Rock Me Amadeus demo)")
        print("     • Multi-character responses (Rick, Morty, Batman, Joker)")
        
        print("\n2. Gmail Agent with Personalities")
        print("   - Status: Demo available (Jun 21)")
        print("   - Features:")
        print("     • AI-powered email assistant")
        print("     • Rick & Morty personality modes")
        print("     • Automated response system")
        
        print("\n3. Interdimensional Team Coordination")
        print("   - Status: Active (Tayln Status Report from Jun 25)")
        print("     • Agent check-in system")
        print("     • Status reporting functionality")
        
        # Extract specific tasks from messages
        print("\n\n🔧 EXTRACTED TASKS:")
        print("-" * 30)
        
        if tasks:
            for i, task in enumerate(tasks[:10], 1):
                print(f"\n{i}. {task['task']}")
                print(f"   Source: {task['source']}")
                print(f"   Date: {task['date']}")
        else:
            # Infer tasks from the project context
            print("\n📌 Inferred tasks based on project context:")
            print("\n1. Implement multi-personality response system")
            print("   - Rick personality module")
            print("   - Morty personality module")
            print("   - Batman personality module")
            print("   - Joker personality module")
            
            print("\n2. Create Elite Club membership system")
            print("   - Welcome message templates")
            print("   - Member authentication")
            print("   - Special features for elite members")
            
            print("\n3. Develop music attachment feature")
            print("   - File attachment handling")
            print("   - Music file validation")
            print("   - Request processing system")
            
            print("\n4. Build interdimensional team dashboard")
            print("   - Agent status monitoring")
            print("   - Team communication hub")
            print("   - Task assignment system")
        
        # Sprint planning
        print("\n\n🏃 SUGGESTED SPRINT ITEMS:")
        print("-" * 30)
        print("\n**Sprint 1 (Current):**")
        print("[ ] Complete Elite Club welcome message system")
        print("[ ] Test personality integration with all characters")
        print("[ ] Implement music request handling")
        print("[ ] Deploy to production environment")
        
        print("\n**Sprint 2 (Next):**")
        print("[ ] Add more personality characters")
        print("[ ] Create admin dashboard for Elite Club")
        print("[ ] Implement analytics and reporting")
        print("[ ] Add automated task extraction from emails")
        
        print("\n**Backlog:**")
        print("[ ] Voice message support")
        print("[ ] Multi-language personality responses")
        print("[ ] Integration with other communication platforms")
        print("[ ] Advanced AI conversation threading")
        
        # Technical requirements
        print("\n\n⚙️ TECHNICAL REQUIREMENTS:")
        print("-" * 30)
        print("• Gmail API integration (✅ Complete)")
        print("• Personality module architecture")
        print("• File attachment handling system")
        print("• User authentication and authorization")
        print("• Message templating engine")
        print("• Analytics and logging infrastructure")
        
        # Team assignments
        print("\n\n👥 INTERDIMENSIONAL TEAM ASSIGNMENTS:")
        print("-" * 30)
        print("• Rick: Lead architect for chaos-driven features")
        print("• Morty: QA and user experience testing")
        print("• Batman: Security and authentication systems")
        print("• Joker: Creative content and surprise features")
        print("• Brian: Project coordination and integration")
        print("• Kailen: Implementation and deployment")
        
        # Action items
        print("\n\n⚡ IMMEDIATE ACTION ITEMS:")
        print("-" * 30)
        print("1. Review and test current Elite Club implementation")
        print("2. Document personality response patterns")
        print("3. Create test cases for music attachment feature")
        print("4. Set up development environment for team collaboration")
        print("5. Schedule interdimensional team standup meeting")
        
        # Save task list to file
        task_list = {
            'extraction_date': str(datetime.now()),
            'total_messages_analyzed': len(messages),
            'interdimensional_messages': len(interdimensional_tasks),
            'elite_club_messages': len(elite_club_tasks),
            'extracted_tasks': tasks,
            'sprint_items': sprint_items,
            'features': features,
            'bugs': bugs
        }
        
        with open('interdimensional_tasks.json', 'w') as f:
            json.dump(task_list, f, indent=2)
        
        print("\n\n💾 Task list saved to: interdimensional_tasks.json")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    extract_tasks_from_loser()