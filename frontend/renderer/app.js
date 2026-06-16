// ── Backend check ──────────────────────────────────────────
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

// ── Pestañas ───────────────────────────────────────────────
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'))
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'))
    tab.classList.add('active')
    document.getElementById('tab-' + tab.dataset.tab).classList.add('active')
  })
})

// ── Carga de archivo ───────────────────────────────────────
let archivoSeleccionado = null

const dropZone = document.getElementById('drop-zone')
const fileInfo = document.getElementById('file-info')
const fileName = document.getElementById('file-name')
const fileMeta = document.getElementById('file-meta')
const btnAnalizar = document.getElementById('btn-analizar')

dropZone.addEventListener('click', () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.mp3,audio/*'
  input.onchange = e => cargarArchivo(e.target.files[0])
  input.click()
})

document.addEventListener('dragover', e => e.preventDefault())
document.addEventListener('drop', e => e.preventDefault())

dropZone.addEventListener('dragover', e => {
  e.preventDefault()
  dropZone.classList.add('drag-over')
})

dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('drag-over')
})

dropZone.addEventListener('drop', e => {
  e.preventDefault()
  dropZone.classList.remove('drag-over')
  const file = e.dataTransfer.files[0]
  if (file) cargarArchivo(file)
})

function cargarArchivo(file) {
  archivoSeleccionado = file
  fileName.textContent = file.name
  fileMeta.textContent = (file.size / 1024 / 1024).toFixed(2) + ' MB'
  fileInfo.classList.remove('hidden')
  btnAnalizar.classList.remove('hidden')
  lcdSet('ARCHIVO CARGADO', file.name.substring(0, 16), '44.1kHz · MP3')
}

// ── Análisis ───────────────────────────────────────────────
btnAnalizar.addEventListener('click', async () => {
  if (!archivoSeleccionado) return

  const progreso = document.getElementById('progreso')
  const progresoFill = document.getElementById('progreso-fill')
  const progresoTxt = document.getElementById('progreso-txt')

  btnAnalizar.classList.add('hidden')
  progreso.classList.remove('hidden')
  lcdSet('ANALIZANDO...', 'SEPARANDO BAJO', 'GPU · demucs')

  // Animación de progreso simulada mientras trabaja la GPU
  let pct = 0
  const intervalo = setInterval(() => {
    pct = Math.min(pct + 1, 90)
    progresoFill.style.width = pct + '%'
  }, 300)

  try {
    const formData = new FormData()
    formData.append('archivo', archivoSeleccionado)

    progresoTxt.textContent = 'Separando bajo con demucs...'
    const r1 = await fetch('http://127.0.0.1:8007/analizar-bajo', {
      method: 'POST',
      body: formData
    })
    const d1 = await r1.json()

    if (d1.error) throw new Error(d1.error)

    progresoTxt.textContent = 'Detectando notas...'
    lcdSet('DETECTANDO', 'NOTAS · librosa', 'Do-Re-Mi')

    // Ahora pedimos la tablatura del bajo extraído
    const nombreBajo = d1.archivo_bajo
    progresoFill.style.width = '95%'
    progresoTxt.textContent = 'Generando tablatura...'

    // Leemos el archivo WAV del bajo y lo mandamos al endpoint de tablatura
    const respWav = await fetch('http://127.0.0.1:8007/bajo-extraido?ruta=' + encodeURIComponent(nombreBajo))
    const wavBlob = await respWav.blob()
    const formData2 = new FormData()
    formData2.append('archivo', wavBlob, 'bajo.wav')

    const r2 = await fetch('http://127.0.0.1:8007/generar-tablatura', {
      method: 'POST',
      body: formData2
    })
    const d2 = await r2.json()

    clearInterval(intervalo)
    progresoFill.style.width = '100%'
    progresoTxt.textContent = 'Análisis completado'
    lcdSet('COMPLETADO', d2.total_notas + ' NOTAS', 'TABLATURA LISTA')

    setTimeout(() => {
      progreso.classList.add('hidden')
      btnAnalizar.classList.remove('hidden')
      mostrarTablatura(d2.tablatura)
    }, 800)

  } catch (err) {
    clearInterval(intervalo)
    progresoTxt.textContent = 'Error: ' + err.message
    lcdSet('ERROR', 'VER CONSOLA', '—')
  }
})

// ── LCD helper ─────────────────────────────────────────────
function lcdSet(l1, l2, l3) {
  document.getElementById('lcd-line1').textContent = l1
  document.getElementById('lcd-line2').textContent = l2
  document.getElementById('lcd-line3').textContent = l3
}

// ── Tablatura ──────────────────────────────────────────────
function mostrarTablatura(notas) {
  const content = document.getElementById('tablatura-content')
  if (!notas || notas.length === 0) {
    content.innerHTML = '<div class="placeholder">No se detectaron notas</div>'
    return
  }

  const cuerdas = ['G', 'D', 'A', 'E']
  let html = '<div class="tab-grid">'

  cuerdas.forEach(cuerda => {
    html += `<div class="tab-cuerda">`
    html += `<span class="tab-cuerda-nombre">${cuerda}</span>`
    html += `<div class="tab-linea">`
    notas.forEach(n => {
      if (n.cuerda === cuerda) {
        html += `<div class="tab-nota" style="left:${(n.tiempo * 40)}px" title="${n.nota} · ${n.tiempo}s">${n.traste}</div>`
      }
    })
    html += `</div></div>`
  })

  html += '</div>'
  content.innerHTML = html
}