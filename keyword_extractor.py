from keybert import KeyBERT
import json

def extract_keywords(input_json="control_summaries.json", output_json="keywords.json"):
    kw_model = KeyBERT()

    with open(input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    keywords_db = {}
    for control_id, text in data.items():
        keywords = kw_model.extract_keywords(text, top_n=10)
        keywords_db[control_id] = [kw[0] for kw in keywords]

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(keywords_db, f, indent=2)

    return keywords_db

if __name__ == "__main__":
    extract_keywords()