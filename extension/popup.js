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
    resultsDiv.innerHTML = '<div class="loading">Searching and opening results...</div>';

    try {
      // Send search request to background script
      const response = await chrome.runtime.sendMessage({
        action: 'search',
        query: query
      });

      // Open first three results automatically
      const results = response.results;
      if (results && results.length > 0) {
        const urlsToOpen = results.slice(0, 3);
        
        // Open each URL in a new tab
        for (const result of urlsToOpen) {
          chrome.tabs.create({ url: result.url }, function(tab) {
            // Send message to content script to highlight the text
            chrome.tabs.sendMessage(tab.id, {
              action: 'highlight',
              text: result.snippet
            });
          });
        }
      }

      // Display all results in the popup
      displayResults(results);
    } catch (error) {
      resultsDiv.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    }
  }

  function displayResults(results) {
    if (!results || results.length === 0) {
      resultsDiv.innerHTML = '<div class="no-results">No results found</div>';
      return;
    }

    const resultsHTML = results.map((result, index) => `
      <div class="result-item" data-url="${result.url}">
        <div class="result-title">
          ${result.title || 'Untitled'}
          ${index < 3 ? '<span style="color: #4CAF50; margin-left: 5px;">(Auto-opened)</span>' : ''}
        </div>
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