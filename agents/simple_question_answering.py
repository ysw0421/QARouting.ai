import json
import os

class SimpleQuestionAnsweringAgent:
    def __init__(self, questions_path=None):
        # 기본 경로: data/simple_legal_questions.json
        self.questions_path = questions_path or os.path.join(os.path.dirname(__file__), '../data/simple_legal_questions.json')
        with open(self.questions_path, 'r', encoding='utf-8') as f:
            self.qa_data = json.load(f)["simple_questions"]

    def answer(self, question: str) -> str:
        # 간단한 정규화 및 매칭 (실제 서비스에서는 임베딩/유사도 검색 추천)
        q_norm = question.strip().lower()
        for qa in self.qa_data:
            if qa["question"].strip().lower() == q_norm:
                return qa["answer"]
        return "[FAQ DB에 없는 질문입니다. 추가 답변 로직 필요]" 