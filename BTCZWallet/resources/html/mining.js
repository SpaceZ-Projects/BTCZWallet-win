
const totalShares = document.getElementById('totalShares')
const hashrate = document.getElementById('hashrate')
const balance = document.getElementById('balance')
const immatureBalance = document.getElementById('immatureBalance')
const paidBalance = document.getElementById('paidBalance')
const estimatedBTCZ = document.getElementById('estimatedBTCZ')
const estimatedCurrency = document.getElementById('estimatedCurrency')

function setTotalShares(value) {
    totalShares.textContent = value ?? '--';
}

function setHashrate(value) {
    hashrate.textContent = value ? `${value}` : '-- Sol/s';
}

function setBalance(value) {
    balance.textContent = value ? `${value} BTCZ` : '-- BTCZ';
}

function setImmatureBalance(value) {
    immatureBalance.textContent = value ? `${value} BTCZ` : '-- BTCZ';
}

function setPaidBalance(value) {
    paidBalance.textContent = value ? `${value} BTCZ` : '-- BTCZ';
}

function setEstimatedBTCZ(value) {
    estimatedBTCZ.textContent = value ? `${value} BTCZ` : '-- BTCZ';
}

function setEstimatedCurrency(value) {
    estimatedCurrency.textContent = value ? `${value}` : '--';
}

document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
});

document.addEventListener('keydown', (e) => {
    e.preventDefault();
});