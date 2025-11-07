
function setBalances(total, transparent, shielded) {
  document.querySelector('.total-box .value').textContent = total;
  document.querySelector('.transparent .amount').textContent = transparent;
  document.querySelector('.shielded .amount').textContent = shielded;
}

function setUnconfirmedBalance(amount) {
  const subBox = document.querySelector('.sub-balances-box');
  let unconfirmedBox = document.querySelector('.balance-item.unconfirmed');

  const numeric = parseFloat(amount.replace(/[^\d.-]/g, '')) || 0;
  if (numeric > 0 || amount === "*.********") {
    if (!unconfirmedBox) {
      unconfirmedBox = document.createElement('div');
      unconfirmedBox.className = 'balance-item unconfirmed fade-in';
      unconfirmedBox.innerHTML = `
        <h3>Unconfirmed</h3>
        <div class="amount">0.00000000</div>
      `;
      subBox.prepend(unconfirmedBox);
    }
    const amountDiv = unconfirmedBox.querySelector('.amount');
    if (amountDiv.textContent !== amount)
      amountDiv.textContent = amount;

    unconfirmedBox.classList.remove('fade-out');
    unconfirmedBox.classList.add('fade-in');
  } else {
    if (unconfirmedBox) {
      unconfirmedBox.classList.remove('fade-in');
      unconfirmedBox.classList.add('fade-out');
      setTimeout(() => unconfirmedBox.remove(), 400);
    }
  }
}

document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
});

document.addEventListener('keydown', (e) => {
    e.preventDefault();
});
