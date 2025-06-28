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
  // 用户昵称
  const [nickname, setNickname] = React.useState(() => localStorage.getItem('nickname') || 'web用户');
  const [editingName, setEditingName] = React.useState(false);
  const [nicknameInput, setNicknameInput] = React.useState(nickname);
  // 聊天消息
  const [messages, setMessages] = React.useState([]);

  // 首次进入弹窗输入昵称
  React.useEffect(() => {
    if (!localStorage.getItem('nickname')) {
      let name = '';
      while (!name) {
        name = window.prompt('请输入你的昵称（用于聊天展示）', 'web用户') || '';
      }
      setNickname(name);
      localStorage.setItem('nickname', name);
    }
  }, []);

  // 获取初始背景和立绘
  React.useEffect(() => {
    // TODO: 调用后端API获取初始背景和立绘
    // setBackground(...)
    // setSprite(...)
  }, []);

  // 获取昵称（数据库/后端）
  React.useEffect(() => {
    fetch('http://127.0.0.1:8050/get_nickname')
      .then(res => res.json())
      .then(data => {
        if (data.nickname) {
          setNickname(data.nickname);
          setNicknameInput(data.nickname);
          localStorage.setItem('nickname', data.nickname);
        }
      })
      .catch(() => {});
  }, []);

  // 修改昵称
  const handleSaveNickname = async () => {
    setEditingName(false);
    setNickname(nicknameInput);
    localStorage.setItem('nickname', nicknameInput);
    // 通知后端保存
    await fetch('http://127.0.0.1:8050/set_nickname', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nickname: nicknameInput })
    });
  };

  // 切换背景
  const handleChangeBackground = (url) => {
    if (url) setBackground(url);
    // TODO: 通知后端切换背景
  };

  // 切换立绘
  const handleChangeSprite = (url) => {
    if (url) setSprite(url);
    // TODO: 通知后端切换立绘
  };

  // 发送消息
  const handleSendMessage = async (msg) => {
    if (!msg) return;
    setMessages(prev => [...prev, { from: 'me', text: msg, nickname }]);
    try {
      const res = await fetch('http://127.0.0.1:8050/send_message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ from_user: 'web', text: msg, nickname })
      });
      if (!res.ok) {
        const err = await res.text();
        console.error('[前端] 消息发送失败，后端响应:', err);
      } else {
        console.log('[前端] 消息已发送到 /send_message 并由后端转发');
      }
    } catch (e) {
      console.error('[前端] 消息发送失败', e);
    }
  };

  // 拉取所有消息（包括适配器回复）
  React.useEffect(() => {
    const fetchMessages = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8050/messages');
        const data = await res.json();
        setMessages(data.map(msg => {
          // 适配麦麦/适配器回传消息的判定
          let from = 'other';
          if (msg.from_user === 'web') from = 'me';
          // 适配麦麦/适配器消息的昵称优先级
          let nickname = msg.nickname || msg.user_nickname || msg.from_user || '麦麦';
          return { from, text: msg.text, nickname };
        }));
      } catch (e) {
        // 可选：日志
      }
    };
    fetchMessages();
    const timer = setInterval(fetchMessages, 2000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="app-root">
      <Background image={background} />
      <div className="main-content">
        <div className="left-panel">
          <div style={{padding: '8px 20px 0 20px', display: 'flex', alignItems: 'center', gap: 8}}>
            {editingName ? (
              <>
                <input value={nicknameInput} onChange={e => setNicknameInput(e.target.value)} style={{width: 120}} />
                <button onClick={handleSaveNickname}>保存</button>
                <button onClick={() => { setEditingName(false); setNicknameInput(nickname); }}>取消</button>
              </>
            ) : (
              <>
                <span style={{fontWeight: 600}}>昵称：</span>
                <span>{nickname}</span>
                <button onClick={() => setEditingName(true)} style={{marginLeft: 8}}>修改</button>
              </>
            )}
          </div>
          <ChatPanel messages={messages} onSend={handleSendMessage} />
        </div>
        <div className="right-panel">
          <SpritePanel sprite={sprite} onChange={handleChangeSprite} />
        </div>
      </div>
      <Toolbar onChangeBackground={handleChangeBackground} onChangeSprite={handleChangeSprite} />
    </div>
  );
}

export default App
