import os
svg_path = os.path.join(os.path.dirname(__file__), "architecture.svg")
html_path = os.path.join(os.path.dirname(__file__), "architecture.html")
with open(svg_path, encoding="utf-8") as f:
    svg = f.read()
html = f"""<!DOCTYPE html><html><body style="margin:0;background:#f8fafc">{svg}</body></html>"""
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Created: {html_path}")
