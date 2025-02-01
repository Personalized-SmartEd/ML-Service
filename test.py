from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Dict, Optional
import asyncio
from groq import Groq
import os
from dotenv import load_dotenv
import json
import logging
from enum import Enum
from contextlib import asynccontextmanager
from functools import lru_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"

class ProficiencyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class StudyPace(str, Enum):
    SLOW = "slow"
    MODERATE = "moderate"
    FAST = "fast"

class ResourceFormat(str, Enum):
    VIDEO = "video"
    PDF = "pdf"
    AUDIO = "audio"
    WEB = "web"

class StudentProfile(BaseModel):
    learning_style: LearningStyle
    current_level: ProficiencyLevel
    weak_areas: List[str] = Field(..., min_items=1, max_items=5)
    performance_history: List[float] = Field(..., min_items=1)
    preferred_pace: StudyPace
    available_hours: int = Field(..., gt=0, le=168)

    @validator('performance_history')
    def validate_performance_scores(cls, v):
        if not all(0 <= score <= 100 for score in v):
            raise ValueError("Performance scores must be between 0 and 100")
        return v

class Resource(BaseModel):
    type: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    format: ResourceFormat
    topics: List[str] = Field(..., min_items=1)
    match_style: LearningStyle
    link: HttpUrl

class DailySchedule(BaseModel):
    day: str
    subjects: List[str]
    duration: float = Field(..., gt=0)
    activities: List[str]

class ExercisePlan(BaseModel):
    type: str
    target: str
    difficulty: ProficiencyLevel

class StudyPlanRecommendation(BaseModel):
    weekly_schedule: List[DailySchedule]
    study_resources: List[Resource]
    time_allocation: Dict[str, float]
    exercise_plan: List[ExercisePlan]
    progress_predictions: Dict[str, float]

class GroqConfiguration:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model_name = os.getenv("GROQ_MODEL", "deepseek-r1-distill-llama-70b")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")

@lru_cache()
def get_groq_config() -> GroqConfiguration:
    return GroqConfiguration()

