// app.js

document.getElementById('upload-btn').addEventListener('click', async () => {
    const repoUrl = document.getElementById('repo-url').value;
    if (!repoUrl) {
        alert('Please enter a GitHub repository URL.');
        return;
    }

    // Show a loading message or spinner if desired

    const formData = new FormData();
    formData.append('repo_url', repoUrl);

    try {
        const response = await fetch('http://localhost:8000/upload_repo', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        alert(data.status);
    } catch (error) {
        console.error('Error uploading repository:', error);
        alert('Error uploading repository. Check console for details.');
    }
});

document.getElementById('send-btn').addEventListener('click', async () => {
    const userInput = document.getElementById('user-input').value;
    if (!userInput) {
        alert('Please enter a message.');
        return;
    }

    // Add user message to chat window
    addMessageToChat('user', userInput);

    // Clear input field
    document.getElementById('user-input').value = '';

    // Send user query to backend
    try {
        const response = await fetch('http://localhost:8000/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: userInput })
        });
        const data = await response.json();
        const botResponse = data.answer;

        // Add bot response to chat window
        addMessageToChat('bot', botResponse);
    } catch (error) {
        console.error('Error fetching bot response:', error);
        alert('Error fetching bot response. Check console for details.');
    }
});

function addMessageToChat(sender, text) {
    const chatWindow = document.getElementById('chat-window');
    const messageElem = document.createElement('div');
    messageElem.classList.add('message', sender);

    const textElem = document.createElement('div');
    textElem.classList.add('text');
    textElem.innerText = text;

    messageElem.appendChild(textElem);
    chatWindow.appendChild(messageElem);

    // Scroll to bottom
    chatWindow.scrollTop = chatWindow.scrollHeight;
}