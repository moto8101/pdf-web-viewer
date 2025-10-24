import axios from 'axios';

// FastAPIサーバーのURL
const API_URL = 'http://localhost:8000';

/**
 * PDFファイルをアップロードし、変換されたHTMLを受け取る
 * @param {File} file ユーザーが選択したPDFファイル
 * @param {Function} onUploadProgress アップロード進捗コールバック
 * @returns {Promise<string>} 整形済みのHTML文字列
 */
export const uploadPdf = async (file, onUploadProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post(`${API_URL}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress, // 進捗イベントをaxiosに渡す
    });
    
    // バックエンドから {"html_content": "..."} というJSONが返ってくる
    return response.data.html_content;

  } catch (error) {
    console.error("Error uploading file:", error);
    if (error.response) {
      // サーバーからのエラーレスポンス (500エラーなど)
      throw new Error(error.response.data.detail || 'Server error');
    } else if (error.request) {
      // サーバーにリクエストが届かなかった (CORSやネットワークエラー)
      throw new Error('Upload failed. Server is not reachable.');
    } else {
      // その他のエラー
      throw new Error(error.message);
    }
  }
};