class GroqRecommendationEngine:
    def __init__(self, config: GroqConfiguration):
        self.client = Groq(api_key=config.api_key)
        self.model_name = config.model_name
        self.logger = logging.getLogger(__name__)

    async def generate_recommendations(self, profile: StudentProfile) -> StudyPlanRecommendation:
        try:
            prompt = self._create_prompt(profile)
            response = await asyncio.to_thread(self._query_groq, prompt)
            return self._parse_response(response)
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            raise

    def _create_prompt(self, profile: StudentProfile) -> str:
        def create_daily_schedule(day_type: str, subjects: List[str]) -> dict:
            if day_type == "weekday":
                return {
                    "06:30 - 07:00": "Wake up and morning routine",
                    "07:00 - 07:30": "Breakfast and preparation for school",
                    "07:30 - 07:55": "Travel to school",
                    "08:00 - 14:00": "School time",
                    "14:00 - 14:30": "Return home",
                    "14:30 - 15:00": "Light snack and short rest",
                    "15:00 - 16:00": f"Study session 1: {subjects[0]}",
                    "16:00 - 16:15": "Short break with light physical activity",
                    "16:15 - 17:00": f"Study session 2: {subjects[1]}",
                    "17:00 - 18:00": "Outdoor play/sports/physical activity",
                    "18:00 - 18:30": "Evening snack and relaxation",
                    "18:30 - 19:15": "Homework completion and revision",
                    "19:15 - 20:00": "Dinner and family time",
                    "20:00 - 20:30": "Free time/light activities",
                    "20:30 - 21:00": "Prepare for bed and sleep"
                }
            else:  # weekend
                return {
                    "07:30 - 08:00": "Wake up naturally",
                    "08:00 - 08:30": "Morning routine",
                    "08:30 - 09:00": "Healthy breakfast and preparation",
                    "09:00 - 10:15": f"Fresh mind study: {subjects[0]}",
                    "10:15 - 10:45": "Active break (stretching/light exercise)",
                    "10:45 - 12:00": f"Focus session: {subjects[1]}",
                    "12:00 - 13:30": "Lunch and relaxation time",
                    "13:30 - 14:45": f"Interactive learning: {subjects[2]}",
                    "14:45 - 16:00": "Extended outdoor play/sports",
                    "16:00 - 16:30": "Snack and energy break",
                    "16:30 - 17:45": "Review and practice exercises",
                    "17:45 - 18:30": "Free time/hobby activities",
                    "18:30 - 19:30": "Dinner and family time",
                    "19:30 - 20:30": "Light revision or reading",
                    "20:30 - 21:30": "Free time and prepare for bed",
                    "21:30": "Bedtime"
                }

        # Create week-long schedule
        weekly_schedule = []
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        subjects_rotation = [
            profile.weak_areas[i % len(profile.weak_areas)] 
            for i in range(len(days) * 3)  # 3 subjects per day max
        ]

        for day_index, day in enumerate(days):
            is_weekend = day in ['Saturday', 'Sunday']
            day_type = "weekend" if is_weekend else "weekday"
            
            # Get subjects for this day
            start_idx = day_index * (3 if is_weekend else 2)
            subjects_for_day = subjects_rotation[start_idx:start_idx + (3 if is_weekend else 2)]

            # Calculate study duration based on pace
            base_duration = 4.0 if is_weekend else 2.5
            pace_multiplier = {
                StudyPace.SLOW: 0.8,
                StudyPace.MODERATE: 1.0,
                StudyPace.FAST: 1.2
            }[profile.preferred_pace]

            # Get style-specific activities
            style_activities = {
                LearningStyle.VISUAL: [
                    "Watch educational videos",
                    "Create mind maps",
                    "Study with diagrams",
                    "Use flashcards"
                ],
                LearningStyle.AUDITORY: [
                    "Listen to educational content",
                    "Group discussions",
                    "Verbal practice",
                    "Record and playback"
                ],
                LearningStyle.KINESTHETIC: [
                    "Hands-on experiments",
                    "Practice problems",
                    "Interactive exercises",
                    "Physical learning games"
                ]
            }[profile.learning_style]

            weekly_schedule.append({
                "day": day,
                "schedule": create_daily_schedule(day_type, subjects_for_day),
                "subjects": subjects_for_day,
                "duration": round(base_duration * pace_multiplier, 1),
                "activities": style_activities  # Fixed field name to match schema
            })

        template = {
            "weekly_schedule": weekly_schedule,
            "study_resources": self._get_default_resources(profile),
            "time_allocation": self._calculate_time_allocation(profile),
            "exercise_plan": [
                {
                    "type": "Daily Practice",
                    "target": subject,
                    "difficulty": profile.current_level
                }
                for subject in profile.weak_areas
            ],
            "progress_predictions": {
                "expected_improvement": self._calculate_expected_improvement(profile)
            }
        }
        
        return f"""
        Create a detailed daily study schedule following this exact JSON structure:
        {json.dumps(template, indent=2)}

        Requirements:
        1. Follow the exact time slots provided for each day
        2. Include these learning style activities for {profile.learning_style}:
        {', '.join(style_activities)}
        3. Maintain appropriate difficulty for {profile.current_level} level
        4. Focus on weak areas: {', '.join(profile.weak_areas)}
        5. Adjust pace according to {profile.preferred_pace} preference
        6. Include specific activities for each time slot
        7. Ensure proper balance between study and rest
        8. Resource formats: {', '.join([f.value for f in ResourceFormat])}

        Important Notes:
        - Keep activities age-appropriate
        - Include specific break activities
        - Maintain consistent meal times
        - Allow flexibility for unexpected events
        - Include daily physical activity
        - Ensure proper rest periods

        Return only valid JSON matching the StudyPlanRecommendation schema.
        """
    def _parse_response(self, response: str) -> StudyPlanRecommendation:
        try:
            return StudyPlanRecommendation.parse_raw(response)
        except Exception as e:
            error_details = "\n".join([f"{err['loc']}: {err['msg']}" for err in e.errors()])
            self.logger.error(f"Response validation failed:\n{error_details}")
            raise ValueError(f"Invalid response format:\n{error_details}")

    def _get_activities_for_style(self, style: LearningStyle) -> List[str]:
        activities = {
            LearningStyle.VISUAL: ["Video tutorials", "Diagram analysis", "Mind mapping"],
            LearningStyle.AUDITORY: ["Audio lectures", "Group discussions", "Verbal exercises"],
            LearningStyle.KINESTHETIC: ["Hands-on practice", "Interactive simulations", "Lab work"]
        }
        return activities.get(style, ["General practice", "Review exercises"])

    def _get_default_resources(self, profile: StudentProfile) -> List[dict]:
        resource_config = {
            LearningStyle.VISUAL: {
                "source": "Khan Academy",
                "base_url": "https://www.khanacademy.org",
                "format": ResourceFormat.VIDEO,
                "type": "Video Tutorial"
            },
            LearningStyle.AUDITORY: {
                "source": "Coursera Audio",
                "base_url": "https://www.coursera.org",
                "format": ResourceFormat.AUDIO,
                "type": "Audio Lecture"
            },
            LearningStyle.KINESTHETIC: {
                "source": "Brilliant Interactive",
                "base_url": "https://www.brilliant.org",
                "format": ResourceFormat.WEB,
                "type": "Interactive Lesson"
            }
        }
        config = resource_config.get(profile.learning_style)
        
        return [{
            "type": config["type"],
            "source": config["source"],
            "format": config["format"].value,
            "topics": [profile.weak_areas[0]],
            "match_style": profile.learning_style.value,
            "link": f"{config['base_url']}/{profile.weak_areas[0].lower().replace(' ', '-')}"
        }]

    def _calculate_time_allocation(self, profile: StudentProfile) -> Dict[str, float]:
        total_hours = float(profile.available_hours)
        num_areas = len(profile.weak_areas)
        base_allocation = total_hours / num_areas
        return {area: base_allocation for area in profile.weak_areas}

    def _calculate_expected_improvement(self, profile: StudentProfile) -> float:
        avg_performance = sum(profile.performance_history) / len(profile.performance_history)
        improvement_factors = {
            StudyPace.SLOW: 1.05,
            StudyPace.MODERATE: 1.10,
            StudyPace.FAST: 1.15
        }
        return min(100.0, avg_performance * improvement_factors[profile.preferred_pace])

    def _query_groq(self, prompt: str) -> str:
        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            return completion.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Groq API error: {str(e)}")
            raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Study Planning API")
    try:
        get_groq_config()
    except ValueError as e:
        logger.error(f"Startup failed: {str(e)}")
        raise
    yield
    logger.info("Shutting down Study Planning API")

app = FastAPI(
    title="Study Planning API",
    description="AI-powered study plan generation using Groq",
    version="2.0.0",
    lifespan=lifespan
)

@app.post("/generate_study_plan/", 
         response_model=StudyPlanRecommendation,
         summary="Generate personalized study plan",
         response_description="A detailed study plan tailored to the student's profile")
async def generate_study_plan(
    profile: StudentProfile,
    groq_config: GroqConfiguration = Depends(get_groq_config)
):
    try:
        logger.info(f"Generating study plan for {profile.learning_style} learner")
        engine = GroqRecommendationEngine(config=groq_config)
        plan = await engine.generate_recommendations(profile)
        logger.info("Study plan generated successfully")
        return plan
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate study plan")