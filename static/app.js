let isPaused = false;
let ws;

// DOM Elements
const btnPause = document.getElementById('toggle-pause');
const kpiRead = document.getElementById('kpi-read');
const kpiDsp = document.getElementById('kpi-dsp');
const kpiWrite = document.getElementById('kpi-write');
const kpiFreq = document.getElementById('kpi-freq');
const logsBox = document.getElementById('logs-box');

// Configuration constants from config.yaml (default assumption)
const samplingRate = 12800;
const samplesPerFrame = 256;
const timeVector = Array.from({length: samplesPerFrame}, (_, i) => (i / samplingRate) * 1000); // in ms

// Chart Setup
Chart.defaults.color = '#e0e0e0';
Chart.defaults.font.family = 'Segoe UI';

const ctxWave = document.getElementById('waveformChart').getContext('2d');
const waveformChart = new Chart(ctxWave, {
    type: 'line',
    data: {
        labels: timeVector.map(t => t.toFixed(1)),
        datasets: [
            {
                label: 'Onda Cruda',
                borderColor: '#C2C0E3',
                backgroundColor: 'rgba(194, 192, 227, 0.1)',
                borderWidth: 2,
                pointRadius: 0,
                data: []
            },
            {
                label: 'Onda Compensada',
                borderColor: '#A7B7CF',
                backgroundColor: 'rgba(167, 183, 207, 0.1)',
                borderWidth: 2,
                pointRadius: 0,
                data: []
            }
        ]
    },
    options: {
        responsive: true,
        animation: false, // For real-time updates
        scales: {
            x: { title: { display: true, text: 'Tiempo (ms)', color: '#aaa' } },
            y: { title: { display: true, text: 'Amplitud', color: '#aaa' } }
        },
        plugins: {
            legend: {
                position: 'top',
            }
        }
    }
});

const ctxSpec = document.getElementById('spectrumChart').getContext('2d');
const spectrumChart = new Chart(ctxSpec, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            label: 'Magnitud (Cruda)',
            backgroundColor: '#FFFF99',
            data: []
        }]
    },
    options: {
        responsive: true,
        animation: false,
        scales: {
            x: { title: { display: true, text: 'Frecuencia (Hz)', color: '#aaa' } },
            y: { title: { display: true, text: 'Magnitud', color: '#aaa' } }
        }
    }
});

function addLog(msg, type='info') {
    const el = document.createElement('div');
    el.className = `log-entry log-${type}`;
    const timestamp = new Date().toLocaleTimeString();
    el.innerText = `[${timestamp}] ${msg}`;
    logsBox.appendChild(el);
    if(logsBox.childNodes.length > 50) {
        logsBox.removeChild(logsBox.firstChild);
    }
    logsBox.scrollTop = logsBox.scrollHeight;
}

// Compute Simple Radix-2 FFT or just DFT for spectrum visualization
// To avoid heavy computation in browser, we compute a simple DFT only for the first few harmonic bins.
function computeMagnitudeSpectrum(waveform) {
    const N = waveform.length;
    // Windowing (Hanning)
    const windowed = waveform.map((val, n) => val * (0.5 * (1 - Math.cos((2 * Math.PI * n) / (N - 1)))));
    
    const magnitudes = [];
    const labels = [];
    const numBins = 10; // Up to 9th harmonic
    
    // Frequency bins size is exactly fundamental freq if fs/N = 50Hz (12800/256 = 50Hz)
    for(let k = 0; k <= numBins; k++) {
        let re = 0;
        let im = 0;
        for(let n = 0; n < N; n++) {
            const angle = (2 * Math.PI * k * n) / N;
            re += windowed[n] * Math.cos(angle);
            im -= windowed[n] * Math.sin(angle);
        }
        // Normalize magnitude
        const mag = Math.sqrt(re*re + im*im) / N * 2; 
        magnitudes.push(k === 0 ? mag / 2 : mag);
        labels.push(`${k * 50} Hz`);
    }
    return { magnitudes, labels };
}

let lastFrameTime = performance.now();
let lastChartUpdate = performance.now();

// New DOM elements
const kpiThdi = document.getElementById('kpi-thdi');
const kpiSat = document.getElementById('kpi-sat');
const satCard = document.getElementById('sat-card');

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

    ws.onopen = () => {
        addLog("Conectado al servidor WebSocket.", "info");
    };

    ws.onmessage = (event) => {
        if(isPaused) return;

        const data = JSON.parse(event.data);
        
        // Update KPIs
        if(kpiRead) kpiRead.innerText = '-- ms'; // Deprecated in HRT
        kpiDsp.innerText = data.t_dsp_ms.toFixed(3) + ' ms';
        kpiFreq.innerText = data.freq_est.toFixed(2) + ' Hz';
        kpiThdi.innerText = data.thdi.toFixed(1) + ' %';
        
        if(data.is_saturated) {
            kpiSat.innerText = 'SATURADO';
            kpiSat.style.color = '#FFFF99';
            satCard.style.borderColor = '#FFFF99';
        } else {
            kpiSat.innerText = 'OK';
            kpiSat.style.color = '#EAEEF4';
            satCard.style.borderColor = 'var(--border-color)';
        }

        const now = performance.now();
        if (now - lastChartUpdate > 200) {
            lastChartUpdate = now;
            
            // Update Waveform Chart
            waveformChart.data.datasets[0].data = data.raw_waveform;
            waveformChart.data.datasets[1].data = data.comp_waveform;
            waveformChart.update();

            // Update Spectrum Chart (using pre-calculated multi-SRF RMS values from server!)
            spectrumChart.data.labels = ['Fund', '3º Arm', '5º Arm', '7º Arm'];
            spectrumChart.data.datasets[0].data = [
                100, // Fundamental is normalized to ~100 in our generator
                data.h3_rms,
                data.h5_rms,
                data.h7_rms
            ];
            spectrumChart.update();
            
            addLog(`Recibida Trama #${data.frame_count} | Freq: ${data.freq_est.toFixed(2)}Hz | THDi: ${data.thdi.toFixed(1)}%`, "info");
        }
    };

    ws.onclose = () => {
        addLog("Conexión WebSocket cerrada. Reconectando en 2s...", "warn");
        setTimeout(connectWebSocket, 2000);
    };

    ws.onerror = (err) => {
        addLog("Error de conexión WebSocket.", "error");
    };
}

btnPause.addEventListener('click', () => {
    isPaused = !isPaused;
    btnPause.innerText = isPaused ? "Reanudar Actualización" : "Pausar Actualización";
    addLog(isPaused ? "Actualización pausada por el usuario." : "Actualización reanudada.", "warn");
});

// Start connection
connectWebSocket();
