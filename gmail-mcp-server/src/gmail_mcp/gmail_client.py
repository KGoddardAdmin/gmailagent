import base64
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional
from pathlib import Path
import mimetypes

from .auth import GmailAuth


class GmailClient:
    def __init__(self, auth: GmailAuth):
        self.auth = auth
        self.service = auth.get_service()
        
    def list_messages(
        self, 
        query: str = "", 
        max_results: int = 10,
        page_token: Optional[str] = None,
        label_ids: Optional[List[str]] = None,
        include_spam_trash: bool = False
    ) -> Dict[str, Any]:
        try:
            params = {
                'userId': 'me',
                'maxResults': max_results,
                'includeSpamTrash': include_spam_trash
            }
            
            if query:
                params['q'] = query
            if page_token:
                params['pageToken'] = page_token
            if label_ids:
                params['labelIds'] = label_ids
                
            results = self.service.users().messages().list(**params).execute()
            return results
        except Exception as e:
            raise Exception(f"Failed to list messages: {str(e)}")
            
    def get_message(self, message_id: str, format: str = 'full') -> Dict[str, Any]:
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format=format
            ).execute()
            return message
        except Exception as e:
            raise Exception(f"Failed to get message {message_id}: {str(e)}")
            
    def get_message_content(self, message_id: str) -> Dict[str, Any]:
        message = self.get_message(message_id)
        result = {
            'id': message['id'],
            'threadId': message.get('threadId'),
            'labelIds': message.get('labelIds', []),
            'snippet': message.get('snippet'),
            'headers': {},
            'body': None,
            'attachments': []
        }
        
        # Extract headers
        if 'payload' in message and 'headers' in message['payload']:
            for header in message['payload']['headers']:
                name = header['name'].lower()
                if name in ['from', 'to', 'subject', 'date', 'cc', 'bcc']:
                    result['headers'][name] = header['value']
                    
        # Extract body
        result['body'] = self._extract_body(message.get('payload', {}))
        
        # Extract attachments info
        result['attachments'] = self._extract_attachments_info(message.get('payload', {}))
        
        return result
        
    def _extract_body(self, payload: Dict[str, Any]) -> Dict[str, Optional[str]]:
        body = {'text': None, 'html': None}
        
        if 'parts' in payload:
            for part in payload['parts']:
                mime_type = part.get('mimeType', '')
                if mime_type == 'text/plain' and not body['text']:
                    data = part.get('body', {}).get('data', '')
                    if data:
                        body['text'] = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                elif mime_type == 'text/html' and not body['html']:
                    data = part.get('body', {}).get('data', '')
                    if data:
                        body['html'] = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                elif 'parts' in part:
                    nested_body = self._extract_body(part)
                    if not body['text'] and nested_body['text']:
                        body['text'] = nested_body['text']
                    if not body['html'] and nested_body['html']:
                        body['html'] = nested_body['html']
        else:
            mime_type = payload.get('mimeType', '')
            data = payload.get('body', {}).get('data', '')
            if data:
                decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                if mime_type == 'text/plain':
                    body['text'] = decoded
                elif mime_type == 'text/html':
                    body['html'] = decoded
                    
        return body
        
    def _extract_attachments_info(self, payload: Dict[str, Any], attachments: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if attachments is None:
            attachments = []
            
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('filename'):
                    attachment = {
                        'filename': part['filename'],
                        'mimeType': part.get('mimeType'),
                        'size': part.get('body', {}).get('size', 0),
                        'attachmentId': part.get('body', {}).get('attachmentId')
                    }
                    attachments.append(attachment)
                elif 'parts' in part:
                    self._extract_attachments_info(part, attachments)
                    
        return attachments
        
    def get_attachment(self, message_id: str, attachment_id: str) -> bytes:
        try:
            attachment = self.service.users().messages().attachments().get(
                userId='me',
                messageId=message_id,
                id=attachment_id
            ).execute()
            
            data = attachment['data']
            return base64.urlsafe_b64decode(data)
        except Exception as e:
            raise Exception(f"Failed to get attachment: {str(e)}")
            
    def send_message(
        self,
        to: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None,
        html: bool = False
    ) -> Dict[str, Any]:
        try:
            message = MIMEMultipart() if attachments else MIMEText(body, 'html' if html else 'plain')
            
            if isinstance(message, MIMEMultipart):
                message.attach(MIMEText(body, 'html' if html else 'plain'))
            
            message['to'] = ', '.join(to)
            message['subject'] = subject
            
            if cc:
                message['cc'] = ', '.join(cc)
            if bcc:
                message['bcc'] = ', '.join(bcc)
                
            if attachments:
                for file_path in attachments:
                    path = Path(file_path)
                    if not path.exists():
                        raise FileNotFoundError(f"Attachment not found: {file_path}")
                        
                    mime_type, _ = mimetypes.guess_type(file_path)
                    if mime_type is None:
                        mime_type = 'application/octet-stream'
                        
                    main_type, sub_type = mime_type.split('/', 1)
                    
                    with open(file_path, 'rb') as f:
                        attachment = MIMEBase(main_type, sub_type)
                        attachment.set_payload(f.read())
                        
                    encoders.encode_base64(attachment)
                    attachment.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{path.name}"'
                    )
                    message.attach(attachment)
                    
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            return result
        except Exception as e:
            raise Exception(f"Failed to send message: {str(e)}")
            
    def create_draft(
        self,
        to: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None,
        html: bool = False
    ) -> Dict[str, Any]:
        try:
            message = MIMEMultipart() if attachments else MIMEText(body, 'html' if html else 'plain')
            
            if isinstance(message, MIMEMultipart):
                message.attach(MIMEText(body, 'html' if html else 'plain'))
            
            message['to'] = ', '.join(to)
            message['subject'] = subject
            
            if cc:
                message['cc'] = ', '.join(cc)
            if bcc:
                message['bcc'] = ', '.join(bcc)
                
            if attachments:
                for file_path in attachments:
                    path = Path(file_path)
                    if not path.exists():
                        raise FileNotFoundError(f"Attachment not found: {file_path}")
                        
                    mime_type, _ = mimetypes.guess_type(file_path)
                    if mime_type is None:
                        mime_type = 'application/octet-stream'
                        
                    main_type, sub_type = mime_type.split('/', 1)
                    
                    with open(file_path, 'rb') as f:
                        attachment = MIMEBase(main_type, sub_type)
                        attachment.set_payload(f.read())
                        
                    encoders.encode_base64(attachment)
                    attachment.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{path.name}"'
                    )
                    message.attach(attachment)
                    
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw_message}}
            ).execute()
            
            return draft
        except Exception as e:
            raise Exception(f"Failed to create draft: {str(e)}")
            
    def update_draft(self, draft_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        try:
            draft = self.service.users().drafts().update(
                userId='me',
                id=draft_id,
                body={'message': message}
            ).execute()
            return draft
        except Exception as e:
            raise Exception(f"Failed to update draft: {str(e)}")
            
    def delete_draft(self, draft_id: str) -> None:
        try:
            self.service.users().drafts().delete(
                userId='me',
                id=draft_id
            ).execute()
        except Exception as e:
            raise Exception(f"Failed to delete draft: {str(e)}")
            
    def list_drafts(self, max_results: int = 10, page_token: Optional[str] = None) -> Dict[str, Any]:
        try:
            params = {
                'userId': 'me',
                'maxResults': max_results
            }
            if page_token:
                params['pageToken'] = page_token
                
            results = self.service.users().drafts().list(**params).execute()
            return results
        except Exception as e:
            raise Exception(f"Failed to list drafts: {str(e)}")
            
    def get_draft(self, draft_id: str) -> Dict[str, Any]:
        try:
            draft = self.service.users().drafts().get(
                userId='me',
                id=draft_id
            ).execute()
            return draft
        except Exception as e:
            raise Exception(f"Failed to get draft: {str(e)}")
            
    def trash_message(self, message_id: str) -> Dict[str, Any]:
        try:
            result = self.service.users().messages().trash(
                userId='me',
                id=message_id
            ).execute()
            return result
        except Exception as e:
            raise Exception(f"Failed to trash message: {str(e)}")
            
    def untrash_message(self, message_id: str) -> Dict[str, Any]:
        try:
            result = self.service.users().messages().untrash(
                userId='me',
                id=message_id
            ).execute()
            return result
        except Exception as e:
            raise Exception(f"Failed to untrash message: {str(e)}")
            
    def delete_message(self, message_id: str) -> None:
        try:
            self.service.users().messages().delete(
                userId='me',
                id=message_id
            ).execute()
        except Exception as e:
            raise Exception(f"Failed to delete message: {str(e)}")
            
    def modify_message(
        self,
        message_id: str,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        try:
            body = {}
            if add_labels:
                body['addLabelIds'] = add_labels
            if remove_labels:
                body['removeLabelIds'] = remove_labels
                
            result = self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body=body
            ).execute()
            return result
        except Exception as e:
            raise Exception(f"Failed to modify message: {str(e)}")
            
    def list_labels(self) -> List[Dict[str, Any]]:
        try:
            results = self.service.users().labels().list(userId='me').execute()
            return results.get('labels', [])
        except Exception as e:
            raise Exception(f"Failed to list labels: {str(e)}")
            
    def create_label(
        self,
        name: str,
        label_list_visibility: str = 'labelShow',
        message_list_visibility: str = 'show'
    ) -> Dict[str, Any]:
        try:
            label_object = {
                'name': name,
                'labelListVisibility': label_list_visibility,
                'messageListVisibility': message_list_visibility
            }
            
            label = self.service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()
            return label
        except Exception as e:
            raise Exception(f"Failed to create label: {str(e)}")
            
    def delete_label(self, label_id: str) -> None:
        try:
            self.service.users().labels().delete(
                userId='me',
                id=label_id
            ).execute()
        except Exception as e:
            raise Exception(f"Failed to delete label: {str(e)}")
            
    def update_label(self, label_id: str, new_name: str) -> Dict[str, Any]:
        try:
            label_object = {'name': new_name}
            
            label = self.service.users().labels().update(
                userId='me',
                id=label_id,
                body=label_object
            ).execute()
            return label
        except Exception as e:
            raise Exception(f"Failed to update label: {str(e)}")
            
    def get_label(self, label_id: str) -> Dict[str, Any]:
        try:
            label = self.service.users().labels().get(
                userId='me',
                id=label_id
            ).execute()
            return label
        except Exception as e:
            raise Exception(f"Failed to get label: {str(e)}")
            
    def get_profile(self) -> Dict[str, Any]:
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return profile
        except Exception as e:
            raise Exception(f"Failed to get profile: {str(e)}")
            
    def batch_modify_messages(
        self,
        message_ids: List[str],
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None
    ) -> None:
        try:
            body = {'ids': message_ids}
            if add_labels:
                body['addLabelIds'] = add_labels
            if remove_labels:
                body['removeLabelIds'] = remove_labels
                
            self.service.users().messages().batchModify(
                userId='me',
                body=body
            ).execute()
        except Exception as e:
            raise Exception(f"Failed to batch modify messages: {str(e)}")
            
    def batch_delete_messages(self, message_ids: List[str]) -> None:
        try:
            self.service.users().messages().batchDelete(
                userId='me',
                body={'ids': message_ids}
            ).execute()
        except Exception as e:
            raise Exception(f"Failed to batch delete messages: {str(e)}")
            
    def list_threads(
        self,
        query: str = "",
        max_results: int = 10,
        page_token: Optional[str] = None,
        label_ids: Optional[List[str]] = None,
        include_spam_trash: bool = False
    ) -> Dict[str, Any]:
        try:
            params = {
                'userId': 'me',
                'maxResults': max_results,
                'includeSpamTrash': include_spam_trash
            }
            
            if query:
                params['q'] = query
            if page_token:
                params['pageToken'] = page_token
            if label_ids:
                params['labelIds'] = label_ids
                
            results = self.service.users().threads().list(**params).execute()
            return results
        except Exception as e:
            raise Exception(f"Failed to list threads: {str(e)}")
            
    def get_thread(self, thread_id: str) -> Dict[str, Any]:
        try:
            thread = self.service.users().threads().get(
                userId='me',
                id=thread_id
            ).execute()
            return thread
        except Exception as e:
            raise Exception(f"Failed to get thread: {str(e)}")
            
    def trash_thread(self, thread_id: str) -> Dict[str, Any]:
        try:
            result = self.service.users().threads().trash(
                userId='me',
                id=thread_id
            ).execute()
            return result
        except Exception as e:
            raise Exception(f"Failed to trash thread: {str(e)}")
            
    def untrash_thread(self, thread_id: str) -> Dict[str, Any]:
        try:
            result = self.service.users().threads().untrash(
                userId='me',
                id=thread_id
            ).execute()
            return result
        except Exception as e:
            raise Exception(f"Failed to untrash thread: {str(e)}")
            
    def delete_thread(self, thread_id: str) -> None:
        try:
            self.service.users().threads().delete(
                userId='me',
                id=thread_id
            ).execute()
        except Exception as e:
            raise Exception(f"Failed to delete thread: {str(e)}")
            
    def modify_thread(
        self,
        thread_id: str,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        try:
            body = {}
            if add_labels:
                body['addLabelIds'] = add_labels
            if remove_labels:
                body['removeLabelIds'] = remove_labels
                
            result = self.service.users().threads().modify(
                userId='me',
                id=thread_id,
                body=body
            ).execute()
            return result
        except Exception as e:
            raise Exception(f"Failed to modify thread: {str(e)}")