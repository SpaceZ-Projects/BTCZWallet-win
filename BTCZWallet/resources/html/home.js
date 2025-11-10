
let btczChart;
let chartFailed = false;

function generateData(prices, currency) {
  const ctx = document.getElementById('btczChart').getContext('2d');

  if (!prices || prices.length === 0) {
    chartFailed = true;
    btczChart = new Chart(ctx, {
      type: 'line',
      data: { labels: [], datasets: [] },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: { enabled: false },
          centerText: { message: "Unable to load market data\nRetrying in 10 minutes..." }
        }
      },
      plugins: [{
        id: 'centerText',
        beforeDraw: (chart) => {
          const {ctx, width, height} = chart;
          const pluginOptions = chart.config.options.plugins.centerText;
          if (!pluginOptions || !pluginOptions.message) return;
          ctx.save();
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.font = '16px Inter, sans-serif';
          ctx.fillStyle = '#ed3a3a';
          const lines = pluginOptions.message.split("\n");
          lines.forEach((line, index) => {
            ctx.fillText(line, width / 2, height / 2 + index * 26);
          });
          ctx.restore();
        }
      }]
    });
    return;
  }

  if (chartFailed && btczChart) {
    btczChart.destroy();
    btczChart = null;
    chartFailed = false;
  }

  const labels = prices.map(p => {
    const d = new Date(p[0]);
    return `${d.getHours()}:${('0'+d.getMinutes()).slice(-2)}`;
  });

  const data = prices.map(p => p[1]);

  const gradientLine = ctx.createLinearGradient(0,0,0,400);
  gradientLine.addColorStop(0,'rgba(3, 240, 252,0.9)');
  gradientLine.addColorStop(1,'rgba(252, 3, 3,0.3)');

  const gradientFill = ctx.createLinearGradient(0,0,0,400);
  gradientFill.addColorStop(0,'rgba(3, 240, 252,0.25)');
  gradientFill.addColorStop(1,'rgba(252, 3, 3,0.05)');

  if (btczChart) {
    btczChart.data.labels = labels;
    btczChart.data.datasets[0].data = data;
    btczChart.data.datasets[0].label = `BTCZ/${currency}`;
    btczChart.update();
    return;
  }

  btczChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: `BTCZ/${currency}`,
        data: data,
        borderColor: gradientLine,
        backgroundColor: gradientFill,
        fill: true,
        tension: 0.35,
        borderWidth: 2.5,
        pointRadius: 3,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: '#00d4ff'
      }]
    },
    options: {
      maintainAspectRatio: false,
      interaction: { mode: 'nearest', intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          enabled: true,
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(0,0,0,0.7)',
          titleColor: '#fff',
          bodyColor: '#fff',
          borderColor: 'rgba(255,255,255,0.2)',
          borderWidth: 1,
          callbacks: { label: ctx => `${currency} ${ctx.parsed.y.toFixed(8)}` }
        }
      },
      scales: {
        x: { grid: { display: false, drawBorder: false }, ticks: { display: false } },
        y: { 
          grid: { color:'rgba(255,255,255,0.05)', borderDash:[4,6] }, 
          ticks: { 
            color:'#9aa4b2',
            callback: value => value < 0.0001 ? value.toFixed(8) : value
          }
        }
      }
    }
  });
}


function setBTCZPrice(value) {
  document.getElementById('btczPrice').textContent = value ?? '--';
}

function setMarketCap(value) {
  document.getElementById('marketCap').textContent = value ?? '--';
}

function setVolume(value) {
  document.getElementById('volume').textContent = value ?? '--';
}

function setChange24h(value) {
  const el = document.getElementById('change24h');
  el.textContent = value ?? '--';
  if (value && !isNaN(parseFloat(value))) {
    const num = parseFloat(value);
    el.style.color = num >= 0 ? '#00d48f' : '#ed3a3a';
  } else {
    el.style.color = '#e6eef6';
  }
}

function setChange7d(value) {
  const el = document.getElementById('change7d');
  el.textContent = value ?? '--';
  if (value && !isNaN(parseFloat(value))) {
    const num = parseFloat(value);
    el.style.color = num >= 0 ? '#00d48f' : '#ed3a3a';
  } else {
    el.style.color = '#e6eef6';
  }
}

function setCirculating(value) {
  document.getElementById('circulating').textContent = value ? `${value} BTCZ` : '-- BTCZ';
}

function setNextHalving(value) {
  const el = document.getElementById('nextHalving');
  el.textContent = value ?? '--';
}

function setDeprecation(value) {
  const el = document.getElementById('deprecation');
  el.textContent = value ?? '--';
}

const tooltip = document.getElementById('tooltip');
const circulatingEl = document.getElementById('circulating');

circulatingEl.addEventListener('mouseenter', e => {
  tooltip.style.left = e.pageX + 'px';
  tooltip.style.top = (e.pageY - 30) + 'px';
  tooltip.style.opacity = '1';
  tooltip.style.transform = 'translateY(0)';
});

circulatingEl.addEventListener('mousemove', e => {
  tooltip.style.left = e.pageX + 'px';
  tooltip.style.top = (e.pageY - 30) + 'px';
});

circulatingEl.addEventListener('mouseleave', () => {
  tooltip.style.opacity = '0';
  tooltip.style.transform = 'translateY(-8px)';
});


function setCirculatingTooltip(text) {
  const tooltip = document.getElementById('tooltip');
  tooltip.textContent = text ?? '';
}


document.addEventListener('contextmenu', function(e) {
  e.preventDefault();
});


document.addEventListener('keydown', (e) => {
    e.preventDefault();
});