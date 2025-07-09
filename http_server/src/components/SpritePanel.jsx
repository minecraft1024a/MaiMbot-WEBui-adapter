import React, { useRef, useState } from 'react'

const SpritePanel = ({ sprite, onChange, onAvatarConfig }) => {
  const fileInputRef = useRef(null)
  const [isLoading, setIsLoading] = useState(false)

  // 处理立绘文件选择
  const handleSpriteChange = (e) => {
    const file = e.target.files[0]
    if (!file) return

    // 检查文件类型
    if (!file.type.startsWith('image/')) {
      alert('请选择图片文件')
      return
    }

    // 检查文件大小 (10MB限制)
    if (file.size > 10 * 1024 * 1024) {
      alert('图片文件不能超过10MB')
      return
    }

    setIsLoading(true)
    const reader = new FileReader()
    reader.onload = (evt) => {
      const dataUrl = evt.target.result
      if (onChange) onChange(dataUrl)
      setIsLoading(false)
    }
    reader.onerror = () => {
      alert('文件读取失败')
      setIsLoading(false)
    }
    reader.readAsDataURL(file)
    e.target.value = '' // 清空文件输入
  }

  // 触发文件选择
  const triggerFileSelect = () => {
    fileInputRef.current?.click()
  }

  // 清除立绘
  const clearSprite = () => {
    if (onChange) onChange('')
  }

  return (
    <div className="sprite-panel">
      {/* 立绘显示区域 */}
      <div className="sprite-container">
        {sprite ? (
          <div className="sprite-wrapper">
            <img 
              src={sprite} 
              alt="立绘" 
              className={`sprite-img ${isLoading ? 'loading' : ''}`}
              onLoad={() => setIsLoading(false)}
              onError={() => {
                setIsLoading(false)
                console.error('立绘加载失败')
              }}
            />
            {isLoading && <div className="loading-overlay">加载中...</div>}
          </div>
        ) : (
          <div className="sprite-placeholder">
            <div className="placeholder-content">
              <div className="placeholder-icon">🖼️</div>
              <div className="placeholder-text">暂无立绘</div>
              <div className="placeholder-hint">点击下方按钮上传</div>
            </div>
          </div>
        )}
      </div>

      {/* 操作按钮组 */}
      <div className="sprite-actions">
        <button 
          className="action-btn primary"
          onClick={triggerFileSelect}
          disabled={isLoading}
          title="更换立绘"
        >
          {sprite ? '更换立绘' : '上传立绘'}
        </button>
        
        {sprite && (
          <button 
            className="action-btn secondary"
            onClick={clearSprite}
            disabled={isLoading}
            title="清除立绘"
          >
            清除
          </button>
        )}
        
        <button 
          className="action-btn avatar"
          onClick={onAvatarConfig}
          title="配置头像"
        >
          头像设置
        </button>
      </div>

      {/* 隐藏的文件输入 */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        style={{ display: 'none' }}
        onChange={handleSpriteChange}
      />
    </div>
  )
}

export default SpritePanel
