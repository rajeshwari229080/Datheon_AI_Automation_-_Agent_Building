"""
Light-Theme Graphics Generator for Enterprise AI Automation Suite.
Generates publication-quality light-theme PNG visuals:
1. image.png (Root LinkedIn banner)
2. docs/assets/linkedin_banner.png
3. docs/assets/module3_invoice_scanner_light.png
4. docs/assets/module4_multiagent_light.png
"""

import os
from PIL import Image, ImageDraw, ImageFont

def get_font(name="segoeui.ttf", size=20, bold=False):
    font_file = "segoeuib.ttf" if bold else "segoeui.ttf"
    font_path = os.path.join("C:/Windows/Fonts", font_file)
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

def draw_rounded_card(draw, xy, fill="#FFFFFF", outline="#E2E8F0", radius=16, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_pill(draw, xy, text, font, fill="#EEF2FF", text_color="#4F46E5", radius=12):
    draw.rounded_rectangle(xy, radius=radius, fill=fill)
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    card_w = xy[2] - xy[0]
    card_h = xy[3] - xy[1]
    draw.text((xy[0] + (card_w - w)/2, xy[1] + (card_h - h)/2 - 2), text, font=font, fill=text_color)

def generate_linkedin_banner(output_paths):
    W, H = 1200, 675
    img = Image.new("RGB", (W, H), "#F8FAFC")
    draw = ImageDraw.Draw(img)

    # Background subtle gradient effect
    for y in range(H):
        ratio = y / H
        r = int(248 * (1 - ratio*0.03))
        g = int(250 * (1 - ratio*0.02))
        b = int(252 * (1 - ratio*0.01))
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Top accent gradient bar
    draw.rectangle([(0, 0), (W, 8)], fill="#4F46E5")

    # Header section
    f_badge = get_font("segoeuib.ttf", 14, bold=True)
    draw_pill(draw, (60, 40, 310, 72), "ENTERPRISE AUTOMATION SUITE", f_badge, fill="#EEF2FF", text_color="#4F46E5", radius=16)
    draw_pill(draw, (325, 40, 480, 72), "4 MODULES + AI AGENTS", f_badge, fill="#ECFDF5", text_color="#059669", radius=16)
    draw_pill(draw, (495, 40, 620, 72), "PRODUCTION READY", f_badge, fill="#F0FDF4", text_color="#166534", radius=16)

    f_title = get_font("segoeuib.ttf", 42, bold=True)
    draw.text((60, 88), "Enterprise AI Automation Suite", font=f_title, fill="#0F172A")

    f_sub = get_font("segoeui.ttf", 20)
    draw.text((60, 142), "Full-Stack Autonomous Workflows: Leads, Support Triage, Invoice OCR & Multi-Agent Ops", font=f_sub, fill="#64748B")

    # 4 Modules Grid
    cards = [
        ("01", "Lead Routing & Qualification", "Deterministic ICP rules, LLM fit analysis, <10s SLA latency, live Airtable & Slack alerts.", "#EEF2FF", "#4F46E5"),
        ("02", "Autonomous Support Triage", "8 intent classifications, grounded RAG citations, prompt injection defense, draft-only queue.", "#F0FDF4", "#059669"),
        ("03", "AI Vision Invoice Scanner", "Binary signature security, OCR line-item extraction, strict arithmetic verification, Sheets sync.", "#EFF6FF", "#2563EB"),
        ("04", "Multi-Agent Enterprise Ops", "9 specialized agents, state machine supervisor, cryptographic Stripe webhook verification.", "#FAF5FF", "#7C3AED")
    ]

    card_w = 260
    card_h = 240
    start_x = 60
    start_y = 195
    gap = 26

    f_card_num = get_font("segoeuib.ttf", 16, bold=True)
    f_card_title = get_font("segoeuib.ttf", 18, bold=True)
    f_card_desc = get_font("segoeui.ttf", 14)

    for i, (num, title, desc, pill_bg, pill_fg) in enumerate(cards):
        cx = start_x + i * (card_w + gap)
        cy = start_y
        draw_rounded_card(draw, (cx, cy, cx + card_w, cy + card_h), fill="#FFFFFF", outline="#E2E8F0", radius=14, width=1)
        
        # Pill number
        draw_pill(draw, (cx + 18, cy + 18, cx + 64, cy + 46), f"M-{num}", f_card_num, fill=pill_bg, text_color=pill_fg, radius=8)
        
        # Title
        # Wrap title
        words = title.split(" ")
        if len(words) > 2:
            t1 = " ".join(words[:2])
            t2 = " ".join(words[2:])
            draw.text((cx + 18, cy + 58), t1, font=f_card_title, fill="#0F172A")
            draw.text((cx + 18, cy + 82), t2, font=f_card_title, fill="#0F172A")
            desc_y = cy + 115
        else:
            draw.text((cx + 18, cy + 62), title, font=f_card_title, fill="#0F172A")
            desc_y = cy + 100

        # Description wrapped
        lines = []
        cur = ""
        for w in desc.split(" "):
            if len(cur + " " + w) < 32:
                cur += (" " if cur else "") + w
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)

        for l_idx, line in enumerate(lines[:5]):
            draw.text((cx + 18, desc_y + l_idx * 20), line, font=f_card_desc, fill="#64748B")

    # Metrics Footer Banner
    draw_rounded_card(draw, (60, 465, W - 60, 615), fill="#FFFFFF", outline="#CBD5E1", radius=14, width=1)
    
    metrics = [
        ("310 ms", "Lead Routing SLA (Target <10s)"),
        ("9 Agents", "Autonomous Enterprise System"),
        ("100% Pass", "20 Automated Pytest Tests"),
        ("Draft-Only", "Human-in-the-Loop Safety"),
        ("HMAC-SHA256", "Cryptographic Stripe Verifier")
    ]

    sec_w = (W - 120) / len(metrics)
    f_val = get_font("segoeuib.ttf", 24, bold=True)
    f_lbl = get_font("segoeui.ttf", 12)

    for i, (val, lbl) in enumerate(metrics):
        mx = 60 + i * sec_w
        # Divider line
        if i > 0:
            draw.line([(mx, 485), (mx, 595)], fill="#E2E8F0", width=1)
        
        draw.text((mx + 20, 500), val, font=f_val, fill="#4F46E5")
        
        # Wrap label
        l_parts = lbl.split(" ")
        mid = len(l_parts) // 2
        l1 = " ".join(l_parts[:mid+1])
        l2 = " ".join(l_parts[mid+1:])
        draw.text((mx + 20, 540), l1, font=f_lbl, fill="#64748B")
        if l2:
            draw.text((mx + 20, 560), l2, font=f_lbl, fill="#64748B")

    # Bottom footer tag
    f_foot = get_font("segoeui.ttf", 13)
    draw.text((60, 635), "Stack: Python 3.12 | FastAPI | SQLite/PostgreSQL | OpenAI | Make.com & n8n | Stripe | Slack | Airtable", font=f_foot, fill="#94A3B8")
    draw.text((W - 320, 635), "GitHub: rajeshwari229080", font=f_foot, fill="#4F46E5")

    for path in output_paths:
        img.save(path, "PNG", quality=95)
        print(f"Generated: {path}")

