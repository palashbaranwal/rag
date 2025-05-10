document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('searchInput');
  const searchButton = document.getElementById('searchButton');
  const resultsDiv = document.getElementById('results');

  // Handle search button click
  searchButton.addEventListener('click', performSearch);
  
  // Handle Enter key press
  searchInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      performSearch();
    }
  });

  async function performSearch() {
    const query = searchInput.value.trim();
    if (!query) return;

    // Show loading state
    resultsDiv.innerHTML = '<div class="loading">Searching...</div>';

    try {
      // Send search request to background script
      const response = await chrome.runtime.sendMessage({
        action: 'search',
        query: query
      });

      displayResults(response.results);
    } catch (error) {
      resultsDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    }
  }

  function displayResults(results) {
    if (!results || results.length === 0) {
      resultsDiv.innerHTML = '<div class="no-results">No results found</div>';
      return;
    }

    const resultsHTML = results.map(result => `
      <div class="result-item" data-url="${result.url}">
        <div class="result-title">${result.title || 'Untitled'}</div>
        <div class="result-url">${result.url}</div>
        <div class="result-snippet">${result.snippet}</div>
      </div>
    `).join('');

    resultsDiv.innerHTML = resultsHTML;

    // Add click handlers to results
    document.querySelectorAll('.result-item').forEach(item => {
      item.addEventListener('click', function() {
        const url = this.dataset.url;
        chrome.tabs.create({ url: url }, function(tab) {
          // Send message to content script to highlight the text
          chrome.tabs.sendMessage(tab.id, {
            action: 'highlight',
            text: results.find(r => r.url === url).snippet
          });
        });
      });
    });
  }
}); 