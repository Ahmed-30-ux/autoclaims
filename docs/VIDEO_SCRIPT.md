# AutoClaims — Demo Video Script (3 minutes)

## Setup
- Open `http://localhost:3010` in fullscreen browser (Chrome/Edge)
- Screen recording: **Windows Game Bar** (Win+G) or **OBS Studio** (free)
- Record at **1920×1080, 30fps minimum**
- Enlarge cursor: Settings > Accessibility > Mouse pointer > Size 3
- Close all other apps (Slack, email, etc.)

> **IMPORTANT:** Before recording, run the pipeline on claim #8 (Henry Nakamura) so the video shows a completed pipeline in action.

---

## Scene 1: Dashboard Overview (0:00–0:30)

**Screen:** `http://localhost:3010` — Dashboard page

**Audio:** "Welcome to AutoClaims — an autonomous AI insurance claims processing system powered by Qwen Cloud. This dashboard gives a real-time view of our claims pipeline."

**Actions:**
1. Pause 2 sec on the hero banner ("AutoClaims Intelligence" with gradient)
2. Slowly mouse-over the 4 stat cards at top: Total Claims (10), Pending Review (1), Resolved, Avg Payout
3. Scroll down slowly to the claims table
4. Hover over each status badge, naming them:
   - Claim #1 Alice — **submitted** (blue) — fresh claim waiting
   - Claim #6 Frank — **pending_review** (orange) — needs human operator
   - Claim #4 Daniel — **resolved** (green) — fully processed
   - Claim #10 James — **rejected** (red) — denied by the pipeline
5. Glance at the Pie Chart and bar chart on the right
6. "We have 10 claims in the system across submitted, pending review, resolved, and rejected states."

---

## Scene 2: New Claim with Photo Upload (0:30–1:00)

**Audio:** "Let's submit a new claim using the AI photo analysis feature."

