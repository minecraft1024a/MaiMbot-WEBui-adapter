import React, { useState } from 'react';
import ReactDOM from 'react-dom';

const Modal = ({ visible, title, placeholder, onOk, onCancel }) => {
  const [value, setValue] = useState('');
  if (!visible) return null;
  // 文件选择
  const handleFileChange = async e => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = evt => {
      onOk(evt.target.result);
      setValue('');
    };
    reader.readAsDataURL(file);
    e.target.value = '';
  };
  const modalContent = (
    <div className="modal-mask">
      <div className="modal-box">
        <div className="modal-title">{title}</div>
        <div className="modal-input-row">
          <input
            className="modal-input"
            type="text"
            placeholder={placeholder}
            value={value}
            onChange={e => setValue(e.target.value)}
            style={{ flex: 1, marginBottom: 0 }}
            autoFocus
          />
          <label className="modal-file-btn">
            选择文件
            <input
              type="file"
              accept="image/*"
              style={{ display: 'none' }}
              onChange={handleFileChange}
            />
          </label>
        </div>
        <div className="modal-actions">
          <button className="modal-btn ok" onClick={() => { onOk(value); setValue(''); }}>确定</button>
          <button className="modal-btn cancel" onClick={() => { onCancel(); setValue(''); }}>取消</button>
        </div>
      </div>
    </div>
  );
  return ReactDOM.createPortal(modalContent, document.body);
};

export default Modal;
