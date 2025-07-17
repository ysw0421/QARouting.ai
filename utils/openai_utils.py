<<<<<<< HEAD
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def gpt_call(prompt, model="gpt-3.5-turbo", temperature=0):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompt}],
        temperature=temperature,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()