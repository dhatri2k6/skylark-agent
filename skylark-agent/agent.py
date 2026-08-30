import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from monday_client import get_items_readable
from data_cleaning import normalize_rows

load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

WORK_ORDERS_BOARD_ID = os.environ["WORK_ORDERS_BOARD_ID"]
DEALS_BOARD_ID = os.environ["DEALS_BOARD_ID"]

SYSTEM_PROMPT = """You are a business intelligence assistant for Skylark Drones' founders and executives.
You have access to two data sources via tools: Work Orders (project execution/billing data) and Deals (sales pipeline data).
Always call the relevant tool(s) before answering any question involving numbers, status, or specific records.
The data is real-world messy: dates may fail to parse, fields may be missing/null, sector names may be inconsistent. Mention data quality caveats briefly when relevant.
If a question is ambiguous, ask a brief clarifying question rather than guessing.
Combine data across both boards when needed. Give context and insights, not just raw numbers."""

def get_work_orders():
    """Fetch all Work Orders board data (project execution, billing, invoicing records)."""
    return json.dumps(normalize_rows(get_items_readable(WORK_ORDERS_BOARD_ID)))

def get_deals():
    """Fetch all Deals board data (sales pipeline, deal stages, sectors, values)."""
    return json.dumps(normalize_rows(get_items_readable(DEALS_BOARD_ID)))

model = genai.GenerativeModel(
    model_name="gemini-3.6-flash",
    system_instruction=SYSTEM_PROMPT,
    tools=[get_work_orders, get_deals],
)

def chat(messages):
    """messages: list of {"role": "user"/"assistant", "content": str}"""
    history = []
    for m in messages[:-1]:
        role = "user" if m["role"] == "user" else "model"
        history.append({"role": role, "parts": [m["content"]]})

    chat_session = model.start_chat(history=history, enable_automatic_function_calling=True)
    response = chat_session.send_message(messages[-1]["content"])
    reply = response.text
    messages.append({"role": "assistant", "content": reply})
    return reply, messages