"""
Fort Fantastic - Interaction Log Analyzer
===========================================
Reads the `interactions` table populated by chat_assistant.py, pairs governed/ungoverned
exchanges that used identical situation text, and auto-flags the presence of card numbers,
order codes, and monetary figures in each response, as a concrete supplement to the
qualitative specificity/consistency/actionability review described in Methodology 3.3.

This does NOT replace manual reading of the transcripts - it gives you simple counts to
cite alongside your own qualitative judgment.

Usage:
    python analyze_interactions.py
    python analyze_interactions.py --csv results.csv     # also export a CSV
"""

import argparse
import re
import sqlite3
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DB_PATH = SCRIPT_DIR / "db" / "fort_fantastic.db"

# ── Detection patterns ────────────────────────────────────────────────────────
CARD_NUM_RE = re.compile(r"#\s?\d{1,4}\b|\bcard\s*#?\s?\d{1,4}\b", re.IGNORECASE)
ORDER_CODE_RE = re.compile(
    r"\b(?:STD|3P|4R)-\d+\b"                          # activity card order codes
    r"|\b(?:PDS|STM)-[A-Z0-9]+-[A-Za-z0-9]+-[ABC]\b",  # infrastructure upgrade codes
)
MONEY_RE = re.compile(r"[\$\u20ac]\s?\d{1,3}(?:,\d{3})*(?:\.\d+)?|\b\d{1,3}(?:,\d{3})+\b")


def extract_counts(text: str) -> dict:
    text = text or ""
    return {
        "card_numbers": len(set(CARD_NUM_RE.findall(text))),
        "order_codes": len(set(ORDER_CODE_RE.findall(text))),
        "monetary_figures": len(set(MONEY_RE.findall(text))),
        "word_count": len(text.split()),
    }


def fetch_interactions():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"No database found at {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT id, timestamp, mode, user_text, image_attached, response_text, "
        "input_tokens, output_tokens FROM interactions ORDER BY timestamp ASC"
    ).fetchall()
    conn.close()
    return rows


def pair_by_situation(rows):
    """Group rows by exact user_text match, since the protocol sends identical
    wording to both modes. Returns dict: situation_text -> {'governed': row, 'ungoverned': row}"""
    pairs = {}
    for row in rows:
        _id, ts, mode, user_text, img, resp, in_tok, out_tok = row
        key = (user_text or "").strip()
        pairs.setdefault(key, {})
        # last write wins if a situation text was reused; flag duplicates separately
        pairs[key].setdefault(mode, []).append(row)
    return pairs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", help="Optional path to also write a CSV summary")
    args = parser.parse_args()

    rows = fetch_interactions()
    if not rows:
        print("No interactions logged yet. Run some governed/ungoverned sessions first.")
        return

    pairs = pair_by_situation(rows)
    summary_lines = []
    csv_rows = [("situation", "mode", "card_numbers", "order_codes",
                 "monetary_figures", "word_count", "input_tokens", "output_tokens",
                 "response_text")]

    print(f"Loaded {len(rows)} logged interactions across {len(pairs)} distinct situation texts.\n")
    print("=" * 100)

    for situation, modes in pairs.items():
        short_situation = (situation[:90] + "...") if len(situation) > 90 else situation
        print(f"\nSITUATION: {short_situation}")

        if "governed" not in modes or "ungoverned" not in modes:
            missing = "ungoverned" if "governed" in modes else "governed"
            print(f"  [INCOMPLETE PAIR - missing {missing} response, skipping comparison]")
            continue

        for mode in ("governed", "ungoverned"):
            for row in modes[mode]:
                _id, ts, _mode, user_text, img, resp, in_tok, out_tok = row
                counts = extract_counts(resp)
                print(f"  [{mode.upper():10s}] cards={counts['card_numbers']} "
                      f"order_codes={counts['order_codes']} "
                      f"money_figs={counts['monetary_figures']} "
                      f"words={counts['word_count']} "
                      f"tokens(in/out)={in_tok}/{out_tok}")
                csv_rows.append((situation, mode, counts["card_numbers"], counts["order_codes"],
                                  counts["monetary_figures"], counts["word_count"], in_tok, out_tok,
                                  resp or ""))

    print("\n" + "=" * 100)
    print("Reminder: these are simple presence counts, not a judgment of quality. Use them as a")
    print("concrete reference point alongside your own manual reading of the response_text.")

    if args.csv:
        import csv as csv_module
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            writer = csv_module.writer(f)
            writer.writerows(csv_rows)
        print(f"\nCSV summary written to {args.csv}")


if __name__ == "__main__":
    main()