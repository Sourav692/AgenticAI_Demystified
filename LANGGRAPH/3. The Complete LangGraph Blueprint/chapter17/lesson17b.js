import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e) => setQuery(e.target.value);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await axios.post(process.env.REACT_APP_AGENT_API_URL, { query });
      setResponse(res.data.response);
    } catch (err) {
      setError('Error: Could not reach the AI agent.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>LangGraph AI Agent Interaction</h1>
      <form onSubmit={handleSubmit}>
        <input type="text" value={query} onChange={handleInputChange} placeholder="Ask the AI agent..." />
        <button type="submit" disabled={loading}>Send</button>
      </form>
      {loading && <p>Loading...</p>}
      {error && <p>{error}</p>}
      <div className="response">
        <h2>Agent Response:</h2>
        <p>{response}</p>
      </div>
    </div>
  );
}

export default App;
