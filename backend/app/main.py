from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import tempfile
import os

from . import converter # converter.py をインポート

app = FastAPI()

# (CORS設定はそのまま)
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "PDF Web Viewer API is running"}


@app.post("/upload", response_model=Dict[str, str])
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF is allowed.")

    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_temp_path = os.path.join(temp_dir, file.filename)
        
        try:
            # 1. PDFを一時保存
            with open(pdf_temp_path, "wb") as f:
                content = await file.read()
                f.write(content)

            # 2. PDFから生のテキストを抽出 (関数名変更)
            raw_text = converter.extract_text_from_pdf(pdf_temp_path)
            
            # 3. テキストをGemini APIでHTMLに整形 (関数名変更)
            cleaned_html = converter.format_text_with_gemini(raw_text)
            
            # 4. 整形済みHTMLを返す
            return {"html_content": cleaned_html}

        except FileNotFoundError as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail="File not found after conversion.")
        except Exception as e:
            print(f"Error during file processing: {e}")
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")