import React, { useState } from 'react'

const SessionSelector = ({ currentSession, onSessionChange }) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [sessions, setSessions] = useState([
    { id: 'default', name: '默认会话' },
    { id: 'user2', name: '会话2' },
    { id: 'user3', name: '会话3' }
  ])

  const currentSessionName = sessions.find(s => s.id === currentSession)?.name || '未知会话'

  const handleNewSession = () => {
    const newSessionId = `session_${Date.now()}`
    const newSessionName = `会话 ${sessions.length + 1}`
    const newSession = { id: newSessionId, name: newSessionName }
    
    setSessions(prev => [...prev, newSession])
    onSessionChange(newSessionId)
    setIsExpanded(false)
  }

  const handleDeleteSession = (sessionId, e) => {
    e.stopPropagation()
    if (sessions.length <= 1) return // 至少保留一个会话
    
    setSessions(prev => prev.filter(s => s.id !== sessionId))
    
    // 如果删除的是当前会话，切换到第一个会话
    if (sessionId === currentSession) {
      const remainingSessions = sessions.filter(s => s.id !== sessionId)
      onSessionChange(remainingSessions[0]?.id || 'default')
    }
  }

  return (
    <div className="session-selector">
      <button 
        className="session-toggle"
        onClick={() => setIsExpanded(!isExpanded)}
        title="切换会话"
      >
        <span className="session-icon">💬</span>
        <span className="session-name">{currentSessionName}</span>
        <span className={`session-arrow ${isExpanded ? 'expanded' : ''}`}>▼</span>
      </button>
      
      {isExpanded && (
        <div className="session-dropdown">
          <div className="session-header">
            <span className="session-title">会话管理</span>
            <button
              className="new-session-btn"
              onClick={handleNewSession}
              title="新建会话"
            >
              <span className="plus-icon">+</span>
            </button>
          </div>
          
          <div className="session-list">
            {sessions.map(session => (
              <div
                key={session.id}
                className={`session-item-wrapper ${session.id === currentSession ? 'active' : ''}`}
              >
                <button
                  className="session-item"
                  onClick={() => {
                    onSessionChange(session.id)
                    setIsExpanded(false)
                  }}
                >
                  <span className="session-item-name">{session.name}</span>
                </button>
                {sessions.length > 1 && (
                  <button
                    className="delete-session-btn"
                    onClick={(e) => handleDeleteSession(session.id, e)}
                    title="删除会话"
                  >
                    ×
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default SessionSelector
