"""Hardened SupportBot. Same model, five layered controls. Runs on port 8001."""
from __future__ import annotations

import os

import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from target.guardrails import (
    HARDENED_SYSTEM_PROMPT,
    encode_for_html,
    input_blocked,
    output_blocked,
)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("TARGET_MODEL", "llama3.2:3b")
REFUSAL = "I can't help with that request."


def call_model(message: str) -> str:
    if input_blocked(message):                      # CONTROL 1: input validation
        return REFUSAL
    payload = {"model": MODEL, "messages": [
        {"role": "system", "content": HARDENED_SYSTEM_PROMPT},  # CONTROL 3: no secrets in prompt
        {"role": "user", "content": message}], "stream": False}
    r = httpx.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=120)
    r.raise_for_status()
    reply = r.json()["message"]["content"]
    if output_blocked(reply):                       # CONTROL 2: output filtering
        return REFUSAL
    return reply                                    # CONTROL 5: no tool dispatch on model output


app = FastAPI(title="Secure SupportBot (hardened)")


class ChatRequest(BaseModel):
    message: str


@app.post("/api/chat")
def chat(req: ChatRequest):
    return JSONResponse({"reply": call_model(req.message)})


def render_page(reply_html: str) -> str:
    return ("<!doctype html><html><head><title>SupportBot</title></head><body>"
            "<h1>AcmeCorp SupportBot (hardened)</h1>"
            "<form method='get' action='/chat'><input name='message'><button>Send</button></form>"
            + reply_html + "</body></html>")


@app.get("/", response_class=HTMLResponse)
def index():
    return render_page("")


@app.get("/chat", response_class=HTMLResponse)
def chat_html(message: str = ""):
    reply = call_model(message) if message else ""
    reply_html = f"<div class='reply'>{encode_for_html(reply)}</div>" if message else ""  # CONTROL 4: encoding
    return render_page(reply_html)
