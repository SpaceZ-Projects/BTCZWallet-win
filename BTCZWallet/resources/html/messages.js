
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
  let left = rect.left + window.scrollX;
  const maxLeft = window.innerWidth - tooltip.offsetWidth - 10;
  const minLeft = 10;

  if (left < minLeft) left = minLeft;
  if (left > maxLeft) left = maxLeft;

  tooltip.style.left = `${left}px`;
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
  text = text.replace(
    urlPattern,
    (match) =>
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

  const imageUrlRegex = /\.(jpg|jpeg|png|gif|webp)$/i;
  const imageTags = [];

  const container = document.createElement("div");
  container.innerHTML = text;

  const links = container.querySelectorAll(".link");

  links.forEach((span) => {
    const url = span.dataset.href;

    if (imageUrlRegex.test(url)) {
      imageTags.push(`<img src="${url}" class="message-image" loading="lazy">`);
    }
  });

  if (imageTags.length > 0) {
    container.innerHTML += `<div class="message-images">${imageTags.join("")}</div>`;
  }

  return container.innerHTML;
}


function _createMessageElement(
  userType, username, content, timestamp, edited_timestamp, amount = 0, includeButtons = true, repliedUsername = null ,repliedMessage = null
) {
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

  let replyBlock = "";
  if (repliedMessage && repliedMessage.trim() !== "") {
    const safeUsername = repliedUsername ? repliedUsername : "Unknown";
    replyBlock = `
      <div class="replied-block-wrapper">
        <i class="fa-solid fa-arrow-turn-down reply-icon"></i>
        <div class="replied-block">
          <div class="replied-user">${safeUsername}</div>
          <div class="replied-snippet">${formatMessageContent(repliedMessage)}</div>
        </div>
      </div>
    `;
  }

  let actionsHTML = "";
  if (includeButtons) {
    actionsHTML = `<button title="Copy"><i class="fa-solid fa-copy"></i></button>`;
    if (username.toLowerCase() === 'you') {
      actionsHTML = `<button title="Edit"><i class="fa-solid fa-pen"></i></button>` + actionsHTML;
    }
    else {
      actionsHTML = `<button title="Reply"><i class="fa-solid fa-reply"></i></button>` + actionsHTML;
    }
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
    ${replyBlock}
    <div class="message-content">${formatMessageContent(content)}</div>
    <div class="editing-label">editing...</div>
    <div class="replying-label">replying...</div>
    <div class="message-actions">${actionsHTML}</div>
  `;

  if (repliedMessage) {
    message.classList.add("replyed");
  }

  if (includeButtons) {
    const replyBtn = message.querySelector('.message-actions button[title="Reply"]');
    const editBtn = message.querySelector('.message-actions button[title="Edit"]');
    const copyBtn = message.querySelector('.message-actions button[title="Copy"]');

    if (editBtn) {
      editBtn.addEventListener('click', (e) => {
        e.stopPropagation();

        const isEditing = !message.classList.contains('editing');
        message.classList.toggle('editing', isEditing);
        message.style.transition = 'background 0.4s';

        const icon = editBtn.querySelector('i');
        const editingLabel = message.querySelector('.editing-label');

        if (isEditing) {
          disableOtherActions(message);

          editBtn.title = 'Cancel';
          if (icon) icon.className = 'fa-solid fa-xmark';
          if (editingLabel) editingLabel.style.display = 'block';
          message.style.background = 'rgba(255, 238, 0, 0.1)';
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
          message.style.background = '';

          enableAllActions();

          if (window.chrome && window.chrome.webview) {
            window.chrome.webview.postMessage({ action: "cancelEdit" });
          }
        }
      });
    }

    if (replyBtn) {
      replyBtn.addEventListener('click', (e) => {
        e.stopPropagation();

        const isReplying = !message.classList.contains('replying');
        const icon = replyBtn.querySelector('i');
        const replyingLabel = message.querySelector('.replying-label');

        message.classList.toggle('replying', isReplying);
        message.style.transition = 'background 0.4s';

        if (isReplying) {
          disableOtherActions(message);

          replyBtn.title = 'Cancel';
          if (icon) icon.className = 'fa-solid fa-xmark';
          if (replyingLabel) replyingLabel.style.display = 'block';
          message.style.background = 'rgba(0, 255, 255, 0.1)';
          message.scrollIntoView({ behavior: 'smooth', block: 'center' });

          const replyData = {
            action: "reply",
            timestamp
          };

          if (window.chrome && window.chrome.webview) {
            window.chrome.webview.postMessage(replyData);
          } 
          
        } else {
          replyBtn.title = 'Reply';
          if (icon) icon.className = 'fa-solid fa-reply';
          if (replyingLabel) replyingLabel.style.display = 'none';
          message.style.background = '';

          enableAllActions();

          if (window.chrome && window.chrome.webview) {
            window.chrome.webview.postMessage({ action: "cancelReply" });
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
  }

  return message;
}

function addMessage(userType, username, content, timestamp, edited_timestamp, amount = 0, repliedUsername = null ,repliedMessage = null) {
  const message = _createMessageElement(userType, username, content, timestamp, edited_timestamp, amount, true, repliedUsername, repliedMessage);
  chatContainer.appendChild(message);
}

function insertMessage(index, userType, username, content, timestamp, edited_timestamp, amount = 0, repliedUsername = null ,repliedMessage = null) {
  const message = _createMessageElement(userType, username, content, timestamp, edited_timestamp, amount, true, repliedUsername, repliedMessage);
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

function addPendingMessage(content, timestamp, amount = 0, repliedUsername = null, repliedMessage = null) {
  const message = _createMessageElement(
    'you',
    'You',
    content,
    timestamp,
    "",
    amount,
    false,
    repliedUsername,
    repliedMessage
  );

  message.classList.add('sending');
  if (repliedUsername) message.dataset.repliedUsername = repliedUsername;
  if (repliedMessage) message.dataset.repliedMessage = repliedMessage;

  chatContainer.appendChild(message);
  chatContainer.scrollTop = chatContainer.scrollHeight;

  return message;
}


function markMessageAsSent(timestamp) {
  const pendingMsg = chatContainer.querySelector(`.message.sending [data-ts="${timestamp}"]`)?.closest('.message');
  if (!pendingMsg) return;

  const content = pendingMsg.dataset.originalContent || pendingMsg.querySelector('.message-content')?.textContent || '';
  const amount = parseFloat(pendingMsg.querySelector('.gift-tag')?.textContent) || 0;
  const repliedUsername = pendingMsg.dataset.repliedUsername || null;
  const repliedMessage = pendingMsg.dataset.repliedMessage || null;

  const sentMsg = _createMessageElement(
    'you',
    'You',
    content,
    timestamp,
    "",
    amount,
    true,
    repliedUsername,
    repliedMessage
  );

  pendingMsg.replaceWith(sentMsg);
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

      const repliedBlock = msg.querySelector('.replied-block');
      if (repliedBlock && msg.dataset.repliedMessage) {
        const repliedUsername = msg.dataset.repliedUsername || "User";
        const repliedMessage = msg.dataset.repliedMessage;
        repliedBlock.innerHTML = `
          <div class="replied-user">@${repliedUsername}</div>
          <div class="replied-snippet">${formatMessageContent(repliedMessage)}</div>
        `;
      }

      const actionsDiv = msg.querySelector('.message-actions');
      if (actionsDiv && actionsDiv.innerHTML.trim() === "") {
        const username = msg.querySelector('.username')?.textContent || 'You';
        let actionsHTML = `<button title="Copy"><i class="fa-solid fa-copy"></i></button>`;
        if (username.toLowerCase() === 'you') {
          actionsHTML = `<button title="Edit"><i class="fa-solid fa-pen"></i></button>` + actionsHTML;
        } else {
          actionsHTML = `<button title="Reply"><i class="fa-solid fa-reply"></i></button>` + actionsHTML;
        }
        actionsDiv.innerHTML = actionsHTML;
      }
    }
  });

  if (!found) {
    console.warn(`Message with timestamp "${timestamp}" not found.`);
  }
}


function cancelEdit() {
  const editingMsg = document.querySelector('.message.editing');
  if (editingMsg) {
    editingMsg.classList.remove('editing');
    editingMsg.style.background = '';

    const editBtn = editingMsg.querySelector('.message-actions button[title="Cancel"]');
    if (editBtn) {
      editBtn.title = 'Edit';
      const icon = editBtn.querySelector('i');
      if (icon) icon.className = 'fa-solid fa-pen';
      editBtn.disabled = false;
    }

    const editingLabel = editingMsg.querySelector('.editing-label');
    if (editingLabel) editingLabel.style.display = 'none';

    enableAllActions();
  }
}

function disableCancelEditButton() {
  const msg = document.querySelector('.message.editing');
  if (!msg) return;

  const cancelBtn = msg.querySelector('.message-actions button[title="Cancel"]');
  if (cancelBtn) cancelBtn.disabled = true;
}

function enableCancelEditButton() {
  const msg = document.querySelector('.message.editing');
  if (!msg) return;

  const cancelBtn = msg.querySelector('.message-actions button[title="Cancel"]');
  if (cancelBtn) cancelBtn.disabled = false;
}

function cancelReply() {
  const replyingMsg = document.querySelector('.message.replying');
  if (replyingMsg) {
    replyingMsg.classList.remove('replying');
    replyingMsg.style.background = '';

    const replyBtn = replyingMsg.querySelector('.message-actions button[title="Cancel"]');
    if (replyBtn) {
      replyBtn.title = 'Reply';
      const icon = replyBtn.querySelector('i');
      if (icon) icon.className = 'fa-solid fa-reply';
      replyBtn.disabled = false;
    }

    const replyingLabel = replyingMsg.querySelector('.replying-label');
    if (replyingLabel) replyingLabel.style.display = 'none';

    enableAllActions();
  }
}

function disableCancelReplyButton() {
  const msg = document.querySelector('.message.replying');
  if (!msg) return;

  const cancelBtn = msg.querySelector('.message-actions button[title="Cancel"]');
  if (cancelBtn) cancelBtn.disabled = true;
}

function enableCancelReplyButton() {
  const msg = document.querySelector('.message.replying');
  if (!msg) return;

  const cancelBtn = msg.querySelector('.message-actions button[title="Cancel"]');
  if (cancelBtn) cancelBtn.disabled = false;
}

function disableOtherActions(exceptMsg = null) {
  document.querySelectorAll('.message').forEach(msg => {
    if (msg === exceptMsg) return;
    msg.querySelectorAll('.message-actions button').forEach(btn => {
      btn.disabled = true;
      btn.style.opacity = '0.5';
      btn.style.pointerEvents = 'none';
    });
  });
}

function enableAllActions() {
  document.querySelectorAll('.message').forEach(msg => {
    msg.querySelectorAll('.message-actions button').forEach(btn => {
      btn.disabled = false;
      btn.style.opacity = '';
      btn.style.pointerEvents = '';
    });
  });
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


document.addEventListener('contextmenu', function(e) {
  e.preventDefault();
});
