# AI-Powered Social Engineering Simulator (OpenRouter Edition)

This is an interactive, full-stack security awareness training suite designed to simulate real-world social engineering engagements. It features a retro-themed browser frontend connected to a Python Flask backend powered by free-tier LLMs via OpenRouter (e.g., `google/gemma-2-9b-it:free`).

Instead of static multiple-choice options, this version implements an **infinite free-text sandbox** where you communicate dynamically with AI targets who evaluate your messages in real-time, compute suspicion scores, and generate automated security audits.

---

## System Architecture

* **Frontend (`index.html`):** Single-file, client-side web application with a classified command console aesthetic. Implements dynamic state tracking for conversation history, custom target selectors, and a simulated human-like typing latency delay (1–2 seconds).
* **Backend (`se_backend.py`):** Lightweight Python Flask API that acts as a secure middleware connecting your frontend to OpenRouter's endpoints.
* **Large Language Model:** Utilizing `google/gemma-2-9b-it:free` (or any compatible OpenRouter model) configured with rigid system prompt guidelines to enforce target personas and enforce clean JSON outputs.

---

## Target Personas Included
1. **Janet (Finance Administrator):** Low tech-savviness. Extremely trusting of corporate authority and highly flustered by urgency or claims of critical accounting errors.
2. **Kevin (IT Helpdesk Specialist):** Medium tech-savviness. Familiar with baseline security protocols but prone to cutting corners and rushing when busy or under pressure.
3. **Dr. Amina (C-Suite Executive Assistant):** High tech-savviness. Meticulously checks credentials, extremely suspicious of unsolicited communication, and highly resilient to common pretexting.

---

## Local Installation & Setup

Because modern Linux distributions (such as Arch, Debian, and Ubuntu) enforce PEP 668, you must run this project within a Python Virtual Environment (`venv`) to avoid system-wide package conflicts.

### 1. Clone the Project & Navigate to Folder
```bash
cd Documents/SE_Simulator
