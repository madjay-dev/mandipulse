import requests
from datetime import datetime
import os
from supabase import create_client

# ── CONFIG ──────────────────────────────────────────────────
SUPABASE_URL  = os.environ.get('SUPABASE_URL')
SUPABASE_KEY  = os.environ.get('SUPABASE_SERVICE_KEY')
AGMARKNET_KEY = os.environ.get('AGMARKNET_KEY')

AGMARKNET_BASE = 'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070'

COMMODITIES = {
  'Grapes':      ['Grapes','Grapes(Black)','Grapes(Green)','Grapes(White)'],
  'Apple':       ['Apple'],
  'Mango':       ['Mango','Mango (Totapuri)','Mango(Alphonso)','Mango(Banginapalli)','Mango(Dasheri)','Mango(Kesar)','Mango(Langra)'],
  'Pomegranate': ['Pomegranate'],
  'Orange':      ['Orange','Mosambi(Sweet Lime)'],
  'Coconut':     ['Coconut','Coconut(Dried)','Tender Coconut'],
  'Garlic':      ['Garlic'],
  'Ginger':      ['Ginger(Dry)','Ginger(Green)','Ginger'],
  'Onion':       ['Onion','Onion(Brown)','Onion Large','Onion Small'],
  'Potato':      ['Potato','Potato(Kufri Jyoti)','Potato(Desi)'],
}

# ── INIT SUPABASE ────────────────────────────────────────────
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── FETCH FROM AGMARKNET ─────────────────────────────────────
def fetch_commodity(name):
    url = (
        f"{AGMARKNET_BASE}"
        f"?api-key={AGMARKNET_KEY}"
        f"&format=json"
        f"&limit=500"
        f"&filters[commodity]={requests.utils.quote(name)}"
    )
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        return res.json().get('records', [])
    except Exception as e:
        print(f"  Error fetching {name}: {e}")
        return []

# ── PARSE DATE ───────────────────────────────────────────────
def parse_date(date_str):
    if not date_str or date_str == '—':
        return datetime.today().strftime('%Y-%m-%d')
    for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']:
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except:
            continue
    return datetime.today().strftime('%Y-%m-%d')

# ── SAVE TO SUPABASE ─────────────────────────────────────────
def save_records(commodity, records):
    # Deduplicate within batch first
    seen = {}
    for r in records:
        modal = int(r.get('modal_price') or r.get('Modal_Price') or 0)
        if modal <= 0:
            continue
        row = {
            'commodity':   commodity,
            'market':      (r.get('market')    or r.get('Market')    or '').strip(),
            'state':       (r.get('state')     or r.get('State')     or '').strip(),
            'district':    (r.get('district')  or r.get('District')  or '').strip(),
            'variety':     (r.get('commodity') or r.get('Commodity') or '').strip(),
            'min_price':   int(r.get('min_price') or r.get('Min_Price') or 0),
            'modal_price': modal,
            'max_price':   int(r.get('max_price') or r.get('Max_Price') or 0),
            'price_date':  parse_date(r.get('arrival_date') or r.get('Arrival_Date')),
        }
        # Use same fields as unique constraint
        key = f"{row['commodity']}|{row['market']}|{row['variety']}|{row['price_date']}"
        if key not in seen:
            seen[key] = row

    rows = list(seen.values())

    if not rows:
        print(f"  No valid rows for {commodity}")
        return 0

    # Upsert — insert new, update existing
    supabase.table('mandi_prices').upsert(
        rows,
        on_conflict='commodity,market,variety,price_date'
    ).execute()

    return len(rows)

# ── MAIN ─────────────────────────────────────────────────────
def main():
    print(f"\n🌾 MandiPulse Scraper — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    total = 0
    for commodity, names in COMMODITIES.items():
        print(f"\n📦 {commodity}")
        count = 0
        for name in names:
            print(f"  Fetching: {name}")
            records = fetch_commodity(name)
            print(f"  Found: {len(records)} records")
            saved = save_records(commodity, records)
            count += saved
        print(f"  ✅ Saved {count} records for {commodity}")
        total += count

    print(f"\n{'='*50}")
    print(f"✅ Done. Total records saved: {total}")

if __name__ == '__main__':
    main()
