import React, { useState, useRef, useEffect } from 'react'

const ChatPanel = ({ messages, onSend, onSendImage, avatarConfig }) => {
  const [input, setInput] = useState('')
  const [imgPreview, setImgPreview] = useState(null)
  const messagesEndRef = useRef(null)
  const fileInputRef = useRef(null)

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // 发送消息
  const handleSend = () => {
    if (input.trim()) {
      onSend(input)
      setInput('')
    }
  }

  // 处理键盘事件
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // 图片选择处理
  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (!file) return

    // 检查文件类型
    if (!file.type.startsWith('image/')) {
      alert('请选择图片文件')
      return
    }

    // 检查文件大小 (5MB限制)
    if (file.size > 5 * 1024 * 1024) {
      alert('图片文件不能超过5MB')
      return
    }

    const reader = new FileReader()
    reader.onload = (evt) => {
      const base64 = evt.target.result.split(',')[1]
      if (onSendImage) onSendImage(base64)
    }
    reader.readAsDataURL(file)
    e.target.value = '' // 清空文件输入
  }

  // 点击图片放大
  const handleImgClick = (src) => {
    setImgPreview(src)
  }

  // 关闭预览
  const closePreview = (e) => {
    if (e) e.stopPropagation()
    setImgPreview(null)
  }

  // 触发文件选择
  const triggerFileSelect = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="chat-panel">
      {/* 消息列表 */}
      <div className="chat-messages">
        {messages.map((msg, idx) => {
          const isMe = msg.from === 'me'
          const role = isMe ? 'user' : 'bot'
          const name = avatarConfig?.[role]?.name || (isMe ? '用户' : '麦麦')
          const avatar = avatarConfig?.[role]?.avatar

          return (
            <div key={idx} className={`message-wrapper ${isMe ? 'me' : 'other'}`}>
              {/* 头像 */}
              {!isMe && (
                <div className="message-avatar">
                  {avatar ? (
                    <img src={avatar} alt={name} />
                  ) : (
                    <div className="default-avatar">🤖</div>
                  )}
                </div>
              )}

              {/* 消息内容 */}
              <div className="message-content">
                <div className="message-header">
                  <span className="message-name">{name}</span>
                  <span className="message-time">
                    {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                
                <div className={`message-bubble ${isMe ? 'me' : 'other'}`}>
                  {msg.text && <div className="message-text">{msg.text}</div>}
                  {msg.image && (
                    <img
                      src={msg.image}
                      alt="图片消息"
                      className="message-image"
                      onClick={() => handleImgClick(msg.image)}
                    />
                  )}
                </div>
              </div>

              {/* 我的头像 */}
              {isMe && (
                <div className="message-avatar">
                  {avatar ? (
                    <img src={avatar} alt={name} />
                  ) : (
                    <div className="default-avatar">👤</div>
                  )}
                </div>
              )}
            </div>
          )
        })}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入栏 */}
      <div className="chat-input-bar">
        <div className="input-group">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入消息... (按 Enter 发送)"
            className="message-input"
          />
          
          <button 
            className="attachment-btn"
            onClick={triggerFileSelect}
            title="发送图片"
          >
            📷
          </button>
          
          <button 
            className="send-btn"
            onClick={handleSend}
            disabled={!input.trim()}
            title="发送消息"
          >
            发送
          </button>
        </div>

        {/* 隐藏的文件输入 */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          style={{ display: 'none' }}
          onChange={handleImageChange}
        />
      </div>

      {/* 全屏图片预览 */}
      {imgPreview && (
        <div className="img-preview-mask" onClick={closePreview}>
          <div className="img-preview-container">
            <img 
              className="img-preview" 
              src={imgPreview} 
              alt="预览" 
              onClick={(e) => e.stopPropagation()} 
            />
            <button className="preview-close" onClick={closePreview}>
              ✕
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default ChatPanel
