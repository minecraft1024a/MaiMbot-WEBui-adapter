import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'

const Modal = ({ visible, title, placeholder, onOk, onCancel, type }) => {
  const [value, setValue] = useState('')
  const [isFileMode, setIsFileMode] = useState(false)

  // 重置状态当模态框关闭时
  useEffect(() => {
    if (!visible) {
      setValue('')
      setIsFileMode(false)
    }
  }, [visible])

  if (!visible) return null

  // 处理文件选择
  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (!file) return

    // 检查文件类型
    if (!file.type.startsWith('image/')) {
      alert('请选择图片文件')
      return
    }

    // 检查文件大小
    const maxSize = type === 'sprite' ? 10 * 1024 * 1024 : 5 * 1024 * 1024 // 立绘10MB，背景5MB
    if (file.size > maxSize) {
      alert(`图片文件不能超过${Math.floor(maxSize / 1024 / 1024)}MB`)
      return
    }

    const reader = new FileReader()
    reader.onload = (evt) => {
      onOk(evt.target.result)
      setValue('')
    }
    reader.onerror = () => {
      alert('文件读取失败')
    }
    reader.readAsDataURL(file)
    e.target.value = ''
  }

  // 处理确定按钮
  const handleOk = () => {
    if (value.trim()) {
      onOk(value.trim())
      setValue('')
    }
  }

  // 处理取消按钮
  const handleCancel = () => {
    onCancel()
    setValue('')
  }

  // 处理键盘事件
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleOk()
    } else if (e.key === 'Escape') {
      handleCancel()
    }
  }

  const modalContent = (
    <div className="modal-mask" onClick={handleCancel}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        {/* 模态框头部 */}
        <div className="modal-header">
          <h3 className="modal-title">{title}</h3>
          <button className="modal-close" onClick={handleCancel}>
            ✕
          </button>
        </div>

        {/* 模态框内容 */}
        <div className="modal-body">
          {/* 选项卡 */}
          <div className="modal-tabs">
            <button 
              className={`modal-tab ${!isFileMode ? 'active' : ''}`}
              onClick={() => setIsFileMode(false)}
            >
              URL输入
            </button>
            <button 
              className={`modal-tab ${isFileMode ? 'active' : ''}`}
              onClick={() => setIsFileMode(true)}
            >
              本地文件
            </button>
          </div>

          {/* 内容区域 */}
          <div className="modal-content">
            {!isFileMode ? (
              /* URL 输入模式 */
              <div className="url-input-section">
                <input
                  className="modal-input"
                  type="text"
                  placeholder={placeholder}
                  value={value}
                  onChange={(e) => setValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  autoFocus
                />
                <div className="input-hint">
                  支持网络图片URL或本地图片的data:image格式
                </div>
              </div>
            ) : (
              /* 文件上传模式 */
              <div className="file-upload-section">
                <label className="file-upload-area">
                  <div className="upload-icon">📁</div>
                  <div className="upload-text">点击选择图片文件</div>
                  <div className="upload-hint">
                    支持 JPG、PNG、GIF 格式，大小不超过 {type === 'sprite' ? '10MB' : '5MB'}
                  </div>
                  <input
                    type="file"
                    accept="image/*"
                    style={{ display: 'none' }}
                    onChange={handleFileChange}
                  />
                </label>
              </div>
            )}
          </div>
        </div>

        {/* 模态框底部 */}
        <div className="modal-footer">
          <button className="modal-btn cancel" onClick={handleCancel}>
            取消
          </button>
          <button 
            className="modal-btn ok" 
            onClick={handleOk}
            disabled={!value.trim() && !isFileMode}
          >
            确定
          </button>
        </div>
      </div>
    </div>
  )

  return ReactDOM.createPortal(modalContent, document.body)
}

export default Modal
