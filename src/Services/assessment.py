from fastapi import HTTPException
from pydantic import BaseModel
from requests import HTTPError

from src.LLMs.gemini_integration import GeminiClient
from src.Models.learning_style import LearningStyleResult, LearningStyleType
from src.Models.quiz import QuizResponseModel, QuizSubmission



class InitialAssessmentService:
    def __init__(self):
        self.gemini = GeminiClient()

    async def generate_initial_quiz(self) -> list:
                prompt = """
                    Generate 15 high-quality VARK assessment questions specifically designed for high school students. Follow these guidelines:

                    1. Question Structure:
                    - Each must present a realistic learning scenario teenagers would encounter
                    - Cover diverse contexts: exam preparation, homework, lectures, group work, labs, and skill acquisition
                    - Phrase questions in natural, conversational English
                    - Ensure only one modality is clearly correct per question

                    2. Options Requirements:
                    - Maintain EXACT order: [Visual, Auditory, Reading/Writing, Kinesthetic]
                    - Keep responses concise (<10 words)
                    - Use distinct modality indicators:
                    Visual: diagrams, charts, images, videos
                    Auditory: discussions, podcasts, verbal explanations
                    Reading/Writing: textbooks, notes, lists, essays
                    Kinesthetic: experiments, hands-on activities, physical movement

                    3. Examples of Good Questions:
                    {
                        "question": "You need to learn how tectonic plates work. You would...",
                        "options": [
                            "Watch an animated video of plate movement",
                            "Listen to a podcast about plate boundaries",
                            "Read a detailed article with definitions",
                            "Build a model using clay layers"
                        ]
                    },
                    {
                        "question": "When memorizing vocabulary words, you prefer to...",
                        "options": [
                            "Create flash cards with pictures",
                            "Repeat the words aloud rhythmically",
                            "Write the words multiple times",
                            "Act out the meanings physically"
                        ]
                    }

                    4. Output Requirements:
                    - Avoid duplicate question themes
                    - Ensure balanced representation of all modalities
                    - Use simple language accessible to 13-18 year olds
                    - No markdown formatting - pure JSON-compatible text
                    """

                
                questions = await self.gemini.generate_structured_data(
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
                                }
                            },
                            "required": ["question", "options"]
                        }
                    }
                )

                return QuizResponseModel(question_count=len(questions['items']), questions=questions['items'])

    async def process_results(self, submission: QuizSubmission) -> LearningStyleResult:
        """Calculate and store learning style"""
        style_scores = {
            LearningStyleType.VISUAL: 0,
            LearningStyleType.AUDITORY: 0,
            LearningStyleType.READING_WRITING: 0,
            LearningStyleType.KINESTHETIC: 0
        }
        answers = submission.responses
        if len(answers) != 15:
            print(answers, len(answers))
            raise HTTPException(status_code=409, detail="Give 15 unique-responses bitch.")

        for response_index in answers.values():
            # Direct mapping based on option order: 0=Visual, 1=Auditory, etc.
            style = [
                LearningStyleType.VISUAL,
                LearningStyleType.AUDITORY,
                LearningStyleType.READING_WRITING,
                LearningStyleType.KINESTHETIC
            ][response_index]
            
            style_scores[style] += 1
        dominant_style = max(style_scores, key=style_scores.get)
        
        explanation = await self.gemini.generate_learning_style_explanation(
            dominant_style.value
        )
        
        return LearningStyleResult(
            style=dominant_style,
            description=explanation
        )