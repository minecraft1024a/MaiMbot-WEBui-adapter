import React, { useState } from 'react';

const ChatPanel = ({ messages, onSend }) => {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim()) {
      onSend(input);
      setInput('');
    }
  };

  return (
    <div className="chat-panel">
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.from === 'me' ? 'me' : 'other'}`}>{msg.text}</div>
        ))}
      </div>
      <div className="chat-input-bar">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          placeholder="输入消息..."
        />
        <button onClick={handleSend}>发送</button>
      </div>
    </div>
  );
};

export default ChatPanel;
