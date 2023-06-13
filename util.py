import os
from pathlib import Path
import uuid


async def fine_tune_save_file(file):
    print("file: ", file)
    # 파일 저장 폴더 생성
    UPLOAD_DIR = Path("./fine_tuning")
    UPLOAD_DIR.mkdir(exist_ok=True)

    # 파일 읽고 폴더에 저장
    file_content = await file.read()
    file_name_without_ext, _ = os.path.splitext(file.filename)
    file_name = f"{file_name_without_ext}-{str(uuid.uuid4())}.txt"

    with open(os.path.join(UPLOAD_DIR, file_name), "wb") as fp:
        fp.write(file_content)

    return {"fileName": file_name, "filePath": f"{str(UPLOAD_DIR)}/{file_name}"}
