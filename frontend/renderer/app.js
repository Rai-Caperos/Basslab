document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'))
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'))
    tab.classList.add('active')
    document.getElementById('tab-' + tab.dataset.tab).classList.add('active')
  })
})

async function checkBackend() {
  try {
    const r = await fetch('http://127.0.0.1:8007/ping')
    const data = await r.json()
    if (data.status === 'ok') {
      document.getElementById('status-dot').classList.add('online')
      document.getElementById('status-txt').textContent = 'ONLINE'
    }
  } catch {
    document.getElementById('status-dot').classList.remove('online')
    document.getElementById('status-txt').textContent = 'OFFLINE'
  }
}

checkBackend()
setInterval(checkBackend, 5000)