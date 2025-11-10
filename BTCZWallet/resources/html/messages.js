
const chatContainer = document.getElementById('chatContainer');
const chatPlaceholder = document.getElementById('chatPlaceholder');
const toast = document.getElementById('toast');
const unreadLabel = document.getElementById('unreadLabel');

let onScrollToBottom = null;
let onScrollToTop = null;

const EMOJI_MAP = {
  ":)": "😊",
  ":-)": "😊",
  ":(": "😞",
  ":-(": "😞",
  ":D": "😄",
  ":-D": "😄",
  ":P": "😛",
  ":-P": "😛",
  ";)": "😉",
  ";-)": "😉",
  ":O": "😮",
  ":-O": "😮",
  ":-/": "😕",
  ":|": "😐",
  ":*": "😘",
  ":-*": "😘",
  "<3": "❤️",
  "T_T": "😭",
  ":'(": "😢",
  "XD": "😆",
  ":3": "😺",
  ">:(": "😠",
  "O:)": "😇",
  "O:-)": "😇",
  ":^)": "🙂",
  ":-}": "😏",
  ":-{": "😒",
  "D:": "😧",
  ">:O": "😡",
  ":v": "😎",
  "UwU": "🥰",
  "owo": "🥺",
  ">_<": "😣",
  "^_^": "😄",
  "^-^": "😄",
  "x_x": "😵",
  "-_-": "😑",
  "o_O": "😳",
  "O_o": "😳",
  ":>": "😏",
  ":}": "😏",
  ":S": "😖",
  ":X": "🤐",
  ">:3": "😼",
  ">:D": "😈",
  ";3": "😼",
  "=)": "😊",
  "=(":"😞",
  ":'D":"😂",
  "D-:":"😧",
  "3:)":"😈",
  "<(\"<)":"🐧",
  "(*_*)":"😍",
  "x3":"😸",
  ":c":"😞",
  ":|]":"🤖",
  "^_^;":"😅",
  "-.-":"😑",
  "¬_¬":"😒",
  "°_°":"😳",
  "ಠ_ಠ":"😒",
  "ಠ‿ಠ":"😏",
  "ಠ︵ಠ":"😠",
  "ಥ_ಥ":"😭",
  "(>_<)":"😣",
  "(T_T)":"😭",
  "(^o^)":"😄",
  "(^_^)/":"👋",
  "(^_~)":"😉",
  "(^_-)-☆":"😉",
  "(^з^)-☆":"😘",
  "(o^-^o)":"😊",
  "(o_o)":"😳",
  "(-.-)Zzz":"😴",
  "(•_•)":"😐",
  "(•_•)>⌐■-■":"😎",
  "(⌐■_■)":"😎",
  "(~_~)":"😴",
  "(=_=)":"😑",
  "(^3^)":"😘",
  "(^_^*)":"😊",
  "(~_^*)":"😉",
  "(o^^o)":"😊",
  "(>_>)":"😏",
  "(<_<)":"😏",
  "(-_-;)":"😅",
  "(;_;)":"😢",
  "m(_ _)m":"🙏",
  "(^_^)b":"👍",
  "(^_^)v":"✌️",
  "(-_-)/~~":"😣"
};

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

function restorePlaceholder() {
  if (chatPlaceholder) {
    if (!chatContainer.contains(chatPlaceholder)) {
      chatContainer.appendChild(chatPlaceholder);
    }
    chatPlaceholder.style.display = 'block';
  }
}

chatContainer.addEventListener('click', (e) => {
  const link = e.target.closest('.link');
  if (link) {
    const url = link.dataset.href;
    if (window.chrome && window.chrome.webview) {
      const payload = { action: "urlClicked", url: url };
      window.chrome.webview.postMessage(payload);
    }
  }
});

chatContainer.addEventListener('mouseover', (e) => {
  const link = e.target.closest('.link');
  if (!link) return;

  const tooltip = document.createElement('div');
  tooltip.className = 'link-tooltip';
  tooltip.textContent = link.dataset.href;
  document.body.appendChild(tooltip);

  const rect = link.getBoundingClientRect();
  tooltip.style.left = `${rect.left + window.scrollX + rect.width / 2}px`;
  tooltip.style.top = `${rect.top + window.scrollY - 28}px`;

  link._tooltip = tooltip;
});

chatContainer.addEventListener('mouseout', (e) => {
  const link = e.target.closest('.link');
  if (link && link._tooltip) {
    link._tooltip.remove();
    link._tooltip = null;
  }
});

