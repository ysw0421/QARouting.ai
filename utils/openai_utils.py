from openai import OpenAI
import os


def gpt_call(prompt, model="gpt-3.5-turbo", temperature=0):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=1024,
    )
    content = response.choices[0].message.content
    return content.strip() if content else "" 