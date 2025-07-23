# Gmail MCP Server

A Model Context Protocol (MCP) server for Gmail that provides comprehensive email management capabilities through the Gmail API.

## Features

- **Message Management**: List, read, send, modify, trash, and delete emails
- **Draft Management**: Create, list, update, and delete drafts
- **Label Management**: Create, list, update, and delete labels
- **Thread Management**: List, get, trash, and modify email threads
- **Attachment Handling**: Download attachments from emails
- **Batch Operations**: Modify or delete multiple messages at once
- **Search**: Use Gmail's powerful search syntax to find messages
- **Profile Information**: Get Gmail account profile details

## Installation

1. Clone this repository and navigate to the `gmail-mcp-server` directory:
```bash
cd gmail-mcp-server
```

2. Install the package:
```bash
pip install -e .
```

## Setup

### 1. Google Cloud Console Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click on it and press "Enable"

### 2. OAuth2 Credentials

1. In Google Cloud Console, go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose "Desktop app" as the application type
4. Download the credentials JSON file
5. Save it to `~/.gmail-mcp/credentials.json` or set the `GMAIL_CREDENTIALS_PATH` environment variable

### 3. First Run Authentication

On first run, the server will:
1. Open a browser window for Google authentication
2. Ask you to authorize the requested Gmail permissions
3. Save the authentication token locally for future use

## Usage

### Running the Server

```bash
gmail-mcp
```

Or with Python:
```bash
python -m gmail_mcp.server
```

### Environment Variables

- `GMAIL_CREDENTIALS_PATH`: Path to your OAuth2 credentials JSON file (optional)

### Integration with Claude Desktop

Add the following to your Claude Desktop configuration file:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "gmail": {
      "command": "gmail-mcp"
    }
  }
}
```

Or if using Python directly:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "python",
      "args": ["-m", "gmail_mcp.server"]
    }
  }
}
```

## Available Tools

### Message Operations
- `gmail_list_messages` - List messages with optional search
- `gmail_get_message` - Get a specific message by ID
- `gmail_get_message_content` - Get parsed message content
- `gmail_send_message` - Send a new email
- `gmail_trash_message` - Move message to trash
- `gmail_untrash_message` - Restore from trash
- `gmail_delete_message` - Permanently delete
- `gmail_modify_message` - Modify message labels

### Draft Operations
- `gmail_create_draft` - Create a new draft
- `gmail_list_drafts` - List all drafts
- `gmail_get_draft` - Get a specific draft
- `gmail_delete_draft` - Delete a draft

### Label Operations
- `gmail_list_labels` - List all labels
- `gmail_create_label` - Create a new label
- `gmail_update_label` - Update label name
- `gmail_delete_label` - Delete a label

### Thread Operations
- `gmail_list_threads` - List email threads
- `gmail_get_thread` - Get a specific thread
- `gmail_trash_thread` - Move thread to trash
- `gmail_untrash_thread` - Restore thread from trash
- `gmail_modify_thread` - Modify thread labels

### Batch Operations
- `gmail_batch_modify_messages` - Modify multiple messages
- `gmail_batch_delete_messages` - Delete multiple messages

### Other Operations
- `gmail_get_profile` - Get account profile information
- `gmail_get_attachment` - Download message attachments

## Example Usage in Claude

```
Human: List my unread emails