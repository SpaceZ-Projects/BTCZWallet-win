
const totalShares = document.getElementById('totalShares')
const hashrate = document.getElementById('hashrate')
const balance = document.getElementById('balance')
const immatureBalance = document.getElementById('immatureBalance')
const paidBalance = document.getElementById('paidBalance')
const estimatedBTCZ = document.getElementById('estimatedBTCZ')
const estimatedCurrency = document.getElementById('estimatedCurrency')
const gpuIcon = document.getElementById('gpuIcon');

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

function startAnimation() {
    gpuIcon.style.color = '';
    gpuIcon.style.textShadow = '';
    gpuIcon.classList.remove('slow-stop');
    gpuIcon.classList.add('active');
}

function stopAnimation() {
    gpuIcon.classList.remove('active');
    gpuIcon.classList.add('slow-stop');

    setTimeout(() => {
        gpuIcon.classList.remove('slow-stop');
        gpuIcon.style.color = '#ff5555';
        gpuIcon.style.textShadow = '0 0 4px rgba(255,85,85,0.6)';
    }, 2500);
}

document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
});

document.addEventListener('keydown', (e) => {
    e.preventDefault();
});