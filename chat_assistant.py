"""
Fort Fantastic - Decision Support Chat Assistant
==================================================
A Tkinter chat window that talks to Claude (Anthropic API), lets you attach a
screenshot with one click, and toggles between:

  GOVERNED   — system prompt includes the full validated knowledge base
               pulled live from db/fort_fantastic.db (attractions, activity
               cards, infrastructure), plus input validation before sending.
  UNGOVERNED — no database context, minimal system prompt, no validation;
               Claude answers from general reasoning and fills gaps itself.

Every exchange is logged (mode, message, response, token usage) into an
`interactions` table in the same database, for use as thesis evidence.

Setup:
    pip install anthropic pillow python-dotenv

    .env file next to this script:
        ANTHROPIC_API_KEY=sk-ant-...

    Expects a SQLite db at:  <this folder>/db/fort_fantastic.db
    (same schema as your existing setup_database.py / seed_data.py)

Run:
    python chat_assistant.py
"""

import base64
import io
import os
import sqlite3
import threading
import tkinter as tk
import tkinter.font as tkfont
from datetime import datetime
from pathlib import Path
from tkinter import ttk

from PIL import ImageGrab, ImageTk
from dotenv import load_dotenv

import anthropic

# ── Paths / API key ───────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_PATH = SCRIPT_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

DB_PATH = SCRIPT_DIR / "db" / "fort_fantastic.db"
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024

# ── Design tokens ─────────────────────────────────────────────────────────────
BG_MAIN          = "#181520"
BG_PANEL         = "#211D2C"
BG_INPUT_PILL    = "#2A2536"
BUBBLE_USER      = "#5B4FE0"
BUBBLE_ASSISTANT = "#252134"
ACCENT_GOLD      = "#D9A653"
TEXT_PRIMARY     = "#ECE9F5"
TEXT_ON_USER     = "#FFFFFF"
TEXT_MUTED       = "#8B85A3"
STATUS_OK        = "#4CD787"
STATUS_BAD       = "#E0566B"

BUBBLE_RADIUS = 14
BUBBLE_PAD_X  = 14
BUBBLE_PAD_Y  = 10
BUBBLE_GAP    = 10
SIDE_MARGIN   = 60
MAX_BUBBLE_W  = 420


def pick_font(candidates, fallback="Helvetica"):
    try:
        families = set(tkfont.families())
    except Exception:
        return fallback
    for name in candidates:
        if name in families:
            return name
    return fallback


