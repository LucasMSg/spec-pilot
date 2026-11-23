import os
import time

from openai import OpenAI

print("model:", os.environ.get("LLM_MODEL"))
print("key set:", bool(os.environ.get("GEMINI_API_KEY")))

client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    timeout=30,
    max_retries=0,
)
start = time.time()
try:
    resp = client.chat.completions.create(
        model=os.environ["LLM_MODEL"],
        messages=[{"role": "user", "content": "Say hello in five words."}],
    )
    print("reply:", resp.choices[0].message.content)
except Exception as e:
    print("ERROR:", type(e).__name__, e)
print(f"took {time.time() - start:.1f}s")