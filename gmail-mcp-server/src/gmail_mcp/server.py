import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import BaseModel, Field

from .auth import GmailAuth
from .gmail_client import GmailClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GmailServer:
    def __init__(self):
        self.server = Server("gmail-mcp-server")
        self.auth = None
        self.client = None
        self._setup_handlers()
        
    def _setup_handlers(self):
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="gmail_list_messages",
                    description="List Gmail messages with optional search query",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Gmail search query (e.g., 'is:unread', 'from:example@gmail.com')"},
                            "max_results": {"type": "integer", "description": "Maximum number of messages to return", "default": 10},
                            "page_token": {"type": "string", "description": "Token for pagination"},
                            "label_ids": {"type": "array", "items": {"type": "string"}, "description": "Filter by label IDs"},
                            "include_spam_trash": {"type": "boolean", "description": "Include spam and trash messages", "default": False}
                        }
                    }
                ),
                Tool(
                    name="gmail_get_message",
                    description="Get a specific Gmail message by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message_id": {"type": "string", "description": "The ID of the message to retrieve"},
                            "format": {"type": "string", "description": "Format of the message (full, minimal, raw)", "default": "full"}
                        },
                        "required": ["message_id"]
                    }
                ),
                Tool(
                    name="gmail_get_message_content",
                    description="Get parsed content of a Gmail message including headers, body, and attachments info",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message_id": {"type": "string", "description": "The ID of the message"}
                        },
                        "required": ["message_id"]
                    }
                ),
                Tool(
                    name="gmail_send_message",
                    description="Send a new email message",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "to": {"type": "array", "items": {"type": "string"}, "description": "Recipient email addresses"},
                            "subject": {"type": "string", "description": "Email subject"},
                            "body": {"type": "string", "description": "Email body content"},
                            "cc": {"type": "array", "items": {"type": "string"}, "description": "CC recipients"},
                            "bcc": {"type": "array", "items": {"type": "string"}, "description": "BCC recipients"},
                            "attachments": {"type": "array", "items": {"type": "string"}, "description": "File paths to attach"},
                            "html": {"type": "boolean", "description": "Whether body is HTML", "default": False}
                        },
                        "required": ["to", "subject", "body"]
                    }
                ),
                Tool(
                    name="gmail_create_draft",
                    description="Create a new email draft",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "to": {"type": "array", "items": {"type": "string"}, "description": "Recipient email addresses"},
                            "subject": {"type": "string", "description": "Email subject"},
                            "body": {"type": "string", "description": "Email body content"},
                            "cc": {"type": "array", "items": {"type": "string"}, "description": "CC recipients"},
                            "bcc": {"type": "array", "items": {"type": "string"}, "description": "BCC recipients"},
                            "attachments": {"type": "array", "items": {"type": "string"}, "description": "File paths to attach"},
                            "html": {"type": "boolean", "description": "Whether body is HTML", "default": False}
                        },
                        "required": ["to", "subject", "body"]
                    }
                ),
                Tool(
                    name="gmail_list_drafts",
                    description="List all email drafts",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "max_results": {"type": "integer", "description": "Maximum number of drafts to return", "default": 10},
                            "page_token": {"type": "string", "description": "Token for pagination"}
                        }
                    }
                ),
                Tool(
                    name="gmail_get_draft",
                    description="Get a specific draft by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "draft_id": {"type": "string", "description": "The ID of the draft"}
                        },
                        "required": ["draft_id"]
                    }
                ),
                Tool(
                    name="gmail_delete_draft",
                    description="Delete a draft",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "draft_id": {"type": "string", "description": "The ID of the draft to delete"}
                        },
                        "required": ["draft_id"]
                    }
                ),
                Tool(
                    name="gmail_trash_message",
                    description="Move a message to trash",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message_id": {"type": "string", "description": "The ID of the message to trash"}
                        },
                        "required": ["message_id"]
                    }
                ),
                Tool(
                    name="gmail_untrash_message",
                    description="Remove a message from trash",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message_id": {"type": "string", "description": "The ID of the message to untrash"}
                        },
                        "required": ["message_id"]
                    }
                ),
                Tool(
                    name="gmail_delete_message",
                    description="Permanently delete a message",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message_id": {"type": "string", "description": "The ID of the message to delete"}
                        },
                        "required": ["message_id"]
                    }
                ),
                Tool(
                    name="gmail_modify_message",
                    description="Modify message labels",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message_id": {"type": "string", "description": "The ID of the message"},
                            "add_labels": {"type": "array", "items": {"type": "string"}, "description": "Label IDs to add"},
                            "remove_labels": {"type": "array", "items": {"type": "string"}, "description": "Label IDs to remove"}
                        },
                        "required": ["message_id"]
                    }
                ),
                Tool(
                    name="gmail_list_labels",
                    description="List all labels in the Gmail account",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="gmail_create_label",
                    description="Create a new label",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Name of the label"},
                            "label_list_visibility": {"type": "string", "description": "Visibility in label list", "default": "labelShow"},
                            "message_list_visibility": {"type": "string", "description": "Visibility in message list", "default": "show"}
                        },
                        "required": ["name"]
                    }
                ),
                Tool(
                    name="gmail_delete_label",
                    description="Delete a label",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "label_id": {"type": "string", "description": "The ID of the label to delete"}
                        },
                        "required": ["label_id"]
                    }
                ),
                Tool(
                    name="gmail_update_label",
                    description="Update a label's name",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "label_id": {"type": "string", "description": "The ID of the label"},
                            "new_name": {"type": "string", "description": "New name for the label"}
                        },
                        "required": ["label_id", "new_name"]
                    }
                ),
                Tool(
                    name="gmail_get_profile",
                    description="Get Gmail account profile information",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="gmail_batch_modify_messages",
                    description="Modify labels for multiple messages at once",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message_ids": {"type": "array", "items": {"type": "string"}, "description": "List of message IDs"},
                            "add_labels": {"type": "array", "items": {"type": "string"}, "description": "Label IDs to add"},
                            "remove_labels": {"type": "array", "items": {"type": "string"}, "description": "Label IDs to remove"}
                        },
                        "required": ["message_ids"]
                    }
                ),
                Tool(
                    name="gmail_batch_delete_messages",
                    description="Permanently delete multiple messages",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message_ids": {"type": "array", "items": {"type": "string"}, "description": "List of message IDs to delete"}
                        },
                        "required": ["message_ids"]
                    }
                ),
                Tool(
                    name="gmail_list_threads",
                    description="List email threads",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Gmail search query"},
                            "max_results": {"type": "integer", "description": "Maximum number of threads", "default": 10},
                            "page_token": {"type": "string", "description": "Token for pagination"},
                            "label_ids": {"type": "array", "items": {"type": "string"}, "description": "Filter by label IDs"},
                            "include_spam_trash": {"type": "boolean", "description": "Include spam and trash", "default": False}
                        }
                    }
                ),
                Tool(
                    name="gmail_get_thread",
                    description="Get a specific email thread",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "thread_id": {"type": "string", "description": "The ID of the thread"}
                        },
                        "required": ["thread_id"]
                    }
                ),
                Tool(
                    name="gmail_trash_thread",
                    description="Move a thread to trash",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "thread_id": {"type": "string", "description": "The ID of the thread to trash"}
                        },
                        "required": ["thread_id"]
                    }
                ),
                Tool(
                    name="gmail_untrash_thread",
                    description="Remove a thread from trash",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "thread_id": {"type": "string", "description": "The ID of the thread to untrash"}
                        },
                        "required": ["thread_id"]
                    }
                ),
                Tool(
                    name="gmail_modify_thread",
                    description="Modify thread labels",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "thread_id": {"type": "string", "description": "The ID of the thread"},
                            "add_labels": {"type": "array", "items": {"type": "string"}, "description": "Label IDs to add"},
                            "remove_labels": {"type": "array", "items": {"type": "string"}, "description": "Label IDs to remove"}
                        },
                        "required": ["thread_id"]
                    }
                ),
                Tool(
                    name="gmail_get_attachment",
                    description="Download an attachment from a message",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message_id": {"type": "string", "description": "The ID of the message"},
                            "attachment_id": {"type": "string", "description": "The ID of the attachment"},
                            "save_path": {"type": "string", "description": "Path to save the attachment"}
                        },
                        "required": ["message_id", "attachment_id", "save_path"]
                    }
                )
            ]
            
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if not self.client:
                    credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH')
                    if credentials_path:
                        self.auth = GmailAuth(credentials_path)
                    else:
                        # Try default location
                        default_creds = Path.home() / '.gmail-mcp' / 'credentials.json'
                        if not default_creds.exists():
                            # Check if the user provided credentials file exists
                            provided_creds = Path('/home/kkman/Downloads/client_secret_229553542595-b6coqr6kpkhclaojftjogr4tnutma0qk.apps.googleusercontent.com.json')
                            if provided_creds.exists():
                                default_creds.parent.mkdir(parents=True, exist_ok=True)
                                import shutil
                                shutil.copy(provided_creds, default_creds)
                        self.auth = GmailAuth()
                    self.client = GmailClient(self.auth)
                
                result = None
                
                if name == "gmail_list_messages":
                    result = self.client.list_messages(**arguments)
                    
                elif name == "gmail_get_message":
                    result = self.client.get_message(**arguments)
                    
                elif name == "gmail_get_message_content":
                    result = self.client.get_message_content(**arguments)
                    
                elif name == "gmail_send_message":
                    result = self.client.send_message(**arguments)
                    
                elif name == "gmail_create_draft":
                    result = self.client.create_draft(**arguments)
                    
                elif name == "gmail_list_drafts":
                    result = self.client.list_drafts(**arguments)
                    
                elif name == "gmail_get_draft":
                    result = self.client.get_draft(**arguments)
                    
                elif name == "gmail_delete_draft":
                    self.client.delete_draft(**arguments)
                    result = {"status": "success", "message": "Draft deleted"}
                    
                elif name == "gmail_trash_message":
                    result = self.client.trash_message(**arguments)
                    
                elif name == "gmail_untrash_message":
                    result = self.client.untrash_message(**arguments)
                    
                elif name == "gmail_delete_message":
                    self.client.delete_message(**arguments)
                    result = {"status": "success", "message": "Message permanently deleted"}
                    
                elif name == "gmail_modify_message":
                    result = self.client.modify_message(**arguments)
                    
                elif name == "gmail_list_labels":
                    result = self.client.list_labels()
                    
                elif name == "gmail_create_label":
                    result = self.client.create_label(**arguments)
                    
                elif name == "gmail_delete_label":
                    self.client.delete_label(**arguments)
                    result = {"status": "success", "message": "Label deleted"}
                    
                elif name == "gmail_update_label":
                    result = self.client.update_label(**arguments)
                    
                elif name == "gmail_get_profile":
                    result = self.client.get_profile()
                    
                elif name == "gmail_batch_modify_messages":
                    self.client.batch_modify_messages(**arguments)
                    result = {"status": "success", "message": "Messages modified"}
                    
                elif name == "gmail_batch_delete_messages":
                    self.client.batch_delete_messages(**arguments)
                    result = {"status": "success", "message": "Messages deleted"}
                    
                elif name == "gmail_list_threads":
                    result = self.client.list_threads(**arguments)
                    
                elif name == "gmail_get_thread":
                    result = self.client.get_thread(**arguments)
                    
                elif name == "gmail_trash_thread":
                    result = self.client.trash_thread(**arguments)
                    
                elif name == "gmail_untrash_thread":
                    result = self.client.untrash_thread(**arguments)
                    
                elif name == "gmail_modify_thread":
                    result = self.client.modify_thread(**arguments)
                    
                elif name == "gmail_get_attachment":
                    attachment_data = self.client.get_attachment(
                        arguments['message_id'],
                        arguments['attachment_id']
                    )
                    save_path = Path(arguments['save_path'])
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(save_path, 'wb') as f:
                        f.write(attachment_data)
                    result = {"status": "success", "message": f"Attachment saved to {save_path}"}
                    
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
                    
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
            except Exception as e:
                logger.error(f"Error in tool {name}: {str(e)}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
                
    async def run(self):
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    import asyncio
    server = GmailServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()