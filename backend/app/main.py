from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import tempfile
import os

# 自作モジュールをインポート
from . import converter

app = FastAPI()

# --- CORS設定 ---
# フロントエンドのURL（Next.jsのデフォルト開発サーバー）
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # すべてのメソッドを許可
    allow_headers=["*"], # すべてのヘッダーを許可
)

# --- APIエンドポイント ---

@app.get("/")
def read_root():
    return {"message": "PDF Web Viewer API is running"}


@app.post("/upload", response_model=Dict[str, str])
async def upload_pdf(file: UploadFile = File(...)):
    """
    PDFファイルを受け取り、変換・整形したHTML文字列を返すAPI
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF is allowed.")

    # 一時ディレクトリを作成して、安全にファイルを処理する
    with tempfile.TemporaryDirectory() as temp_dir:
        pdf_temp_path = os.path.join(temp_dir, file.filename)
        
        try:
            # 1. アップロードされたPDFを一時ファイルに保存
            with open(pdf_temp_path, "wb") as f:
                content = await file.read()
                f.write(content)

            # 2. PDFをHTMLに変換 (converter.py)
            html_file_path = converter.convert_pdf_to_html(pdf_temp_path, temp_dir)
            
            # 3. HTMLを整形 (converter.py)
            cleaned_html = converter.clean_html(html_file_path)
            
            # 4. 整形済みHTMLをJSONで返す
            return {"html_content": cleaned_html}

        except FileNotFoundError as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail="HTML file not found after conversion.")
        except Exception as e:
            print(f"Error during file processing: {e}")
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
        
        # 'with tempfile.TemporaryDirectory()' ブロックを抜けると、
        # temp_dir とその中のファイル (一時PDF, 一時HTML) は自動的に削除される