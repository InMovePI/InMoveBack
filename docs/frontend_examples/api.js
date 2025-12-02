// Exemplo simples de service para o frontend (usar fetch ou axios)
export async function apiFetch(path, { method = 'GET', token = null, body = null } = {}) {
  const base = import.meta?.env?.VITE_API_BASE || 'http://localhost:8000'
  const headers = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const opts = { method, headers }
  if (body) opts.body = JSON.stringify(body)

  const resp = await fetch(`${base}${path}`, opts)
  if (!resp.ok) throw resp
  return resp.json()
}

export async function searchFoods(q, country = 'BR', lang = 'pt', token) {
  const base = import.meta?.env?.VITE_API_BASE || 'http://localhost:8000'
  const resp = await fetch(`${base}/meals/search-food/?q=${encodeURIComponent(q)}&country=${country}&lang=${lang}`, { headers: token ? { Authorization: `Bearer ${token}` } : {} })
  if (!resp.ok) throw resp
  return resp.json()
}

export async function createMeal(payload, token) {
  const base = import.meta?.env?.VITE_API_BASE || 'http://localhost:8000'
  const resp = await fetch(`${base}/meals/`, { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` }, body: JSON.stringify(payload) })
  if (resp.status !== 201) throw resp
  return resp.json()
}
