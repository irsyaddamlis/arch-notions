import re
import time
from datetime import datetime, timedelta
from functools import lru_cache
from io import BytesIO

import pandas as pd
import pdfplumber
import pytesseract
import requests
import yfinance as yf
from babel.dates import format_date
from bs4 import BeautifulSoup
from dbnomics import fetch_series
from pdf2image import convert_from_bytes
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==================
# PREPARE CONNECTION
# ==================

EXCHANGE_RATE_API_KEY = "fe666249f2d157a154442e5b"
er_url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/latest/USD"

ALPHA_VANTAGE_API_KEY = "B759VK2V5RWBZQA2"
av_url = f"https://www.alphavantage.co/query?function=WTI&interval=daily&apikey={ALPHA_VANTAGE_API_KEY}"

FRED_API_KEY = "660a6283c8f929627a5eff8f5f1e89bb"
fr_url = "https://api.stlouisfed.org/fred/series/observations"

BIBROAD_URL = "https://www.bi.go.id/SEKI/tabel/TABEL1_1.pdf"
BIDEPOSIT_URL = "https://www.bi.go.id/SEKI/tabel/TABEL1_28.pdf"
BILOAN_URL = "https://www.bi.go.id/SEKI/tabel/TABEL1_26.pdf"
# NOTE: BIDEPOSIT_URL and BILOAN_URL currently point at the SAME table
# (TABEL1_28.pdf). Please confirm the correct BI table numbers for
# deposit rates vs loan rates - I've left the constants as you had them,
# but wired deposit_rate() to read from BIDEPOSIT_URL (previously it
# silently read from BILOAN_URL, which was presumably a copy/paste slip).

