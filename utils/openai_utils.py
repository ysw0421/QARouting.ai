import openai
import os


def gpt_call(prompt, model="gpt-3.5-turbo", temperature=0):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "system", "content": prompt}],
        temperature=temperature,
        max_tokens=1024,
    )
    return response['choices'][0]['message']['content'].strip() 