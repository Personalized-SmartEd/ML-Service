import ast
from typing import List
from fastapi import HTTPException
import joblib
import numpy as np
import pandas as pd
from src.LLMs.gemini_integration import GeminiClient
from src.Models.static_assessment import AssessmentResult, LearningStyleResult, LearningStyleType, PastScoresModel, PerformanceLevel, Trend
from src.Models.dynamic_assessment import QuizResponseModel, QuizSubmission, VARKQuestion



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

                # creating valid response object for returning the quiz
                vark_questions = []
                id = 1
                for item in questions['items']:
                    vark_questions.append(VARKQuestion(qid=id, question=item['question'], options=item['options']))
                    id += 1
                return QuizResponseModel(question_count=len(questions['items']), questions=vark_questions)

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
            raise HTTPException(status_code=409, detail="Give 15 responses bitch.")

        for response_index in answers:
            if response_index > 3:
                raise HTTPException(status_code=300, detail='Options should be between 0 to 3')
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
    


class DynamicAssessmentService:
    def __init__(self):
        self.average_score_model = joblib.load('./src/Weights/predicted_performance_level_model.pkl')
        self.performance_level_model = joblib.load('./src/Weights/current_performance_level_model.pkl')
        self.trend_model = joblib.load('./src/Weights/trend_model.pkl')
        self.scaler = joblib.load('./src/Weights/scaler.pkl')

    def calculate_performance(self,scores_data: PastScoresModel) -> AssessmentResult:
        """Calculate performance metrics based on historical scores"""
        subject = scores_data.subject
        scores = scores_data.scores

        average, level, trend = self.xgb_evaluation(scores=scores)

        return AssessmentResult(
            subject=subject,
            performance_level=level,
            average_score=average,
            trend=trend
        )
    
    def extract_features(self, row):
        scores = row['score_history']
        if isinstance(scores, (int, float)):
            scores = [float(scores)]
        elif isinstance(scores, str):
            try:
                scores = ast.literal_eval(scores) if '[' in scores else [float(scores)]
            except (ValueError, SyntaxError):
                return [0, 0, 0]
        scores = [float(s) for s in scores if isinstance(s, (int, float)) or str(s).replace('.', '', 1).isdigit()]
        if not scores:
            return [0, 0, 0]
        return [np.mean(scores), np.var(scores), np.std(scores)]

    def xgb_evaluation(self, scores):
        sample_data = pd.DataFrame({
            'score_history': [scores]
        })

        # preprocessing
        sample_data[['mean_score', 'variance', 'std_dev']] = sample_data.apply(self.extract_features, axis=1, result_type='expand')
        X_sample = sample_data[['mean_score', 'variance', 'std_dev']]
        X_sample_scaled = self.scaler.transform(X_sample)

        # prediction
        avg_score_pred = self.average_score_model.predict(X_sample_scaled)
        perf_pred = self.performance_level_model.predict(X_sample_scaled)
        trend_pred = self.trend_model.predict(X_sample_scaled)

        perf_enum = {0:PerformanceLevel.ADVANCED, 1:PerformanceLevel.INTERMEDIATE, 2:PerformanceLevel.BEGINNER}
        trend_enum = {0:Trend.IMPROVING, 1:Trend.DECLINING, 2:Trend.STABLE}

        return avg_score_pred, perf_enum[perf_pred[0]], trend_enum[trend_pred[0]]
         
