import os

import pandas as pd

from ai_summary import build_campaign_summary_prompt, generate_ai_summary


def test_prompt_includes_top_and_bottom_campaigns():
    df = pd.DataFrame([
        {"Campaign Name": "A", "Brand": "Knorr", "Campaign Type": "Lucky draw", "Visit": 100, "Conversion": 50, "Conversion Rate": 50.0},
        {"Campaign Name": "B", "Brand": "Axe", "Campaign Type": "Lucky draw", "Visit": 200, "Conversion": 5, "Conversion Rate": 2.5},
    ])
    prompt = build_campaign_summary_prompt(df)
    assert "A" in prompt and "B" in prompt
    assert "Conversion Rate" in prompt


def test_prompt_handles_no_positive_conversions():
    df = pd.DataFrame([
        {"Campaign Name": "C", "Brand": "Axe", "Campaign Type": "Lucky draw", "Visit": 100, "Conversion": 0, "Conversion Rate": 0.0},
    ])
    prompt = build_campaign_summary_prompt(df)
    assert "(ไม่มีข้อมูล)" in prompt


def test_generate_ai_summary_without_api_key():
    os.environ.pop("OPENAI_API_KEY", None)
    df = pd.DataFrame([
        {"Campaign Name": "A", "Brand": "Knorr", "Campaign Type": "x", "Visit": 1, "Conversion": 1, "Conversion Rate": 1.0},
    ])
    assert "OPENAI_API_KEY" in generate_ai_summary(df)


def test_generate_ai_summary_empty_df():
    assert generate_ai_summary(pd.DataFrame()) == "ไม่มีข้อมูลแคมเปญให้สรุป"


if __name__ == "__main__":
    test_prompt_includes_top_and_bottom_campaigns()
    test_prompt_handles_no_positive_conversions()
    test_generate_ai_summary_without_api_key()
    test_generate_ai_summary_empty_df()
    print("OK")
