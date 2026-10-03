#!/usr/bin/env python3
"""
narrator/generate_narrative.py
Part 3 — Gemini SCR narrative with offline fallback + Task 5 checker.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINDINGS_PATH = ROOT / "narrator" / "findings.json"
SAMPLE_OUT = ROOT / "narrator" / "sample_output.txt"

REQUIRED = [
    ("cleaned total revenue", ["97358.30", "97358.3", "97,358.30", "97,358.3"]),
    ("COD return rate", ["44.4"]),
    ("COD + Tier-2 return rate", ["54.5"]),
    ("duplicate reconciliation delta", ["2501.90", "2501.9", "2,501.90", "2,501.9"]),
    ("peak month March revenue", ["20318.90", "20318.9", "20,318.90", "20,318.9"]),
]


def load_findings() -> dict:
    if not FINDINGS_PATH.exists():
        raise SystemExit(f"Missing {FINDINGS_PATH}. Run analysis/clean_and_eda.py first.")
    return json.loads(FINDINGS_PATH.read_text(encoding="utf-8"))


def generate_scr_narrative_offline(findings: dict) -> dict:
    """Keyless, deterministic SCR template — same return shape as the online path."""
    rev = findings["cleaned_total_revenue_inr"]
    raw = findings["raw_total_revenue_inr"]
    delta = findings["duplicate_reconciliation_delta_inr"]
    rates = findings["return_rate_by_payment"]
    risk = findings["highest_risk_segment"]
    peak = findings["true_peak_month"]
    jan = findings["outlier_inflated_month"]

    narrative = f"""Situation
Mamaearth's Growth Analytics team processed 180 raw order lines through a relational store and a cleaned pandas pipeline. Gross revenue on the raw extract is ₹{raw:,.2f}. After removing five double-submit duplicates, cleaned total revenue is ₹{rev:,.2f} (reconciliation delta ₹{delta:,.2f}).

Complication
Returns are not uniform. COD posts a return rate of {rates['COD']}%, versus CARD at {rates['CARD']}% and UPI at {rates['UPI']}%. The risk concentrates further: the COD + Tier-2 segment reaches {risk['return_rate_pct']}% return rate — the single highest-risk slice. January appeared to lead monthly revenue at ₹{jan['apparent_revenue_inr']:,.2f}, but that was an artifact of two bulk quantity outliers; the true peak month is March at ₹{peak['revenue_inr']:,.2f}.

Resolution
1. Restrict or partially prepay COD in Tier-2 cities where the {risk['return_rate_pct']}% return rate is concentrated.
2. Block double-submit at checkout (customer + product + date) to eliminate the ₹{delta:,.2f} reconciliation gap.
3. Investigate the two quantity outliers (25 and 30 units) before trusting January trend reads.
4. Protect March inventory and marketing around the verified ₹{peak['revenue_inr']:,.2f} peak.
"""
    return {"status": "success", "narrative": narrative.strip(), "tokens": None}


def generate_scr_narrative(findings: dict) -> dict:
    """
    Online path via google-genai.
    temperature=0.0 — factual business report, not creative writing.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip() or os.environ.get("GOOGLE_API_KEY", "").strip()
    if not api_key:
        return {
            "status": "error",
            "narrative": None,
            "message": "No GEMINI_API_KEY / GOOGLE_API_KEY configured",
        }

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        system_instruction = (
            "You are a senior data analyst writing for Mamaearth's regional ops and finance heads. "
            "Respond with exactly three labeled sections: Situation, Complication, Resolution. "
            "Every number in the output must come from the supplied findings and appear with the same value — no invented statistics."
        )
        user_prompt = (
            "Write the SCR narrative from these verified findings only:\n"
            + json.dumps(findings, indent=2)
        )
        # temperature=0.0 for determinism; max_output_tokens explicit; timeout via request options
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0,
                max_output_tokens=512,
                http_options=types.HttpOptions(timeout=30000),  # 30s >= 10s minimum
            ),
        )
        text = (response.text or "").strip()
        if not text:
            return {"status": "error", "narrative": None, "message": "Empty Gemini response"}
        tokens = None
        try:
            tokens = response.usage_metadata.total_token_count  # type: ignore[attr-defined]
        except Exception:
            pass
        return {"status": "success", "narrative": text, "tokens": tokens}
    except Exception as err:  # noqa: BLE001
        return {"status": "error", "narrative": None, "message": str(err)}


def check_narrative(text: str) -> bool:
    """Task 5 — numeric accuracy checklist."""
    norm = text.replace(",", "")
    all_ok = True
    print("=== Task 5 numeric accuracy checklist ===")
    for label, variants in REQUIRED:
        ok = any(v.replace(",", "") in norm for v in variants)
        if label.startswith("peak month"):
            ok = ok and ("March" in text or "march" in text.lower())
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_ok = False
        print(f"  {status}: {label} (need one of {variants})")
    print("=== overall:", "PASS" if all_ok else "FAIL", "===")
    return all_ok


def main() -> None:
    findings = load_findings()

    result = generate_scr_narrative(findings)
    if result["status"] != "success":
        print(f"[info] Online path unavailable ({result.get('message')}); using offline fallback.")
        result = generate_scr_narrative_offline(findings)
    else:
        print("[info] Online Gemini path succeeded.")

    narrative = result["narrative"]
    print("\n----- narrative -----\n")
    print(narrative)
    print("\n----- end -----\n")

    SAMPLE_OUT.write_text(narrative, encoding="utf-8")
    print(f"Wrote {SAMPLE_OUT}")

    ok = check_narrative(narrative)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
