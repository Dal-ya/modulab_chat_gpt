import mimetypes
import os
from pathlib import Path
import uuid
import openai
from fastapi import HTTPException, UploadFile


async def fine_tune_save_file(file: UploadFile):
    try:
        # 파일 확장자 확인
        if not mimetypes.guess_type(file.filename)[0].startswith("text/"):
            raise HTTPException(status_code=400, detail="올바른 텍스트 파일을 업로드 해야 합니다.")

        # 파일 저장 폴더 생성
        UPLOAD_DIR = Path("./fine_tuning")
        UPLOAD_DIR.mkdir(exist_ok=True)

        # 파일 읽고 폴더에 저장
        file_content = await file.read()
        file_name_without_ext, _ = os.path.splitext(file.filename)
        file_name = f"{file_name_without_ext}-{str(uuid.uuid4())}.txt"

        with open(os.path.join(UPLOAD_DIR, file_name), "wb") as fp:
            fp.write(file_content)

        return {
            "success": True,
            "message": "success to save file",
            "data": {
                "fileName": file_name,
                "filePath": os.path.join(UPLOAD_DIR, file_name)
            }
        }

    except Exception as e:
        print(str(e))
        return {"success": False, "message": "fail to save file", "data": {}}


# Jaehun-JaydenJa's util code
def get_gpt3_responses(chunk: str, QUESTION_COUNT=5, TEMPERATURE_VALUE=0.5):
    # Create chat message with the request for the assistant
    messages = [{
        "role":
            "system",
        "content":
            "You are an assistant that generates JSONL prompts and completions based on input parts from a novel for "
            "fine tuning."
    }, {
        "role":
            "user",
        "content":
            f"다음의 <> 안에 오는 내용에 대한 직접적인 질문과 그 질문에 대한 답변의 쌍 {QUESTION_COUNT}개를 한국어로 생성하여 그 결과만 반드시 {{\"prompt\": "
            f"\"질문\",\"completion\": \"답변\"}}의 jsonl 포맷으로 출력해. each line의 마지막, 즉 }} 문자 다음에는 개행문자를 반드시 추가해. jsonl 포맷 "
            f"데이터 이외의 내용은 절대 출력하면 안돼. 모든 Question의 처음 부분에 [황순원 소설 소나기]라는 문구를 꼭 추가해. 질문과 답변을 만들때 반드시 <> 내의 내용만 한정해서 "
            f"사용하고 없는 내용을 상상해서 지어내면 안돼. 확실히 알수 없는 답변이 있으면 내용을 절대 상상하지 말고 해당 질문 답변 쌍을 출력에서 제외해. 질문시에 용어에 대한 질문과 등장인물에게 "
            f"물어보는 질문은 절대 하면 안돼. <{chunk}>"
    }]

    # Generate response from OpenAI's gpt-3.5-turbo

    try:
        print(
            f"openai.ChatCompletion API is being called to create {QUESTION_COUNT} Q&A pairs"
        )
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                messages=messages,
                                                temperature=TEMPERATURE_VALUE)

        if response['choices'][0]['finish_reason'] == "stop":  # 성공
            print("The API Request has completed, Finish Reason: stop")

            # Extract assistant's reply
            return response['choices'][0]['message']['content']
        else:  # 실패
            print(
                f"The API request has not stopped, Finish Reason: {response['choices'][0]['finish_reason']}"
            )
            return None

    except openai.error.APIError as e:  # 에러
        print(f"The API request has failed, Error: {str(e)}")
        return None


# Jaehun-JaydenJa's util code
def create_jsonl(file_name: str, file_path: str, CHUNK_SIZE=500):
    try:
        with open(file_path, "r") as input_file:
            data = input_file.read()

        # Replace newline characters with space and replace quotes with apostrophes
        data = data.replace('\n', ' ').replace('"', "'")

        chunks = [data[i:i + CHUNK_SIZE] for i in range(0, len(data), CHUNK_SIZE)]

        # 파일 저장 폴더 생성
        JSONL_DIR = Path("./jsonl_files")
        JSONL_DIR.mkdir(exist_ok=True)

        file_name_without_ext, _ = os.path.splitext(file_name)
        jsonl_file_name = f"{file_name_without_ext}-{str(uuid.uuid4())}.jsonl"

        with open(os.path.join(JSONL_DIR, jsonl_file_name), "w") as output_file:
            for chunk in chunks:
                response: str = get_gpt3_responses(chunk)
                if response is None:
                    Exception("The get_gpt3_responses has failed")

                # Write response directly to output.jsonl
                output_file.write(response + "\n")

        return {"success": True, "message": "success to create jsonl file", "data": {
            "fileName": jsonl_file_name,
            "filePath": os.path.join(JSONL_DIR, jsonl_file_name)
        }}
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"success": False, "message": "fail to create jsonl file", "data": {}}
