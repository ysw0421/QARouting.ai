import sys
import os
import json

# 프로젝트 최상단 디렉토리 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)

# classify_intention import
from agents.question_intention_ingester import classify_intention

# Simple 질문 데이터 로드
simple_data_path = os.path.join(project_root, 'data', 'simple_legal_questions.json')
with open(simple_data_path, 'r', encoding='utf-8') as file:
    simple_data = json.load(file)

# Complex 질문 데이터 로드
complex_data_path = os.path.join(project_root, 'data', 'complex_legal_questions.json')
with open(complex_data_path, 'r', encoding='utf-8') as file:
    complex_data = json.load(file)
    
print("=== Simple Questions ===")
for item in simple_data['simple_questions']:
    question_text = item['question']

    intention = classify_intention(question_text)
    
    print(f"[{item['id']}] 질문: {question_text}\n=> 분류 결과: {intention}\n")

print("\n=== Complex Questions ===")
for item in complex_data['complex_questions']:
    question_text = item['question']
    
    intention = classify_intention(question_text)
    
    print(f"[{item['id']}] 질문: {question_text}\n=> 분류 결과: {intention}\n")
