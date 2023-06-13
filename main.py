from fastapi import FastAPI, APIRouter, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import subprocess
from dto import PaintDTO, CreatePaintDTO, APIResponse, CreateFineTuneNameDTO
from openai_func import translate_description, generate_image, upload_jsonl, get_file_list, create_fine_tune_model, \
    get_fine_tune_list
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
async def create_fine_tune(file: UploadFile, modelName: str = Form(...)):
    try:
        # 텍스트 파일 저장
        fine_tune_save_file_result = await fine_tune_save_file(file)
        if not fine_tune_save_file_result["success"]:
            print(fine_tune_save_file_result["message"])
            Exception("fail to save file")

        file_name = fine_tune_save_file_result["data"]["fileName"]
        file_path = fine_tune_save_file_result["data"]["filePath"]

        # jsonl 파일 생성
        create_jsonl_result = create_jsonl(file_name, file_path)
        if not create_jsonl_result["success"]:
            print(create_jsonl_result["message"])
            Exception("fail to create jsonl")

        # jsonl 파일 업로드
        upload_jsonl_result = upload_jsonl(create_jsonl_result["data"]["filePath"])
        if not upload_jsonl_result["success"]:
            print(upload_jsonl_result["message"])
            Exception("fail to upload jsonl")

        # fine tune 모델 생성
        create_fine_tune_model_result = create_fine_tune_model(upload_jsonl_result["data"]["fileId"], modelName)
        if not create_fine_tune_model_result["success"]:
            print(create_fine_tune_model_result["message"])
            Exception("fail to create fine tune")

        # print("create_fine_tune_model_result: ", create_fine_tune_model_result)

        return {
            "success": True,
            "message": "success to create fine tune",
            "data": {}
        }

    except Exception as e:
        print(str(e))
        return {"success": False, "message": "fail to create fine tune", "data": {}}


@router.get('/list-file')
async def list_file():
    try:
        get_file_list_result = get_file_list()
        if not get_file_list_result["success"]:
            print(get_file_list_result["message"])
            Exception("fail to get file list")

        return {
            "success": True,
            "message": "success to get file list",
            "data": get_file_list_result["data"]
        }

    except Exception as e:
        print(str(e))
        return {"success": False, "message": "fail to get file list", "data": {}}


@router.get('/list-fine-tune')
async def list_fine_tune():
    try:
        get_fine_tune_list_result = get_fine_tune_list()
        if not get_fine_tune_list_result["success"]:
            print(get_fine_tune_list_result["message"])
            Exception("fail to get fine tune list")

        return {
            "success": True,
            "message": "success to get fine tune list",
            "data": get_fine_tune_list_result["data"]
        }

    except Exception as e:
        print(str(e))
        return {"success": False, "message": "fail to get fine tune list", "data": {}}


@router.post('/test')
async def test_post(file: UploadFile, modelName: str = Form(...)):
    print(file.filename)
    print("modelName: ", modelName)
    return {"message": f"{modelName} ..."}


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
