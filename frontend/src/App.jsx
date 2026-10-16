
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';

function App() {
  const [message, setMessage] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    if (!message.trim()) {
      setError('Please enter a message.');
      return;
    }

    setLoading(true);
    setError('');
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
      setError(err.message || 'Could not connect to the backend.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <h1>AI Response Generator</h1>
      <p>Enter a message to detect its intent and generate an AI response.</p>

      <form onSubmit={handleSubmit}>
        <label htmlFor="message">Your message</label>
        <textarea
          id="message"
          rows="4"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Example: My payment was deducted twice."
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Generating...' : 'Generate response'}
        </button>
      </form>

      {error && <p role="alert">{error}</p>}

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
    </main>
  );
}

export default App;