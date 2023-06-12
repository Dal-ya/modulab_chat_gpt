import os
import uuid
from fastapi import FastAPI, APIRouter, UploadFile
import uvicorn
import subprocess
from dto import PaintDTO, CreatePaintDTO
from openai_func import translate_description, generate_image


app = FastAPI()
router = APIRouter(prefix="/api")


@router.get("/")
async def root():
    return {"message": "Hello World"}


@router.post("/paint", response_model=PaintDTO)
async def create_paint(paint: CreatePaintDTO) -> PaintDTO:
    translate_description_result = translate_description(paint.description)

    if translate_description_result.success:
        prompt = f"{translate_description_result.data}, depicted in the style of {paint.author}'s paintings."
        generate_image_result = generate_image(prompt)
        if generate_image_result.success:
            return PaintDTO(**{
                "success": True,
                "message": "success to create paint",
                "data": generate_image_result.data
            })
        else:
            return PaintDTO(**{
                "success": False,
                "message": generate_image_result.message,
                "data": {}
            })
    else:
        return PaintDTO(**{
            "success": False,
            "message": translate_description_result.message,
            "data": {}
        })


@router.get('/cmd')
async def cmd():
    # test python system call
    cmd_msg = "ls -al"
    return_cmd_value = subprocess.call(cmd_msg, shell=True)
    print(f"result: {return_cmd_value}")
    # return_cmd_value = subprocess.check_output(cmd_msg)
    # return {"message": return_cmd_value.decode("utf-8")}
    return {"message": return_cmd_value}


@router.post('/create-fine-tune')
async def create_fine_tune(file: UploadFile):
    UPLOAD_DIR = "./fine_tuning"
    file_content = await file.read()
    file_name = f"{file.filename}-{str(uuid.uuid4())}.txt"
    with open(os.path.join(UPLOAD_DIR, file_name), "wb") as fp:
        fp.write(file_content)  # 서버 로컬 스토리지에 이미지 저장 (쓰기)

    return {"fileName": file_name}


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
