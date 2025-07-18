from openai import OpenAI
import os


def gpt_call(prompt, model="gpt-3.5-turbo", temperature=0):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다. .env 파일 또는 시스템 환경변수를 확인하세요.")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=1024,
    )
    content = response.choices[0].message.content
    return content.strip() if content else "" 