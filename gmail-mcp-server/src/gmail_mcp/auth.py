import os
import json
from pathlib import Path
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.settings.basic',
    'https://www.googleapis.com/auth/gmail.metadata',
    'https://www.googleapis.com/auth/gmail.insert',
    'https://www.googleapis.com/auth/gmail.addons.current.action.compose',
    'https://www.googleapis.com/auth/gmail.addons.current.message.action',
    'https://www.googleapis.com/auth/gmail.addons.current.message.metadata',
    'https://www.googleapis.com/auth/gmail.addons.current.message.readonly',
]

TOKEN_PATH = Path.home() / '.gmail-mcp' / 'token.json'
CREDENTIALS_PATH = Path.home() / '.gmail-mcp' / 'credentials.json'


class GmailAuth:
    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = Path(credentials_path) if credentials_path else CREDENTIALS_PATH
        self.token_path = TOKEN_PATH
        self.creds: Optional[Credentials] = None
        
    def authenticate(self) -> Credentials:
        if self.creds and self.creds.valid:
            return self.creds
            
        self.token_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.token_path.exists():
            self.creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
            
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Credentials file not found at {self.credentials_path}. "
                        "Please download your OAuth2 credentials from Google Cloud Console."
                    )
                    
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                self.creds = flow.run_local_server(port=0)
                
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())
                
        return self.creds
        
    def get_service(self):
        creds = self.authenticate()
        return build('gmail', 'v1', credentials=creds)