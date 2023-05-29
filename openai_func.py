from typing import Any, Generic, TypeVar
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ['OPENAI_API_KEY']

T = TypeVar("T")


class ResponseResult(BaseModel, Generic[T]):
    success: bool
    message: str
    data: T


class ResponseImage(BaseModel):
    url: str


def translate_description(description: str) -> ResponseResult[str | dict]:
    try:
        messages = [
            {"role": "system", "content": "You are a very helpful assistant that translates English to Korean."},
            {
                "role": "user",
                "content": f"'{description}'. 문장을 영어로 번역해 줘."
            }
        ]

        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, temperature=0)

        if response['choices'][0]['finish_reason'] == "stop":
            return ResponseResult(**{
                "success": True,
                "message": "success to translate",
                "data": response["choices"][0]["message"]["content"]
            })
        else:
            return ResponseResult(**{
                "success": False,
                "message": f"Request has not stopped. Finish Reason: {response['choices'][0]['finish_reason']}",
                "data": {}
            })
    except openai.error.APIError as e:
        return ResponseResult(**{
            "success": False,
            "message": f"Request has failed. Error: {e.code}",
            "data": {}
        })


def generate_image(prompt: str) -> ResponseResult[list[ResponseImage] | dict]:
    print("prompt: ", prompt)
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512",
        )

        return ResponseResult(**{
            "success": True,
            "message": "success to generate image",
            "data": response["data"]
        })
    except openai.error.APIError as e:
        return ResponseResult(**{
            "success": False,
            "message": f"Request has failed. Error: {e.code}",
            "data": {}
        })
