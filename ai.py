from groq import Groq
import os, json
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an AI assistant that helps users manage their Gmail and Google Calendar.

Respond ONLY with a JSON object:
{
  "action": "action_name",
  "params": {}
}

Available actions:
- "get_unread_emails" → params: {"max_results": 5}
- "search_emails" → params: {"query": "search term", "max_results": 5}
- "send_email" → params: {"to": "email@example.com", "subject": "Subject", "body": "Email body"}
- "get_todays_events" → params: {}
- "get_upcoming_events" → params: {"days": 7}
- "create_event" → params: {"title": "Event name", "date_str": "YYYY-MM-DD", "time_str": "HH:MM", "duration_hours": 1, "description": ""}
- "delete_event" → params: {"event_title": "Event name"}
- "chat" → params: {"reply": "your conversational response"}
"""

def understand_command(user_message: str, today_date: str) -> dict:
    prompt = f"Today's date is {today_date}.\n\nUser message: {user_message}"
    try:
        response = client.chat.completions.create(
           model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.1,
        )
        text = response.choices[0].message.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as e:
        return {
            "action": "chat",
            "params": {"reply": f"Sorry, I had trouble with that. (Error: {str(e)})"}
        }