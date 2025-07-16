import openai
import os

def gpt_call(prompt, model="gpt-3.5-turbo", temperature=0):
    # 직접 API 키를 코드에 명시 (보안상 실제 서비스에는 사용 금지)
    openai.api_key = "TEST"
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "system", "content": prompt}],
        temperature=temperature,
        max_tokens=1024,
    )
    return response['choices'][0]['message']['content'].strip() 