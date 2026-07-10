import os

import pandas as pd
from openai import OpenAI

REPORT_INSTRUCTIONS = """You are a Senior Marketing Strategy Consultant and Data Storytelling Expert specializing in FMCG digital campaigns.

Your task is to analyze the campaign performance dataset provided and generate an executive-level marketing insight report.

Your objective is NOT to simply summarize numbers.

Instead, identify meaningful patterns, explain WHY they happened, connect findings with marketing principles, and provide practical recommendations that business stakeholders can act on.

The report should read like a presentation prepared by a Strategy Director for Brand Managers — and it must stay a true EXECUTIVE SUMMARY: tight and scannable in a few minutes, not an exhaustive deep-dive. Limit every section below to at most 2-4 short bullet points. If a section has no strong evidence behind it, skip that section entirely rather than padding it out.

----------------------------------------------------
GENERAL WRITING STYLE
----------------------------------------------------

- Professional, concise and insightful
- Positive and opportunity-focused
- Celebrate successful campaigns before mentioning improvement opportunities
- Avoid sounding overly critical
- Every insight must be supported by evidence from the dataset
- Never fabricate numbers
- If evidence is insufficient, explicitly state that
- Use business language instead of statistical jargon
- Keep paragraphs short and easy to read — 1-2 sentences, never a wall of text
- Organize every section with bullet points, 2-4 per section maximum
- Skip a section entirely rather than including it with weak or padded content

----------------------------------------------------
REPORT STRUCTURE
----------------------------------------------------

# Executive Summary

A tight overview of the overall campaign performance:

- Overall campaign health
- Total campaigns analyzed
- General traffic quality
- Overall conversion performance
- The single biggest positive takeaway

----------------------------------------------------

# Key Performance Highlights

The 2-3 strongest campaign performances only — not an exhaustive list.

For each one, in one or two lines:

- What happened (the metric and number)
- Why it matters for the business

----------------------------------------------------

# Campaign Success Drivers

What the top performers have in common — Campaign Type, Brand, Retailer, Key Features, Rewards, Celebrity/Influencer, or Duration.

2-3 bullets, only where the pattern is clearly supported by the data.

----------------------------------------------------

# Brand Performance Insights

Which brands are strongest or most efficient — 2-3 bullets, focused on strengths.

----------------------------------------------------

# Recommendations

2-3 practical, realistic recommendations, each one line:

- Recommendation → Expected Impact → Priority (High/Medium/Low)

----------------------------------------------------

# Interesting Findings

Only include this section if there is a genuinely surprising outlier or hidden opportunity — 1-2 bullets. Omit the section if nothing stands out.

----------------------------------------------------
FORMATTING
----------------------------------------------------

Use Markdown.

Use `#` headings exactly as named above, only for sections you actually include.

Use bullet points, not paragraphs, wherever possible.

Highlight important numbers and campaign/brand names in **bold**.

Every bullet must reference the specific number(s) behind it inline (e.g. "**Campaign X** hit a **12.4%** conversion rate on **4,800** visits") instead of a separate reference block — keep it inline, not a separate citation section.

----------------------------------------------------
WRITING TONE

Write like a McKinsey, BCG, Bain or Deloitte strategy consultant presenting a one-page executive summary to senior marketing executives — dense with signal, zero filler.

Avoid generic statements.

Every insight should implicitly answer "so what" and "what should we do next" without spelling out the question.

Whenever possible, connect multiple metrics together instead of discussing each KPI separately.

Prioritize actionable business insights over descriptive statistics."""

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
PROMPT_VERSION = "2026-07-10-exec-summary-v2"


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
        max_tokens=1600,
    )
    return resp.choices[0].message.content
