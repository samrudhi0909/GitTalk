// src/App.jsx

import React, { useState } from 'react';
import RepositoryInput from './components/RepositoryInput';
import ChatWindow from './components/ChatWindow';
import './App.css';

function App() {
  const [repoLoaded, setRepoLoaded] = useState(false);

  return (
    <div className="container">
      <div className="left-side">
        <RepositoryInput setRepoLoaded={setRepoLoaded} />
      </div>
      <div className="right-side">
        <ChatWindow repoLoaded={repoLoaded} />
      </div>
    </div>
  );
}

export default App;