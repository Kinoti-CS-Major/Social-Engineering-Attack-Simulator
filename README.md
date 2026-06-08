# Social Engineering Attack Simulator

An interactive, client-side educational simulation game designed to demonstrate the mechanics of social engineering from both offensive (Red Team) and defensive (Blue Team) perspectives. Built as a lightweight, single-file application with native HTML, CSS, and vanilla JavaScript, this tool serves as a secure conceptual environment for security awareness training.

## Features

### 1. Dual-Perspective Gameplay
* **Red Team Mode (Intruder Training):** Allows users to play as an authorized assessment trainee trying to establish access at a fictional company ("NovaCorp"). 
  * Select from 4 primary attack vectors: *Phishing Email*, *Vishing Call Script*, *Pretexting (on-site impersonation)*, or *USB Drop (physical media placement)*.
  * Navigate multi-step branching choices that test different psychological levers (urgency, authority, fear, curiosity, familiarity, and liking).
  * Interact with a dynamic target NPC whose compliance and suspicion ratings adjust based on choices made.
* **Blue Team Mode (Defensive Auditing):** Shifts the perspective to a defensive analyst inspecting incoming logs or communications.
  * Analyze realistic transcripts and email structures.
  * Interactively highlight suspect indicators ("Red Flags") embedded in the text before making the final decision to approve or block the communication.

### 2. Comprehensive Post-Scenario Debrief
* Evaluates outcomes based on target compliance and suspicion thresholds.
* Details the psychological influence principles leveraged during the scenario.
* Outlines the explicit security indicators or human-factor protocols that would allow an employee to detect the vector in a real-world setting.
* Provides baseline security industry threat intelligence and context after each session.

## Educational Value

The simulation emphasizes practical human-centric security awareness, including:
* **Mismatched Domains:** Spotting typosquatted or external email addresses masquerading as internal senders.
* **High-Pressure Tactics:** Identifying emotional manipulation techniques, such as artificial urgency, executive intimidation, or technical decoys.
* **Physical & Voice Boundaries:** Explaining physical tailgating controls, secure callback validation procedures, and the absolute restriction against sharing authentication tokens (MFA) over voice channels.

## Technical Structure

- **Languages:** HTML5, CSS3, ES6 JavaScript
- **Theme:** Terminal/Classified document dark mode aesthetic.
- **Dependencies:** Zero external dependencies or frameworks. 
- **Responsiveness:** Uses structured grids and flexbox to scale across mobile, tablet, and desktop viewports.

## How to Run

1. Clone or download this repository.
2. Launch the `.html` file directly in any modern web browser.
3. No server setup, database connection, or internet access is required to run the simulation core.
