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


def upload_jsonl(file_path: str, purpose="fine-tune"):
    try:
        with open(file_path, "rb") as f:
            print("file_path: ", file_path)
            response = openai.File.create(file=f, purpose=purpose)
            print("response: ", response)
            print("response type", type(response))
            return {
                "success": True,
                "message": "success to upload jsonl",
                "data": {"fileId": response["id"]}
            }
    except openai.error.APIError as e:
        print(e)
        return {
            "success": False,
            "message": "fail upload jsonl",
            "data": {}
        }


def get_file_list():
    try:
        response = openai.File.list()
        return {
            "success": True,
            "message": "success to get file list",
            "data": response["data"]
        }
    except openai.error.APIError as e:
        print(e)
        return {
            "success": False,
            "message": "fail to get file list",
            "data": {}
        }


def create_fine_tune_model(openai_file_id: str, model_name="test-fine-tune"):
    try:
        response = openai.FineTune.create(
            training_file=openai_file_id,
            model="curie",  # "ada", "babbage", "curie(default)", "davinci"
            suffix=model_name
            # n_epochs=1, # default: 4
            # batch_size=1, # default: null
        )
        return {
            "success": True,
            "message": "success to create fine tune",
            "data": response["id"]  # "ft-AF1WoRqd3aJAHsqc9NY7iL8F"
        }

    except openai.error.APIError as e:
        print(e)
        return {
            "success": False,
            "message": "fail to create fine tune",
            "data": {}
        }


def get_fine_tune_list():
    try:
        response = openai.FineTune.list()
        return {
            "success": True,
            "message": "success to get fine tune list",
            "data": response["data"]
        }
    except openai.error.APIError as e:
        print(e)
        return {
            "success": False,
            "message": "fail to get fine tune list",
            "data": {}
        }
