import React, { useState } from 'react'

const SettingsPanel = ({ onClose, apiBase }) => {
  const [settings, setSettings] = useState({
    theme: 'auto',
    notifications: true,
    soundEnabled: true,
    autoScroll: true,
    messagePageSize: 50
  })

  const handleSave = () => {
    // 保存设置到 localStorage
    localStorage.setItem('appSettings', JSON.stringify(settings))
    onClose()
    
    // 可以在这里触发全局设置更新
    window.dispatchEvent(new CustomEvent('settingsUpdated', { detail: settings }))
  }

  const handleReset = () => {
    const defaultSettings = {
      theme: 'auto',
      notifications: true,
      soundEnabled: true,
      autoScroll: true,
      messagePageSize: 50
    }
    setSettings(defaultSettings)
  }

  const handleClearData = async () => {
    if (!confirm('确定要清除所有聊天数据吗？此操作不可恢复。')) {
      return
    }

    try {
      // 清除本地存储
      localStorage.clear()
      
      // 如果有API支持，也清除服务器数据
      if (apiBase) {
        // 这里可以添加清除服务器数据的API调用
        console.log('清除服务器数据...')
      }
      
      alert('数据清除成功！页面将刷新。')
      window.location.reload()
    } catch (error) {
      alert('数据清除失败，请稍后重试。')
    }
  }

  return (
    <div className="settings-modal-mask" onClick={onClose}>
      <div className="settings-modal-box" onClick={(e) => e.stopPropagation()}>
        {/* 头部 */}
        <div className="settings-header">
          <h3 className="settings-title">应用设置</h3>
          <button className="settings-close" onClick={onClose}>
            ✕
          </button>
        </div>

        {/* 设置内容 */}
        <div className="settings-body">
          {/* 外观设置 */}
          <div className="settings-section">
            <h4 className="section-title">🎨 外观设置</h4>
            
            <div className="setting-item">
              <label className="setting-label">主题模式</label>
              <select 
                className="setting-select"
                value={settings.theme}
                onChange={(e) => setSettings(prev => ({ ...prev, theme: e.target.value }))}
              >
                <option value="auto">跟随系统</option>
                <option value="light">浅色模式</option>
                <option value="dark">深色模式</option>
              </select>
            </div>
          </div>

          {/* 聊天设置 */}
          <div className="settings-section">
            <h4 className="section-title">💬 聊天设置</h4>
            
            <div className="setting-item">
              <label className="setting-label">
                <input
                  type="checkbox"
                  className="setting-checkbox"
                  checked={settings.autoScroll}
                  onChange={(e) => setSettings(prev => ({ ...prev, autoScroll: e.target.checked }))}
                />
                自动滚动到最新消息
              </label>
            </div>

            <div className="setting-item">
              <label className="setting-label">消息加载数量</label>
              <input
                type="number"
                className="setting-number"
                value={settings.messagePageSize}
                onChange={(e) => setSettings(prev => ({ ...prev, messagePageSize: parseInt(e.target.value) }))}
                min="10"
                max="200"
                step="10"
              />
            </div>
          </div>

          {/* 通知设置 */}
          <div className="settings-section">
            <h4 className="section-title">🔔 通知设置</h4>
            
            <div className="setting-item">
              <label className="setting-label">
                <input
                  type="checkbox"
                  className="setting-checkbox"
                  checked={settings.notifications}
                  onChange={(e) => setSettings(prev => ({ ...prev, notifications: e.target.checked }))}
                />
                启用桌面通知
              </label>
            </div>

            <div className="setting-item">
              <label className="setting-label">
                <input
                  type="checkbox"
                  className="setting-checkbox"
                  checked={settings.soundEnabled}
                  onChange={(e) => setSettings(prev => ({ ...prev, soundEnabled: e.target.checked }))}
                />
                启用提示音
              </label>
            </div>
          </div>

          {/* 数据管理 */}
          <div className="settings-section">
            <h4 className="section-title">🗂️ 数据管理</h4>
            
            <div className="setting-item">
              <button className="danger-btn" onClick={handleClearData}>
                清除所有数据
              </button>
              <p className="setting-hint">
                这将清除所有聊天记录、配置和缓存数据
              </p>
            </div>
          </div>
        </div>

        {/* 底部按钮 */}
        <div className="settings-footer">
          <button className="settings-btn secondary" onClick={handleReset}>
            重置设置
          </button>
          <button className="settings-btn primary" onClick={handleSave}>
            保存设置
          </button>
        </div>
      </div>
    </div>
  )
}

export default SettingsPanel
