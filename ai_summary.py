import os

import pandas as pd
from openai import OpenAI

REPORT_INSTRUCTIONS = """You are a Senior Marketing Strategy Consultant and Data Storytelling Expert specializing in FMCG digital campaigns.

Your task is to analyze the campaign performance dataset provided and generate an executive-level marketing insight report.

Your objective is NOT to simply summarize numbers.

Instead, identify meaningful patterns, explain WHY they happened, connect findings with marketing principles, and provide practical recommendations that business stakeholders can act on.

The report should read like a presentation prepared by a Strategy Director for Brand Managers.

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
- Keep paragraphs short and easy to read
- Organize every section with bullet points

----------------------------------------------------
REPORT STRUCTURE
----------------------------------------------------

# Executive Summary

Provide a concise overview of the overall campaign performance including:

- Overall campaign health
- Total campaigns analyzed
- General traffic quality
- Overall conversion performance
- Major highlights
- Positive business takeaway

----------------------------------------------------

# Key Performance Highlights

Identify the strongest campaign performances.

Include observations such as:

- Highest Visits
- Highest Unique Visitors
- Highest Conversion
- Highest Conversion Rate
- Highest Engagement
- Outstanding performers
- Consistent performers

For every point include:

Observation

Reference Data

Business Interpretation

Why it matters

----------------------------------------------------

# Campaign Success Drivers

Identify patterns among successful campaigns.

Look for relationships involving:

- Campaign Type
- Brand
- Category
- Retailer
- Key Features
- Rewards
- Celebrity or Influencer
- Campaign Duration

Explain what characteristics successful campaigns have in common.

Support every conclusion using evidence.

----------------------------------------------------

# Audience & Behavioral Insights

Analyze user behavior throughout the campaign journey.

Possible observations include:

- High traffic but lower conversion
- High engagement
- Strong conversion efficiency
- Repeat visitation
- User intent
- Campaign stickiness

Explain the possible behavioral reasons behind the observed patterns.

----------------------------------------------------

# Brand Performance Insights

Compare brands fairly.

Highlight:

- Strongest performing brands
- Most efficient brands
- Brands generating the highest audience
- Brands with balanced performance

Focus on strengths rather than weaknesses.

----------------------------------------------------

# Campaign Mechanics Insights

Evaluate which campaign mechanics appear to perform well.

Examples:

- Lucky Draw
- Quiz
- Game
- Receipt Upload
- Sampling
- Instant Win
- Coupon
- Meet & Greet

Explain why those mechanics may influence user participation.

----------------------------------------------------

# Strategic Marketing Insights

Interpret findings using established marketing theories when appropriate.

You may reference concepts such as:

- AIDA Model
- Consumer Decision Journey
- Customer Engagement Funnel
- Hook Model
- Uses & Gratifications Theory
- Social Proof
- Scarcity Principle
- FOMO
- Gamification
- Behavioral Economics
- Mental Availability
- Distinctive Brand Assets
- Mere Exposure Effect
- Integrated Marketing Communication
- Customer Journey
- Loyalty Loop
- Choice Architecture

Only reference theories when they genuinely support the insight.

Do NOT force theory into every observation.

----------------------------------------------------

# Positive Opportunities

Instead of focusing on weaknesses, identify opportunities such as:

- Winning mechanics worth scaling
- Best practices worth replicating
- Brands worth using as benchmarks
- Campaign ideas that can be reused
- Cross-brand learning opportunities

----------------------------------------------------

# Recommendations

Provide practical recommendations.

Recommendations must be realistic.

Each recommendation should contain:

Recommendation

Expected Business Impact

Supporting Evidence

Priority

High / Medium / Low

----------------------------------------------------

# Interesting Findings

Highlight any surprising findings including:

- Unexpected high performers
- Efficient niche campaigns
- Outliers
- Hidden opportunities
- Interesting correlations

----------------------------------------------------

# Confidence Level

For every major insight provide:

Evidence Level

High

Medium

Low

Explain why.

----------------------------------------------------
FORMATTING
----------------------------------------------------

Use Markdown.

Separate every topic clearly using headings.

Use bullet points.

Highlight important numbers in bold.

Use short paragraphs.

Avoid large blocks of text.

----------------------------------------------------
REFERENCE FORMAT
----------------------------------------------------

Every insight MUST include a reference section.

Example

Reference

- Campaign:
- Brand:
- Category:
- Visits:
- Unique Visitors:
- Conversion:
- Conversion Rate:
- Duration:
- Other supporting metrics:

Never provide an insight without citing supporting data.

----------------------------------------------------
WRITING TONE

Write like a McKinsey, BCG, Bain or Deloitte strategy consultant presenting findings to senior marketing executives.

Avoid generic statements.

Every insight should answer:

"What happened?"

"So what?"

"Why does it matter?"

"What should we do next?"

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


def generate_ai_summary(df: pd.DataFrame) -> str:
    if df.empty:
        return "ไม่มีข้อมูลแคมเปญให้สรุป"
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "⚠️ ไม่พบ OPENAI_API_KEY กรุณาตั้งค่าใน .env"
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": build_campaign_summary_prompt(df)}],
        max_tokens=4096,
    )
    return resp.choices[0].message.content
