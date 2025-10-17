import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const [streamingResponse, setStreamingResponse] = useState('');
  const handleStreamSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStreamingResponse('');
  
    try {
      const response = await fetch('http://localhost:8000/api/research/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });
  
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
  
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let done = false;
  
      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
  
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          setStreamingResponse((prev) => prev + chunk);
        }
      }
    } catch (error) {
      console.error('Streaming error:', error);
      setStreamingResponse('An error occurred while streaming the response.');
    } finally {
      setLoading(false);
    }
  };
  
  
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Research Assistant</h1>
      <form onSubmit={handleStreamSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full p-2 border rounded mb-4"
          placeholder="Enter your research query..."
        />
     
      {response && (
        <div className="mt-4 p-4 border rounded">
          <h2 className="font-bold mb-2">Response:</h2>
          <p>{response}</p>
        </div>
      )}
      <div className="mt-4">
        <button 
          onClick={handleStreamSubmit}
          className="bg-green-500 text-white px-4 py-2 rounded ml-2"
          disabled={loading}
        >
          Stream Response
        </button>
      </div> 
      </form>
      {streamingResponse && (
        <div className="mt-4 p-4 border rounded">
          <h2 className="font-bold mb-2">Streaming Response:</h2>
          <p>{streamingResponse}</p>
        </div>
      )}

    </div>
    
  );
}

export default App;