def rounded_rect_points(x1, y1, x2, y2, r):
    r = max(2, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    return [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]


# ==============================================================================
# GOVERNED KNOWLEDGE BASE — loaded once from the game database
# ==============================================================================

def load_full_context() -> str:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"No database file at {DB_PATH}")

    conn = sqlite3.connect(str(DB_PATH))
    sections = []

    sections.append("""
## FORT FANTASTIC — PARK OVERVIEW

Fort Fantastic is a theme park in Texas, open April–September (180 days/year),
10 hours/day. ~1,000,000 visitors per year. Average revenue per visitor: 16.
Overhead expenses: 3.2M p.a. (increases 2% p.a.). Appeal declines 2% p.a.
Target profit margin: >10%. Investment budget = 40-60% of retained round profit.

### Visitor Calculation — THREE equally weighted factors (33% each):
  1. Current Appeal     = sum of attraction appeal values × their availability
  2. Total Availability = sum of attraction availability percentages
  3. Customer Satisfaction = current + 100-day weighted average

### Operational Condition (OpCon)
  GREEN=100% | YELLOW=75%(penalty 20k) | ORANGE=50%(penalty 40k) | RED=0%(penalty 70k)

### System Charges (target = ZERO)
  Wrong solution code: 15,000 | Buy Solution: 75,000
  Cause Analysis (inconclusive): 15,000 | Cause Analysis (repeated): 50,000

### Activity Card EI Scale: -10 to +10 (each point ≈ 10,000 profit impact)
  Cards financed from CURRENT EARNINGS only. Cannot buy cards at a loss.

### Infrastructure Risk (PDS/STM): node utilization < 75% = zero risk
  Synergy savings: 2 attractions=5%, 3=12%, 4=21%, 5+=32% cost reduction
""")

    rows = conn.execute("""
        SELECT name, is_base, category, appeal,
               fixed_costs_per_day, variable_costs_per_user,
               capacity_per_day, utilization_pct, utilization_abs,
               overall_costs_day, sales_breakdown_day, gross_profit_day,
               acquisition_cost, pds_capacity, pds_norm, stm_capacity, stm_norm
        FROM attractions ORDER BY is_base DESC, gross_profit_day DESC
    """).fetchall()

    base_lines, extra_lines = [], []
    hdr = (f"  {'Name':<26}{'Cat':<12}{'Appeal':>7}{'FixCost/d':>10}{'VarCst/u':>9}"
           f"{'Cap/d':>7}{'Util%':>6}{'TotCost/d':>10}{'Sales/d':>9}{'GrossProfit/d':>14}{'PDS':>8}{'STM':>7}")
    for r in rows:
        name, is_base, cat, appeal, fixed, var_c, cap, util_pct, util_abs, tot, sales, gp, acq, pds_c, pds_n, stm_c, stm_n = r
        line = (f"  {name:<26}{cat:<12}{appeal:>7.1f}{fixed:>10,.0f}{var_c:>9.2f}"
                f"{cap:>7,.0f}{util_pct:>5.0f}%{tot:>10,.0f}{sales:>9,.0f}{gp:>14,.0f}"
                f"{str(pds_c) + '(' + pds_n + ')':>8}{str(stm_c) + '(' + stm_n + ')':>7}")
        (base_lines if is_base else extra_lines).append(line)

    sections.append(f"## ATTRACTION MASTER DATA\n### Base Attractions\n{hdr}\n" +
                     "\n".join(base_lines) +
                     f"\n\n### Additional Attractions (purchasable)\n{hdr}\n" +
                     "\n".join(extra_lines))

    cats = conn.execute("SELECT DISTINCT category FROM activity_cards ORDER BY category").fetchall()
    card_text = ["\n## ACTIVITY CARDS"]
    for (cat,) in cats:
        cards = conn.execute("""
            SELECT id, title, order_code_std, order_code_3p, order_code_4r,
                   delivery_days, implementation_days, runtime_days,
                   price, uses, attraction, attractions_multi,
                   infrastructure_module, component,
                   effect_visitors_min_pct, effect_visitors_max_pct,
                   effect_appeal, effect_fixed_costs, effect_variable_costs,
                   effect_capacity, effect_utilization_pct,
                   effect_general_expense_min, effect_general_expense_max
            FROM activity_cards WHERE category=? ORDER BY id
        """, (cat,)).fetchall()
        card_text.append(f"\n### {cat}")
        for c in cards:
            (cid, title, std, p3, p4r, deliv, impl, runtime, price, uses, attr, multi,
             infra, comp, vm, vx, ae, fe, ve, ce, ue, gm, gx) = c
            codes = " / ".join(filter(None, [std, p3, p4r]))
            timing = ", ".join(filter(None, [
                f"delivery:{deliv}d" if deliv else None,
                f"impl:{impl}d" if impl else None,
                f"runtime:{runtime}d" if runtime else None])) or "immediate"
            scope = " | ".join(filter(None, [attr, multi, f"[{infra}]" if infra else None,
                                              f"→{comp}" if comp else None])) or "Park-wide"
            efx = []
            if vm is not None:
                efx.append(f"visitors {vm:+.1f}%~{vx:+.1f}%" if vm != vx else f"visitors {vm:+.1f}%")
            if ae: efx.append(f"appeal {ae:+.1f}")
            if fe: efx.append(f"fixed {fe:+,.0f}/d")
            if ve: efx.append(f"var {ve:+.2f}/u")
            if ce: efx.append(f"cap {ce:+,.0f}")
            if ue: efx.append(f"util {ue:+.0f}%")
            if gm: efx.append(f"overhead {gm:+.1f}%~{gx:+.1f}%" if gm != gx else f"overhead {gm:+.1f}%")
            price_s = f"{price:,.0f}" if price else "0"
            card_text.append(f"  #{cid:>3}[{codes:<14}] {title:<48} €{price_s:>8} uses:{uses:<10} {timing}\n"
                              f"       Scope:{scope} | Effects:{' | '.join(efx) or 'operational fix'}")
    sections.append("\n".join(card_text))

    domains = conn.execute("""
        SELECT d.abbreviation, d.full_name, d.is_reconfigurable,
               GROUP_CONCAT(n.node_id || COALESCE('('||n.norm||')',''), ', ')
        FROM infrastructure_domains d
        LEFT JOIN infrastructure_nodes n ON n.domain_id=d.id
        GROUP BY d.id ORDER BY d.is_reconfigurable DESC, d.abbreviation
    """).fetchall()
    d_lines = [f"  {a} ({fn}): {'RECONFIGURABLE' if r else 'auto'} | Nodes: {nd}" for a, fn, r, nd in domains]
    sections.append("## INFRASTRUCTURE\n" + "\n".join(d_lines) +
                     "\n\nUpgrade format: [Module]-[Norm]-[NodeID]-[Type] e.g. PDS-EU52-Y1-A\n"
                     "PDS EU52/US68: A=+50cap(80k,30d) B=+20cap(60k,10d) C=+30cap(50k,60d)\n"
                     "STM U/G/Q:     A=+30cap(70k,30d) B=+10cap(50k,10d) C=+15cap(40k,60d)")

    conn.close()
    return "\n\n".join(sections)


