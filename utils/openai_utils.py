import openai
import os

def gpt_call(prompt, model="gpt-3.5-turbo", temperature=0):
    # 직접 API 키를 코드에 명시 (보안상 실제 서비스에는 사용 금지)
    openai.api_key = "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"
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "system", "content": prompt}],
        temperature=temperature,
        max_tokens=1024,
    )
    return response['choices'][0]['message']['content'].strip() 