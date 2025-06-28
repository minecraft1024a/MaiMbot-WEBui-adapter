import React, { useState } from 'react';

const CustomInputModal = ({ visible, title, placeholder, onOk, onCancel }) => {
  const [value, setValue] = useState('');
  if (!visible) return null;
  return (
    <div className="modal-mask">
      <div className="modal-box">
        <div className="modal-title">{title}</div>
        <input
          className="modal-input"
          type="text"
          placeholder={placeholder}
          value={value}
          onChange={e => setValue(e.target.value)}
          autoFocus
        />
        <div className="modal-actions">
          <button className="modal-btn ok" onClick={() => { onOk(value); setValue(''); }}>确定</button>
          <button className="modal-btn cancel" onClick={() => { onCancel(); setValue(''); }}>取消</button>
        </div>
      </div>
    </div>
  );
};

const Toolbar = ({ onChangeBackground, onChangeSprite }) => {
  const [modal, setModal] = useState({ type: '', visible: false });

  const openModal = (type) => setModal({ type, visible: true });
  const closeModal = () => setModal({ type: '', visible: false });
  const handleOk = (value) => {
    if (modal.type === 'bg' && onChangeBackground) onChangeBackground(value);
    if (modal.type === 'sprite' && onChangeSprite) onChangeSprite(value);
    closeModal();
  };

  return (
    <div className="toolbar custom-toolbar">
      <div className="toolbar-title">聊天立绘面板</div>
      <div className="toolbar-actions">
        <button className="toolbar-btn" onClick={() => openModal('bg')}>
          <span role="img" aria-label="bg">🖼️</span> 切换背景
        </button>
        <button className="toolbar-btn" onClick={() => openModal('sprite')}>
          <span role="img" aria-label="sprite">🎭</span> 切换立绘
        </button>
      </div>
      <CustomInputModal
        visible={modal.visible}
        title={modal.type === 'bg' ? '输入背景图片URL:' : '输入立绘图片URL:'}
        placeholder={modal.type === 'bg' ? '背景图片URL' : '立绘图片URL'}
        onOk={handleOk}
        onCancel={closeModal}
      />
    </div>
  );
};

export default Toolbar;
