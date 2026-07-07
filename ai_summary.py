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
        "คุณคือ Senior Marketing Data Analyst ที่เชี่ยวชาญด้านการวิเคราะห์ campaign performance "
        "ให้วิเคราะห์ข้อมูลแคมเปญด้านล่าง แล้วตอบเป็นภาษาไทย ใช้หัวข้อและ bullet points ดังนี้:\n\n"
        "1. Overview: สรุปภาพรวมสถานการณ์ปัจจุบันสั้นๆ (2-3 บรรทัด)\n"
        "2. แคมเปญที่ได้รับความสนใจ/performance ดีที่สุด: ระบุแคมเปญและวิเคราะห์ว่าอะไรที่ทำให้สำเร็จ "
        "(เช่น Big Prize, Retailer, Campaign Type ที่ตรงกลุ่มเป้าหมาย)\n"
        "3. แคมเปญที่ performance ไม่ดี: แยกวิเคราะห์ตาม root cause ของแต่ละ metric อย่างชัดเจน เช่น\n"
        "   - Visit ต่ำ = ปัญหาเรื่อง reach/awareness\n"
        "   - Visit สูงแต่ Conversion Rate ต่ำ = ปัญหาเรื่อง offer/UX/แรงจูงใจไม่พอ\n"
        "   - Time on page สั้น = engagement ต่ำ ผู้ใช้ไม่สนใจเนื้อหา\n"
        "   - Conversion เป็น 0 ทั้งที่ Visit สูง = ปัญหาร้ายแรงที่ conversion funnel\n"
        "4. Pattern ระดับ Campaign Type: จากข้อมูลสรุปรายประเภทด้านล่าง ชี้ให้เห็นว่าประเภทแคมเปญไหนมี "
        "ประสิทธิภาพดี/แย่กว่าค่าเฉลี่ยอย่างมีนัยสำคัญ\n"
        "5. ข้อเสนอแนะเชิง actionable: แยกเป็นข้อๆ ตามแคมเปญหรือกลุ่มปัญหาที่พบ พร้อมระบุว่าควรแก้ที่จุดไหนก่อน\n\n"
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
    )
    return resp.choices[0].message.content
