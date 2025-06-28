import React, { useState } from 'react';

const CustomInputModal = ({ visible, title, placeholder, onOk, onCancel, isFile }) => {
  const [value, setValue] = useState('');
  if (!visible) return null;
  // 文件选择
  const handleFileChange = async e => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = evt => {
      // 直接 base64 传给 onOk
      onOk(evt.target.result);
      setValue('');
    };
    reader.readAsDataURL(file);
    e.target.value = '';
  };
  return (
    <div className="modal-mask">
      <div className="modal-box">
        <div className="modal-title">{title}</div>
        {isFile ? (
          <input
            className="modal-input"
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            autoFocus
          />
        ) : (
          <input
            className="modal-input"
            type="text"
            placeholder={placeholder}
            value={value}
            onChange={e => setValue(e.target.value)}
            autoFocus
          />
        )}
        <div className="modal-actions">
          {!isFile && <button className="modal-btn ok" onClick={() => { onOk(value); setValue(''); }}>确定</button>}
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
  const handleOk = async (value) => {
    if (modal.type === 'bg' && onChangeBackground) {
      // 如果是base64图片，上传到后端
      if (value.startsWith('data:image/')) {
        await fetch('http://127.0.0.1:8050/background', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: value })
        });
        onChangeBackground(value);
      } else {
        // url
        await fetch('http://127.0.0.1:8050/background', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: value })
        });
        onChangeBackground(value);
      }
    }
    if (modal.type === 'sprite' && onChangeSprite) {
      if (value.startsWith('data:image/')) {
        await fetch('http://127.0.0.1:8050/sprite', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: value })
        });
        onChangeSprite(value);
      } else {
        await fetch('http://127.0.0.1:8050/sprite', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: value })
        });
        onChangeSprite(value);
      }
    }
    closeModal();
  };

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
      <CustomInputModal
        visible={modal.visible}
        title={modal.type === 'bg' ? '选择或输入背景图片' : '选择或输入立绘图片'}
        placeholder={modal.type === 'bg' ? '背景图片URL' : '立绘图片URL'}
        isFile={modal.visible}
        onOk={async (value) => {
          if (modal.type === 'bg' && onChangeBackground) {
            if (value.startsWith('data:image/')) {
              await fetch('http://127.0.0.1:8050/background', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: value })
              });
              onChangeBackground(value);
            } else {
              await fetch('http://127.0.0.1:8050/background', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: value })
              });
              onChangeBackground(value);
            }
            closeModal(); // 选择完背景后自动关闭弹窗
          }
          if (modal.type === 'sprite' && onChangeSprite) {
            if (value.startsWith('data:image/')) {
              await fetch('http://127.0.0.1:8050/sprite', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: value })
              });
              onChangeSprite(value);
            } else {
              await fetch('http://127.0.0.1:8050/sprite', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: value })
              });
              onChangeSprite(value);
            }
            closeModal();
          }
        }}
        onCancel={closeModal}
      />
    </div>
  );
};

export default Toolbar;
