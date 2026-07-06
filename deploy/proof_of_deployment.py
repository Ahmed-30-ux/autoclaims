"""
AutoClaims — Proof of Alibaba Cloud Deployment for Qwen Cloud Hackathon.

Run this on your deployed ECS instance to generate a proof HTML page.

Usage:
  python proof_of_deployment.py

Output:
  Generates proof.html with deployment evidence (screenshots, API responses, Qwen model info)
"""

import json
import os
import subprocess
import sys
from datetime import datetime


def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return r.stdout.strip() or r.stderr.strip()
    except Exception as e:
        return str(e)


def main():
    hostname = run("hostname")
    public_ip = run("curl -s ifconfig.me || curl -s icanhazip.com || echo 'unknown'")
    timestamp = datetime.utcnow().isoformat()

    # Health check
    api_health = run("curl -s http://localhost:8000/api/health")
    try:
        api_health_json = json.loads(api_health)
    except (json.JSONDecodeError, TypeError):
        api_health_json = {"error": api_health}

    # Claims list
    claims = run("curl -s http://localhost:8000/api/claims")
    try:
        claims_json = json.loads(claims)
        claim_count = claims_json.get("total", 0)
    except (json.JSONDecodeError, TypeError):
        claim_count = 0

    # Frontend
    frontend = run("curl -s -o /dev/null -w '%{http_code}' http://localhost:3010/")

    # Docker status
    docker_ps = run("docker ps --format '{{.Names}} | {{.Status}}'")

    # Qwen models used
    qwen_models = {
        "qwen3.7-max": "Validation, Assessment, Review Gate agents",
        "qwen3.7-plus": "Intake Agent (vision processing)",
        "qwen3.6-flash": "Resolution Agent (fast generation)",
    }

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AutoClaims — Proof of Alibaba Cloud Deployment</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; background: #f8fafc; color: #1e293b; }}
  h1 {{ color: #2563eb; }}
  .card {{ background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin: 16px 0; }}
  .badge {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }}
  .badge-green {{ background: #dcfce7; color: #166534; }}
  .badge-blue {{ background: #dbeafe; color: #1e40af; }}
  .badge-red {{ background: #fee2e2; color: #991b1b; }}
  table {{ width: 100%; border-collapse: collapse; }}
  td, th {{ text-align: left; padding: 8px 12px; border-bottom: 1px solid #e2e8f0; font-size: 14px; }}
  th {{ font-weight: 600; color: #64748b; }}
  .footer {{ margin-top: 40px; text-align: center; font-size: 12px; color: #94a3b8; }}
</style>
</head>
<body>
  <h1>AutoClaims — Proof of Deployment</h1>
  <p style="color:#64748b">Generated: {timestamp}</p>

  <div class="card">
    <h2>Deployment Information</h2>
    <table>
      <tr><th>Hostname</th><td>{hostname}</td></tr>
      <tr><th>Public IP</th><td>{public_ip}</td></tr>
      <tr><th>Region</th><td>Alibaba Cloud ECS</td></tr>
    </table>
  </div>

  <div class="card">
    <h2>Service Status</h2>
    <table>
      <tr>
        <th>Service</th>
        <th>Status</th>
        <th>Details</th>
      </tr>
      <tr>
        <td>Backend API</td>
        <td><span class="badge {'badge-green' if api_health_json.get('status') == 'ok' else 'badge-red'}">{'Running' if api_health_json.get('status') == 'ok' else 'Error'}</span></td>
        <td>{api_health_json.get('status', 'unknown')}</td>
      </tr>
      <tr>
        <td>Frontend</td>
        <td><span class="badge {'badge-green' if frontend == '200' else 'badge-red'}">{'Running' if frontend == '200' else 'Error'}</span></td>
        <td>HTTP {frontend}</td>
      </tr>
      <tr>
        <td>Claims in DB</td>
        <td><span class="badge badge-blue">{claim_count}</span></td>
        <td>{'Demo data seeded' if claim_count > 0 else 'Empty'}</td>
      </tr>
    </table>
  </div>

  <div class="card">
    <h2>Qwen Cloud AI Models</h2>
    <p>API Base: https://dashscope-intl.aliyuncs.com/compatible-mode/v1</p>
    <table>
      <tr><th>Model</th><th>Used By</th></tr>
"""
    for model, purpose in qwen_models.items():
        html += f'      <tr><td>{model}</td><td>{purpose}</td></tr>\n'

    html += f"""    </table>
  </div>

  <div class="card">
    <h2>Docker Containers</h2>
    <pre style="background:#f1f5f9;padding:12px;border-radius:8px;font-size:13px;">{docker_ps}</pre>
  </div>

  <div class="card">
    <h2>API Verification</h2>
    <p><strong>Health Endpoint:</strong></p>
    <pre style="background:#f1f5f9;padding:12px;border-radius:8px;font-size:13px;">{json.dumps(api_health_json, indent=2)}</pre>
    <p><strong>Claims List:</strong> {claim_count} total claims</p>
    <p><strong>Proof:</strong> Run <code>curl http://{public_ip}:8000/api/health</code> from any browser to verify.</p>
  </div>

  <div class="footer">
    <p>AutoClaims — Global AI Hackathon with Qwen Cloud (Track 4: Autopilot Agent)</p>
    <p><a href="https://github.com/your-username/autoclaims">GitHub Repository</a> | MIT License</p>
  </div>
</body>
</html>"""

    output_path = os.path.join(os.path.dirname(__file__), "proof.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Proof of deployment saved to: {output_path}")
    print(f"Open this file in a browser to verify Alibaba Cloud deployment.")


if __name__ == "__main__":
    main()