**Actions:**
1. Click **"New Claim"** button (top right or hero CTA)
2. Fill the form (type fast, it's OK to pre-type the text):
   - Claimant Name: `Sarah Chen`
   - Email: `sarah@email.com`
   - Phone: `+1-555-0101`
   - Policy Number: `POL-2026-001`
   - Claim Type: `Auto`
   - Description: `Rear-ended at traffic light. Damage to rear bumper and trunk lid.`
   - Incident Date: `2026-07-05`
   - Location: `San Francisco, CA`
   - Estimated Loss: `3200`
3. **Photo upload:** Drag a car damage photo (or any image) into the dotted upload zone
   - If you don't have one, take a photo of a scratched item with your phone
   - After dropping, show the **image preview** thumbnail with a remove "×" button
4. Click **"Submit Claim"** 
5. "The photo will be analyzed by Qwen3.7-Plus vision API during intake."

---

## Scene 3: Pipeline Processing (1:00–1:45)

**Audio:** "Now watch the five AI agents process this claim."

**Actions (on claim detail page after redirect):**
1. Click **"Run Pipeline"** button
2. **Zoom into the horizontal pipeline visualization** at the top of the page
3. Speak as each agent activates (the animation shows pulsing blue dots on the active node):
   - **Intake Agent** (Qwen3.7-Plus): "Extracting structured data from the submission and analyzing the damage photo — it identifies this as a rear-end collision with moderate bumper damage."
   - **Validation Agent** (Qwen3.7-Max): "Checking policy POL-2026-001 — it's active with $50,000 auto coverage. Claimant Sarah Chen is listed as a covered driver. Validated."
   - **Assessment Agent** (Qwen3.7-Max): "Estimating repair costs based on damage description — $2,800 for bumper replacement and trunk repair. Fraud risk is low at 12%."
   - **Review Gate** (Qwen3.7-Max): "Low fraud risk and under $5,000 threshold — auto-approving without human review."
   - **Resolution Agent** (Qwen3.6-Flash): "Generating the approval letter and calculating the net payout — $2,300 after the $500 deductible."
4. Point to each node's **confidence bar** filling up as they complete
5. Point to the **pipeline progress bar** at the bottom reaching 100%
6. "The entire pipeline completed in seconds. Each agent uses a specialized Qwen model."

---

## Scene 4: Results & Photo Analysis (1:45–2:20)

**Audio:** "Here's what each agent found, including the AI vision results."

**Actions:**
1. Scroll down to **"Agent Results"** section
2. Point to each result card:
   - **Intake Analysis Card** — Show the photo analysis result:
     - Damage Type: Collision / Rear-end
     - Severity: Moderate
     - Est. Repair Cost: $2,800–$3,500
     - Fraud Indicators: None detected
   - **Validation** — Policy valid, coverage active, confidence 96%
   - **Assessment** — $2,800 est. payout, moderate severity, low fraud
   - **Review Gate** — Auto-approved (no human review needed)
   - **Resolution** — Approved, net payout: $2,300
3. Scroll back up to the status banner showing "Resolved" with payout
4. "This is a fully resolved claim — approved and ready for payment."

---

## Scene 5: Rejected Claim & Human Review (2:20–2:45)

**Audio:** "Not all claims get approved. Let's look at a rejected one and the human review flow."

**Actions:**
1. Navigate to dashboard (`/`)
2. Find **Claim #10 — James Brown** in the table, status: **rejected** (red)
3. Click on claim #10 to open detail page
4. Scroll to Agent Results:
   - Intake: **Flags: delayed reporting, high value, no police report**
   - Assessment: **Fraud risk: high (95% confidence)**, multiple fraud flags
   - Resolution: **Rejected — fraudulent pattern detected**
5. "The pipeline detected red flags: $50,000 watch claimed 3 weeks after travel, no police report, no proof of purchase — and the policy only covers $500 per item."
6. Navigate to **Reviews** (`/reviews`)
7. Point to **Frank Wilson** (claim #6) — pending review
8. "For claims like this $25,000 liability case flagged by the Review Gate, a human operator reviews and makes the final decision — the human-in-the-loop safeguard."

---

## Scene 6: Architecture & Wrap (2:45–3:00)

**Audio:** "Here's the system architecture and how it all fits together."

**Actions:**
1. Open `docs/architecture.svg` in the browser (drag the file into Chrome)
2. Mouse-over each layer as you describe:
   - **Frontend** (Next.js) — Dashboard, claim form, pipeline visualization, reviews
   - **API Gateway** (FastAPI) — REST endpoints
   - **Agent Orchestrator** — Chains 5 agents with state persistence
   - **AI Agents** — Intake → Validation → Assessment → Review Gate → Resolution
   - **Qwen Cloud** — 3 models: Plus (vision), Max (reasoning), Flash (speed)
   - **Data Layer** — SQLite database with claims, policies, reviews
3. Switch to GitHub: `https://github.com/Ahmed-30-ux/autoclaims`
4. "Full source code, Docker deployment scripts, and documentation are on GitHub. Built for the Qwen Cloud Global AI Hackathon — Track 4: Autopilot Agent. Thanks for watching!"

---

## Key Shots to Capture (record as separate clips)

1. Dashboard with all 10 claims visible
2. Claim form with photo being dragged in
3. Pipeline animation running (record 10-15 sec of the processing)
4. Completed pipeline with all green nodes
5. Photo analysis result card
6. Rejected claim (James #10) with fraud flags
7. Human review dashboard
8. Architecture diagram
9. GitHub repo page

## Recording Tips

1. **Audio:** Use a headset mic, record in a quiet room. Speak clearly and at a steady pace.
2. **Mouse:** Move smoothly — don't rush. Pause 2-3 seconds on each element.
3. **Background music:** Add low-volume royalty-free music (YouTube Audio Library has good options).
4. **Captions:** Add subtitles using CapCut, DaVinci Resolve, or VEED.io for accessibility.
5. **No watermark:** Use OBS or Game Bar — no free version watermarks.
6. **Export:** H.264 MP4, 1080p, ~50-100 MB max.
