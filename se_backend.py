import os
import re
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

# Load key variables from .env
load_dotenv()

app = Flask(__name__)
# Enable CORS to allow local HTML files to make cross-origin API requests
CORS(app)

# Initialize OpenAI client mapped to OpenRouter
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("Missing 'OPENROUTER_API_KEY' in your .env file.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

MODEL_ID = os.getenv("OPENROUTER_MODEL", "google/gemma-2-9b-it:free")

# Hardcoded NPC Personas
NPC_PERSONAS = {
    "janet": {
        "name": "Janet",
        "age": 52,
        "role": "Finance Administrator",
        "savviness": "low",
        "base_suspicion": 15,
        "traits": (
            "Works in accounts payable. Low tech-savviness. Trusts corporate authority "
            "figures implicitly and gets flustered by claims of accounting errors. "
            "Highly responsive to urgency."
        ),
        "trigger": "direct wire transfers, financial logs, or bypassing manager approval"
    },
    "kevin": {
        "name": "Kevin",
        "age": 28,
        "role": "IT Helpdesk Specialist",
        "savviness": "medium",
        "base_suspicion": 35,
        "traits": (
            "Handles remote desktop troubleshooting. Medium tech-savviness. Tries to "
            "follow procedures but cuts corners when busy or confronted with an angry user."
        ),
        "trigger": "providing MFA tokens, temporary passwords, or installing unapproved remote tools"
    },
    "amina": {
        "name": "Dr. Amina",
        "age": 41,
        "role": "Executive Assistant to C-Suite",
        "savviness": "high",
        "base_suspicion": 65,
        "traits": (
            "Gatekeeper for executives. High tech-savviness. Very suspicious of unsolicited "
            "contact, unusual instructions, or non-standard administrative bypasses."
        ),
        "trigger": "sharing confidential files, modifying board calendars, or executing password resets"
    }
}


def clean_and_parse_json(raw_text):
    """
    Safely extracts and parses JSON payload, removing markdown wrappers if present.
    """
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned.replace("```json", "", 1)
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("```", 1)[0]
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback regex to search for the outer JSON braces if extra text was included
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError("Response text could not be parsed as valid JSON.")


@app.route('/api/chat', methods=['POST'])
def handle_chat():
    data = request.json or {}
    scenario = data.get("scenario", "Internal spearphishing assessment")
    attacker_message = data.get("attacker_message", "")
    npc_key = data.get("npc_profile", "janet").lower()
    history = data.get("conversation_history", [])  # Expects list of {"role": "attacker"|"npc", "content": "..."}

    persona = NPC_PERSONAS.get(npc_key)
    if not persona:
        return jsonify({"status": "error", "message": "Unknown NPC profile specified"}), 400

    if not attacker_message.strip():
        return jsonify({"status": "error", "message": "Attacker message cannot be empty"}), 400

    system_prompt = f"""You are {persona['name']}, a {persona['age']}-year-old {persona['role']} at NovaCorp.
Your traits: {persona['traits']}
Your overall tech savviness is {persona['savviness']}. Your baseline suspicion score is {persona['base_suspicion']}/100.

You are interacting in this active simulation scenario: "{scenario}"

INSTRUCTIONS:
1. Respond ONLY in character as {persona['name']}. Never break character, and never explain that you are an AI.
2. Formulate your response dynamically based on the attacker's message and the conversation history.
3. Review the message for common social engineering markers: urgency language, requests for credentials or sensitive data, unusual tasks, or poor social context.
4. Calculate your updated suspicion score on a scale from 0 to 100:
   - Increase suspicion significantly if the message targets your primary vulnerability trigger: {persona['trigger']}.
   - Increase suspicion moderately for suspicious indicators (requests for tokens, high pressure, external link clicks).
   - If the attacker builds trust or uses valid pretexting, suspicion can hold steady or slowly decline.
5. You must output your response in valid JSON matching the format below. Do not include any conversational text outside of the JSON block.

REQUIRED JSON OUTPUT FORMAT:
{{
  "response": "Your actual in-character dialogue goes here...",
  "suspicion_score": 45
}}"""

    # Format the message history to conform to standard OpenAI specifications
    openai_messages = [{"role": "system", "content": system_prompt}]
    
    for turn in history:
        role = "user" if turn.get("role") == "attacker" else "assistant"
        openai_messages.append({
            "role": role,
            "content": turn.get("content", "")
        })

    # Append the current message if it's not already at the end of the list
    if len(openai_messages) == 1 or openai_messages[-1]["content"] != attacker_message:
        openai_messages.append({
            "role": "user",
            "content": attacker_message
        })

    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=openai_messages,
            temperature=0.7,
            extra_headers={
                "HTTP-Referer": "http://127.0.0.1:5000",
                "X-Title": "SENTINEL Social Engineering Simulator"
            }
        )

        raw_content = response.choices[0].message.content
        parsed_data = clean_and_parse_json(raw_content)
        
        score = min(100, max(0, int(parsed_data.get("suspicion_score", persona['base_suspicion']))))

        return jsonify({
            "status": "success",
            "npc_response": parsed_data.get("response", ""),
            "suspicion_score": score
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to generate response: {str(e)}"}), 500


@app.route('/api/debrief', methods=['POST'])
def handle_debrief():
    data = request.json or {}
    history = data.get("conversation_history", [])

    if not history:
        return jsonify({"status": "error", "message": "No conversation history provided"}), 400

    transcript = ""
    for turn in history:
        sender = "Attacker" if turn.get("role") == "attacker" else "NPC Target"
        transcript += f"[{sender}]: {turn.get('content', '')}\n"

    system_prompt = """You are a senior Red Team assessment auditor and social engineering analyst.
Analyze the provided transcript of a social engineering simulation. Match the attacker's actions to standard security concepts and provide technical audit feedback.

Analyze the transcript for the following details and return your evaluation in strict JSON format:
1. Identified MITRE ATT&CK social engineering techniques (e.g., T1566 - Phishing).
2. Underlying psychological principles exploited (e.g., Urgency, Authority, Fear, Liking).
3. Specific red flags that the target should have noticed.
4. An overall 'defender_score' from 0 (complete compromise) to 100 (complete containment).
5. Three specific actionable lessons learned for employee training.

Do not write any introduction, commentary, or wrapping outside the JSON block.

REQUIRED JSON OUTPUT FORMAT:
{
  "mitre_techniques": ["TXXXX - Name", "TYYYY - Name"],
  "psychological_principles": ["Principle A", "Principle B"],
  "red_flags": ["Description of first red flag", "Description of second red flag"],
  "defender_score": 75,
  "lessons": [
    "Lesson 1...",
    "Lesson 2...",
    "Lesson 3..."
  ]
}"""

    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this interaction:\n\n{transcript}"}
            ],
            temperature=0.3,
            extra_headers={
                "HTTP-Referer": "http://127.0.0.1:5000",
                "X-Title": "SENTINEL Social Engineering Simulator"
            }
        )

        parsed_debrief = clean_and_parse_json(response.choices[0].message.content)

        return jsonify({
            "status": "success",
            "debrief": parsed_debrief
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to generate debrief: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)