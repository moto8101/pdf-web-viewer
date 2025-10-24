import subprocess
import os
import tempfile
from dotenv import load_dotenv

# SDKドキュメントに基づくインポート
from google import genai
from google.genai import types

# .env ファイルから環境変数を読み込む
# Client() は自動的に 'GEMINI_API_KEY' または 'GOOGLE_API_KEY' を環境変数から読み取ります
load_dotenv() 

def extract_text_from_pdf(pdf_temp_path: str) -> str:
    """
    Popplerの「pdftotext」コマンドを実行し、
    PDFから生のテキスト文字列を抽出する。(変更なし)
    """
    
    command = [
        "pdftotext",
        "-layout",   # レイアウトをある程度維持してテキスト化
        "-enc", "UTF-8",
        pdf_temp_path, # 入力ファイル
        "-"          # 結果を標準出力(stdout)に出す
    ]
    
    print(f"--- Running command: {' '.join(command)}")
    
    try:
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='ignore'
        )
        print("--- pdftotext text extraction successful.")
        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"!!! pdftotext command failed: {e.stderr}")
        raise Exception("PDF to Text conversion failed")
    except FileNotFoundError:
        print("!!! エラー: 'pdftotext' コマンドが見つかりません。Popplerが正しくインストールされ、Pathが通っているか確認してください。")
        raise

def format_text_with_gemini(raw_text: str) -> str:
    """
    抽出した生のテキストをGemini APIに渡し、HTMLに整形させる。
    (SDKドキュメントの Client パターンを使用)
    """
    
    # APIキーが環境変数に設定されているか確認
    if "GEMINI_API_KEY" not in os.environ and "GOOGLE_API_KEY" not in os.environ:
        print("!!! エラー: GEMINI_API_KEY が .env ファイルに設定されていません。")
        raise Exception("APIキーが設定されていません。")

    system_prompt = """
    あなたはPDFのテキストをHTMLに整形するエキスパートです。
    以下のルールに従い、入力された生のテキストをクリーンなHTMLに変換してください。

    ルール:
    1. 元のPDFに含まれるであろうヘッダー、フッター、ページ番号は完全に削除してください。
    2. 文書タイトルと思われる部分は <h1> タグで囲んでください。
    3. 主要なセクション見出し（例: "1. Introduction", "ABSTRACT"）は <h2> タグで囲んでください。
    4. サブセクションの見出しは <h3> タグで囲んでください。
    5. 本文の段落は <p> タグで囲んでください。
    6. 意味のない改行や余分なスペースは削除し、自然な文章の流れにしてください。
    7. 出力はHTMLの本文（<body>の中身）のみとし、<html>や<body>タグ自体は含めないでください。
    8. style属性やclass属性は一切追加しないでください。
    """
    
    user_prompt = f"以下のテキストを整形してください:\n\n---\n{raw_text}\n---"

    print("--- Calling Gemini API for HTML formatting...")
    
    try:
        # ドキュメント推奨のコンテキストマネージャを使用
        with genai.Client() as client:
            response = client.models.generate_content(
                model='gemini-2.5-flash', # または 'gemini-2.5-flash'
                contents=user_prompt, #
                config=types.GenerateContentConfig(
                    # system_instruction の設定方法
                    system_instruction=system_prompt 
                )
            )
            
            cleaned_html = response.text
            print("--- Gemini API formatting successful.")
            return cleaned_html

    except Exception as e:
        # エラーハンドリング
        # (ここでは汎用的な Exception をキャッチ)
        print(f"!!! Gemini API Error: {e}")
        raise Exception(f"Gemini APIでの整形中にエラーが発生しました: {e}")