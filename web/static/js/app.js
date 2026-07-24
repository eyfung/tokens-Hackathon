// Clarity — Trial Design Agent (Ventriloc editorial style)

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('trial-form');
    const resultsPlaceholder = document.getElementById('results-placeholder');

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const btn = document.getElementById('run-btn');
            btn.disabled = true;
            btn.textContent = 'Simulating...';

            if (resultsPlaceholder) {
                resultsPlaceholder.innerHTML = `
                    <div class="loading">
                        <p class="text-steel">Running 10,000 virtual trials...</p>
                        <p class="text-slate caption" style="margin-top:8px;">
                            Querying Actian for similar designs...
                        </p>
                    </div>
                `;
            }

            const data = {
                disease: document.getElementById('disease').value,
                endpoint: document.getElementById('endpoint').value,
                effect: parseFloat(document.getElementById('effect').value),
                variability: parseFloat(document.getElementById('variability').value),
                n: parseInt(document.getElementById('n-per-arm').value),
            };

            try {
                const response = await fetch('/api/simulate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                });
                const result = await response.json();
                displayResults(result);
            } catch (err) {
                if (resultsPlaceholder) {
                    resultsPlaceholder.innerHTML = `
                        <div class="result-section">
                            <p style="color: var(--color-ember-orange);">Error: ${err.message}</p>
                            <p class="text-slate caption mt-8">Run the Streamlit app for full functionality.</p>
                        </div>
                    `;
                }
            }

            btn.disabled = false;
            btn.textContent = 'Run Simulation';
        });
    }
});

function displayResults(result) {
    const placeholder = document.getElementById('results-placeholder');
    if (!placeholder) return;

    const viable = result.power >= 0.80;
    const dotClass = viable ? 'viable' : 'fail';
    const statusText = viable ? 'Design viable' : 'Underpowered';

    placeholder.innerHTML = `
        <div class="result-section">
            <div class="metric-row">
                <div class="metric">
                    <div class="metric-value">${(result.power * 100).toFixed(0)}%</div>
                    <div class="metric-label">Statistical Power</div>
                </div>
                <div class="metric">
                    <div class="metric-value">
                        <span class="status-dot ${dotClass}"></span>
                    </div>
                    <div class="metric-label">${statusText}</div>
                </div>
            </div>
        </div>
        <hr />
        <div class="result-section">
            <p class="text-steel">
                ${result.advice || 'Design meets the target power threshold.'}
            </p>
        </div>
        <div class="result-section">
            <span class="tag">n=${result.sample_size || '—'}</span>
            <span class="tag tag-brass">CI: ${(result.ci_lower !== undefined ? (result.ci_lower * 100).toFixed(1) : '—')}–${(result.ci_upper !== undefined ? (result.ci_upper * 100).toFixed(1) : '—')}%</span>
        </div>
    `;
}
