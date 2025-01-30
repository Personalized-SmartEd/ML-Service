from src.Models.doubt_bot import DoubtBotRequest, DoubtBotResponse, VisualAnnotation


class DoubtBotService:
    async def solve_doubt(self, request: DoubtBotRequest) -> DoubtBotResponse:
        """Process single doubt without any history"""
        # Mock implementation - integrate actual AI here
        return DoubtBotResponse(
            explanation="This is the solution to your doubt about...",
            visual_annotations=[
                VisualAnnotation(
                    coordinates=[0.2, 0.3, 0.4, 0.5],
                    explanation="Relevant diagram section",
                    annotation_type="highlight"
                )
            ],
            follow_up_questions=["Would you like more details about any specific part?"]
        )