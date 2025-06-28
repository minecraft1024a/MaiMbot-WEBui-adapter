import React, { useState } from 'react';

const ChatPanel = ({ messages, onSend, onSendImage }) => {
  const [input, setInput] = useState('');
  const [imgPreview, setImgPreview] = useState(null);

  const handleSend = () => {
    if (input.trim()) {
      onSend(input);
      setInput('');
    }
  };

  // 图片选择并转base64
  const handleImageChange = e => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new window.FileReader();
    reader.onload = evt => {
      const base64 = evt.target.result.split(',')[1];
      if (onSendImage) onSendImage(base64);
    };
    reader.readAsDataURL(file);
    e.target.value = '';
  };

  // 点击图片放大
  const handleImgClick = (src) => {
    setImgPreview(src);
  };
  // 关闭预览
  const closePreview = () => setImgPreview(null);

  return (
    <div className="chat-panel">
      <div className="chat-messages">
        {messages.map((msg, idx) => {
          let prefix = '';
          if (msg.from === 'me') {
            prefix = '用户: ';
          } else if (msg.from === 'other') {
            prefix = '麦麦: ';
          }
          return (
            <div key={idx} className={`chat-message ${msg.from === 'me' ? 'me' : 'other'}`}>
              {msg.text && <span>{prefix}{msg.text}</span>}
              {msg.image && (
                <img
                  src={msg.image}
                  alt="图片消息"
                  style={{maxWidth: 180, maxHeight: 180, display: 'block', marginTop: 6, borderRadius: 8, cursor: 'pointer'}} 
                  onClick={() => handleImgClick(msg.image)}
                />
              )}
            </div>
          );
        })}
      </div>
      <div className="chat-input-bar">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          placeholder="输入消息..."
        />
        {/* 图片上传按钮 */}
        <label style={{ cursor: 'pointer', marginLeft: 8 }}>
          <span role="img" aria-label="上传图片">🖼️</span>
          <input
            type="file"
            accept="image/*"
            style={{ display: 'none' }}
            onChange={handleImageChange}
          />
        </label>
        <button onClick={handleSend}>发送</button>
      </div>
      {/* 全屏图片预览 */}
      {imgPreview && (
        <div className="img-preview-mask" onClick={closePreview}>
          <img className="img-preview" src={imgPreview} alt="预览" onClick={e => e.stopPropagation()} />
        </div>
      )}
    </div>
  );
};

export default ChatPanel;
