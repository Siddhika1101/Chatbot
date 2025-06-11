import React, { useState } from 'react';

const Sidebar = ({ chatSessions, currentSessionId, onChatSelect, onNewChat, onUpdateTitle, onDeleteSession }) => {
  const [editingTitle, setEditingTitle] = useState(null);
  const [tempTitle, setTempTitle] = useState('');

  const handleTitleClick = (session) => {
    setEditingTitle(session.id);
    setTempTitle(session.title);
  };

  const handleTitleSave = (sessionId) => {
    if (tempTitle.trim()) {
      onUpdateTitle(sessionId, tempTitle.trim());
    }
    setEditingTitle(null);
  };

  const handleKeyDown = (e, sessionId) => {
    if (e.key === 'Enter') {
      handleTitleSave(sessionId);
    } else if (e.key === 'Escape') {
      setEditingTitle(null);
    }
  };

  const handleDelete = (e, sessionId) => {
    e.stopPropagation(); // Prevent triggering chat selection
    if (window.confirm('Are you sure you want to delete this chat?')) {
      onDeleteSession(sessionId);
    }
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>Chats</h2>
        <button className="new-chat-button" onClick={onNewChat}>
          New Chat
        </button>
      </div>
      <div className="chat-history">
        {chatSessions.map((session) => (
          <div 
            key={session.id} 
            className={`chat-history-item ${session.id === currentSessionId ? 'active' : ''}`}
            onClick={() => onChatSelect(session.id)}
          >
            <div className="chat-item-content">
              {editingTitle === session.id ? (
                <input
                  type="text"
                  value={tempTitle}
                  onChange={(e) => setTempTitle(e.target.value)}
                  onBlur={() => handleTitleSave(session.id)}
                  onKeyDown={(e) => handleKeyDown(e, session.id)}
                  autoFocus
                  className="title-input"
                  onClick={(e) => e.stopPropagation()}
                />
              ) : (
                <div 
                  className="chat-title"
                  onDoubleClick={() => handleTitleClick(session)}
                >
                  {session.title}
                  {session.messages.length > 0 && 
                    <span className="message-preview">
                      {session.messages[session.messages.length - 1].user.substring(0, 30)}
                      {session.messages[session.messages.length - 1].user.length > 30 ? '...' : ''}
                    </span>
                  }
                </div>
              )}
              <button 
                className="delete-chat-button"
                onClick={(e) => handleDelete(e, session.id)}
                title="Delete chat"
              >
                ×
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Sidebar;