function formatMessageContent(text) {
  if (!text) return "";
  try {
    if (text.includes('\\n') || text.includes('\\"')) {
      text = JSON.parse(`"${text}"`);
    }
  } catch {
    text = text.replace(/\\n/g, '\n')
               .replace(/\\"/g, '"')
               .replace(/\\\\/g, '\\');
  }
  text = text.replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;");

  text = text.replace(/```([\s\S]*?)```/g, (_, code) => {
    try {
      if (code.includes('\\"') || code.includes('\\n') || code.includes('\\\\')) {
        code = JSON.parse(`"${code}"`);
      }
    } catch {
      code = code
        .replace(/\\\\/g, "\\")
        .replace(/\\"/g, '"')
        .replace(/\\n/g, '\n');
    }
    const safeCode = code
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    return `<pre class="code-block"><code>${safeCode.trim()}</code></pre>`;
  });
  text = text.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
  text = text.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
  text = text.replace(/'([^']+)'/g, '<span class="box">$1</span>');

  if (/^- /m.test(text)) {
    const lines = text.split(/\n+/);
    let inList = false;
    let result = '';

    for (const line of lines) {
      if (line.trim().startsWith('- ')) {
        if (!inList) {
          result += '<ul class="msg-list">';
          inList = true;
        }
        result += `<li>${line.trim().substring(2)}</li>`;
      } else {
        if (inList) {
          result += '</ul>';
          inList = false;
        }
        result += line + '\n';
      }
    }
    if (inList) result += '</ul>';
    text = result;
  }

  const urlPattern = /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gi;
  text = text.replace(urlPattern, (match) => 
    `<span class="link" data-href="${match}" style="color:#00bfff; text-decoration:underline; cursor:pointer;">${match}</span>`
  );

  for (const [emoticon, emoji] of Object.entries(EMOJI_MAP)) {
    const escaped = emoticon.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(escaped, "g");
    text = text.replace(regex, emoji);
  }

  const emojiRegex = /([\p{Emoji_Presentation}\p{Extended_Pictographic}])/gu;
  text = text.replace(emojiRegex, '<span class="emoji">$1</span>');

  text = text.replace(/\n/g, "<br>");

  return text;
}

function _createMessageElement(userType, username, content, timestamp, edited_timestamp, amount = 0) {
  const message = document.createElement('div');
  message.className = `message ${userType}`;
  message.dataset.originalContent = content;

  const hasGift = parseFloat(amount) > 0.0001;
  const giftTag = hasGift
    ? `<span class="gift-tag" style="margin-left:30px;">
         <i class="fa-solid fa-gift"></i> ${amount}
       </span>`
    : '';
  const timestampStyle = hasGift ? '' : 'style="margin-left:30px;"';

  let editedTag = "";
  if (edited_timestamp && edited_timestamp.trim() !== "") {
    editedTag = `<span class="edited-tag" data-tooltip="Edited on ${edited_timestamp}">(edited)</span>`;
  }

  let actionsHTML = `<button title="Copy"><i class="fa-solid fa-copy"></i></button>`;
  if (username.toLowerCase() === 'you') {
    actionsHTML = `<button title="Edit"><i class="fa-solid fa-pen"></i></button>` + actionsHTML;
  }

  message.innerHTML = `
    <div class="message-header">
      <span class="username">${username}</span>
      <div class="header-right">
        ${giftTag}
        <span class="timestamp" ${timestampStyle} data-ts="${timestamp}">
          ${timestamp} ${editedTag}
        </span>
      </div>
    </div>
    <div class="message-content">${formatMessageContent(content)}</div>
    <div class="editing-label">editing...</div>
    <div class="message-actions">${actionsHTML}</div>
  `;

  const editBtn = message.querySelector('i.fa-pen')?.parentElement;
  const copyBtn = message.querySelector('i.fa-copy')?.parentElement;

  if (editBtn) {
    editBtn.addEventListener('click', (e) => {
      e.stopPropagation();

      const currentlyEditing = document.querySelector('.message.editing');
      if (currentlyEditing && currentlyEditing !== message) {
        return;
      }

      const isEditing = !message.classList.contains('editing');
      message.classList.toggle('editing', isEditing);
      const icon = editBtn.querySelector('i');
      const editingLabel = message.querySelector('.editing-label');

      if (isEditing) {
        editBtn.title = 'Cancel';
        if (icon) icon.className = 'fa-solid fa-xmark';
        if (editingLabel) editingLabel.style.display = 'block';
        message.scrollIntoView({ behavior: 'smooth', block: 'center' });

        const contentToEdit = message.dataset.originalContent || message.querySelector('.message-content').textContent;

        if (window.chrome && window.chrome.webview) {
          window.chrome.webview.postMessage({
            action: "edit",
            content: contentToEdit,
            timestamp
          });
        }

      } else {
        editBtn.title = 'Edit';
        if (icon) icon.className = 'fa-solid fa-pen';
        if (editingLabel) editingLabel.style.display = 'none';

        if (window.chrome && window.chrome.webview) {
          window.chrome.webview.postMessage({ action: "cancelEdit" });
        }
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

  return message;
}

function addMessage(userType, username, content, timestamp, edited_timestamp, amount = 0) {
  const message = _createMessageElement(userType, username, content, timestamp, edited_timestamp, amount);
  chatContainer.appendChild(message);
}

function insertMessage(index, userType, username, content, timestamp, edited_timestamp, amount = 0) {
  const message = _createMessageElement(userType, username, content, timestamp, edited_timestamp, amount);
  const messages = chatContainer.querySelectorAll('.message');

  const oldScrollTop = chatContainer.scrollTop;
  const oldScrollHeight = chatContainer.scrollHeight;

  if (messages.length === 0) {
    chatContainer.appendChild(message);
  } else if (index <= 0) {
    chatContainer.insertBefore(message, messages[0]);
  } else if (index >= messages.length) {
    chatContainer.appendChild(message);
  } else {
    chatContainer.insertBefore(message, messages[index]);
  }

  const newScrollHeight = chatContainer.scrollHeight;
  const heightDiff = newScrollHeight - oldScrollHeight;
  chatContainer.scrollTop = oldScrollTop + heightDiff;
}

function editMessage(timestamp, content, edited_timestamp) {
  const messages = chatContainer.querySelectorAll('.message');
  let found = false;

  messages.forEach(msg => {
    const tsElem = msg.querySelector('.timestamp');
    if (tsElem && tsElem.dataset.ts === timestamp) {
      found = true;

      const contentElem = msg.querySelector('.message-content');
      if (contentElem) {
        contentElem.innerHTML = formatMessageContent(content);
        msg.dataset.originalContent = content;
      }

      let editedTag = msg.querySelector('.edited-tag');
      if (edited_timestamp && edited_timestamp.trim() !== "") {
        if (!editedTag) {
          editedTag = document.createElement('span');
          editedTag.className = 'edited-tag';
          editedTag.textContent = '(edited)';
          editedTag.setAttribute('data-tooltip', `Edited on ${edited_timestamp}`);
          tsElem.insertAdjacentElement('beforeend', editedTag);
        } else {
          editedTag.setAttribute('data-tooltip', `Edited on ${edited_timestamp}`);
        }
      }

      msg.style.transition = 'background 0.4s';
      msg.style.background = 'rgba(255, 255, 0, 0.1)';
      setTimeout(() => (msg.style.background = ''), 500);
    }
  });

  if (!found) {
    console.warn(`Message with timestamp "${timestamp}" not found.`);
  }
}

function addPendingMessage(userType, username, content, timestamp, amount = 0) {
  const message = _createMessageElement(userType, username, content, timestamp, "", amount);
  message.classList.add('sending');
  chatContainer.appendChild(message);
  chatContainer.scrollTop = chatContainer.scrollHeight;
  return message;
}

function markMessageAsSent(timestamp) {
  const messages = chatContainer.querySelectorAll('.message.sending');
  messages.forEach(msg => {
    const tsElem = msg.querySelector('.timestamp');
    if (tsElem && tsElem.dataset.ts === timestamp) {
      msg.classList.remove('sending');
      msg.style.opacity = 1;
    }
  });
}

function markMessageAsFailed(timestamp) {
  const msg = chatContainer.querySelector(`.message.sending [data-ts="${timestamp}"]`)?.closest('.message');
  if (!msg) return;

  msg.classList.remove('sending');
  msg.classList.add('failed');

  setTimeout(() => {
    msg.style.opacity = '0';
    msg.style.transform = 'scale(0.95)';
    setTimeout(() => msg.remove(), 400);
  }, 2000);
}


function cancelEdit() {
  const editingMsg = document.querySelector('.message.editing');
  if (editingMsg) {
    editingMsg.classList.remove('editing');

    const editBtn = editingMsg.querySelector('.message-actions button[title="Cancel"]');
    if (editBtn) {
      editBtn.title = 'Edit';
      const icon = editBtn.querySelector('i');
      if (icon) icon.className = 'fa-solid fa-pen';
      editBtn.disabled = false;
    }

    const editingLabel = editingMsg.querySelector('.editing-label');
    if (editingLabel) editingLabel.style.display = 'none';
  }
}

function disableCancelButton() {
  const msg = document.querySelector('.message.editing');
  if (!msg) return;

  const cancelBtn = msg.querySelector('.message-actions button[title="Cancel"]');
  if (cancelBtn) cancelBtn.disabled = true;
}

function enableCancelButton() {
  const msg = document.querySelector('.message.editing');
  if (!msg) return;

  const cancelBtn = msg.querySelector('.message-actions button[title="Cancel"]');
  if (cancelBtn) cancelBtn.disabled = false;
}

function showUnreadLabel() {
  const { scrollHeight, clientHeight } = chatContainer;
  const canScroll = scrollHeight > clientHeight + 5;
  if (canScroll) {
    unreadLabel.style.display = 'block';
  } else {
    unreadLabel.style.display = 'none';
    if (window.chrome && window.chrome.webview) {
      window.chrome.webview.postMessage({ action: "scrolledToBottom" });
    }
  }
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
  
  if (scrollTop === 0) {
    if (typeof onScrollToTop === 'function') {
      onScrollToTop();
    }
  }
});

onScrollToBottom = function() {
  if (window.chrome && window.chrome.webview) {
    const payload = { action: "scrolledToBottom" };
    window.chrome.webview.postMessage(payload);
  }
};

onScrollToTop = function() {
  if (window.chrome && window.chrome.webview) {
    const payload = { action: "scrolledToTop" };
    window.chrome.webview.postMessage(payload);
  }
};

document.addEventListener('keydown', (e) => {
  const isCopy = (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'c';
  if (!isCopy) {
    e.preventDefault();
    e.stopPropagation();
  }
});
