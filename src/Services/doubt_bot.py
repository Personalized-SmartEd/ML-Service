from typing import List, Optional
from src.Utils.find_docs import find_pdf
from src.LLMs.gemini_integration import GEMINI_API_KEY, GeminiClient
from src.Models.doubt_bot import DoubtBotRequest, DoubtBotResponse
from src.Models.static_assessment import SubjectType

from fastapi import HTTPException
import httpx
import base64
import google.generativeai as genai
from typing import Optional, Dict, List

class DoubtSolver:
    def __init__(self):
        self.gemini_api_key = GEMINI_API_KEY
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")
        self.response_schema = {
            "type": "object",
            "properties": {
                "explanation": {"type": "string"},
                "key_points": {"type": "array", "items": {"type": "string"}},
                "follow_up_questions": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["explanation", "follow_up_questions"]
        }

    def _construct_prompt(self, doubt: Dict, docs) -> str:
        student = doubt['student']
        prompt = f"""**Student Profile:**
            - Grade: {student['student_class']}th
            - Learning Style: {student['student_learning_style'].value.title()}
            - Performance: {student['student_performance_level'].value.title()}
            - Pace: {student['study_pace'].value.title()}

            **Question:** {doubt['doubt']['question']}
            """

        if docs:
            prompt += f"\n**Relevant Study Materials:**\n{docs}\n"

        if doubt['doubt']['image_description']:
            prompt += f"\n**Image Context:** {doubt['doubt']['image_description']}\n"

        prompt += """
            **Response Requirements:**
            1. Clear explanation tailored to student's profile
            2. 3-5 key points using kinesthetic learning examples
            3. 2-3 follow-up questions to assess understanding

            **Response Format:**
            Explanation: <start here>
            Key Points:
            - <point 1>
            - <point 2>
            Follow-up Questions:
            - <question 1>
            - <question 2>
        """
        return prompt

    def solve_doubt(self, doubt: Dict, docs) -> Dict:
        parts = []
        
        # Handle image if available
        if doubt['doubt']['image_url']:
            try:
                image = httpx.get(str(doubt['doubt']['image_url'])).content
                parts.append({
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(image).decode("utf-8"),
                })
            except Exception as e:
                print(f"Error loading image: {e}")
                raise HTTPException(status_code=303, detail='Error loading image,')

        # Add text prompt
        text_prompt = self._construct_prompt(doubt, docs)
        parts.append(text_prompt)

        # print('DEBUG: ', text_prompt)
        # Generate response
        response = self.model.generate_content(parts)
        
        # Parse response
        return self._parse_response(response.text)

    def _parse_response(self, response_text: str) -> Dict:
        sections = {
            "explanation": "",
            "key_points": [],
            "follow_up_questions": []
        }
        current_section = None
        
        for line in response_text.split('\n'):
            line = line.strip()
            if line.lower().startswith("explanation:"):
                current_section = "explanation"
                sections["explanation"] = line[len("explanation:"):].strip()
            elif line.lower().startswith("key points:"):
                current_section = "key_points"
            elif line.lower().startswith("follow-up questions:"):
                current_section = "follow_up_questions"
            elif current_section == "explanation":
                sections["explanation"] += " " + line
            elif current_section == "key_points" and line.startswith("-"):
                sections["key_points"].append(line[1:].strip())
            elif current_section == "follow_up_questions" and line.startswith("-"):
                sections["follow_up_questions"].append(line[1:].strip())
        
        # Clean up explanation
        sections["explanation"] = sections["explanation"].strip()
        
        return sections
    
    async def doubt_solver(self, request: DoubtBotRequest) -> DoubtBotResponse:
        # 1. get related documents from the vector-db
        course_context = find_pdf(
            student_class=request.student.student_class,
            subject=request.subject.value,
            chapter='',
            query=request.doubt.question
        )
        

        response = self.solve_doubt(request.model_dump(), course_context)
        # print('DEBUG: ', response)
        final_response = DoubtBotResponse(
            explanation=response['explanation'],
            keypoints=response['key_points'],
            follow_up_questions=response['follow_up_questions']
        )
        return final_response
        
