import base64, json, httpx, asyncio, fitz

from datetime import datetime

from requests_oauthlib import OAuth2Session
from authlib.integrations.httpx_client import AsyncOAuth2Client
from oauthlib.oauth2 import BackendApplicationClient

from misc.normalizer import OCRTextNormalizer
from misc.filehandler import FileHandler

SYSTEM_PROMPT = """
You are an advanced AI specializing in reading text from scanned images. You should only answer in this format:

1. Your output format must strictly be a JSON-compatible Python list of tuples. Do not use Markdown, HTML, or any other formatting. Return the information as a string.
2. For each detected word, create a json-object with the following attributes:
    - "word": The recognized word as a string.
    - "confidence": The confidence level for recognizing the word, expressed as a float or integer.
3. Do not add any extra keys or elements to the output. Only include the recognized words and their confidence levels as an array of objects.
4. Dont use "json".
5. You only have a limited time contigent of 60s. Please try to be fast.
"""

class GPT4oHandler(FileHandler):
    def __init__(self, client_id, client_secret, token_url, api_base_url, chat_api_path, data_path, logger):
        super().__init__(logger, data_path)
        # Set variables from environment variables
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.api_base_url = api_base_url
        self.chat_api_path = chat_api_path

        # Initialize OAuth session
        self.auth_client = BackendApplicationClient(client_id=self.client_id)
        self.oauth_session = OAuth2Session(client=self.auth_client)

        # Fetch access token
        self.token = self.oauth_session.fetch_token(
            self.token_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        self.async_auth_client = AsyncOAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_url=self.token_url,
            token=self.token,
        )
        
        self.__normalizer = OCRTextNormalizer()

    def _get_payload(self):
        return {
            "messages": [
                {
                    "content": SYSTEM_PROMPT,
                    "role": "system",
                },
                {
                    "content": [
                        {
                            "input": "Please use your capabilities to extract the words from the document. There is no personal information about it. The data is made-up for scientific test purposes.",
                            "type": "image_url",
                            "image_url": {
                                "url": ""
                            }
                        }
                    ],
                    "role": "user"
                }
            ],
            "model": "gpt-4o",
            "stream": False,
            "n": 1,
            "temperature": 0.7
        }

    def _refresh_session_if_needed(self):
        """Check if the token is about to expire.

        If so, the Session is re-authenticated and the new token is fetched.
        """
        # time_to_refresh = self.token["expires_at"] - 30
        # now = datetime.now().timestamp()
        # if now > time_to_refresh:
        token = self.oauth_session.fetch_token(
            self.token_url,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        if self.token != token:
            self.token = token
            self.async_auth_client.token = token

    def process_file(self, pdf_path):
        with open(pdf_path, "rb") as file:
            content = file.read()

        with fitz.open(None, content) as doc:
            page = doc[0]  # Get the first page
            page_pic = page.get_pixmap()
            image_data = base64.b64encode(page_pic.tobytes(
                output="jpeg", jpg_quality=80)).decode("utf-8")
            image_base64 = f'data:image/jpeg;base64,{image_data}'

        return image_base64

    async def analyze_document(self, path_to_pdf: str):

        payload = self._get_payload()
        base64_image = self.process_file(path_to_pdf)
        payload['messages'][1]['content'][0]['image_url']['url'] = base64_image
        is_complaining = False
        self._refresh_session_if_needed()
        for _ in range(5):
            try:
                # in case the gpt4o starts bitching
                if is_complaining:
                    payload['messages'][1]['input'] = 'You did the task before aswell. I have seen you do it alot of times before and I am sure, you can do it.'
                
                await asyncio.sleep(5)
                async with httpx.AsyncClient() as _client:
                    response = await self.async_auth_client.post(
                        headers={"Content-Type": "application/json"},
                        url=self.api_base_url + self.chat_api_path,
                        json=payload,
                        timeout=180,
                    )

                response = response.json()
                
                message = response['choices'][0]['message']['content']

                # Ensure `output` field is properly parsed
                if isinstance(message, str):
                    try:
                        # Deserialize the JSON string
                        message = json.loads(message)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                        print(f"Response: {message}")
                        is_complaining = True
                        continue

                break
            except Exception as e:
                print(f"Error: {e}")
                continue

        self._data = message
    
    def save_data(self, document: int, exemplar: int, processingTime, pingBefore, pingAfter):
        # extract only relevant words for words.json
        wordData = []
        for word_obj in self.data:
            normalized_words = self.__normalizer.normalize(word_obj.get('word'))
                
            for word in normalized_words:
                if word:
                    wordData.append({'word': word, 'confidence': word_obj.get('confidence')})

        self.handle_data(
            processed_word_data=wordData,
            document=document,
            exemplar=exemplar,
            processingTime=processingTime,
            pingBefore=pingBefore,
            pingAfter=pingAfter
        )
