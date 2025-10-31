
const chatContainer = document.getElementById('chatContainer');
const chatPlaceholder = document.getElementById('chatPlaceholder');
const toast = document.getElementById('toast');
const unreadLabel = document.getElementById('unreadLabel');

let onScrollToBottom = null;


function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => {
    toast.classList.remove('show');
  }, 1500);
}

function clearChat() {
  while (chatContainer.firstChild) {
    chatContainer.firstChild.remove();
  }
  chatContainer.scrollTop = 0;
}

function formatMessageContent(text) {
  if (!text) return "";
  text = text.replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;");

  const urlPattern = /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gi;
  text = text.replace(urlPattern, (match) => 
    `<span class="link" data-href="${match}" style="color:#00bfff; text-decoration:underline; cursor:pointer;">${match}</span>`
  );

  text = text.replace(/\n/g, "<br>");
  return text;
}

chatContainer.addEventListener('click', (e) => {
  const link = e.target.closest('.link');
  if (link) {
    const url = link.dataset.href;
    if (window.chrome && window.chrome.webview) {
      window.chrome.webview.postMessage(url);
    }
  }
});

function addMessage(userType, username, content, timestamp, amount = 0) {
  const message = document.createElement('div');
  message.className = `message ${userType}`;

  const hasGift = parseFloat(amount) > 0.0001;
  const giftTag = hasGift
    ? `<span class="gift-tag" style="margin-left:30px;">
         <i class="fa-solid fa-gift"></i> ${amount}
       </span>`
    : '';
  const timestampStyle = hasGift ? '' : 'style="margin-left:30px;"';

  let actionsHTML = `<button title="Copy"><i class="fa-solid fa-copy"></i></button>`;
  if (username.toLowerCase() === 'you') {
    actionsHTML =
      `<button title="Edit"><i class="fa-solid fa-pen"></i></button>` + actionsHTML;
  }

  message.innerHTML = `
    <div class="message-header">
      <span class="username">${username}</span>
      <div class="header-right">
        ${giftTag}
        <span class="timestamp" ${timestampStyle}>${timestamp}</span>
      </div>
    </div>
    <div class="message-content">${formatMessageContent(content)}</div>
    <div class="message-actions">${actionsHTML}</div>
  `;

  chatContainer.appendChild(message);

  const editBtn = message.querySelector('i.fa-pen')?.parentElement;
  const copyBtn = message.querySelector('i.fa-copy')?.parentElement;

  if (editBtn) {
    editBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (window.chrome && window.chrome.webview) {
        const payload = {
          action: "edit",
          username,
          content,
          timestamp
        };
        window.chrome.webview.postMessage(payload);
      }
    });
  }

  if (copyBtn) {
    copyBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const contentText = message.querySelector('.message-content').textContent;
      navigator.clipboard.writeText(contentText);
      showToast('Copied!');
    });
  }
}

function showUnreadLabel() {
  unreadLabel.style.display = 'block';
}

function hideUnreadLabel() {
  unreadLabel.style.display = 'none';
}

document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
});

function scrollToBottom() {
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

chatContainer.addEventListener('scroll', () => {
  const { scrollTop, scrollHeight, clientHeight } = chatContainer;
  if (scrollTop + clientHeight >= scrollHeight) {
    if (typeof onScrollToBottom === 'function') {
      onScrollToBottom();
    }
  }
});

onScrollToBottom = function() {
  if (window.chrome && window.chrome.webview) {
    const payload = {action: "scrolledToBottom"};
    window.chrome.webview.postMessage(payload);
  }
};

document.addEventListener('keydown', function(e) {
    if (e.key === 'F5') e.preventDefault();
    if (e.key === 'F7') e.preventDefault();
    if (e.key === 'F12') e.preventDefault();
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') e.preventDefault();
});
