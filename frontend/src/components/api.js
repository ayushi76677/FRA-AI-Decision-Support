export async function getJson(api, path) { const response = await fetch(`${api}${path}`); if (!response.ok) throw new Error(`Request failed (${response.status})`); return response.json() }
export async function getOptional(api, path, fallback) { try { return await getJson(api, path) } catch { return fallback } }
