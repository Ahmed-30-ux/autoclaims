import json
from openai import OpenAI
from app.config import settings


_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.qwen_api_key,
            base_url=settings.qwen_base_url,
        )
    return _client


def chat(
    model: str,
    messages: list[dict],
    tools: list[dict] | None = None,
    response_format: dict | None = None,
    temperature: float = 0.7,
    max_tokens: int | None = None,
) -> str:
    client = get_client()
    kwargs = dict(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    if tools:
        kwargs["tools"] = tools
    if response_format:
        kwargs["response_format"] = response_format
    if max_tokens:
        kwargs["max_tokens"] = max_tokens

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message


def chat_structured(model: str, messages: list[dict], schema: type) -> dict:
    response_format = {
        "type": "json_schema",
        "json_schema": {
            "name": schema.__name__,
            "strict": True,
            "schema": _pydantic_to_json_schema(schema),
        }
    }
    msg = chat(model, messages, response_format=response_format, temperature=0.1)
    return json.loads(msg.content)


def _pydantic_to_json_schema(model: type) -> dict:
    schema = model.model_json_schema()
    return schema


def chat_json(model: str, messages: list[dict], temperature: float = 0.1) -> dict:
    msg = chat(model, messages, response_format={"type": "json_object"}, temperature=temperature)
    content = msg.content
    if content is None:
        refusal = getattr(msg, "refusal", None)
        raise ValueError(f"Qwen API returned empty content. Refusal: {refusal}")
    return json.loads(content)


def analyze_image(model: str, image_url: str, prompt: str) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }],
    )
    return response.choices[0].message.content
