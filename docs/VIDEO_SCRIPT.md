# AutoClaims — Demo Video Script (3 minutes)

## Setup
- Open `http://localhost:3010` in fullscreen browser
- Screen recording software ready (OBS, Windows Game Bar: Win+G, or QuickTime)
- Clean browser — no other tabs open

---

## Scene 1: Dashboard Overview (0:00–0:30)

**Audio:** "Welcome to AutoClaims — an autonomous AI insurance claims processing system powered by Qwen Cloud. Here's the dashboard showing our claims pipeline in action."

**Screen:** Dashboard page at `http://localhost:3010`

- Mouse-over the hero section: "AutoClaims Intelligence" banner with badges
- Point to the 4 stat cards (Total Claims, Pending Review, Resolved, Avg Payout)
- Scroll down to the claims table — point out different statuses:
  - "submitted" (blue)
  - "resolved" (green)  
  - "pending_review" (orange)
  - "rejected" (red)
- Point to the Pie Chart (Claims by Type) and Pipeline Activity bars

---

## Scene 2: New Claim with Photos (0:30–1:00)

**Audio:** "Let's submit a new claim with damage photos to show the AI vision capability."

**Screen:** Click "New Claim" button → navigate to `http://localhost:3010/new`

- Fill in the form quickly:
  - Name: "Test User"
  - Email: "test@email.com"
  - Policy: "POL-2026-001"
  - Type: "Auto"
  - Description: "Car hit a pothole, damaged front right wheel and suspension"
  - Incident Date: today's date
  - Location: "San Francisco, CA"
  - Estimated Loss: "2500"
- **Drag & drop a damage photo** (use any car damage image from your computer) into the upload zone
- Click "Submit Claim"

---

## Scene 3: Pipeline Processing (1:00–1:45)

**Audio:** "The claim is submitted. Now watch the AI pipeline process it automatically."

**Screen:** After submission, you're redirected to the claim detail page

- Click "Run Pipeline" button
- **Zoom in on the React Flow pipeline visualization** at the top
- Watch as each agent activates sequentially (the animation shows):
  1. **Intake** → extracts claim data (blue highlight + pulsing dot)
  2. **Validation** → verifies policy (green)
  3. **Assessment** → estimates payout ($2,000) 
  4. **Review Gate** → auto-approves (low risk)
  5. **Resolution** → generates approval letter
- Point to the **confidence bars** in each completed node
- Point to the **pipeline progress bar** filling up

**Audio:** "Five AI agents processed this claim in seconds — Intake used Qwen3.7-Plus vision to analyze the photo, Validation and Assessment used Qwen3.7-Max for reasoning, and Resolution used Qwen3.6-Flash for speed."

---

## Scene 4: Results & Agent Data (1:45–2:15)

**Audio:** "Here are the results from each agent."

**Screen:** Scroll down to "Agent Results" section

- Point to each ResultCard:
  - **Intake:** extracted data (claimant name, type, date, location, confidence 95%)
  - **Validation:** policy valid, coverage active
  - **Assessment:** $2,000 estimated payout, moderate damage severity
  - **Review Gate:** auto-approved, low fraud risk
  - **Resolution:** approved, net payout: $1,500 (after deductible)
- Scroll back up to the status panel showing "Resolved" with payout amount

---

## Scene 5: Human Review Flow (2:15–2:45)

**Audio:** "For high-value claims, the system flags them for human review."

**Screen:** Navigate to `http://localhost:3010/reviews`

- Point to the Frank Wilson claim (liability, $25,000 — flagged for review)
- Click "Review" or show the approve/reject UI
- Explain: "Claims over $5,000 or with medium-to-high fraud risk are sent to a human operator who can approve, reject, or add notes. This fulfills the 'human-in-the-loop' requirement for Track 4: Autopilot Agent."

**Screen:** Navigate back to dashboard, show the full table with all 9 claims in different states

---

## Scene 6: Architecture & Wrap (2:45–3:00)

**Audio:** "The architecture uses FastAPI as the API gateway, an agent orchestrator chains 5 specialized AI agents, and the entire system is deployed on Alibaba Cloud infrastructure with Qwen Cloud API for inference."

**Screen:** Show the architecture diagram (`docs/architecture.svg` — open in browser)

- Briefly point to: Frontend → API → Orchestrator → Agents → Qwen Cloud
- Show the repo on GitHub

**Audio:** "Built for the Qwen Cloud Global AI Hackathon — Track 4: Autopilot Agent. Full source code, deployment scripts, and documentation available on GitHub. Thanks for watching!"

---

## Tips for Recording

1. **Clean audio** — use a USB mic or good headset, record in a quiet room
2. **1920x1080** resolution at 30fps minimum
3. **Cursor visible** — enlarge cursor in Windows settings (Settings > Accessibility > Mouse pointer)
4. **No background apps** — close Slack, email, notifications
5. **Smooth mouse movements** — don't rush, let each scene breathe for 2-3 seconds
6. **Background music** — add low-volume royalty-free music (YouTube Audio Library)
7. **Captions** — add subtitles for accessibility (CapCut, DaVinci Resolve, or VEED.io)

## Example Screenshots to Include (record separately)

1. Full dashboard page
2. Claim form with photo upload
3. Pipeline visualization mid-processing (agents 3/5 completed)
4. Complete pipeline with all green nodes
5. Agent Results cards
6. Human Review dashboard
7. Architecture diagram
8. GitHub repo page
