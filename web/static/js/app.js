// Clarity — Trial Design Agent (Static UI placeholder)
// The Streamlit app (web/app.py) is the primary UI.
// This JS file exists for the static HTML template.

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('trial-form');
    const resultsPlaceholder = document.getElementById('results-placeholder');

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const btn = document.getElementById('run-btn');
            btn.disabled = true;
            btn.textContent = '⏳ Simulating...';

            if (resultsPlaceholder) {
                resultsPlaceholder.innerHTML = `
                    <div class="loading">
                        <p>🧪 Running 10,000 virtual trials...</p>
                        <p style="color: var(--text-muted); font-size: 0.9rem;">
                            Querying Actian for similar designs...
                        </p>
                    </div>
                `;
            }

            // Collect form data
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
                        <p style="color: var(--error);">Error: ${err.message}</p>
                        <p style="color: var(--text-muted);">Run the Streamlit app for full functionality.</p>
                    `;
                }
            }

            btn.disabled = false;
            btn.textContent = '🚀 Run Simulation';
        });
    }
});

function displayResults(result) {
    const placeholder = document.getElementById('results-placeholder');
    if (!placeholder) return;

    const viable = result.power >= 0.80;
    placeholder.innerHTML = `
        <div class="metric-row">
            <div class="metric">
                <span class="metric-value">${(result.power * 100).toFixed(0)}%</span>
                <span class="metric-label">Statistical Power</span>
            </div>
            <div class="metric">
                <span class="metric-value">${viable ? '✅' : '❌'}</span>
                <span class="metric-label">Design Viable</span>
            </div>
        </div>
        <p style="margin-top: 1rem; color: var(--accent);">
            🤖 Agent advised: ${result.advice || 'Design is viable.'}
        </p>
    `;
}
