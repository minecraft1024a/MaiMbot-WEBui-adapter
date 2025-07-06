import React, { useState } from 'react'

const SessionSelector = ({ currentSession, onSessionChange }) => {
  const [isExpanded, setIsExpanded] = useState(false)

  const sessions = [
    { id: 'default', name: '默认会话' },
    { id: 'user2', name: '会话2' },
    { id: 'user3', name: '会话3' }
  ]

  const currentSessionName = sessions.find(s => s.id === currentSession)?.name || '未知会话'

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
          {sessions.map(session => (
            <button
              key={session.id}
              className={`session-item ${session.id === currentSession ? 'active' : ''}`}
              onClick={() => {
                onSessionChange(session.id)
                setIsExpanded(false)
              }}
            >
              {session.name}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default SessionSelector
