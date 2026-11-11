"""Thin, provider-agnostic LLM client (any OpenAI-compatible endpoint)."""
import json
import os
import sys
import time

from openai import OpenAI, RateLimitError

DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def _client() -> OpenAI:
    api_key = os.environ.get("LLM_API_KEY") or os.environ["GEMINI_API_KEY"]
    base_url = os.environ.get("LLM_BASE_URL", DEFAULT_BASE_URL)
    return OpenAI(api_key=api_key, base_url=base_url)


def chat(messages, tools=None, temperature=0.2, retries=5):
    """One model call, with backoff when the free tier rate-limits us."""
    kwargs = {"model": os.environ["LLM_MODEL"], "messages": messages,
              "temperature": temperature}
    if tools:
        kwargs["tools"] = tools
    client = _client()
    for attempt in range(retries):
        try:
            return client.chat.completions.create(**kwargs).choices[0].message
        except RateLimitError:
            wait = 5 * 2 ** attempt
            log(f"rate limited, retrying in {wait}s")
            time.sleep(wait)
    raise RuntimeError("still rate limited after retries")


def run_agent(system, task, tools, handlers, max_steps=25):
    """The agent loop: call the model, run requested tools, repeat."""
    messages = [{"role": "system", "content": system},
                {"role": "user", "content": task}]
    for _ in range(max_steps):
        msg = chat(messages, tools=tools)
        if not msg.tool_calls:
            return msg.content or ""

        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {"id": tc.id, "type": "function",
                 "function": {"name": tc.function.name,
                              "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ],
        })
        for tc in msg.tool_calls:
            name, raw_args = tc.function.name, tc.function.arguments or "{}"
            try:
                result = handlers[name](**json.loads(raw_args))
            except Exception as e:  # report errors back to the model
                result = f"ERROR: {type(e).__name__}: {e}"
            log(f"  tool {name}({raw_args}) -> {len(result)} chars")
            messages.append({"role": "tool", "tool_call_id": tc.id,
                             "content": result})
    raise RuntimeError(f"agent did not finish within {max_steps} steps")