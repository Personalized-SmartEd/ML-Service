from src.Utils.find_docs import find_pdf
from src.Models.dynamic_assessment import QuizQuestion, QuizResponseModel, VARKQuestion
from src.Models.quiz_bot import QuizRequestBody
from src.LLMs.gemini_integration import GeminiClient

class QuizBotService:
    def __init__(self):
        self.quiz_bot = GeminiClient()

    async def get_quiz(self, request: QuizRequestBody):
        # Retrieve relevant course material from vector DB
        course_context = find_pdf(
            student_class=request.student_info.student_class,
            subject=request.subject_info.subject.value,
            chapter=request.subject_info.chapter,
            query=request.subject_info.topic_description
        )
        course_context  = course_context['documents']

        # Construct enhanced prompt
        prompt = self._construct_prompt(request, course_context)
        print('DEBUG : ', prompt)

        # Generate structured quiz questions
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

        return self._create_response(questions['items'])

    def _construct_prompt(self, request: QuizRequestBody, context: str) -> str:
        """Build context-aware quiz generation prompt"""
        return f"""
        Act as an expert quiz generator for {request.subject_info.subject.value} students. Consider these parameters:
        
        Student Profile:
        - Class/Grade: {request.student_info.student_class}
        - Academic Performance: {request.student_info.student_performance_from_1_to_100}%
        - Learning Style: {request.student_info.student_learning_style.value}
        - Preferred Difficulty: {request.student_info.student_performance_level.value}

        Chapter: {request.subject_info.chapter}
        Topic: {request.subject_info.topic_description}
        
        Relevant Course Context:
        {context}

        Generate multiple-choice questions that:
        1. Assess understanding of key chapter concepts
        2. Match the student's academic level and learning style
        3. Include varying difficulty levels (basic recall to application)
        4. Contain plausible distractors based on common misconceptions

        Format Requirements:
         - Number of questions : {request.quiz_info.number_of_questions}
         - Question difficulty from 1 to 10 : {request.quiz_info.quiz_difficulty_from_1_to_10}
         - Quiz duration in minutes : {request.quiz_info.quiz_duration_minutes}

        Include these question types based on learning style:
        {self._get_question_types_instructions(request.student_info.student_learning_style.value)}

        NOTE : Try to follow the provided context as closely as possible.
        """

    def _get_question_types_instructions(self, learning_style: VARKQuestion) -> str:
        """Get learning-style specific question instructions"""
        style_instructions = {
            "visual": "Include diagram-based questions and spatial relationships",
            "aural": "Focus on lecture-like scenarios and sound-related concepts",
            "read/write": "Emphasize text analysis and written responses",
            "kinesthetic": "Use real-world application scenarios and hands-on problems"
        }
        return style_instructions.get(learning_style, "Mix of different question types")

    def _create_response(self, items: list) -> QuizResponseModel:
        """Convert raw items to validated response model"""
        quiz_questions = [
            QuizQuestion(
                qid=idx+1,
                question=item['question'],
                options=item['options'],
                correct_option=item.get('correct_option', 1),
                answer=item.get('answer', item['options'][0]),
                explanation=item.get('explanation', '')
            )
            for idx, item in enumerate(items)
        ]
        
        return QuizResponseModel(
            question_count=len(quiz_questions),
            questions=quiz_questions
        )