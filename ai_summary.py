import os

import pandas as pd
from openai import OpenAI

REPORT_INSTRUCTIONS = """You are a Senior Marketing Strategy Consultant specializing in FMCG digital campaigns.

Write a concise EXECUTIVE SUMMARY of the campaign performance data below — not a full report. It should read in under a minute.

WRITING STYLE
- Professional, concise, opportunity-focused
- Every claim must cite a specific number from the data — never fabricate
- Business language, not statistical jargon
- Full markdown: **bold** key numbers/campaign/brand names, a `>` blockquote for the single most important takeaway, short one-line bullets
- No headers (#), no long paragraphs, nothing beyond the structure below

STRUCTURE (exactly this, nothing more)
1. One short paragraph (2-3 sentences) on overall campaign health, closed with a `>` blockquote for the single biggest takeaway.
2. Up to 5 one-line bullets covering: the best performer (with the reason), the worst performer (with the metric behind it), one Campaign Type/Brand pattern if there genuinely is one, and the single highest-priority recommendation.

Do not add extra sections, tables, or theory references — this is a quick-read summary, not a deep-dive report."""

DATA_COLUMNS = [
    "Campaign Name", "Brand", "Brand Category", "Campaign Type", "Retailer",
    "Campaign Key Features", "Sub-Campaign Key Features", "Big Prize", "Big Bet",
    "Success KPI", "Visit", "Unique Visitor", "Time duration (interaction)",
    "Conversion", "Conversion(Times)", "Conversion Rate", "Conversion/users",
    "Key Event", "Start Date", "End Date", "Campaign Duration (days)", "Source Type",
]


def _full_data_table(df: pd.DataFrame) -> str:
    cols = [c for c in DATA_COLUMNS if c in df.columns]
    return df[cols].to_csv(index=False)


def build_campaign_summary_prompt(df: pd.DataFrame) -> str:
    return (
        f"{REPORT_INSTRUCTIONS}\n\n"
        "----------------------------------------------------\n"
        "CAMPAIGN DATASET (full dataset, CSV format — one row per campaign)\n"
        "----------------------------------------------------\n\n"
        f"{_full_data_table(df)}"
    )


# ponytail: st.cache_data hashes generate_ai_summary's own source, not the
# other functions/constants it calls — editing the prompt above won't bust an
# already-cached result on its own. Bump this whenever the prompt changes so
# the cache key changes too.
PROMPT_VERSION = "2026-07-10-concise-exec-summary"


def generate_ai_summary(df: pd.DataFrame, prompt_version: str = PROMPT_VERSION) -> str:
    if df.empty:
        return "ไม่มีข้อมูลแคมเปญให้สรุป"
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "⚠️ ไม่พบ OPENAI_API_KEY กรุณาตั้งค่าใน .env"
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": build_campaign_summary_prompt(df)}],
        max_tokens=500,
    )
    return resp.choices[0].message.content
