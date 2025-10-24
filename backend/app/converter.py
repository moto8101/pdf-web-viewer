import subprocess
import os
import uuid
from bs4 import BeautifulSoup
import tempfile

def convert_pdf_to_html(pdf_temp_path: str, output_dir: str) -> str:
    """
    Popplerのpdftohtmlコマンドを実行し、構造化されたHTMLを生成する。
    """
    unique_name = str(uuid.uuid4())
    output_base_path = os.path.join(output_dir, unique_name)
    
    # 修正点: コマンドオプションの追加
    # -i: 画像を無視 (HTMLに埋め込まれない)
    # -fmt: フッター/ヘッダーを無視
    # -p: ページ区切りとして新しいファイルではなく、HTMLのHRタグを使用
    command = [
        "pdftohtml",
        "-s",        # 構造化モード
        "-noframes", # フレームなし
        "-i",        # 画像を無視
        "-fmt",      # フッター・ヘッダーを無視
        "-p",        # ページ区切りをHTMLの<hr>タグにする (これは後で削除するかも)
        pdf_temp_path,
        output_base_path
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
        
        print(f"--- pdftohtml STDOUT: {result.stdout}")
        print(f"--- pdftohtml STDERR: {result.stderr}")

    except subprocess.CalledProcessError as e:
        print(f"!!! pdftohtml command failed with code {e.returncode}")
        print(f"!!! STDOUT: {e.stdout}")
        print(f"!!! STDERR: {e.stderr}")
        raise Exception("PDF to HTML conversion failed (CalledProcessError)")
    
    files_in_output_dir = os.listdir(output_dir)
    print(f"--- Files in output directory: {files_in_output_dir}")

    generated_html_path = f"{output_base_path}.html" # -s をつけても .html で出力されることが多いので修正
    
    if not os.path.exists(generated_html_path):
        # もし .html がない場合、別のHTMLファイルを探す
        for file in files_in_output_dir:
            if file.startswith(unique_name) and file.endswith(".html"):
                print(f"--- Fallback: Using file {file} instead.")
                return os.path.join(output_dir, file) 

        raise FileNotFoundError(f"pdftohtml did not create the expected HTML file: {generated_html_path}")
            
    return generated_html_path


def clean_html(html_file_path: str) -> str:
    """
    pdftohtmlが生成したHTMLを読み込み、不要なタグを削除して整形する。
    さらに、意味のある段落に再構成する。
    """
    try:
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(html_file_path, 'r', encoding='shift_jis', errors='ignore') as f:
                content = f.read()

        soup = BeautifulSoup(content, 'html.parser')

        # 不要なタグを削除
        tags_to_remove = ['head', 'meta', 'title', 'style', 'script', 'img', 'hr'] # <hr>もページ区切りなので削除
        for tag_name in tags_to_remove:
            for tag in soup.find_all(tag_name):
                tag.decompose()
        
        for tag in soup.find_all(True): # True は「すべてのタグ」を意味します
            if 'style' in tag.attrs:
                del tag.attrs['style']

        body_content = soup.body if soup.body else soup # bodyがなければ全体を対象

        # --- 段落の再構成ロジック ---
        # pdftohtmlは <p> タグを必ずしも適切に使わないため、
        # 改行が多い箇所を新しい段落と見なして再構成する
        
        new_body_content = BeautifulSoup('', 'html.parser')
        current_paragraph_text = []

        # body_contentの子要素をループ
        for element in body_content.children:
            # テキストノードの場合
            if element.name is None: 
                text = str(element).strip()
                if text:
                    current_paragraph_text.append(text)
                
            # タグの場合 (例: <span>, <p>など)
            elif element.name:
                text = element.get_text(separator=' ', strip=True) # タグ内のテキストをスペース区切りで取得
                
                # pdftohtmlが生成する特定のdivやspanを段落区切りとして利用
                # 例: <div> や <p> で囲まれていても、中身が短いと改行とみなす
                if element.name in ['p', 'div'] and text:
                    # これまでのテキストがあれば段落化
                    if current_paragraph_text:
                        p_tag = soup.new_tag("p")
                        p_tag.string = " ".join(current_paragraph_text)
                        new_body_content.append(p_tag)
                        current_paragraph_text = []
                    
                    # 現在の要素も新しい段落として追加
                    p_tag = soup.new_tag("p")
                    p_tag.string = text
                    new_body_content.append(p_tag)
                elif text:
                    current_paragraph_text.append(text)
            
            # 連続する改行や空白だけの要素で段落を区切るヒントにする
            if str(element).strip() == "":
                if current_paragraph_text:
                    p_tag = soup.new_tag("p")
                    p_tag.string = " ".join(current_paragraph_text)
                    new_body_content.append(p_tag)
                    current_paragraph_text = []
        
        # ループ終了後に残ったテキストがあれば段落化
        if current_paragraph_text:
            p_tag = soup.new_tag("p")
            p_tag.string = " ".join(current_paragraph_text)
            new_body_content.append(p_tag)


        html_content = new_body_content.decode_contents()
        
        # 最終的なクリーンアップ (複数スペースの除去など)
        html_content = ' '.join(html_content.split())
            
        return html_content

    except Exception as e:
        print(f"An error occurred in clean_html: {e}")
        raise Exception("HTML cleaning failed")