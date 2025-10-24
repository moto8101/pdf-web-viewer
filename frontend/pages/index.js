import Head from 'next/head';
import { useState } from 'react';
import { uploadPdf } from '../lib/api'; // さっき作ったAPIモジュール
import HtmlViewer from '../components/HtmlViewer'; // HTML表示コンポーネント

// --- スタイルパネル ---
const StylePanel = () => {
  // フォントサイズ変更
  const changeFontSize = (direction) => {
    const root = document.documentElement;
    // 現在のフォントサイズを取得 (例: "18px")
    const currentSizeStr = getComputedStyle(root).getPropertyValue('--main-font-size') || '18px';
    // "px" を取り除いて数値に
    let currentSize = parseFloat(currentSizeStr);

    if (direction === 'increase') {
      currentSize += 1;
    } else {
      currentSize -= 1;
    }
    // CSS変数を更新
    root.style.setProperty('--main-font-size', `${currentSize}px`);
  };

  // テーマ変更
  const changeTheme = (themeName) => {
    // body のクラスを切り替える (globals.css で定義済み)
    document.body.className = themeName ? `theme-${themeName}` : '';
  };

  return (
    <div style={{ padding: '10px', borderBottom: '1px solid #ccc', textAlign: 'center' }}>
      <strong>デザイン変更:</strong>
      <button onClick={() => changeFontSize('decrease')}>A-</button>
      <button onClick={() => changeFontSize('increase')}>A+</button>
      <button onClick={() => changeTheme(null)}>ライト</button>
      <button onClick={() => changeTheme('dark')}>ダーク</button>
      <button onClick={() => changeTheme('sepia')}>セピア</button>
    </div>
  );
};

// --- メインページ ---
export default function Home() {
  const [htmlContent, setHtmlContent] = useState(''); // サーバーから受け取ったHTML
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // ファイルが選択されたときの処理
  const handleFileChange = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setIsLoading(true);
    setError(null);
    setHtmlContent(''); // 古い内容をクリア

    try {
      // APIを呼び出してHTMLを取得
      const html = await uploadPdf(file, (progressEvent) => {
        console.log(`Upload Progress: ${Math.round((progressEvent.loaded * 100) / progressEvent.total)}%`);
      });
      setHtmlContent(html);

    } catch (err) {
      setError(err.message || 'ファイルの変換に失敗しました。');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <Head>
        <title>PDF Web Viewer</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      </Head>

      <header>
        {/* スタイル変更パネル */}
        <StylePanel />

        {/* ファイルアップロード */}
        <div style={{ padding: '20px', textAlign: 'center', borderBottom: '1px solid #ccc' }}>
          <input type="file" accept="application/pdf" onChange={handleFileChange} disabled={isLoading} />
        </div>
      </header>

      <main>
        {isLoading && <p style={{ textAlign: 'center' }}>変換中...</p>}
        {error && <p style={{ textAlign: 'center', color: 'red' }}>エラー: {error}</p>}
        
        {/* HTML描画エリア */}
        {!isLoading && htmlContent && <HtmlViewer htmlString={htmlContent} />}
        
        {!isLoading && !htmlContent && !error && (
          <p style={{ textAlign: 'center', color: '#888', marginTop: '50px' }}>
            PDFファイルをアップロードしてください
          </p>
        )}
      </main>
    </div>
  );
}