PERSONALITY_AND_RULES = """YOUR ROLE:
- Keep responses under 250 words. Use brief bullet points, not full paragraphs.
- You are a decision-support advisor, not an autopilot: your job is to help the player make
  a better-informed decision themselves, not to make the decision for them.
- When a real decision is open (which activity card, whether to upgrade infrastructure,
  whether to invest), present 2-3 concrete, ranked options with their trade-offs (cost,
  timing, risk, expected effect) rather than a single directive instruction. Let the player
  choose.
- Each option must still be concrete and specific: name real card numbers, order codes, and
  costs where relevant, so the player can act on whichever option they pick.
- Only give a single, undebatable recommendation when the game's stated rules make one option
  strictly dominant (e.g. only one option is affordable, or a rule eliminates the alternatives).
- Explain the reasoning behind each option in terms of the game's KPIs, not just the conclusion.
- Adapt to the player's skill level (explain basics to beginners, move faster for experts), but
  always preserve the options-based framing.
- Flag urgencies clearly (RED/ORANGE attractions need attention this round), framed as "here
  are your options given the urgency," not "do this."

WHEN ANALYZING A SCREENSHOT:
- Identify the current day and round
- Note the OpCon (color dots) for each visible attraction
- Read customer satisfaction value and smiley
- Note the message box contents (incidents, notifications)
- Read the purchase panel (cards in progress, their EI and costs)
- Read the profit chart trend
- Then present options based on what you observe

WHEN PRESENTING ACTIVITY CARD OPTIONS, for each option include:
  Card number | Order code | Price | Effect | Timing (implementation days = downtime) | Trade-off

IMPORTANT GAME RULES TO ALWAYS ENFORCE:
- Cannot buy activity cards when operating at a loss
- Activity cards financed from current earnings, NOT investment budget
- New attractions financed from investment budget (retained profits)
- Wrong solution codes cost 15,000 penalty each
- Flag when an attraction is at risk of staying RED/ORANGE without intervention, but leave the
  final call to the player"""

UNGOVERNED_SYSTEM_PROMPT = """You are a decision support assistant for someone playing Fort
Fantastic, a business simulation game where the player manages an amusement park. Keep 
responses under 250 words using brief bullet points. You have NO
access to the game's internal database, exact figures, card catalog, or rules engine — work
only from whatever the player tells you or shows you in a screenshot, plus your own general
knowledge of business simulations. Your job is to help the player make a better-informed
decision themselves, not to make the decision for them: present 2-3 concrete, ranked options
with their trade-offs rather than a single directive instruction, unless one option is clearly
and obviously dominant. Give your best practical options even if specific numbers, costs, or
rules are missing or unclear; fill gaps with reasonable assumptions rather than asking for more
information, and note where you are assuming rather than certain."""

