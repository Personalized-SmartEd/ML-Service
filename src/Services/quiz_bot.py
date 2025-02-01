from src.Models.dynamic_assessment import QuizQuestion, QuizResponseModel, VARKQuestion
from src.Models.quiz_bot import QuizRequestBody
from src.LLMs.gemini_integration import GeminiClient


class QuizBotService:
    def __init__(self):
        self.quiz_bot = GeminiClient()

    async def get_quiz(self, request: QuizRequestBody):
        prompt = f"Generate quiz questions based on following data : {request}"

        #TODO : vector search
        # above rpompt is just for testing purpose.
        # we would need a call to vecordb for getting relevant course-ware before generating the quiz.

        questions = await self.quiz_bot.generate_structured_data(
            prompt=prompt,
            response_schema={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {"type": "string"},
                        "options": {
                            "type": "array",
                            "minItems": 4,
                            "maxItems": 4,
                            "items": {"type": "string"}
                        },
                        "answer": {"type": "string"},
                        "correct_option": {"type": "integer"},
                        "explanation": {"type": "string"}
                    },
                    "required": ["question", "options"]
                }
            }
        )

        # creating valid response object for returning the quiz
        vark_questions = []
        id = 1
        for item in questions['items']:
            vark_questions.append(QuizQuestion(qid=id, question=item['question'], options=item['options'], correct_option=item['correct_option'], answer = item['answer'], explanation = item['explanation']))
            id += 1
        return QuizResponseModel(question_count=len(questions['items']), questions=vark_questions)
