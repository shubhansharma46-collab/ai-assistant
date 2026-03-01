from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64, json
from email.mime.text import MIMEText

def get_gmail_service(creds: Credentials):
    return build("gmail", "v1", credentials=creds)

def get_unread_emails(creds: Credentials, max_results: int = 5):
    """Get unread emails from inbox"""
    service = get_gmail_service(creds)
    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX", "UNREAD"],
        maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    if not messages:
        return "No unread emails found."

    emails = []
    for msg in messages:
        detail = service.users().messages().get(
            userId="me", id=msg["id"], format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()
        headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
        emails.append({
            "from":    headers.get("From", "Unknown"),
            "subject": headers.get("Subject", "No subject"),
            "date":    headers.get("Date", ""),
            "id":      msg["id"]
        })

    output = f"📧 You have {len(emails)} unread email(s):\n\n"
    for i, e in enumerate(emails, 1):
        output += f"{i}. From: {e['from']}\n   Subject: {e['subject']}\n   Date: {e['date']}\n\n"
    return output

def search_emails(creds: Credentials, query: str, max_results: int = 5):
    """Search emails by query"""
    service = get_gmail_service(creds)
    results = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    if not messages:
        return f"No emails found for: '{query}'"

    emails = []
    for msg in messages:
        detail = service.users().messages().get(
            userId="me", id=msg["id"], format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()
        headers = {h["name"]: h["value"] for h in detail["payload"]["headers"]}
        emails.append({
            "from":    headers.get("From", "Unknown"),
            "subject": headers.get("Subject", "No subject"),
            "date":    headers.get("Date", ""),
        })

    output = f"🔍 Found {len(emails)} email(s) for '{query}':\n\n"
    for i, e in enumerate(emails, 1):
        output += f"{i}. From: {e['from']}\n   Subject: {e['subject']}\n   Date: {e['date']}\n\n"
    return output

def send_email(creds: Credentials, to: str, subject: str, body: str):
    """Send an email"""
    service = get_gmail_service(creds)
    message = MIMEText(body)
    message["to"]      = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(
        userId="me", body={"raw": raw}
    ).execute()
    return f"✅ Email sent to {to} with subject '{subject}'"

def get_email_body(creds: Credentials, message_id: str):
    """Get full body of a specific email"""
    service = get_gmail_service(creds)
    msg = service.users().messages().get(
        userId="me", id=message_id, format="full"
    ).execute()

    def extract_body(payload):
        if "parts" in payload:
            for part in payload["parts"]:
                result = extract_body(part)
                if result:
                    return result
        elif payload.get("mimeType") == "text/plain":
            data = payload.get("body", {}).get("data", "")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
        return ""

    body = extract_body(msg["payload"])
    return body[:2000] if body else "Could not extract email body."