def generate_module3_graphic(output_path):
    W, H = 1200, 675
    img = Image.new("RGB", (W, H), "#F8FAFC")
    draw = ImageDraw.Draw(img)

    for y in range(H):
        ratio = y / H
        r = int(248 * (1 - ratio*0.03))
        g = int(250 * (1 - ratio*0.02))
        b = int(252 * (1 - ratio*0.01))
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Top accent
    draw.rectangle([(0, 0), (W, 8)], fill="#2563EB")

    f_badge = get_font("segoeuib.ttf", 14, bold=True)
    draw_pill(draw, (60, 35, 340, 67), "MODULE 3: INVOICE INTELLIGENCE", f_badge, fill="#EFF6FF", text_color="#2563EB", radius=16)

    f_title = get_font("segoeuib.ttf", 34, bold=True)
    draw.text((60, 80), "AI Vision Invoice Scanner & Accounting Sync", font=f_title, fill="#0F172A")
    f_sub = get_font("segoeui.ttf", 18)
    draw.text((60, 125), "Secure PDF ingestion, OCR line-item extraction, and deterministic arithmetic verification", font=f_sub, fill="#64748B")

    # Left Card: Upload & Extracted Invoice
    draw_rounded_card(draw, (60, 175, 540, 620), fill="#FFFFFF", outline="#E2E8F0", radius=14)
    f_sec = get_font("segoeuib.ttf", 18, bold=True)
    draw.text((85, 200), "Extracted Invoice Provenance", font=f_sec, fill="#0F172A")
    draw_pill(draw, (380, 195, 515, 227), "%PDF- VERIFIED", f_badge, fill="#ECFDF5", text_color="#059669", radius=8)

    f_body = get_font("segoeui.ttf", 14)
    f_body_b = get_font("segoeuib.ttf", 14, bold=True)

    draw.text((85, 245), "Vendor Name:", font=f_body, fill="#64748B")
    draw.text((210, 245), "CloudScale Infrastructure Inc.", font=f_body_b, fill="#0F172A")

    draw.text((85, 275), "Invoice Number:", font=f_body, fill="#64748B")
    draw.text((210, 275), "INV-2026-9042", font=f_body_b, fill="#0F172A")

    draw.text((85, 305), "Invoice Date:", font=f_body, fill="#64748B")
    draw.text((210, 305), "2026-10-18 (Parsed UTC)", font=f_body_b, fill="#0F172A")

    draw.text((85, 335), "SHA-256 Hash:", font=f_body, fill="#64748B")
    draw.text((210, 335), "e3b0c44298fc1c14... (No Duplicates)", font=f_body_b, fill="#059669")

    # Line item preview box
    draw_rounded_card(draw, (85, 380, 515, 590), fill="#F8FAFC", outline="#E2E8F0", radius=10)
    draw.text((105, 395), "Line Items Extracted", font=f_body_b, fill="#0F172A")
    draw.line([(105, 420), (495, 420)], fill="#E2E8F0")

    items = [
        ("Kubernetes Cluster (3 Nodes)", "1 mo", "$1,200.00"),
        ("Enterprise Storage Volume 2TB", "1 mo", "$450.00"),
        ("Dedicated Egress Bandwidth", "500 GB", "$150.00")
    ]
    for idx, (desc, qty, amt) in enumerate(items):
        iy = 435 + idx * 35
        draw.text((105, iy), desc, font=f_body, fill="#334155")
        draw.text((350, iy), qty, font=f_body, fill="#64748B")
        draw.text((430, iy), amt, font=f_body_b, fill="#0F172A")

    # Right Card: Arithmetic & Google Sheets Export
    draw_rounded_card(draw, (570, 175, W - 60, 620), fill="#FFFFFF", outline="#E2E8F0", radius=14)
    draw.text((595, 200), "Financial Verification & Sync", font=f_sec, fill="#0F172A")

    # Math Verification Panel
    draw_rounded_card(draw, (595, 240, W - 85, 430), fill="#F0FDF4", outline="#86EFAC", radius=10)
    draw.text((615, 260), "Mathematical Invariant Checks", font=f_sec, fill="#166534")

    checks = [
        ("Sum of Line Items == Subtotal", "$1,200 + $450 + $150 = $1,800.00", "PASS"),
        ("Tax Calculation (8.25%)", "$1,800.00 * 0.0825 = $148.50", "PASS"),
        ("Grand Total Balance Check", "$1,800.00 + $148.50 = $1,948.50", "MATCH")
    ]
    for idx, (title, formula, st) in enumerate(checks):
        cy = 295 + idx * 40
        draw.text((615, cy), f"[OK] {title}", font=f_body_b, fill="#15803D")
        draw.text((615, cy + 18), formula, font=get_font("segoeui.ttf", 12), fill="#166534")

    # Sync to Sheets Panel
    draw_rounded_card(draw, (595, 450, W - 85, 590), fill="#F8FAFC", outline="#E2E8F0", radius=10)
    draw.text((615, 470), "Google Sheets Accounting Sync", font=f_sec, fill="#0F172A")
    draw.text((615, 500), "Status: Verified & Exported (Row #148 added to Ledger)", font=f_body, fill="#334155")
    draw.text((615, 525), "Retry Policy: Transactional rollback with exponential backoff", font=f_body, fill="#64748B")

    draw_pill(draw, (615, 555, 760, 583), "EXPORTED", f_badge, fill="#ECFDF5", text_color="#059669", radius=6)
    draw_pill(draw, (770, 555, 920, 583), "RETRY SAFE", f_badge, fill="#EFF6FF", text_color="#2563EB", radius=6)

    img.save(output_path, "PNG", quality=95)
    print(f"Generated: {output_path}")

