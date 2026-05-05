export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');

  const SUPABASE_URL = process.env.SUPABASE_URL || 'https://neqmepestaetsooulxqz.supabase.co';
  const SUPABASE_KEY = process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5lcW1lcGVzdGFldHNvb3VseHF6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc1NDM1OTUsImV4cCI6MjA5MzExOTU5NX0.KJcYjdQ_HjSVgbkRp4qZ_-LslHQ27755mRCP6Urrh2s';

  const { commodity, state } = req.query;

  if (!commodity) {
    return res.status(400).json({ error: 'commodity param required' });
  }

  try {
    let url = `${SUPABASE_URL}/rest/v1/mandi_prices`
            + `?commodity=eq.${encodeURIComponent(commodity)}`
            + `&order=price_date.desc,modal_price.desc`
            + `&limit=200`;

    if (state) {
      url += `&state=eq.${encodeURIComponent(state)}`;
    }

    const response = await fetch(url, {
      headers: {
        'apikey':        SUPABASE_KEY,
        'Authorization': `Bearer ${SUPABASE_KEY}`,
        'Content-Type':  'application/json',
      }
    });

    const data = await response.json();

    const records = data.map(r => ({
      market:       r.market,
      state:        r.state,
      district:     r.district,
      commodity:    r.variety,
      min_price:    r.min_price,
      modal_price:  r.modal_price,
      max_price:    r.max_price,
      arrival_date: r.price_date,
    }));

    return res.status(200).json({ records });

  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}
