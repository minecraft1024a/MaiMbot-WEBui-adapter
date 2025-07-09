import React, { useState, useEffect } from 'react'

const defaultConfig = {
  user: {
    name: '用户',
    avatar: '',
  },
  bot: {
    name: '麦麦',
    avatar: '',
  },
}

const AvatarConfigModal = ({ visible, onClose, onSave, initialConfig }) => {
  const [config, setConfig] = useState(initialConfig || defaultConfig)

  // 当初始配置改变时更新本地状态
  useEffect(() => {
    if (initialConfig) {
      setConfig(initialConfig)
    }
  }, [initialConfig])

  // 重置状态当模态框关闭时
  useEffect(() => {
    if (!visible && initialConfig) {
      setConfig(initialConfig)
    }
  }, [visible, initialConfig])

  const handleChange = (role, field, value) => {
    setConfig(prev => ({
      ...prev,
      [role]: {
        ...prev[role],
        [field]: value,
      },
    }))
  }

  const handleImageChange = (role, e) => {
    const file = e.target.files[0]
    if (!file) return

    // 检查文件类型
    if (!file.type.startsWith('image/')) {
      alert('请选择图片文件')
      return
    }

    // 检查文件大小 (2MB限制)
    if (file.size > 2 * 1024 * 1024) {
      alert('头像图片不能超过2MB')
      return
    }

    const reader = new FileReader()
    reader.onload = (evt) => {
      handleChange(role, 'avatar', evt.target.result)
    }
    reader.onerror = () => {
      alert('文件读取失败')
    }
    reader.readAsDataURL(file)
    e.target.value = ''
  }

  const handleSave = () => {
    // 验证输入
    if (!config.user.name.trim()) {
      alert('请输入用户名字')
      return
    }
    if (!config.bot.name.trim()) {
      alert('请输入机器人名字')
      return
    }

    onSave(config)
  }

  const handleClose = () => {
    // 恢复到初始配置
    if (initialConfig) {
      setConfig(initialConfig)
    }
    onClose()
  }

  const clearAvatar = (role) => {
    handleChange(role, 'avatar', '')
  }

  if (!visible) return null

  return (
    <div className="avatar-modal-mask" onClick={handleClose}>
      <div className="avatar-modal-box" onClick={(e) => e.stopPropagation()}>
        {/* 模态框头部 */}
        <div className="avatar-modal-header">
          <h3 className="avatar-modal-title">头像和名字设置</h3>
          <button className="avatar-modal-close" onClick={handleClose}>
            ✕
          </button>
        </div>

        {/* 模态框内容 */}
        <div className="avatar-modal-body">
          {[
            { role: 'user', label: '用户', icon: '👤' },
            { role: 'bot', label: '机器人', icon: '🤖' }
          ].map(({ role, label, icon }) => (
            <div key={role} className="avatar-config-section">
              <div className="config-header">
                <span className="config-icon">{icon}</span>
                <span className="config-label">{label}配置</span>
              </div>

              <div className="config-row">
                <div className="config-field">
                  <label className="field-label">显示名字</label>
                  <input
                    type="text"
                    className="field-input"
                    value={config[role].name}
                    onChange={(e) => handleChange(role, 'name', e.target.value)}
                    placeholder={`输入${label}的显示名字`}
                    maxLength={20}
                  />
                </div>

                <div className="config-field">
                  <label className="field-label">头像URL</label>
                  <div className="avatar-input-group">
                    <input
                      type="text"
                      className="field-input avatar-url-input"
                      value={config[role].avatar}
                      onChange={(e) => handleChange(role, 'avatar', e.target.value)}
                      placeholder="输入头像URL或选择本地文件"
                    />
                    <label className="avatar-upload-btn">
                      <span>�</span>
                      <input
                        type="file"
                        accept="image/*"
                        style={{ display: 'none' }}
                        onChange={(e) => handleImageChange(role, e)}
                      />
                    </label>
                    {config[role].avatar && (
                      <button 
                        className="avatar-clear-btn"
                        onClick={() => clearAvatar(role)}
                        title="清除头像"
                      >
                        🗑️
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* 头像预览 */}
              <div className="avatar-preview-section">
                <div className="preview-label">预览效果：</div>
                <div className="avatar-preview">
                  <div className="preview-avatar">
                    {config[role].avatar ? (
                      <img 
                        src={config[role].avatar} 
                        alt="头像预览" 
                        onError={(e) => {
                          e.target.style.display = 'none'
                          e.target.nextElementSibling.style.display = 'flex'
                        }}
                      />
                    ) : (
                      <div className="default-preview-avatar">{icon}</div>
                    )}
                    <div className="avatar-error" style={{ display: 'none' }}>
                      ❌
                    </div>
                  </div>
                  <div className="preview-name">{config[role].name || `${label}名字`}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 模态框底部 */}
        <div className="avatar-modal-footer">
          <button className="avatar-modal-btn cancel" onClick={handleClose}>
            取消
          </button>
          <button className="avatar-modal-btn save" onClick={handleSave}>
            保存配置
          </button>
        </div>
      </div>
    </div>
  )
}

export default AvatarConfigModal
