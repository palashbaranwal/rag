// Handle messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'highlight') {
    highlightText(request.text);
  }
});

function highlightText(text) {
  // Remove any existing highlights
  removeHighlights();

  // Create a new highlight
  const highlight = document.createElement('div');
  highlight.style.position = 'fixed';
  highlight.style.top = '0';
  highlight.style.left = '0';
  highlight.style.width = '100%';
  highlight.style.backgroundColor = 'rgba(255, 255, 0, 0.3)';
  highlight.style.padding = '10px';
  highlight.style.zIndex = '10000';
  highlight.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
  highlight.style.fontSize = '14px';
  highlight.style.color = '#333';
  highlight.style.textAlign = 'center';
  highlight.innerHTML = `
    <div style="max-width: 800px; margin: 0 auto;">
      <strong>Relevant Content:</strong> ${text}
      <button onclick="this.parentElement.parentElement.remove()" 
              style="margin-left: 10px; padding: 2px 8px; cursor: pointer;">
        Close
      </button>
    </div>
  `;

  document.body.appendChild(highlight);

  // Scroll to the highlight
  highlight.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function removeHighlights() {
  const highlights = document.querySelectorAll('div[style*="background-color: rgba(255, 255, 0, 0.3)"]');
  highlights.forEach(highlight => highlight.remove());
} 