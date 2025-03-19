from datetime import datetime
from http.client import HTTPException
import os
import uuid
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import re
from pytubefix import YouTube
from src.Models.v2_video import VideoURL, SummaryOptions, SummaryRequest, SummaryResponse
from google import genai

load_dotenv()  

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class V2VideoServiceWrapper:
    def summarize_youtube_video(self, request : SummaryRequest) -> SummaryResponse:
        video_id = V2VideoService.extract_video_id(request.url)
        print(video_id)
        if not video_id:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        metadata = V2VideoService.get_video_metadata(video_id)
        if not metadata:
            raise HTTPException(status_code=400, detail="Error getting video metadata")
        transcript = V2VideoService.get_video_transcript(video_id)
        summary = V2VideoService.summarize_text(transcript, request.options)
        summary_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        response = {
            "id": summary_id,
            "summary": summary,
            "transcript": transcript,
            "metadata": {
                **metadata,
                "timestamp": timestamp,
                "video_id": video_id,
                "options": request.options.dict() if request.options else {},
            }
        }
        
        return response

class V2VideoService:
    
    @staticmethod
    def extract_video_id(url):
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:watch\?v=|\/)([0-9A-Za-z_-]{11})',
            r'youtu\.be\/([0-9A-Za-z_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def get_thumbnail(video_id):
        return f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"

    @staticmethod
    def get_video_transcript(video_id):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return ' '.join([line['text'] for line in transcript])
        except Exception as e:
            print(f"Error getting transcript: {str(e)}")
            return "None"

    @staticmethod
    def get_video_metadata(video_id):
        try:
            url = YouTube(f"http://youtube.com/watch?v={video_id}")
            return {  
                "title": url.title,
                "author": url.author,
                "length": url.length,
                "views": url.views,
                "thumbnail_url": url.thumbnail_url,
            }
        except Exception as e:
            print(f"Error getting metadata: {str(e)}")
            return {}
        
    @staticmethod
    def get_summary_prompt(text, options):
        format_instruction = ""
        length_instruction = ""
        
        if options.format == "bullet":
            format_instruction = "Format the summary as bullet points."
        elif options.format == "narrative":
            format_instruction = "Format the summary as a narrative."
        else:
            format_instruction = "Format the summary using markdown with headings, bullet points, and emphasis where appropriate."
            
        if options.length == "short":
            length_instruction = "Keep the summary very concise(about 100-150 words)."
        elif options.length == "long":
            length_instruction = "Provide a comprehensive summary covering all major points(about 400-500 words)."
        else:
            length_instruction = "Provide a balanced summary that covers all major points(about 200-300 words)."
        
        prompt = f"""Please summarize the following content:
        {text}
        {format_instruction} {length_instruction} Focus on the main ideas, key points, and conclusions. Include the most important details while removing redundancy."""
        
        return prompt

    @staticmethod
    def summarize_text(text, options=SummaryOptions()):
        try:
            prompt = V2VideoService.get_summary_prompt(text, options)
            # print(prompt)
            # messages = [
            #     {"role": "system", "content": "You are a helpful assistant that summarizes video content in a clear, concise manner."},
            #     {"role": "user", "content": prompt}
            # ]
            
            # response = gemini.generate_content(messages)
            # summary = response.text
            
            # if options.language and options.language.lower() != "english":
            #     translation_messages = [
            #         {"role": "system", "content": f"You are a translator. Translate the following text to {options.language}."},
            #         {"role": "user", "content": summary}
            #     ]
                
            #     translation_response = gemini.generate_content(translation_messages)
            #     summary = translation_response.text
            prompt += f'\n\nONLY provide the response in this language **{options.language.upper()}**'
            summary = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt])
                
            return summary.text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error summarizing text: {str(e)}")