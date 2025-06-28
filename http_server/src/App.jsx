import React, { useState } from 'react'
import ChatPanel from './components/ChatPanel';
import SpritePanel from './components/SpritePanel';
import Background from './components/Background';
import Toolbar from './components/Toolbar';
import './App.css'

function App() {
  // 背景和立绘的图片url
  const [background, setBackground] = React.useState('');
  const [sprite, setSprite] = React.useState('');
  // 聊天消息
  const [messages, setMessages] = React.useState([]);
  const [input, setInput] = React.useState('');
  // 后端API地址
  const [apiBase, setApiBase] = React.useState('');

  // 动态获取后端host/port
  React.useEffect(() => {
    fetch('/server_config.json')
      .then(res => res.json())
      .then(cfg => {
        if (cfg.host && cfg.port) {
          setApiBase(`http://${cfg.host}:${cfg.port}`);
        } else {
          setApiBase('http://127.0.0.1:8050');
        }
      })
      .catch(() => setApiBase('http://127.0.0.1:8050'));
  }, []);

  // 获取初始背景和立绘
  React.useEffect(() => {
    if (!apiBase) return;
    fetch(`${apiBase}/background`)
      .then(res => res.json())
      .then(data => { if (data.url) setBackground(data.url); });
    fetch(`${apiBase}/sprite`)
      .then(res => res.json())
      .then(data => { if (data.url) setSprite(data.url); });
  }, [apiBase]);

  // 拉取所有消息（包括适配器回复）
  React.useEffect(() => {
    if (!apiBase) return;
    const fetchMessages = async () => {
      try {
        const res = await fetch(`${apiBase}/messages`);
        const data = await res.json();
        setMessages(data.map(msg => {
          let from = 'other';
          if (msg.from_user === 'web') from = 'me';
          // 图片消息适配
          if (msg.type === 'image' || msg.image_b64) {
            let b64 = msg.image_b64 || msg.text;
            return {
              from,
              text: '',
              image: b64 ? `data:image/png;base64,${b64}` : undefined
            };
          }
          return { from, text: msg.text };
        }));
      } catch (e) {}
    };
    fetchMessages();
    const timer = setInterval(fetchMessages, 2000);
    return () => clearInterval(timer);
  }, [apiBase]);

  // 聊天输入框回车发送
  const handleInputKeyDown = e => {
    if (e.key === 'Enter') {
      handleSendMessage(input);
      setInput('');
    }
  };

  // 发送消息
  const handleSendMessage = async (msg) => {
    if (!msg || !apiBase) return;
    setMessages(prev => [...prev, { from: 'me', text: msg }]);
    try {
      await fetch(`${apiBase}/send_message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ from_user: 'web', text: msg })
      });
    } catch (e) {}
  };

  // 发送图片消息
  const handleSendImage = async (base64) => {
    if (!apiBase) return;
    setMessages(prev => [...prev, { from: 'me', text: '', image: `data:image/png;base64,${base64}` }]);
    try {
      await fetch(`${apiBase}/send_message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ from_user: 'web', type: 'image', image_b64: base64, text: '' })
      });
    } catch (e) {}
  };

  // 切换背景
  const handleChangeBackground = (url) => {
    if (url) setBackground(url);
    if (!apiBase) return;
    fetch(`${apiBase}/background`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
  };

  // 切换立绘
  const handleChangeSprite = (url) => {
    if (url) setSprite(url);
    if (!apiBase) return;
    fetch(`${apiBase}/sprite`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
  };

  return (
    <div className="app-root">
      <Background image={background} />
      <div className="main-content">
        <div className="left-panel">
          <ChatPanel messages={messages} onSend={handleSendMessage} onSendImage={handleSendImage} />
        </div>
        <div className="right-panel">
          <SpritePanel sprite={sprite} onChange={handleChangeSprite} />
        </div>
      </div>
      <Toolbar onChangeBackground={handleChangeBackground} onChangeSprite={handleChangeSprite} apiBase={apiBase} />
    </div>
  );
}

export default App