BIRATE_URL = "https://www.bi.go.id/id/statistik/indikator/bi-rate.aspx"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/pdf,*/*",
    "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
    "Referer": "https://www.bi.go.id/id/statistik/ekonomi-keuangan/seki/default.aspx",
    "Connection": "keep-alive",
}

today = datetime.today()
one_month_ago = today - timedelta(days=30)
today_str = today.strftime('%Y-%m-%d')
start_date_str = one_month_ago.strftime('%Y-%m-%d')
end_date_str = (today + timedelta(days=2)).strftime('%Y-%m-%d')


# ============
# DEFINE MODEL
# ============

# ---- Exchange rates: fetched ONCE per process and reused everywhere ----
# (previously each currency function hit the API separately - 7 calls
# instead of 1). lru_cache means this only refreshes if you restart the
# process / clear the cache - fine for a one-shot script or scheduled
# job, but call usd_exc.cache_clear() (or restart) if this ends up
# running as a long-lived server and you need fresh rates periodically.
@lru_cache(maxsize=1)
def _get_conversion_rates():
    resp = requests.get(er_url, timeout=15)
    resp.raise_for_status()
    return resp.json()["conversion_rates"]


def _fmt(value, prefix="", suffix=""):
    if value is None:
        return "N/A"
    return f"{prefix}{value:,.2f}{suffix}"


def _idr_value(target_code=None):
    """Returns IDR value of 1 unit of target_code (or 1 USD if None)."""
    rates = _get_conversion_rates()
    idr_rate = rates.get("IDR")
    if idr_rate is None:
        return None
    if target_code is None:  # USD -> IDR: base currency is already USD
        return idr_rate
    target_rate = rates.get(target_code)
    if not target_rate:
        return None
    # base is USD, so 1 <target_code> = idr_rate / target_rate IDR
    return idr_rate / target_rate


# 1. Exchange USD to IDR
def usd_exc():
    try:
        return _fmt(_idr_value())
    except Exception:
        return "N/A"


# 2. Exchange Poundsterling to IDR
def pond_exc():
    try:
        return _fmt(_idr_value("GBP"))
    except Exception:
        return "N/A"


# 3. Exchange Euro to IDR
def eur_exc():
    try:
        return _fmt(_idr_value("EUR"))
    except Exception:
        return "N/A"


# 4. Exchange SGD to IDR
def sgd_exc():
    try:
        return _fmt(_idr_value("SGD"))
    except Exception:
        return "N/A"


# 5. Exchange Yuan to IDR
def cny_exc():
    try:
        return _fmt(_idr_value("CNY"))
    except Exception:
        return "N/A"


# 6. Exchange AUD to IDR
def aud_exc():
    try:
        return _fmt(_idr_value("AUD"))
    except Exception:
        return "N/A"


# 7. Exchange Yen to IDR
def jpy_exc():
    try:
        return _fmt(_idr_value("JPY"))
    except Exception:
        return "N/A"


# 8. Global Oil Price
def oil_prc():
    try:
        av_response = requests.get(av_url, timeout=15).json()
        return _fmt(float(av_response['data'][0]['value']), prefix="$")
    except Exception:
        return "N/A"


# 9. "Indeks Harga Saham Gabungan"
def ihsg():
    try:
        hist = yf.Ticker('^JKSE').history(period='1d')
        return _fmt(hist['Close'].iloc[-1])
    except Exception:
        return "N/A"


# 10. Consumer Price Index
def cpi():
    try:
        fr_response = requests.get(
            fr_url,
            params={
                'series_id': 'IDNCPALTT01IXNBM',  # Indonesia CPI
                'api_key': FRED_API_KEY,
                'file_type': 'json',
                'sort_order': 'desc',
                'limit': 5,
            },
            timeout=15,
        )
        obs = fr_response.json()['observations'][0]
        cpi_val = obs['value']
        return round(float(cpi_val), 2) if cpi_val != '.' else None
    except Exception:
        return None


# 11. GDP Growth
def gdp():
    try:
        df = fetch_series(
            provider_code='WB', dataset_code='WDI',
            series_code='A-NY.GDP.MKTP.KD.ZG-IDN'
        ).sort_values(by='period', ascending=False)
        return _fmt(float(df.iloc[0]['value']), suffix="%")
    except Exception:
        return "N/A"


'''FETCHING DATA FROM BI'''


def bi_response(url):
    """Downloads the file (PDF or Image) from the web using robust retries."""
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    last_err = None
    for attempt in range(3):
        try:
            resp = session.get(url, headers=headers, timeout=60)
            resp.raise_for_status()
            return resp
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            last_err = e
            time.sleep(3 * (attempt + 1))

    raise ConnectionError(f"Could not reach target after retries: {last_err}")


# --- FUNCTION 1: NATIVE DIGITAL PDF PROCESSING ---
# Cached: several functions read the same URL (e.g. BILOAN_URL is read by
# lending_rate/loan_rate/deposit_rate) - this avoids downloading + parsing
# the same PDF 3x per dashboard refresh.
@lru_cache(maxsize=None)
def fetch_bi(url):
    """Downloads a native PDF and extracts its digital text layout."""
    resp = bi_response(url)
    with pdfplumber.open(BytesIO(resp.content)) as pdf:
        full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    return full_text


# --- FUNCTION 2: PURE IMAGE / SCANNED PDF PROCESSING ---
@lru_cache(maxsize=None)
def fetch_bi_img(url):
    """Downloads a scanned PDF page and processes it via OCR."""
    resp = bi_response(url)
    pages = convert_from_bytes(resp.content, first_page=33, last_page=33, dpi=300)
    img = pages[0]
    full_text = pytesseract.image_to_string(img, config="--psm 6")
    return full_text


def _extract_last_number(full_text, label):
    """Shared helper: find the line containing `label` and pull the last number off it."""
    lines = [line for line in full_text.splitlines() if label in line]
    if not lines:
        return None
    target_line = lines[-1]
    data_portion = target_line.split(label)[-1]
    numbers = re.findall(r'[\d,]+', data_portion)
    values = [int(n.replace(',', '')) for n in numbers if n.replace(',', '').isdigit()]
    return values[-1] if values else None


# 12. Broad Money (M2)
def broad_money():
    try:
        full_text = fetch_bi(BIBROAD_URL)
        for label in ("Broad Money (M2)", "Uang Beredar Luas(M2)"):
            value = _extract_last_number(full_text, label)
            if value is not None:
                return _fmt(value, suffix=" billion")
        return "N/A"
    except Exception:
        return "N/A"


# 13. Lending Rate (working-capital loans given)
def lending_rate():
    try:
        full_text = fetch_bi(BILOAN_URL)
        rate = _extract_last_number(full_text, "Pinjaman Modal Kerja Yang Diberikan")
        return _fmt(rate, suffix="%") if rate is not None else "N/A"
    except Exception:
        return "N/A"


# 14. Loan Rate (consumer loans given)
def loan_rate():
    try:
        full_text = fetch_bi(BILOAN_URL)
        rate = _extract_last_number(full_text, "Pinjaman Konsumsi Yang Diberikan")
        return _fmt(rate, suffix="%") if rate is not None else "N/A"
    except Exception:
        return "N/A"


# 15. Deposit Rate (1-month)
def deposit_rate():
    try:
        # Was reading BILOAN_URL before - switched to BIDEPOSIT_URL since
        # that's clearly the intent. See the NOTE near the URL constants.
        full_text = fetch_bi(BIDEPOSIT_URL)
        rate = _extract_last_number(full_text, "1 Bulan")
        return _fmt(rate, suffix="%") if rate is not None else "N/A"
    except Exception:
        return "N/A"


def _sulni_url_for(dt):
    month_name = format_date(dt, "MMMM", locale="id_ID")
    return f"https://www.bi.go.id/en/statistik/ekonomi-keuangan/sulni/Documents/SULNI-{month_name}-{dt.year}.pdf"


# 16. Indonesian External Debt
def id_debt():
    # SULNI reports are published with a lag, so the current month's PDF
    # often doesn't exist yet - fall back to the previous month if so.
    label = "TOTAL (142)"
    candidates = [datetime.today(), datetime.today().replace(day=1) - timedelta(days=1)]
    for dt in candidates:
        url = _sulni_url_for(dt)
        try:
            full_text = fetch_bi_img(url)
            debt = _extract_last_number(full_text, label)
            if debt is not None:
                return _fmt(debt, prefix="$", suffix=" million")
        except Exception:
            continue
    return "N/A"


# 17. BI Rate
def bi_rate():
    try:
        resp = bi_response(BIRATE_URL)
        soup = BeautifulSoup(resp.text, "html.parser")
        table_tag = soup.find("table")
        if table_tag is None:
            return "N/A"

        records = []
        for tr in table_tag.find_all("tr"):
            cells = tr.find_all(["th", "td"])
            if len(cells) < 3:
                continue
            no = cells[0].get_text(strip=True)
            tanggal = cells[1].get_text(strip=True)
            rate = cells[2].get_text(strip=True)
            if not no.isdigit():
                continue
            records.append({"Tanggal": tanggal, "BI_Rate": rate})

        if not records:
            return "N/A"

        df = pd.DataFrame(records)
        latest_rate = df.iloc[0]["BI_Rate"].replace('%', '').strip()
        return f"{float(latest_rate)}%"
    except Exception:
        return "N/A"


# 18. Trend: $ Exchange & IHSG (1-month trend)
def trend():
    try:
        currency_hist = yf.Ticker("USDIDR=X").history(start=start_date_str, end=end_date_str)
        if not currency_hist.empty:
            currency_hist = currency_hist.reset_index()
            currency_hist['Date'] = currency_hist['Date'].dt.strftime('%Y-%m-%d')
            currency_df = currency_hist[['Date', 'Close']].rename(columns={'Close': '$-Exchange'})
            currency_df['$-Exchange'] = currency_df['$-Exchange'].round(2)
        else:
            currency_df = pd.DataFrame(columns=['Date', '$-Exchange'])
    except Exception:
        currency_df = pd.DataFrame(columns=['Date', '$-Exchange'])

    try:
        ihsg_hist = yf.Ticker("^JKSE").history(start=start_date_str, end=end_date_str)
        if not ihsg_hist.empty:
            ihsg_hist = ihsg_hist.reset_index()
            ihsg_hist['Date'] = ihsg_hist['Date'].dt.strftime('%Y-%m-%d')
            ihsg_clean = ihsg_hist[['Date', 'Close']].rename(columns={'Close': 'IHSG'})
        else:
            ihsg_clean = pd.DataFrame(columns=['Date', 'IHSG'])
    except Exception:
        ihsg_clean = pd.DataFrame(columns=['Date', 'IHSG'])

    if currency_df.empty and ihsg_clean.empty:
        return pd.DataFrame(columns=['Date', '$-Exchange', 'IHSG'])

    master_dates = pd.date_range(start=one_month_ago, end=today)
    final_df = pd.DataFrame({'Date': master_dates.strftime('%Y-%m-%d')})
    final_df = pd.merge(final_df, currency_df, on='Date', how='left')
    final_df = pd.merge(final_df, ihsg_clean, on='Date', how='left')

    final_df['$-Exchange'] = final_df['$-Exchange'].ffill().bfill()
    final_df['IHSG'] = final_df['IHSG'].ffill().bfill().round(2)

    return final_df