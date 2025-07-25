import React, { useState, useEffect } from 'react'
import { themeAPI, apiKeyAPI, databaseAPI } from '../utils/api'

const SettingsPanel = ({ onClose }) => {
  const [settings, setSettings] = useState(() => {
    // 从localStorage加载已保存的设置
    const saved = localStorage.getItem('appSettings')
    return saved ? JSON.parse(saved) : {
      theme: 'auto',
      notifications: true,
      soundEnabled: true,
      autoScroll: true,
      messagePageSize: 50,
      chatColors: {
        userBubbleColor: '#667eea',
        botBubbleColor: '#f0f0f0',
        userTextColor: '#ffffff',
        botTextColor: '#333333'
      }
    }
  })

  // API密钥状态
  const [apiKeys, setApiKeys] = useState({
    siliconflow: ''
  })
  const [apiKeysLoaded, setApiKeysLoaded] = useState(false)

  // 加载API密钥
  useEffect(() => {
    loadApiKeys()
    loadTheme()
  }, [])

  const loadApiKeys = async () => {
    try {
      const response = await apiKeyAPI.getAll()
      if (response.keys) {
        const keyMap = {}
        response.keys.forEach(key => {
          keyMap[key.key] = key.value
        })
        setApiKeys(keyMap)
      }
      setApiKeysLoaded(true)
    } catch (error) {
      console.error('加载API密钥失败:', error)
      setApiKeysLoaded(true)
    }
  }

  const loadTheme = async () => {
    try {
      const response = await themeAPI.get()
      if (response.theme) {
        setSettings(prev => ({ ...prev, theme: response.theme }))
        updateTheme(response.theme)
      }
    } catch (error) {
      console.error('加载主题失败:', error)
    }
  }

  // 监听设置变化，实时更新样式
  useEffect(() => {
    updateChatColors(settings.chatColors)
    updateTheme(settings.theme)
  }, [settings.chatColors, settings.theme])

  // 应用主题设置
  const updateTheme = (theme) => {
    const root = document.documentElement
    
    if (theme === 'dark') {
      root.setAttribute('data-theme', 'dark')
    } else if (theme === 'light') {
      root.setAttribute('data-theme', 'light')
    } else {
      // 跟随系统
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      root.setAttribute('data-theme', prefersDark ? 'dark' : 'light')
    }
  }

  // 更新聊天框颜色的CSS变量
  const updateChatColors = (colors) => {
    const root = document.documentElement
    root.style.setProperty('--user-bubble-color', colors.userBubbleColor)
    root.style.setProperty('--bot-bubble-color', colors.botBubbleColor)
    root.style.setProperty('--user-text-color', colors.userTextColor)
    root.style.setProperty('--bot-text-color', colors.botTextColor)
  }

  const handleSave = async () => {
    try {
      // 保存主题设置到服务器
      await themeAPI.set(settings.theme)
      
      // 保存API密钥到服务器
      for (const [key, value] of Object.entries(apiKeys)) {
        if (value.trim()) {
          await apiKeyAPI.set(key, value)
        }
      }
      
      // 保存设置到 localStorage
      localStorage.setItem('appSettings', JSON.stringify(settings))
      updateChatColors(settings.chatColors)
      updateTheme(settings.theme)
      
      alert('设置保存成功！')
      onClose()
      
      // 触发全局设置更新事件
      window.dispatchEvent(new CustomEvent('settingsUpdated', { detail: settings }))
    } catch (error) {
      console.error('保存设置失败:', error)
      alert('保存设置失败: ' + error.message)
    }
  }

  const handleReset = () => {
    const defaultSettings = {
      theme: 'auto',
      notifications: true,
      soundEnabled: true,
      autoScroll: true,
      messagePageSize: 50,
      chatColors: {
        userBubbleColor: '#667eea',
        botBubbleColor: '#f0f0f0',
        userTextColor: '#ffffff',
        botTextColor: '#333333'
      }
    }
    setSettings(defaultSettings)
    setApiKeys({ siliconflow: '' })
    updateChatColors(defaultSettings.chatColors)
    updateTheme(defaultSettings.theme)
  }

  const handleClearData = async () => {
    if (!confirm('确定要清除所有聊天数据吗？此操作不可恢复。')) {
      return
    }

    try {
      // 清除服务器数据
      await databaseAPI.clearData()
      
      // 清除本地存储
      localStorage.clear()
      
      alert('数据清除成功！页面将刷新。')
      window.location.reload()
    } catch (error) {
      console.error('清除数据失败:', error)
      alert('数据清除失败: ' + error.message)
    }
  }

  const handleClearDatabase = async () => {
    if (!confirm('确定要删除整个数据库吗？此操作将删除数据库文件并重新初始化，不可恢复！')) {
      return
    }

    try {
      // 清空数据库文件
      await databaseAPI.clearDatabase()
      
      // 清除本地存储
      localStorage.clear()
      
      alert('数据库清空成功！页面将刷新。')
      window.location.reload()
    } catch (error) {
      console.error('清空数据库失败:', error)
      alert('清空数据库失败: ' + error.message)
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

            <div className="setting-item">
              <label className="setting-label">用户消息气泡颜色</label>
              <input
                type="color"
                className="color-picker"
                value={settings.chatColors.userBubbleColor}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  chatColors: { ...prev.chatColors, userBubbleColor: e.target.value }
                }))}
              />
            </div>

            <div className="setting-item">
              <label className="setting-label">机器人消息气泡颜色</label>
              <input
                type="color"
                className="color-picker"
                value={settings.chatColors.botBubbleColor}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  chatColors: { ...prev.chatColors, botBubbleColor: e.target.value }
                }))}
              />
            </div>

            <div className="setting-item">
              <label className="setting-label">用户消息文字颜色</label>
              <input
                type="color"
                className="color-picker"
                value={settings.chatColors.userTextColor}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  chatColors: { ...prev.chatColors, userTextColor: e.target.value }
                }))}
              />
            </div>

            <div className="setting-item">
              <label className="setting-label">机器人消息文字颜色</label>
              <input
                type="color"
                className="color-picker"
                value={settings.chatColors.botTextColor}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  chatColors: { ...prev.chatColors, botTextColor: e.target.value }
                }))}
              />
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
                清除数据
              </button>
              <p className="setting-hint">
                这将清除所有聊天记录、配置和缓存数据
              </p>
            </div>

            <div className="setting-item">
              <button className="danger-btn" onClick={handleClearDatabase}>
                删除数据库文件
              </button>
              <p className="setting-hint">
                这将删除数据库文件并重新初始化，比清除数据更彻底
              </p>
            </div>
          </div>

          {/* API配置 */}
          <div className="settings-section">
            <h4 className="section-title">🔑 API配置</h4>
            
            <div className="setting-item">
              <label className="setting-label">SiliconFlow API密钥</label>
              <input
                type="password"
                className="setting-input"
                placeholder="请输入语音转文字服务的API密钥"
                value={apiKeys.siliconflow || ''}
                onChange={(e) => setApiKeys(prev => ({ ...prev, siliconflow: e.target.value }))}
                disabled={!apiKeysLoaded}
              />
              <p className="setting-hint">
                用于语音转文字功能，从 SiliconFlow 获取
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
