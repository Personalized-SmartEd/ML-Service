from src.Models.dynamic_assessment import QuizResponseModel
from src.Models.quiz_bot import QuizRequestBody
from src.LLMs.gemini_integration import GeminiClient


class QuizBotService:
    def __init__(self):
        self.quiz_bot = GeminiClient()

    async def get_quiz(self, request: QuizRequestBody):
        prompt = f"Generate quiz questions based on following data : {request}"

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

        return QuizResponseModel(question_count=len(questions['items']), questions=questions['items'])