def generate_module4_graphic(output_path):
    W, H = 1200, 675
    img = Image.new("RGB", (W, H), "#F8FAFC")
    draw = ImageDraw.Draw(img)

    for y in range(H):
        ratio = y / H
        r = int(248 * (1 - ratio*0.03))
        g = int(250 * (1 - ratio*0.02))
        b = int(252 * (1 - ratio*0.01))
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Top accent
    draw.rectangle([(0, 0), (W, 8)], fill="#7C3AED")

    f_badge = get_font("segoeuib.ttf", 14, bold=True)
    draw_pill(draw, (60, 35, 340, 67), "MODULE 4: MULTI-AGENT OPS", f_badge, fill="#FAF5FF", text_color="#7C3AED", radius=16)

    f_title = get_font("segoeuib.ttf", 34, bold=True)
    draw.text((60, 80), "End-to-End Multi-Agent Enterprise Operations", font=f_title, fill="#0F172A")
    f_sub = get_font("segoeui.ttf", 18)
    draw.text((60, 125), "State machine supervisor coordinating 9 autonomous agents with cryptographic Stripe verification", font=f_sub, fill="#64748B")

    # 9 Agents Architecture Grid
    agents = [
        ("Intake Agent", "Validates customer intake"),
        ("Lead Intel Agent", "Scores & qualifies leads"),
        ("Support Triage", "Classifies email requests"),
        ("Invoice Agent", "Validates financial docs"),
        ("Contract Agent", "Prepares legal templates"),
        ("Payment Verifier", "HMAC Stripe validator"),
        ("Collab Agent", "Configures Slack channels"),
        ("Reporting Agent", "Prepares executive digest"),
        ("Supervisor", "Enforces state machine")
    ]

    aw, ah = 330, 80
    f_aname = get_font("segoeuib.ttf", 16, bold=True)
    f_arole = get_font("segoeui.ttf", 13)

    for i, (name, role) in enumerate(agents):
        col = i % 3
        row = i // 3
        ax = 60 + col * (aw + 45)
        ay = 175 + row * (ah + 20)
        
        is_sup = (name == "Supervisor")
        bg = "#F5F3FF" if is_sup else "#FFFFFF"
        border = "#7C3AED" if is_sup else "#E2E8F0"
        txt_c = "#6D28D9" if is_sup else "#0F172A"

        draw_rounded_card(draw, (ax, ay, ax + aw, ay + ah), fill=bg, outline=border, radius=12, width=2 if is_sup else 1)
        draw.text((ax + 18, ay + 16), name, font=f_aname, fill=txt_c)
        draw.text((ax + 18, ay + 44), role, font=f_arole, fill="#64748B")

    # Bottom FSM Lifecycle Bar
    draw_rounded_card(draw, (60, 480, W - 60, 620), fill="#FFFFFF", outline="#E2E8F0", radius=14)
    draw.text((85, 500), "Finite State Machine (FSM) Lifecycle", font=get_font("segoeuib.ttf", 16, bold=True), fill="#0F172A")

    states = ["INTAKE_RECEIVED", "QUALIFIED", "CONTRACT_DRAFTED", "PAYMENT_VERIFIED", "COMPLETED"]
    f_st = get_font("segoeuib.ttf", 13, bold=True)

    for i, st in enumerate(states):
        sx = 85 + i * 215
        sy = 540
        draw_rounded_card(draw, (sx, sy, sx + 180, sy + 45), fill="#F8FAFC", outline="#CBD5E1", radius=8)
        draw.text((sx + 14, sy + 13), st, font=f_st, fill="#334155")
        if i < len(states) - 1:
            draw.text((sx + 192, sy + 10), "->", font=get_font("segoeuib.ttf", 18, bold=True), fill="#94A3B8")

    img.save(output_path, "PNG", quality=95)
    print(f"Generated: {output_path}")

if __name__ == "__main__":
    os.makedirs("docs/assets", exist_ok=True)
    generate_linkedin_banner(["image.png", "docs/assets/linkedin_banner.png"])
    generate_module3_graphic("docs/assets/module3_invoice_scanner_light.png")
    generate_module4_graphic("docs/assets/module4_multiagent_light.png")
    print("All light-theme PNG assets successfully generated!")
