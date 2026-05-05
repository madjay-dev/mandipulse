export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');

  const API_KEY = '579b464db66ec23bdd000001d10eef9e75364fcd6bc278c4f024c720';
  const BASE    = 'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070';

  const { commodity } = req.query;

  if (!commodity) {
    return res.status(400).json({ error: 'commodity param required' });
  }

  try {
    const url = `${BASE}?api-key=${API_KEY}&format=json&limit=100&filters[commodity]=${encodeURIComponent(commodity)}`;
    const response = await fetch(url);
    const data     = await response.json();
    return res.status(200).json(data);
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}