try:
    DB_CONTEXT = load_full_context()
    DB_LOAD_ERROR = None
    GOVERNED_SYSTEM_PROMPT = f"""You are the AI Decision Support Advisor for Fort Fantastic theme park management simulation.

You have COMPLETE knowledge of all game mechanics, attractions, activity cards, and infrastructure,
provided below as a governed knowledge base extracted directly from the live game database.

{PERSONALITY_AND_RULES}

DATA GOVERNANCE NOTICE: the knowledge base below has been extracted directly from validated
database tables. If the player's question or screenshot conflicts with this data, or if
information needed to answer is missing from both, say so explicitly rather than guessing.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPLETE FORT FANTASTIC KNOWLEDGE BASE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{DB_CONTEXT}
"""
except Exception as e:
    DB_CONTEXT = None
    DB_LOAD_ERROR = str(e)
    GOVERNED_SYSTEM_PROMPT = None


# ── Interaction log (raw evidence for the thesis Results chapter) ───────────
def ensure_log_table():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            mode TEXT NOT NULL,
            user_text TEXT,
            image_attached INTEGER NOT NULL,
            response_text TEXT,
            input_tokens INTEGER,
            output_tokens INTEGER
        )
    """)
    conn.commit()
    conn.close()


def log_interaction(governed, user_text, image_attached, response_text, input_tokens, output_tokens):
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute(
            "INSERT INTO interactions "
            "(timestamp, mode, user_text, image_attached, response_text, input_tokens, output_tokens) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                datetime.utcnow().isoformat(),
                "governed" if governed else "ungoverned",
                user_text,
                int(image_attached),
                response_text,
                input_tokens,
                output_tokens,
            ),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass  # logging failures shouldn't crash the chat


# ==============================================================================
# UI
# ==============================================================================

class ChatAssistant:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Fort Fantastic — Decision Support")
        self.root.geometry("700x820")
        self.root.minsize(560, 580)
        self.root.configure(bg=BG_MAIN)

        self.font_display = (pick_font(["Segoe UI Semibold", "Helvetica Neue", "Helvetica"]), 15, "bold")
        self.font_eyebrow  = (pick_font(["Segoe UI", "Helvetica Neue", "Helvetica"]), 9, "bold")
        self.font_body     = (pick_font(["Segoe UI", "Helvetica Neue", "Helvetica"]), 11)
        self.font_mono     = (pick_font(["Cascadia Mono", "Consolas", "Menlo", "Courier New"]), 9, "bold")

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None

        self.governed = True  # default mode; toggled via the header badge

        self.messages: list[dict] = []
        self.pending_image_b64: str | None = None
        self.pending_thumb_tk = None
        self.typing_ids: list[int] = []
        self._typing_y_before = None
        self._msg_y = BUBBLE_GAP
        self._waiting = False

        self._build_header()
        self._build_chat_area()
        self._build_thumb_strip()
        self._build_input_bar()

        self.root.after(60, self._draw_input_bar)
        self.root.after(80, self._init_status_messages)
        ensure_log_table()

    # ── Header ────────────────────────────────────────────────────────────────
    def _build_header(self):
        header = tk.Frame(self.root, bg=BG_PANEL, height=66)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)

        text_frame = tk.Frame(header, bg=BG_PANEL)
        text_frame.pack(side=tk.LEFT, padx=18, pady=10)
        tk.Label(text_frame, text="DECISION SUPPORT", font=self.font_eyebrow,
                 fg=ACCENT_GOLD, bg=BG_PANEL).pack(anchor="w")
        tk.Label(text_frame, text="Fort Fantastic Assistant", font=self.font_display,
                 fg=TEXT_PRIMARY, bg=BG_PANEL).pack(anchor="w")

        status_frame = tk.Frame(header, bg=BG_PANEL)
        status_frame.pack(side=tk.RIGHT, padx=(6, 18))
        self.status_canvas = tk.Canvas(status_frame, width=10, height=10, bg=BG_PANEL,
                                        highlightthickness=0)
        self.status_canvas.pack(side=tk.LEFT, padx=(0, 6))
        color = STATUS_OK if self.client else STATUS_BAD
        self.status_canvas.create_oval(1, 1, 9, 9, fill=color, outline="")
        tk.Label(status_frame, text=("connected" if self.client else "no API key"),
                 font=self.font_mono, fg=TEXT_MUTED, bg=BG_PANEL).pack(side=tk.LEFT)

        mode_frame = tk.Frame(header, bg=BG_PANEL)
        mode_frame.pack(side=tk.RIGHT, padx=6)
        self.mode_canvas = tk.Canvas(mode_frame, width=120, height=28, bg=BG_PANEL,
                                      highlightthickness=0)
        self.mode_canvas.pack()
        self.mode_canvas.bind("<Button-1>", self._toggle_mode)
        self.mode_canvas.bind("<Enter>", lambda e: self.mode_canvas.config(cursor="hand2"))
        self.mode_canvas.bind("<Leave>", lambda e: self.mode_canvas.config(cursor=""))
        self._draw_mode_badge()

        reset_frame = tk.Frame(header, bg=BG_PANEL)
        reset_frame.pack(side=tk.RIGHT, padx=6)
        self.reset_canvas = tk.Canvas(reset_frame, width=28, height=28, bg=BG_PANEL,
                                       highlightthickness=0)
        self.reset_canvas.pack()
        self.reset_canvas.create_oval(1, 1, 27, 27, outline=TEXT_MUTED, width=1.4)
        self.reset_canvas.create_text(14, 14, text="\u21bb", font=(self.font_body[0], 13), fill=TEXT_MUTED)
        self.reset_canvas.bind("<Button-1>", lambda e: self._reset_conversation())
        self.reset_canvas.bind("<Enter>", lambda e: self.reset_canvas.config(cursor="hand2"))
        self.reset_canvas.bind("<Leave>", lambda e: self.reset_canvas.config(cursor=""))

    def _draw_mode_badge(self):
        c = self.mode_canvas
        c.delete("all")
        w, h = 120, 28
        if self.governed:
            fill, fg, label = ACCENT_GOLD, BG_MAIN, "GOVERNED"
        else:
            fill, fg, label = BG_INPUT_PILL, TEXT_MUTED, "UNGOVERNED"
        c.create_polygon(rounded_rect_points(0, 0, w, h, h / 2), smooth=True, fill=fill, outline="")
        c.create_text(w / 2, h / 2, text=label, font=self.font_mono, fill=fg)

    def _toggle_mode(self, event=None):
        self.governed = not self.governed
        self._draw_mode_badge()

    def _reset_conversation(self):
        self.messages = []
        self._clear_pending_image()
        self.canvas.delete("all")
        self._msg_y = BUBBLE_GAP
        self._append_system(
            "New conversation started — context cleared. The next message starts with no "
            "prior history in either mode."
        )

    # ── Chat area ─────────────────────────────────────────────────────────────
    def _build_chat_area(self):
        wrap = tk.Frame(self.root, bg=BG_MAIN)
        wrap.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(wrap, bg=BG_MAIN, highlightthickness=0)
        scrollbar = ttk.Scrollbar(wrap, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(14, 0), pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 6))

        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-e.delta / 40), "units"))
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-3, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(3, "units"))

    def _on_canvas_resize(self, event):
        self.canvas.configure(scrollregion=(0, 0, event.width, max(self._msg_y, event.height)))

    def _init_status_messages(self):
        if not self.client:
            found = ENV_PATH.exists()
            self._append_system(
                f"No ANTHROPIC_API_KEY found. Looked for .env at: {ENV_PATH} "
                f"(file {'exists' if found else 'does NOT exist at that path'})."
            )
        if DB_LOAD_ERROR:
            self._append_system(
                f"Governed mode's knowledge base failed to load ({DB_LOAD_ERROR}). "
                f"Looked for the database at: {DB_PATH}. Ungoverned mode still works; "
                "fix the path or run your setup/seed scripts to enable governed mode."
            )
        if self.client and not DB_LOAD_ERROR:
            self._append_system(
                "Ready. Click the GOVERNED / UNGOVERNED badge top-right to switch modes. "
                "Type a message, or click the camera icon to attach a screenshot first."
            )

    # ── Bubble rendering ─────────────────────────────────────────────────────
    def _add_bubble(self, text, kind, tag=None):
        canvas_w = self.canvas.winfo_width() or 640

        if tag:
            tag_color = ACCENT_GOLD if tag == "GOVERNED" else TEXT_MUTED
            tag_id = self.canvas.create_text(
                canvas_w - SIDE_MARGIN / 3, self._msg_y, text=tag,
                font=self.font_mono, fill=tag_color, anchor="ne",
            )
            tag_bbox = self.canvas.bbox(tag_id)
            self._msg_y += (tag_bbox[3] - tag_bbox[1]) + 4

        if kind == "system":
            font, fg = self.font_mono, TEXT_MUTED
            wrap_w = min(360, int(canvas_w * 0.6))
        else:
            font = self.font_body
            fg = TEXT_ON_USER if kind == "user" else TEXT_PRIMARY
            wrap_w = max(120, min(MAX_BUBBLE_W, int(canvas_w * 0.66)))

        tmp = self.canvas.create_text(0, 0, text=text, font=font, width=wrap_w, anchor="nw")
        bbox = self.canvas.bbox(tmp)
        self.canvas.delete(tmp)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

        extra_left = 8 if kind == "assistant" else 0
        bubble_w = text_w + BUBBLE_PAD_X * 2 + extra_left
        bubble_h = text_h + BUBBLE_PAD_Y * 2

        if kind == "user":
            x2 = canvas_w - SIDE_MARGIN / 3
            x1 = x2 - bubble_w
        elif kind == "assistant":
            x1 = SIDE_MARGIN / 3
            x2 = x1 + bubble_w
        else:
            x1 = (canvas_w - bubble_w) / 2
            x2 = x1 + bubble_w

        y1 = self._msg_y
        y2 = y1 + bubble_h

        ids = []
        fill = {"user": BUBBLE_USER, "assistant": BUBBLE_ASSISTANT, "system": BG_PANEL}[kind]
        radius = bubble_h / 2 if kind == "system" else BUBBLE_RADIUS
        pts = rounded_rect_points(x1, y1, x2, y2, radius)
        ids.append(self.canvas.create_polygon(pts, smooth=True, fill=fill, outline=""))

        if kind == "assistant":
            ids.append(self.canvas.create_rectangle(x1 + 4, y1 + 4, x1 + 8, y2 - 4,
                                                      fill=ACCENT_GOLD, outline=""))

        ids.append(self.canvas.create_text(x1 + BUBBLE_PAD_X + extra_left, y1 + BUBBLE_PAD_Y,
                                            text=text, font=font, width=wrap_w,
                                            anchor="nw", fill=fg))

        self._msg_y = y2 + BUBBLE_GAP
        self.canvas.configure(scrollregion=(0, 0, canvas_w, self._msg_y))
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
        return ids

    def _append_user(self, text, tag=None):
        self._add_bubble(text, "user", tag=tag)

    def _append_assistant(self, text):
        self._add_bubble(text, "assistant")

    def _append_system(self, text):
        self._add_bubble(text, "system")

    def _show_typing(self):
        self._typing_y_before = self._msg_y
        self.typing_ids = self._add_bubble("· · ·", "assistant")

    def _hide_typing(self):
        if self.typing_ids:
            self.canvas.delete(*self.typing_ids)
            self.typing_ids = []
            if self._typing_y_before is not None:
                self._msg_y = self._typing_y_before

    # ── Thumbnail strip ──────────────────────────────────────────────────────
    def _build_thumb_strip(self):
        self.thumb_frame = tk.Frame(self.root, bg=BG_MAIN)
        self.thumb_frame.pack(side=tk.TOP, fill=tk.X, padx=18)

    def _show_thumb(self, thumb_img):
        self.pending_thumb_tk = ImageTk.PhotoImage(thumb_img)
        if hasattr(self, "thumb_canvas"):
            self.thumb_canvas.destroy()

        w, h = thumb_img.width + 46, thumb_img.height + 16
        self.thumb_canvas = tk.Canvas(self.thumb_frame, width=w, height=h,
                                       bg=BG_MAIN, highlightthickness=0)
        self.thumb_canvas.pack(anchor="w", pady=(0, 8))
        pts = rounded_rect_points(0, 0, w, h, 10)
        self.thumb_canvas.create_polygon(pts, smooth=True, fill=BG_PANEL, outline="")
        self.thumb_canvas.create_image(8, 8, image=self.pending_thumb_tk, anchor="nw")
        close_id = self.thumb_canvas.create_text(w - 18, h / 2, text="✕",
                                                    font=self.font_body, fill=TEXT_MUTED)
        self.thumb_canvas.tag_bind(close_id, "<Button-1>", lambda e: self._clear_pending_image())
        self.thumb_canvas.tag_bind(close_id, "<Enter>", lambda e: self.thumb_canvas.config(cursor="hand2"))
        self.thumb_canvas.tag_bind(close_id, "<Leave>", lambda e: self.thumb_canvas.config(cursor=""))

    def _clear_pending_image(self):
        self.pending_image_b64 = None
        if hasattr(self, "thumb_canvas"):
            self.thumb_canvas.destroy()
            del self.thumb_canvas

    # ── Input bar ─────────────────────────────────────────────────────────────
    def _build_input_bar(self):
        bar = tk.Frame(self.root, bg=BG_MAIN)
        bar.pack(side=tk.BOTTOM, fill=tk.X, padx=18, pady=16)
        self.input_canvas = tk.Canvas(bar, height=50, bg=BG_MAIN, highlightthickness=0)
        self.input_canvas.pack(fill=tk.X)
        self.input_canvas.bind("<Configure>", self._draw_input_bar)

    def _draw_input_bar(self, event=None):
        c = self.input_canvas
        c.delete("all")
        w = c.winfo_width() or 600
        h = c.winfo_height() or 50
        btn_d, gap = 38, 8
        pill_x1, pill_x2 = btn_d + gap, w - btn_d - gap
        pill_y1, pill_y2 = (h - 40) / 2, (h - 40) / 2 + 40

        cx, cy = btn_d / 2, h / 2
        cam_id = c.create_oval(cx - btn_d / 2, cy - btn_d / 2, cx + btn_d / 2, cy + btn_d / 2,
                                fill=BG_PANEL, outline="")
        c.create_rectangle(cx - 8, cy - 5, cx + 8, cy + 6, outline=TEXT_PRIMARY, width=1.4)
        c.create_rectangle(cx - 3, cy - 8, cx + 3, cy - 5, outline=TEXT_PRIMARY, width=1.4)
        c.create_oval(cx - 4, cy - 3, cx + 4, cy + 5, outline=TEXT_PRIMARY, width=1.4)
        c.tag_bind(cam_id, "<Button-1>", lambda e: self.capture_screenshot())
        c.tag_bind(cam_id, "<Enter>", lambda e: c.config(cursor="hand2"))
        c.tag_bind(cam_id, "<Leave>", lambda e: c.config(cursor=""))

        c.create_polygon(rounded_rect_points(pill_x1, pill_y1, pill_x2, pill_y2, 20),
                          smooth=True, fill=BG_INPUT_PILL, outline="")
        if not hasattr(self, "entry"):
            self.entry = tk.Entry(c, font=self.font_body, fg=TEXT_PRIMARY, bg=BG_INPUT_PILL,
                                   insertbackground=TEXT_PRIMARY, relief="flat",
                                   highlightthickness=0, bd=0)
            self.entry.bind("<Return>", lambda e: self.send_message())
            self.entry.focus_set()
        c.create_window((pill_x1 + pill_x2) / 2, (pill_y1 + pill_y2) / 2, window=self.entry,
                         width=max(40, pill_x2 - pill_x1 - 24), height=28)

        sx, sy = w - btn_d / 2, h / 2
        send_id = c.create_oval(sx - btn_d / 2, sy - btn_d / 2, sx + btn_d / 2, sy + btn_d / 2,
                                 fill=ACCENT_GOLD, outline="")
        c.create_polygon([sx - 6, sy - 6, sx + 7, sy, sx - 6, sy + 6, sx - 2, sy],
                          fill=BG_MAIN, outline="")
        c.tag_bind(send_id, "<Button-1>", lambda e: self.send_message())
        c.tag_bind(send_id, "<Enter>", lambda e: c.config(cursor="hand2"))
        c.tag_bind(send_id, "<Leave>", lambda e: c.config(cursor=""))

    # ── Screenshot capture ───────────────────────────────────────────────────
    def capture_screenshot(self):
        self.root.withdraw()
        self.root.after(350, self._do_capture)

    def _do_capture(self):
        try:
            img = ImageGrab.grab()
        except Exception as e:
            self.root.deiconify()
            self._append_system(f"Screenshot failed: {e}")
            return

        self.root.deiconify()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        self.pending_image_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        thumb = img.copy()
        thumb.thumbnail((160, 100))
        self._show_thumb(thumb)
        self._append_system(f"Screenshot captured at {datetime.now().strftime('%H:%M:%S')} "
                             "— it will be sent with your next message.")

    # ── Sending messages ─────────────────────────────────────────────────────
    def send_message(self):
        if self._waiting:
            return

        text = self.entry.get().strip()
        has_image = bool(self.pending_image_b64)
        if not text and not has_image:
            return

        governed_now = self.governed  # capture mode at send time

        if governed_now:
            if GOVERNED_SYSTEM_PROMPT is None:
                self._append_system(
                    "Governed mode is unavailable (knowledge base failed to load). "
                    "Switch to UNGOVERNED or fix the database path, then try again."
                )
                return
            if has_image and not text:
                self._append_system(
                    "Governed mode requires a short question or description alongside "
                    "a screenshot — type something before sending."
                )
                return
            if not has_image and len(text) < 3:
                self._append_system("Governed mode requires a non-trivial message.")
                return

        self.entry.delete(0, tk.END)
        self._append_user(text if text else "[Screenshot attached]",
                           tag="GOVERNED" if governed_now else "UNGOVERNED")

        content = []
        if self.pending_image_b64:
            content.append({
                "type": "image",
                "source": {"type": "base64", "media_type": "image/png", "data": self.pending_image_b64},
            })
        if text:
            content.append({"type": "text", "text": text})

        self.messages.append({"role": "user", "content": content})
        self._clear_pending_image()

        self._waiting = True
        self._show_typing()
        threading.Thread(target=self._call_api, args=(governed_now, text, has_image), daemon=True).start()

    def _call_api(self, governed_now, user_text, had_image):
        if not self.client:
            self.root.after(0, self._hide_typing)
            self.root.after(0, lambda: self._append_system(
                "No API key configured. Set ANTHROPIC_API_KEY in .env and restart."))
            self.root.after(0, self._unblock)
            return

        system_prompt = GOVERNED_SYSTEM_PROMPT if governed_now else UNGOVERNED_SYSTEM_PROMPT
        try:
            response = self.client.messages.create(
                model=MODEL, max_tokens=MAX_TOKENS, system=system_prompt, messages=self.messages,
            )
            reply = "".join(b.text for b in response.content if b.type == "text")
            self.messages.append({"role": "assistant", "content": reply})
            log_interaction(governed_now, user_text, had_image, reply,
                             response.usage.input_tokens, response.usage.output_tokens)
            self.root.after(0, self._hide_typing)
            self.root.after(0, lambda: self._append_assistant(reply))
        except Exception as e:
            self.root.after(0, self._hide_typing)
            self.root.after(0, lambda: self._append_system(f"API error: {e}"))
        finally:
            self.root.after(0, self._unblock)

    def _unblock(self):
        self._waiting = False


if __name__ == "__main__":
    root = tk.Tk()
    ChatAssistant(root)
    root.mainloop()