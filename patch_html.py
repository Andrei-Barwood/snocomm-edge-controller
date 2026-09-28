with open('templates/index.html', 'r') as f:
    html = f.read()

# Add button
if 'data-view="diagnostic"' not in html:
    html = html.replace(
        '<button class="nav-item active" data-view="calculator" aria-current="page">Calculadora</button>',
        '<button class="nav-item active" data-view="calculator" aria-current="page">Calculadora</button>\n    <button class="nav-item" data-view="diagnostic">Diagnóstico General</button>'
    )

# Add section
new_section = """
    <section id="diagnostic-view" class="view" aria-labelledby="diagnostic-title" hidden>
      <div class="page-heading">
        <div>
          <p class="eyebrow">DIAGNÓSTICO COMPLETO</p>
          <h1 id="diagnostic-title">Diagnóstico General (24 Plantillas)</h1>
          <p>Exportador de texto en PDF que genera un análisis completo con sugerencias de mitigación eléctrica (filtros, reactores, SNR) y evalúa las 24 plantillas simultáneamente.</p>
        </div>
      </div>
      <div class="calculator-layout">
        <form id="diagnostic-form" class="panel design-form">
          <div class="panel-title">
            <div>
              <p class="eyebrow">GENERACIÓN DE DIAGNÓSTICO</p>
              <h2>Subir campaña para análisis global</h2>
            </div>
          </div>
          <div class="import-grid calc-files">
            <label>Campaña CSV (Osciloscopio) <input id="diag-csv" type="file" accept=".csv,.txt,text/csv" required></label>
            <label>THDi medido (%) <input id="diag-thdi" type="number" step="0.1" value="12.0" name="thdi_medido"></label>
          </div>
          <button class="button primary" type="submit">Generar Diagnóstico Completo PDF</button>
          <p id="diag-message" class="form-message" role="alert"></p>
        </form>
        <section id="diagnostic-result" class="result-stack" aria-live="polite">
          <article class="panel empty-result">
            <p class="eyebrow">REPORTE FINAL</p>
            <h2>Listo para generar</h2>
            <p>Al procesar, se compilarán las 24 plantillas y el texto de tesis sugerido por Gemini en un solo archivo PDF.</p>
          </article>
        </section>
      </div>
    </section>
"""

if 'id="diagnostic-view"' not in html:
    html = html.replace(
        '</main>',
        new_section + '\n  </main>'
    )

with open('templates/index.html', 'w') as f:
    f.write(html)
