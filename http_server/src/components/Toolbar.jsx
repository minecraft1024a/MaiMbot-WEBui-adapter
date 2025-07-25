import React, { useState } from 'react'
import Modal from './Modal'
import { Image, User, Settings, Bot, UserCog } from 'lucide-react'

const Toolbar = ({ onChangeBackground, onChangeSprite, apiBase, onAvatarConfig, onOpenSettings }) => {
  const [modal, setModal] = useState({ type: '', visible: false })

  const openModal = (type) => setModal({ type, visible: true })
  const closeModal = () => setModal({ type: '', visible: false })

  const handleModalOk = async (value) => {
    if (!value || !apiBase) return

    try {
      if (modal.type === 'bg' && onChangeBackground) {
        await fetch(`${apiBase}/background`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: value })
        })
        onChangeBackground(value)
      } else if (modal.type === 'sprite' && onChangeSprite) {
        await fetch(`${apiBase}/sprite`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: value })
        })
        onChangeSprite(value)
      }
      closeModal()
    } catch (error) {
      console.error('Failed to update:', error)
      alert('更新失败，请稍后重试')
    }
  }

  return (
    <div className="toolbar">
      <div className="toolbar-content">
        <div className="toolbar-title">
          <Bot size={20} className="title-icon" />
          <span className="title-text">MaiMbot</span>
        </div>
        
        <div className="toolbar-divider"></div>
        
        <div className="toolbar-actions">
          <button 
            className="toolbar-btn"
            onClick={() => openModal('bg')}
            title="更换背景"
          >
            <Image size={14} className="btn-icon" />
            <span className="btn-text">背景</span>
          </button>
          
          <button 
            className="toolbar-btn"
            onClick={() => openModal('sprite')}
            title="更换立绘"
          >
            <User size={14} className="btn-icon" />
            <span className="btn-text">立绘</span>
          </button>
          
          <button 
            className="toolbar-btn avatar-btn"
            onClick={onAvatarConfig}
            title="头像设置"
          >
            <UserCog size={14} className="btn-icon" />
            <span className="btn-text">头像</span>
          </button>

          <button 
            className="toolbar-btn settings-btn"
            onClick={onOpenSettings}
            title="应用设置"
          >
            <Settings size={14} className="btn-icon" />
            <span className="btn-text">设置</span>
          </button>
        </div>
      </div>

      <Modal
        visible={modal.visible}
        title={modal.type === 'bg' ? '更换背景图片' : '更换立绘图片'}
        placeholder={modal.type === 'bg' ? '请输入背景图片URL或选择本地文件' : '请输入立绘图片URL或选择本地文件'}
        onOk={handleModalOk}
        onCancel={closeModal}
        type={modal.type}
      />
    </div>
  )
}

export default Toolbar
