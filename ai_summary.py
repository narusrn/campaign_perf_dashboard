import os

import pandas as pd
from openai import OpenAI


def _fmt_rows(rows: pd.DataFrame) -> str:
    if rows.empty:
        return "(ไม่มีข้อมูล)"
    lines = [
        f"- {r['Campaign Name']} (Brand: {r['Brand']}, Type: {r['Campaign Type']}): "
        f"Visit={int(r['Visit'])}, Conversion={int(r['Conversion'])}, "
        f"Conversion Rate={r['Conversion Rate']:.2f}%"
        for _, r in rows.iterrows()
    ]
    return "\n".join(lines)


def build_campaign_summary_prompt(df: pd.DataFrame) -> str:
    top = df.sort_values("Conversion", ascending=False).head(5)
    bottom = df[df["Conversion"] > 0].sort_values("Conversion Rate", ascending=True).head(5)
    return (
        "คุณคือนักวิเคราะห์การตลาด สรุปผลลัพธ์แคมเปญด้านล่างเป็นภาษาไทย กระชับ เป็น bullet points 3 หัวข้อ:\n"
        "1. แคมเปญที่ได้รับความสนใจ/conversion สูงสุด\n"
        "2. แคมเปญที่ performance ไม่ดี พร้อมระบุว่ามาจาก metric ไหน (Visit ต่ำ, Conversion Rate ต่ำ ฯลฯ)\n"
        "3. ข้อเสนอแนะเพื่อ improve แคมเปญที่ performance ไม่ดี\n\n"
        f"แคมเปญที่มี conversion สูงสุด:\n{_fmt_rows(top)}\n\n"
        f"แคมเปญที่มี conversion rate ต่ำสุด (เฉพาะที่มี conversion > 0):\n{_fmt_rows(bottom)}"
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
    )
    return resp.choices[0].message.content
