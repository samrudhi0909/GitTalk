import React, { useState } from 'react';
import axios from 'axios';

function RepositoryInput({ setRepoLoaded }) {
  const [repoUrl, setRepoUrl] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRepoSubmit = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/fetch-repo', {
        repoUrl: repoUrl,
      });
      if (response.status === 200) {
        alert('Repository processed successfully!');
        setRepoLoaded(true);
      } else {
        alert('Failed to process repository.');
      }
    } catch (error) {
      alert('Error processing repository.');
    }
    setLoading(false);
  };

  return (
    <div>
      <h2>Enter GitHub Repository URL</h2>
      <input
        type="text"
        value={repoUrl}
        onChange={(e) => setRepoUrl(e.target.value)}
        placeholder="https://github.com/username/repo"
      />
      <button onClick={handleRepoSubmit} disabled={loading || !repoUrl}>
        {loading ? 'Processing...' : 'Load Repository'}
      </button>
    </div>
  );
}

export default RepositoryInput;