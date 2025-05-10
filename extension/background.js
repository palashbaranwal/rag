// API endpoint for our RAG server
const API_ENDPOINT = 'http://localhost:5000';

// Handle messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'search') {
    performSearch(request.query)
      .then(sendResponse)
      .catch(error => sendResponse({ error: error.message }));
    return true; // Required for async response
  }
});

async function performSearch(query) {
  try {
    const response = await fetch(`${API_ENDPOINT}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      throw new Error('Search request failed');
    }

    const data = await response.json();
    return {
      results: data.results.map(result => ({
        url: result.url,
        title: result.title || extractTitleFromUrl(result.url),
        snippet: result.content
      }))
    };
  } catch (error) {
    console.error('Search error:', error);
    throw error;
  }
}

function extractTitleFromUrl(url) {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname;
  } catch {
    return url;
  }
} 