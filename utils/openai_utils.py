import openai
import os


def gpt_call(prompt, model="gpt-3.5-turbo", temperature=0):
    # 보안을 위해 환경 변수에서 API 키를 불러옵니다.
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "system", "content": prompt}],
        temperature=temperature,
        max_tokens=1024,
    )
    return response['choices'][0]['message']['content'].strip() 