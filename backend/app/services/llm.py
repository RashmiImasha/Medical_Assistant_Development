from groq import Groq
from pydantic import BaseModel
from app.core.config import get_settings
import re, json

settings = get_settings()

def get_groq_client():
    return Groq(
        api_key=settings.groq_api_key
    )

def get_structured_output(
        prompt: str,
        response_model: type[BaseModel],
        model: str | None = None,
) -> BaseModel:
    """
    Generate structured output.

    Args:
        prompt: Input prompt.
        response_model: Pydantic response model.
        model: Groq model.

    Returns:
        Parsed response model.
    """
    client = get_groq_client()
    model = model or settings.groq_model

    messages = [
        {
            "role": "system",
            "content": "You are an expert financial analyst."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

  
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )

    text = response.choices[0].message.content

    match = re.search(r"\{.*\}", text, re.S)

    if not match:
        raise ValueError(
            f"No JSON object found in model response: {text}"
        )

    json_text = match.group(0)
    data = json.loads(json_text)

    return response_model.model_validate(data)

