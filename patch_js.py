with open('static/app.js', 'r') as f:
    js = f.read()

new_js = """
// Diagnostic form logic
const diagForm = document.getElementById("diagnostic-form");
if (diagForm) {
  diagForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const msg = document.getElementById("diag-message");
    const resultBox = document.getElementById("diagnostic-result");
    msg.textContent = "Generando diagnóstico global...";
    msg.className = "form-message";
    
    const fd = new FormData();
    const file = document.getElementById("diag-csv").files[0];
    if (file) fd.append("csv_file", file);
    
    const thdi = document.getElementById("diag-thdi").value;
    fd.append("params", JSON.stringify({ thdi_medido: parseFloat(thdi) }));
    
    try {
      const res = await fetch("/api/diagnostic/run", { method: "POST", body: fd });
      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(errorText);
      }
      const data = await res.json();
      
      msg.textContent = "Diagnóstico generado con éxito.";
      
      resultBox.innerHTML = `
        <article class="panel">
          <div class="panel-title">
            <div><p class="eyebrow">DIAGNÓSTICO FINAL</p><h2>Reporte PDF Listo</h2></div>
            <a href="${data.pdf.url}" target="_blank" class="button primary">Descargar PDF</a>
          </div>
          <p><strong>Resultado de sugerencias:</strong> ${data.mitigacion_text}</p>
          <p><strong>Plantillas evaluadas:</strong> ${data.resultados_24_count}</p>
        </article>
      `;
    } catch (err) {
      msg.textContent = "Error: " + err.message;
      msg.className = "form-message form-error";
    }
  });
}
"""

if 'diagnostic-form' not in js:
    js += '\n' + new_js
    with open('static/app.js', 'w') as f:
        f.write(js)
