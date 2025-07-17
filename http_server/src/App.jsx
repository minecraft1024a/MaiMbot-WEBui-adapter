import React, { useState, useEffect, useCallback } from 'react'
import ChatPanel from './components/ChatPanel'
import SpritePanel from './components/SpritePanel'
import Background from './components/Background'
import Toolbar from './components/Toolbar'
import AvatarConfigModal from './components/AvatarConfigModal'
import SessionSelector from './components/SessionSelector'
import SettingsPanel from './components/SettingsPanel'
import './App.css'

function App() {
  // 状态管理
  const [background, setBackground] = useState('')
  const [sprite, setSprite] = useState('')
  const [messages, setMessages] = useState([])
  const [apiBase, setApiBase] = useState('')
  const [sessionId, setSessionId] = useState('default')
  const [showAvatarModal, setShowAvatarModal] = useState(false)
  const [showSettingsPanel, setShowSettingsPanel] = useState(false)
  
  // 头像配置状态
  const [avatarConfig, setAvatarConfig] = useState(() => {
    const saved = localStorage.getItem('avatarConfig')
    return saved ? JSON.parse(saved) : {
      user: { name: '用户', avatar: '' },
      bot: { name: '麦麦', avatar: '' }
    }
  })

  // 初始化API地址
  useEffect(() => {
    const initializeApiBase = async () => {
      try {
        const response = await fetch('/server_config.json')
        const config = await response.json()
        const baseUrl = config.host && config.port 
          ? `http://${config.host}:${config.port}` 
          : 'http://127.0.0.1:8050'
        setApiBase(baseUrl)
      } catch (error) {
        console.warn('Failed to load server config, using default:', error)
        setApiBase('http://127.0.0.1:8050')
      }
    }
    
    initializeApiBase()
  }, [])

  // 加载初始配置
  useEffect(() => {
    if (!apiBase) return

    const loadConfigurations = async () => {
      try {
        // 并行加载背景和立绘配置
        const [backgroundRes, spriteRes] = await Promise.all([
          fetch(`${apiBase}/background?session_id=${sessionId}`),
          fetch(`${apiBase}/sprite?session_id=${sessionId}`)
        ])
        
        const [backgroundData, spriteData] = await Promise.all([
          backgroundRes.json(),
          spriteRes.json()
        ])
        
        if (backgroundData.url) setBackground(backgroundData.url)
        if (spriteData.url) setSprite(spriteData.url)
      } catch (error) {
        console.error('Failed to load configurations:', error)
      }
    }

    loadConfigurations()
  }, [apiBase, sessionId])

  // 加载历史消息
  useEffect(() => {
    if (!apiBase) return;

    const fetchMessages = async () => {
      try {
        const response = await fetch(`${apiBase}/messages?session_id=${sessionId}`);
        const data = await response.json();
        
        const formattedMessages = data.map(msg => {
          const isFromWeb = msg.from_user === 'web';
          if (msg.type === 'image' || msg.image_b64) {
            const imageData = msg.image_b64 || msg.text;
            return {
              from: isFromWeb ? 'me' : 'other',
              text: '',
              image: imageData ? `data:image/png;base64,${imageData}` : undefined
            };
          }
          return {
            from: isFromWeb ? 'me' : 'other',
            text: msg.text || ''
          };
        });
        
        setMessages(formattedMessages);
      } catch (error) {
        console.error('Failed to fetch messages:', error);
      }
    };

    fetchMessages();
  }, [apiBase, sessionId]);

  // WebSocket连接
  useEffect(() => {
    if (!apiBase) return;

    const wsUrl = apiBase.replace(/^http/, 'ws') + `/ws/${sessionId}`;
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      
      const isFromWeb = msg.from_user === 'web';
      // 如果是自己发送的消息，我们已经通过乐观更新添加了，所以忽略
      if (isFromWeb) return;

      let newMessage;
      if (msg.type === 'image' || msg.image_b64) {
        const imageData = msg.image_b64 || msg.text;
        newMessage = {
          from: 'other',
          text: '',
          image: imageData ? `data:image/png;base64,${imageData}` : undefined
        };
      } else {
        newMessage = {
          from: 'other',
          text: msg.text || ''
        };
      }
      setMessages(prev => [...prev, newMessage]);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      ws.close();
    };
  }, [apiBase, sessionId]);

  // 发送文本消息
  const handleSendMessage = useCallback(async (text) => {
    if (!text.trim() || !apiBase) return

    // 立即更新UI
    setMessages(prev => [...prev, { from: 'me', text }])

    try {
      await fetch(`${apiBase}/send_message?session_id=${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          from_user: 'web', 
          text,
          type: 'text'
        })
      })
    } catch (error) {
      console.error('Failed to send message:', error)
      // 可以考虑在这里显示错误提示
    }
  }, [apiBase, sessionId])

  // 发送图片消息
  const handleSendImage = useCallback(async (base64) => {
    if (!apiBase) return

    // 立即更新UI
    setMessages(prev => [...prev, { 
      from: 'me', 
      text: '', 
      image: `data:image/png;base64,${base64}` 
    }])

    try {
      await fetch(`${apiBase}/send_message?session_id=${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          from_user: 'web', 
          type: 'image', 
          image_b64: base64, 
          text: '' 
        })
      })
    } catch (error) {
      console.error('Failed to send image:', error)
    }
  }, [apiBase, sessionId])

  // 更改背景
  const handleChangeBackground = useCallback(async (url) => {
    if (!url) return
    
    setBackground(url)
    
    if (apiBase) {
      try {
        await fetch(`${apiBase}/background?session_id=${sessionId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url })
        })
      } catch (error) {
        console.error('Failed to update background:', error)
      }
    }
  }, [apiBase, sessionId])

  // 更改立绘
  const handleChangeSprite = useCallback(async (url) => {
    if (!url) return
    
    setSprite(url)
    
    if (apiBase) {
      try {
        await fetch(`${apiBase}/sprite?session_id=${sessionId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url })
        })
      } catch (error) {
        console.error('Failed to update sprite:', error)
      }
    }
  }, [apiBase, sessionId])

  // 保存头像配置
  const handleSaveAvatarConfig = useCallback(async (config) => {
    setAvatarConfig(config)
    localStorage.setItem('avatarConfig', JSON.stringify(config))
    setShowAvatarModal(false)

    if (apiBase) {
      try {
        await fetch(`${apiBase}/avatar_config?session_id=${sessionId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(config)
        })
      } catch (error) {
        console.error('Failed to save avatar config:', error)
      }
    }
  }, [apiBase, sessionId])

  // 切换会话
  const handleSwitchSession = useCallback((id) => {
    setSessionId(id)
    setMessages([]) // 清空消息，等待新会话消息加载
  }, [])

  return (
    <div className="app-root">
      {/* 会话选择器 */}
      <SessionSelector
        currentSession={sessionId}
        onSessionChange={handleSwitchSession}
      />
      
      {/* 背景层 */}
      <Background image={background} />
      
      {/* 主要内容区域 */}
      <div className="main-content">
        <div className="left-panel">
          <ChatPanel 
            messages={messages}
            onSend={handleSendMessage}
            onSendImage={handleSendImage}
            avatarConfig={avatarConfig}
          />
        </div>
        
        <div className="right-panel">
          <SpritePanel 
            sprite={sprite}
            onChange={handleChangeSprite}
            onAvatarConfig={() => setShowAvatarModal(true)}
          />
        </div>
      </div>
      
      {/* 工具栏 */}
      <Toolbar
        onChangeBackground={handleChangeBackground}
        onChangeSprite={handleChangeSprite}
        onAvatarConfig={() => setShowAvatarModal(true)}
        onOpenSettings={() => setShowSettingsPanel(true)}
        apiBase={apiBase}
      />
      
      {/* 头像配置弹窗 */}
      <AvatarConfigModal
        visible={showAvatarModal}
        onClose={() => setShowAvatarModal(false)}
        onSave={handleSaveAvatarConfig}
        initialConfig={avatarConfig}
      />
      
      {/* 设置面板 */}
      {showSettingsPanel && (
        <SettingsPanel
          onClose={() => setShowSettingsPanel(false)}
          apiBase={apiBase}
        />
      )}
    </div>
  )
}

export default App
