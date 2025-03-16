import base64
from google import genai
from google.genai import types
import io
import httpx
import os
import pyshorteners


from src.Models.v2 import MindmapResponse

s = pyshorteners.Shortener()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
class V2Service:
    def summarise_pdf(self, long_context_pdf_path: str) -> str:
        # Retrieve and upload the PDF using the File API
        doc_io = io.BytesIO(httpx.get(long_context_pdf_path).content)
        sample_doc = client.files.upload(
            file=doc_io, 
            config=dict(mime_type='application/pdf')
        )
        prompt = "Summarize this document"
        response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[sample_doc, prompt])
        # print(response.text)
        return response.text
    

    def summarise_youtube(self, youtube_url: str) -> str:
        response = client.models.generate_content(
            model='models/gemini-2.0-flash',
            contents=types.Content(
                parts=[
                    types.Part(text='Can you summarize this video?'),
                    types.Part(
                        file_data=types.FileData(file_uri=youtube_url)
                    )
                ]
            )
        )
        # print(response.text)
        return response.text
    

    def generate_mindmap(self, topic: str) -> MindmapResponse:
        prompt = '''
        Your are the best mindmap generator in the world.
        For the given topic(s) generate all possible academically related subtopics and then create a mind map of the topic and its subtopics. 
        The mindmap should be comprehensive, **CONCISE** and complete,
        Return **ONLY** the mermaid code for the mind map. The mermaid code should be completely correct and should be able to generate the mind map without any further preprocessing.
        '''
        response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[topic, prompt]
        )

        # separating the mermaid code
        start_idx = response.text.find('mindmap')
        mermaid_code = response.text[start_idx:-4]  

        # generating url
        graphbytes = mermaid_code.encode("utf8")
        base64_bytes = base64.urlsafe_b64encode(graphbytes)
        base64_string = base64_bytes.decode("ascii")
        url = f'https://mermaid.ink/img/{base64_string}?theme=forest&width=1500&height=750&scale=3'

        return MindmapResponse(image_url=s.tinyurl.short(url), mermaid_code=mermaid_code)