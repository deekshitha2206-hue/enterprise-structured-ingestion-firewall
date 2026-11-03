

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('chat');

  // Week 2 states
  const [message, setMessage] = useState('');
  const [result, setResult] = useState(null);
  const [analysisError, setAnalysisError] = useState('');
  const [analysisLoading, setAnalysisLoading] = useState(false);

  // Week 3 states
  const [chatMessage, setChatMessage] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [history, setHistory] = useState([]);
  const [chatError, setChatError] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  async function handleAnalyze(event) {
    event.preventDefault();

    if (!message.trim()) {
      setAnalysisError('Please enter a message.');
      return;
    }

    setAnalysisLoading(true);
    setAnalysisError('');
    setResult(null);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : 'Request failed. Check the backend terminal.'
        );
      }

      setResult(data);
    } catch (err) {
      setAnalysisError(err.message || 'Could not connect to the backend.');
    } finally {
      setAnalysisLoading(false);
    }
  }

  async function handleChat(event) {
    event.preventDefault();

    if (!chatMessage.trim()) {
      setChatError('Please enter a message.');
      return;
    }

    setChatLoading(true);
    setChatError('');

    try {
      const response = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: chatMessage,
          session_id: sessionId,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : 'Chat request failed.'
        );
      }

      setSessionId(data.session_id);
      setHistory(data.history || []);
      setChatMessage('');
    } catch (err) {
      setChatError(err.message || 'Could not connect to the backend.');
    } finally {
      setChatLoading(false);
    }
  }

  function handleNewChat() {
    setSessionId(null);
    setHistory([]);
    setChatMessage('');
    setChatError('');
  }

  return (
    <main className="app-shell">
      <h1>Enterprise Structured Ingestion Firewall</h1>
      <p>AI-powered message analysis and conversation memory.</p>

      <div className="tab-buttons">
        <button
          type="button"
          className={activeTab === 'chat' ? 'active-tab' : 'secondary-button'}
          onClick={() => setActiveTab('chat')}
        >
          Chat with Memory
        </button>

        <button
          type="button"
          className={activeTab === 'analyze' ? 'active-tab' : 'secondary-button'}
          onClick={() => setActiveTab('analyze')}
        >
          AI Response Generator
        </button>
      </div>

      {activeTab === 'chat' && (
        <section className="chat-panel">
          <div className="chat-header">
            <div>
              <h2>Chat with AI</h2>
              <p>Ask questions and continue the conversation.</p>
            </div>

            <button
              type="button"
              className="new-chat-button"
              onClick={handleNewChat}
              disabled={chatLoading}
            >
              + New Chat
            </button>
          </div>

          {sessionId && (
            <p className="session-id">
              <strong>Session ID:</strong> {sessionId}
            </p>
          )}

          <div className="chat-history">
            {history.length === 0 ? (
              <p className="empty-chat">
                No messages yet. Start a new conversation!
              </p>
            ) : (
              history.map((item, index) => (
                <div
                  className={`chat-message ${item.role}`}
                  key={`${index}-${item.role}`}
                >
                  <strong>
                    {item.role === 'user' ? 'You' : 'AI Assistant'}
                  </strong>

                  <ReactMarkdown>{item.content}</ReactMarkdown>
                </div>
              ))
            )}
          </div>

          <form onSubmit={handleChat} className="chat-form">
            <label htmlFor="chat-message">Your message</label>

            <textarea
              id="chat-message"
              rows="3"
              value={chatMessage}
              onChange={(event) => setChatMessage(event.target.value)}
              placeholder="Example: My name is Ravi. I am learning Python."
            />

            <button type="submit" disabled={chatLoading}>
              {chatLoading ? 'Sending...' : 'Send Message'}
            </button>
          </form>

          {chatError && <p className="error-message">{chatError}</p>}
        </section>
      )}

      {activeTab === 'analyze' && (
        <section className="analysis-panel">
          <h2>AI Response Generator</h2>
          <p>Enter a message to detect its intent and generate an AI response.</p>

          <form onSubmit={handleAnalyze}>
            <label htmlFor="message">Your message</label>

            <textarea
              id="message"
              rows="4"
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="Example: My payment was deducted twice."
            />

            <button type="submit" disabled={analysisLoading}>
              {analysisLoading ? 'Generating...' : 'Generate Response'}
            </button>
          </form>

          {analysisError && (
            <p className="error-message">{analysisError}</p>
          )}

          {result && (
            <>
              <section>
                <h2>Generated Response</h2>
                <ReactMarkdown>
                  {result.response_markdown || ''}
                </ReactMarkdown>
              </section>

              <section>
                <h2>Detected Intent</h2>
                <p><strong>Intent:</strong> {result.analysis.intent}</p>
                <p><strong>Risk:</strong> {result.analysis.risk_profile}</p>
                <p><strong>Priority:</strong> {result.analysis.priority}</p>
                <p>
                  <strong>Requires action:</strong>{' '}
                  {result.analysis.requires_action ? 'Yes' : 'No'}
                </p>
                <p><strong>Summary:</strong> {result.analysis.summary}</p>
              </section>
            </>
          )}
        </section>
      )}
    </main>
  );
}

export default App;
