from fastapi import FastAPI, APIRouter, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import subprocess
from dto import PaintDTO, CreatePaintDTO, APIResponse
from openai_func import translate_description, generate_image
from util import fine_tune_save_file, create_jsonl

app = FastAPI()

# CORS middleware 등록 (선택적)
app.add_middleware(CORSMiddleware, allow_origins=["*"])

router = APIRouter(prefix="/api")


@router.get("/", response_model=APIResponse[str])
async def root():
    try:
        return {"success": True, "message": "success get message", "data": "Hello World"}
    except Exception as e:
        print(e)
        return {"success": False, "message": "Request has failed", "data": {}}


@router.post("/paint", response_model=PaintDTO)
async def create_paint(paint: CreatePaintDTO) -> PaintDTO:  # fastapi test
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


@router.post('/create-fine-tune', response_model=APIResponse[str])
async def create_fine_tune(file: UploadFile):
    try:
        fine_tune_save_file_result = await fine_tune_save_file(file)
        print(f"fine_tune_save_file_result: {fine_tune_save_file_result['data']}")

        if not fine_tune_save_file_result["success"]:
            print(fine_tune_save_file_result["message"])
            Exception("fail to save file")

        file_name = fine_tune_save_file_result["data"]["fileName"]
        file_path = fine_tune_save_file_result["data"]["filePath"]

        create_jsonl_result = create_jsonl(file_name, file_path)
        print(f"create_jsonl_result: {create_jsonl_result['data']}")

        if not create_jsonl_result["success"]:
            print(create_jsonl_result["message"])
            Exception("fail to create jsonl")

        return {
            "success": True,
            "message": "success to create fine tune",
            "data": {}
        }

    except Exception as e:
        print(e)
        return {"success": False, "message": "fail to create fine tune", "data": {}}


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
