// Handle messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'highlight') {
    highlightText(request.text, request.query);
  }
});

function highlightText(text, query) {
  // Remove any existing highlights
  removeHighlights();

  // Create a new highlight for the snippet
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

  // Highlight matching keywords in the page content
  if (query) {
    highlightKeywords(query);
  }

  // Scroll to the highlight
  highlight.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function highlightKeywords(query) {
  // Split query into words
  const keywords = query.toLowerCase().split(/\s+/);
  
  // Create a tree walker to traverse text nodes
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    null,
    false
  );

  const nodesToReplace = [];
  let node;

  // Find all text nodes containing keywords
  while (node = walker.nextNode()) {
    const text = node.textContent;
    const lowerText = text.toLowerCase();
    
    // Check if any keyword is in this text node
    if (keywords.some(keyword => lowerText.includes(keyword))) {
      nodesToReplace.push(node);
    }
  }

  // Replace text nodes with highlighted versions
  nodesToReplace.forEach(node => {
    const span = document.createElement('span');
    let html = node.textContent;
    
    // Highlight each keyword
    keywords.forEach(keyword => {
      const regex = new RegExp(keyword, 'gi');
      html = html.replace(regex, match => 
        `<span style="background-color: #ffeb3b; padding: 2px;">${match}</span>`
      );
    });
    
    span.innerHTML = html;
    node.parentNode.replaceChild(span, node);
  });
}

function removeHighlights() {
  // Remove the floating highlight
  const highlights = document.querySelectorAll('div[style*="background-color: rgba(255, 255, 0, 0.3)"]');
  highlights.forEach(highlight => highlight.remove());

  // Remove keyword highlights
  const keywordHighlights = document.querySelectorAll('span[style*="background-color: #ffeb3b"]');
  keywordHighlights.forEach(highlight => {
    const parent = highlight.parentNode;
    parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
    // Normalize the parent node to merge adjacent text nodes
    parent.normalize();
  });
} 