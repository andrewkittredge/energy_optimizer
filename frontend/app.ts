const form = document.getElementById('params-form') as HTMLFormElement;
const result = document.getElementById('result') as HTMLElement;

interface OptimizeBody {
  [key: string]: number | Record<string, number>;
}

form.addEventListener('submit', async (ev: Event): Promise<void> => {
  ev.preventDefault();
  const data = new FormData(form);
  const body: OptimizeBody = {};
  
  for (const [k, v] of data.entries()) {
    if (k === 'solar_installation_sizes') {
      try {
        body[k] = JSON.parse(v as string);
      } catch (err) {
        result.textContent = 'Invalid JSON for solar sizes';
        return;
      }
    } else if (v !== '') {
      body[k] = Number(v);
    }
  }

  result.textContent = 'Running...';

  try {
    const resp = await fetch('/optimize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const j = await resp.json();
    result.textContent = JSON.stringify(j, null, 2);
  } catch (err) {
    result.textContent = 'Request failed: ' + (err instanceof Error ? err.message : String(err));
  }
});
