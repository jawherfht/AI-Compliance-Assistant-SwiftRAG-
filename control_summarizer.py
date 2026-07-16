import json
import ollama
import pandas as pd

def summarize_controls(csv_path="swift_controls.csv", output_json="control_summaries.json"):
    df = pd.read_csv(csv_path)
    summaries = {}

    for _, row in df.iterrows():
        prompt = f"""
You are a SWIFT CSCF expert.

Control:
{row.get('title', row.get('control'))}

Generate:

1 Objective
2 Summary
3 Main Risk
4 Requirements

Return JSON only.
"""

        response = ollama.chat(
            model="gemma3:4b",
            messages=[
                {
                    "role":"user",
                    "content":prompt
                }
            ]
        )

        control_id = row.get("control_id", row.get("id"))
        summaries[control_id] = response["message"]["content"]

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)

    return summaries

if __name__ == "__main__":
    summarize_controls()