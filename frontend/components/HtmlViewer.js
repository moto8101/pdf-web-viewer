import React from 'react';

/**
 * サーバーから受け取ったHTML文字列を安全に描画するコンポーネント
 * @param {{ htmlString: string }} props
 */
const HtmlViewer = ({ htmlString }) => {
  return (
    <div className="html-content-wrapper">
      {/* dangerouslySetInnerHTML はXSS脆弱性のリスクがあるが、
        今回はバックエンドで <script> タグなどを除去しているため、
        リスクを理解した上で使用する。
      */}
      <div dangerouslySetInnerHTML={{ __html: htmlString }} />
    </div>
  );
};

export default HtmlViewer;