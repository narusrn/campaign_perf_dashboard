import os

import pandas as pd
from openai import OpenAI


def _fmt_rows(rows: pd.DataFrame) -> str:
    if rows.empty:
        return "(ไม่มีข้อมูล)"
    lines = [
        f"- {r['Campaign Name']} | Brand: {r['Brand']} | Type: {r['Campaign Type']} | "
        f"Retailer: {r.get('Retailer', '-')} | Big Prize: {r.get('Big Prize', '-')} | "
        f"Visit={int(r['Visit'])}, Unique Visitor={r.get('Unique Visitor', '-')}, "
        f"Time on page={r.get('Time duration (interaction)', '-')}, "
        f"Conversion={int(r['Conversion'])}, Conversion Rate={r['Conversion Rate']:.2f}%"
        for _, r in rows.iterrows()
    ]
    return "\n".join(lines)


def _fmt_type_breakdown(df: pd.DataFrame) -> str:
    g = df.groupby("Campaign Type").agg(
        campaigns=("Campaign Name", "count"),
        total_visit=("Visit", "sum"),
        total_conversion=("Conversion", "sum"),
        avg_conv_rate=("Conversion Rate", "mean"),
    ).sort_values("avg_conv_rate", ascending=False)
    if g.empty:
        return "(ไม่มีข้อมูล)"
    return "\n".join(
        f"- {ct}: {int(r.campaigns)} แคมเปญ, Visit รวม={int(r.total_visit):,}, "
        f"Conversion รวม={int(r.total_conversion):,}, Avg Conversion Rate={r.avg_conv_rate:.2f}%"
        for ct, r in g.iterrows()
    )


def build_campaign_summary_prompt(df: pd.DataFrame) -> str:
    total_campaigns = len(df)
    zero_conv = df[df["Conversion"] == 0]
    active = df[df["Conversion"] > 0]

    top = active.sort_values("Conversion", ascending=False).head(5)
    bottom = active.sort_values("Conversion Rate", ascending=True).head(5)
    zero_conv_worst = zero_conv.sort_values("Visit", ascending=False).head(5)

    return (
        "คุณคือ Senior Marketing Data Analyst สรุปข้อมูลแคมเปญด้านล่างเป็น Executive Summary ภาษาไทย "
        "ให้กระชับที่สุด ไม่เกิน 5 bullet points บรรทัดเดียวต่อข้อ ห้ามมีหัวข้อย่อยซ้อนหรือคำนำ/สรุปท้าย:\n"
        "- แคมเปญ/กลุ่มที่ performance ดีที่สุดและเหตุผลสั้นๆ\n"
        "- แคมเปญ/กลุ่มที่ performance แย่ที่สุดและ metric ที่เป็นสาเหตุหลัก\n"
        "- Pattern สำคัญระดับ Campaign Type (ถ้ามี)\n"
        "- ข้อเสนอแนะที่ควรทำก่อนอันดับแรก\n\n"
        f"จำนวนแคมเปญทั้งหมด: {total_campaigns} | มี conversion: {len(active)} | "
        f"ไม่มี conversion เลย (0): {len(zero_conv)}\n\n"
        f"แคมเปญที่มี conversion สูงสุด (Top 5):\n{_fmt_rows(top)}\n\n"
        f"แคมเปญที่มี conversion rate ต่ำสุด แต่ยังมี conversion (Bottom 5):\n{_fmt_rows(bottom)}\n\n"
        f"แคมเปญที่ไม่เกิด conversion เลย เรียงตาม Visit สูงสุด (Top 5 ที่ควรกังวลที่สุด):\n{_fmt_rows(zero_conv_worst)}\n\n"
        f"สรุปประสิทธิภาพตาม Campaign Type:\n{_fmt_type_breakdown(df)}"
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
        max_tokens=300,
    )
    return resp.choices[0].message.content
