/pdf-web-viewer/
|
|-- backend/          (FastAPI サーバーサイド)
|   |-- app/
|   |   |-- __init__.py
|   |   |-- main.py         (FastAPIアプリ本体、/upload エンドポイント定義)
|   |   |-- converter.py    (Poppler と BeautifulSoup の処理ロジック)
|   |   `-- schemas.py      (APIのデータ型定義 Pydantic)
|   |
|   |-- requirements.txt  (fastapi, uvicorn, beautifulsoup4 など)
|   `-- .env.example      (環境変数設定例)
|
|-- frontend/         (Next.js クライアントサイド)
|   |-- pages/
|   |   |-- _app.js         (全ページ共通のAppコンポーネント)
|   |   |-- index.js        (メインのアップロード・閲覧ページ)
|   |   `-- _document.js
|   |
|   |-- components/       (Reactコンポーネント)
|   |   |-- UploadButton.js (ファイルアップロードボタン)
|   |   |-- StylePanel.js   (デザイン変更UI)
|   |   `-- HtmlViewer.js   (サーバーから受信したHTMLを描画する領域)
|   |
|   |-- styles/
|   |   |-- globals.css     (CSS変数 :root を定義)
|   |   `-- Home.module.css (index.js用のスタイル)
|   |
|   |-- lib/
|   |   `-- api.js          (バックエンドAPIを呼び出すfetch処理をまとめる)
|   |
|   |-- public/
|   |
|   `-- package.json
|
|-- .gitignore
`-- README.md         (プロジェクトの説明、起動方法)