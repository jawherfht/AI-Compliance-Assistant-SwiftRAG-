from openai import OpenAI
from dotenv import load_dotenv #reads any env file where our api key is stored

#to load the env file where api key is stored
load_dotenv()
client = OpenAI()

resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "say hello"}]
)

print(resp.choices[0].message.content)
