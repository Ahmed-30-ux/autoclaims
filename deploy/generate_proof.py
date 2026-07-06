import json, os, subprocess, sys
from datetime import datetime

def run(cmd, timeout=5):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()[:500] or r.stderr.strip()[:500]
    except:
        return "N/A"

hostname = run("hostname")
timestamp = datetime.utcnow().isoformat()

api_health = run("curl.exe -s http://localhost:8000/api/health")
frontend = run("curl.exe -s -o /dev/null -w '%{http_code}' http://localhost:3010/")
claims_raw = run("curl.exe -s http://localhost:8000/api/claims")

try:
    health = json.loads(api_health) if api_health else {}
except:
    health = {}

claim_count = 0
claims = []
if claims_raw and claims_raw != "N/A":
    try:
        data = json.loads(claims_raw)
        claim_count = data.get("total", 0)
        claims = data.get("claims", [])
    except:
        pass

# Build claim table rows
claim_rows = ""
for c in claims:
    status_badge = "🟢" if c["status"] == "resolved" else "🟡" if c["status"] in ("submitted","pending_review") else "🔴"
    intake = "✅" if c.get("intake_data") else "❌"
    agent = "✅" if c.get("resolution_data") or c.get("review_gate_data") else "❌"
    claim_rows += f"""
    <tr>
      <td>#{c['id']}</td>
      <td>{c['claimant_name']}</td>
      <td>{c['claim_type']}</td>
      <td><span class="status-dot">{status_badge}</span> {c['status']}</td>
      <td>{intake}</td>
      <td>{agent}</td>
    </tr>"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AutoClaims — Proof of Deployment</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: #e2e8f0; line-height: 1.6; }}
  .container {{ max-width: 960px; margin: 0 auto; padding: 40px 24px; }}
  h1 {{ font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 4px; }}
  .subtitle {{ color: #94a3b8; font-size: 0.9rem; margin-bottom: 32px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 32px; }}
  .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; }}
  .card h3 {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; margin-bottom: 8px; }}
  .card .value {{ font-size: 1.5rem; font-weight: 700; }}
  .card .value.green {{ color: #34d399; }}
  .card .value.yellow {{ color: #fbbf24; }}
  .card .value.blue {{ color: #60a5fa; }}
  .card .value.purple {{ color: #a78bfa; }}
  .section-title {{ font-size: 1.1rem; font-weight: 600; margin-bottom: 12px; margin-top: 32px; color: #f1f5f9; }}
  table {{ width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 12px; overflow: hidden; }}
  th {{ background: #334155; padding: 10px 14px; text-align: left; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; }}
  td {{ padding: 10px 14px; border-bottom: 1px solid #1e293b; font-size: 0.85rem; }}
  tr:last-child td {{ border-bottom: none; }}
  .status-dot {{ font-size: 0.8rem; }}
  .badge {{ display: inline-block; padding: 2px 10px; border-radius: 9999px; font-size: 0.7rem; font-weight: 600; }}
  .badge-green {{ background: rgba(52,211,153,0.15); color: #34d399; }}
  .badge-yellow {{ background: rgba(251,191,36,0.15); color: #fbbf24; }}
  .badge-red {{ background: rgba(248,113,113,0.15); color: #f87171; }}
  .code {{ background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 12px 16px; font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 0.8rem; overflow-x: auto; white-space: pre-wrap; color: #a5b4fc; }}
  .footer {{ margin-top: 48px; padding-top: 24px; border-top: 1px solid #334155; text-align: center; font-size: 0.8rem; color: #64748b; }}
  .footer a {{ color: #60a5fa; text-decoration: none; }}
  .qwen-list {{ display: flex; gap: 12px; flex-wrap: wrap; }}
  .qwen-item {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 12px 16px; flex: 1; min-width: 180px; }}
  .qwen-item .model {{ font-weight: 600; color: #a78bfa; font-size: 0.85rem; }}
  .qwen-item .desc {{ color: #94a3b8; font-size: 0.75rem; margin-top: 4px; }}
  .screenshots {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; margin-top: 12px; }}
  .screenshot {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; overflow: hidden; }}
  .screenshot img {{ width: 100%; display: block; }}
  .screenshot .label {{ padding: 8px 12px; font-size: 0.75rem; color: #94a3b8; }}
</style>
</head>
<body>
<div class="container">

  <h1>AutoClaims</h1>
  <p class="subtitle">Multi-Agent AI Insurance Claims Processing — Proof of Deployment<br>Generated: {timestamp}</p>

  <!-- Status Cards -->
  <div class="grid">
    <div class="card">
      <h3>Backend API</h3>
      <div class="value {'green' if health.get('status') == 'ok' else 'red'}">{'Running' if health.get('status') == 'ok' else 'Error'}</div>
      <div style="font-size:0.75rem;color:#64748b;margin-top:4px;">Port 8000</div>
    </div>
    <div class="card">
      <h3>Frontend</h3>
      <div class="value {'green' if frontend == '200' else 'red'}">{'Serving' if frontend == '200' else 'Down'}</div>
      <div style="font-size:0.75rem;color:#64748b;margin-top:4px;">Port 3010</div>
    </div>
    <div class="card">
      <h3>Qwen API</h3>
      <div class="value {'green' if health.get('qwen_configured') else 'red'}">{'Configured' if health.get('qwen_configured') else 'Missing'}</div>
      <div style="font-size:0.75rem;color:#64748b;margin-top:4px;">{health.get('qwen_configured', False) and 'API Key Active' or 'Not Set'}</div>
    </div>
    <div class="card">
      <h3>Claims</h3>
      <div class="value blue">{claim_count}</div>
      <div style="font-size:0.75rem;color:#64748b;margin-top:4px;">In Database</div>
    </div>
  </div>

  <!-- Architecture -->
  <div class="section-title">Architecture Overview</div>
  <div class="card" style="padding:16px;">
    <img src="file:///C:/Users/aaa13/autoclaims/docs/architecture.svg" alt="Architecture Diagram" style="width:100%;max-width:800px;border-radius:8px;display:block;margin:0 auto;" onerror="this.style.display='none'">
    <div style="font-size:0.75rem;color:#64748b;margin-top:8px;text-align:center;">docs/architecture.svg — 5-agent pipeline: Intake → Validation → Assessment → Review Gate → Resolution</div>
  </div>

  <!-- Qwen Models -->
  <div class="section-title">Qwen Cloud AI Models</div>
  <div class="qwen-list">
    <div class="qwen-item">
      <div class="model">qwen3.7-max</div>
      <div class="desc">Validation, Assessment, Review Gate</div>
    </div>
    <div class="qwen-item">
      <div class="model">qwen3.7-plus</div>
      <div class="desc">Intake Agent (vision + analysis)</div>
    </div>
    <div class="qwen-item">
      <div class="model">qwen3.6-flash</div>
      <div class="desc">Resolution Agent (email generation)</div>
    </div>
  </div>

  <!-- Claims Table -->
  <div class="section-title">Claims Database ({claim_count} total)</div>
  <table>
    <thead>
      <tr><th>ID</th><th>Claimant</th><th>Type</th><th>Status</th><th>Intake</th><th>Agent Data</th></tr>
    </thead>
    <tbody>
      {claim_rows}
    </tbody>
  </table>

  <!-- API Verification -->
  <div class="section-title">API Verification</div>
  <div style="font-size:0.85rem;color:#94a3b8;margin-bottom:8px;">Health endpoint response:</div>
  <div class="code">{json.dumps(health, indent=2) if health else 'N/A'}</div>

  <!-- Screenshots -->
  <div class="section-title">Screenshots</div>
  <div class="screenshots">
    <div class="screenshot">
      <img src="file:///C:/Users/aaa13/autoclaims/docs/screenshots/dashboard.png" onerror="this.alt='Screenshot not found';this.style.display='none'">
      <div class="label">Dashboard</div>
    </div>
    <div class="screenshot">
      <img src="file:///C:/Users/aaa13/autoclaims/docs/screenshots/claim_detail.png" onerror="this.alt='Screenshot not found';this.style.display='none'">
      <div class="label">Claim Detail — Pipeline View</div>
    </div>
    <div class="screenshot">
      <img src="file:///C:/Users/aaa13/autoclaims/docs/screenshots/new_claim.png" onerror="this.alt='Screenshot not found';this.style.display='none'">
      <div class="label">New Claim Form</div>
    </div>
    <div class="screenshot">
      <img src="file:///C:/Users/aaa13/autoclaims/docs/screenshots/reviews.png" onerror="this.alt='Screenshot not found';this.style.display='none'">
      <div class="label">Human Reviews</div>
    </div>
    <div class="screenshot">
      <img src="file:///C:/Users/aaa13/autoclaims/docs/screenshots/architecture.png" onerror="this.alt='Screenshot not found';this.style.display='none'">
      <div class="label">Architecture Diagram</div>
    </div>
  </div>

  <!-- System Info -->
  <div class="section-title">System Information</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:0.85rem;">
    <div><span style="color:#64748b;">Hostname:</span> {hostname}</div>
    <div><span style="color:#64748b;">Platform:</span> Windows</div>
    <div><span style="color:#64748b;">Backend:</span> FastAPI + SQLite</div>
    <div><span style="color:#64748b;">Frontend:</span> Next.js 15 (React 19)</div>
    <div><span style="color:#64748b;">AI:</span> Qwen Cloud API</div>
    <div><span style="color:#64748b;">Docker:</span> Ready (Dockerfiles created)</div>
  </div>

  <div class="footer">
    <p><strong>AutoClaims</strong> — Global AI Hackathon with Qwen Cloud (Track 4: Autopilot Agent)</p>
    <p>5 AI Agents • Human-in-the-Loop Review • Photo Vision Analysis • Qwen3.7-Powered</p>
    <p>Proof generated locally — ready for Alibaba Cloud ECS deployment</p>
  </div>

</div>
</body>
</html>"""

output_path = os.path.join(os.path.dirname(__file__), "proof_of_deployment.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Saved: {output_path}")
print(f"Open in browser to view proof of deployment.")
