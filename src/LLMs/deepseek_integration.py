import asyncio
import json
from typing import Dict
from dotenv import load_dotenv
from groq import Groq
from src.Models.static_assessment import LearningStyleType
from src.Models.base_student import Pace
from src.Models.recommendation_engine import ResourceFormat, StudentProfile, StudyPlanRecommendation
import os

load_dotenv()
class GroqConfiguration:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
    def get_groq_config(self):
        return self
class GroqRecommendationEngine:
    def __init__(self, config: GroqConfiguration):
        self.client = Groq(api_key=config.api_key)
        self.model_name = config.model_name

    async def generate_recommendations(self, profile: StudentProfile) -> StudyPlanRecommendation:
        try:
            prompt = self._create_prompt(profile)
            response = await asyncio.to_thread(self._query_groq, prompt)
            return self._parse_response(response)
        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            raise

    def _create_prompt(self, profile: StudentProfile) -> str:
        template = {
            "student_profile": {
                "weak_areas": profile.weak_areas,
                "learning_style": profile.learning_style.value,
                "preferred_pace": profile.preferred_pace.value,
                "performance_history": profile.performance_history,
                "available_hours": profile.available_hours
            }
        }
        
        return f"""
Your task is to generate a study plan in the exact JSON format provided below.

### **STRICT FORMAT RULES**
1. Your response **MUST** follow this **exact** JSON structure:
   - `"weekly_schedule"`
   - `"study_resources"`
   - `"time_allocation"`
   - `"exercise_plan"`
   - `"progress_predictions"`
2. **Ensure that `study_resources.match_style` is ONLY one of these values**:
   - `"visual"`
   - `"auditory"`
   - `"reading_writing"`
   - `"kinesthetic"`
   - ❌ `"textual"` is **NOT** allowed!
3. Each study resource should have a **different learning format** (e.g., audio, video, textbook, web).
4. **Subjects must not repeat in a single day's schedule.**
5. **Activities must be unique across different days.**
6. The student will study **5 hours each day**, with more time allocated to weak subjects and less to stronger subjects.
7. The subjects to be covered are **English, Math, Hindi, Science, and Social Science**.
8. Every day student should have **at least 4 activities**.
9. Every day student should have **at least 2 subjects**.
10. every day student study **5 hours**.

---

### **📌 Correct JSON Format**
{{
    "weekly_schedule": [
        {{
            "day": "Monday",
            "subjects": ["Mathematics", "Physics"],
            "duration": 5.0,
            "activities": [
                "Watch an educational video",
                "Solve practice problems",
                "Take notes",
                "Summarize key concepts"
            ]
        }}
    ],
    "study_resources": [
        {{
            "type": "Video Lecture",
            "source": "Khan Academy",
            "format": "video",
            "topics": ["Mathematics"],
            "match_style": "visual",
            "link": "https://www.khanacademy.org/math"
        }},
        {{
            "type": "Audio Lecture",
            "source": "Coursera",
            "format": "audio",
            "topics": ["Physics"],
            "match_style": "auditory",
            "link": "https://www.coursera.org/physics"
        }},
        {{
            "type": "Textbook",
            "source": "MIT OpenCourseWare",
            "format": "pdf",
            "topics": ["Physics"],
            "match_style": "reading_writing",
            "link": "https://ocw.mit.edu/courses/physics"
        }},
        {{
            "type": "Interactive Lab",
            "source": "PhET Simulations",
            "format": "web",
            "topics": ["Physics"],
            "match_style": "kinesthetic",
            "link": "https://phet.colorado.edu/"
        }}
    ],
    "time_allocation": {{
        "Mathematics": 2.0,
        "Physics": 2.0
    }},
    "exercise_plan": [
        {{
            "type": "Daily Practice",
            "target": "Mathematics",
            "difficulty": "intermediate"
        }}
    ],
    "progress_predictions": {{
        "expected_improvement": 85.4
    }}
}}

**⚠️ Important:** Follow the format strictly to get accurate recommendations.
- ACTIVITIES and SUBJECTS **MUST** be unique across different days. And ACTIVITIES must be based on the given subjects and learning style.
- `study_resources.match_style` **MUST** be `"visual"`, `"auditory"`, `"reading_writing"`, or `"kinesthetic"`.
- `study_resources.format` **MUST** be `"video"`, `"pdf"`, `"audio"`, or `"web"`.
- `exercise_plan.difficulty` **MUST** be `"beginner"`, `"intermediate"`, or `"advanced"`.     
- Ensure all constraints are followed before returning the response.
"""

    def _parse_response(self, response: str) -> StudyPlanRecommendation:
        try:
            response_json = json.loads(response)
            if "study_plan" in response_json:
                response_json = response_json["study_plan"]  # Extract correct data
            study_plan_recommendation = StudyPlanRecommendation(**response_json)
            return study_plan_recommendation
        except Exception as e:
            print(f"Response validation failed: {str(e)}")
            raise ValueError("Invalid response format.")


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
            print(f"Groq API error: {str(e)}")
            raise
