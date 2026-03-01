from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
from datetime import datetime
import os, json, pathlib

load_dotenv()

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = FastAPI()
app.mount("/static", StaticFiles(directory="frontend"), name="static")

CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI  = os.getenv("GOOGLE_REDIRECT_URI")

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar",
]

CREDS_FILE = "user_credentials.json"

def get_flow():
    return Flow.from_client_config(
        client_config={
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )

def save_credentials(creds):
    with open(CREDS_FILE, "w") as f:
        json.dump({
            "token":         creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri":     creds.token_uri,
            "client_id":     creds.client_id,
            "client_secret": creds.client_secret,
            "scopes":        list(creds.scopes) if creds.scopes else SCOPES,
        }, f)

def load_credentials():
    if not pathlib.Path(CREDS_FILE).exists():
        return None
    with open(CREDS_FILE) as f:
        data = json.load(f)
    return Credentials(
        token=data["token"],
        refresh_token=data["refresh_token"],
        token_uri=data["token_uri"],
        client_id=data["client_id"],
        client_secret=data["client_secret"],
        scopes=data["scopes"],
    )

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("frontend/index.html", encoding="utf-8") as f:
        return f.read()

@app.get("/auth/login")
async def login():
    flow = get_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return RedirectResponse(auth_url)

@app.get("/auth/callback")
async def callback(request: Request):
    flow = get_flow()
    flow.fetch_token(authorization_response=str(request.url))
    save_credentials(flow.credentials)
    return RedirectResponse("/")

@app.get("/auth/status")
async def auth_status():
    creds = load_credentials()
    if creds and creds.valid:
        return JSONResponse({"logged_in": True})
    elif creds and creds.expired and creds.refresh_token:
        import google.auth.transport.requests
        creds.refresh(google.auth.transport.requests.Request())
        save_credentials(creds)
        return JSONResponse({"logged_in": True})
    return JSONResponse({"logged_in": False})

@app.get("/auth/logout")
async def logout():
    if pathlib.Path(CREDS_FILE).exists():
        os.remove(CREDS_FILE)
    return JSONResponse({"message": "Logged out"})

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_message = body.get("message", "")

    creds = load_credentials()
    if not creds:
        return JSONResponse({"reply": "Please login with Google first!"}, status_code=401)

    if creds.expired and creds.refresh_token:
        import google.auth.transport.requests
        creds.refresh(google.auth.transport.requests.Request())
        save_credentials(creds)

    from ai import understand_command
    from gmail import get_unread_emails, search_emails, send_email
    from calender import get_todays_events, get_upcoming_events, create_event, delete_event

    today = datetime.now().strftime("%Y-%m-%d")
    command = understand_command(user_message, today)

    action = command.get("action", "chat")
    params = command.get("params", {})

    try:
        if action == "get_unread_emails":
            reply = get_unread_emails(creds, **params)
        elif action == "search_emails":
            reply = search_emails(creds, **params)
        elif action == "send_email":
            reply = send_email(creds, **params)
        elif action == "get_todays_events":
            reply = get_todays_events(creds)
        elif action == "get_upcoming_events":
            reply = get_upcoming_events(creds, **params)
        elif action == "create_event":
            reply = create_event(creds, **params)
        elif action == "delete_event":
            reply = delete_event(creds, **params)
        else:
            reply = params.get("reply", "I'm not sure how to help with that!")
    except Exception as e:
        reply = f"❌ Something went wrong: {str(e)}"

    return JSONResponse({"reply": reply})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
