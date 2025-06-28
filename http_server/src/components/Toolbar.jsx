import React, { useState } from 'react';
import Modal from './Modal';

const Toolbar = ({ onChangeBackground, onChangeSprite }) => {
  const [modal, setModal] = useState({ type: '', visible: false });

  const openModal = (type) => setModal({ type, visible: true });
  const closeModal = () => setModal({ type: '', visible: false });

  return (
    <div className="toolbar custom-toolbar">
      <div className="toolbar-title" style={{background: 'rgba(255,255,255,0.5)', borderRadius: 12, padding: '2px 12px'}}>聊天立绘面板</div>
      <div className="toolbar-actions">
        <button className="toolbar-btn" onClick={() => openModal('bg')}>
          <span role="img" aria-label="bg">🖼️</span> 切换背景
        </button>
        <button className="toolbar-btn" onClick={() => openModal('sprite')}>
          <span role="img" aria-label="sprite">🎭</span> 切换立绘
        </button>
      </div>
      <Modal
        visible={modal.visible}
        title={modal.type === 'bg' ? '选择或输入背景图片' : '选择或输入立绘图片'}
        placeholder={modal.type === 'bg' ? '背景图片URL' : '立绘图片URL'}
        onOk={async (value) => {
          if (!value) return;
          if (modal.type === 'bg' && onChangeBackground) {
            await fetch('http://127.0.0.1:8050/background', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ url: value })
            });
            onChangeBackground(value);
            closeModal();
          }
          if (modal.type === 'sprite' && onChangeSprite) {
            await fetch('http://127.0.0.1:8050/sprite', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ url: value })
            });
            onChangeSprite(value);
            closeModal();
          }
        }}
        onCancel={closeModal}
      />
    </div>
  );
};

export default Toolbar;
