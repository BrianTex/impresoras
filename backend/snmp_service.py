import httpx
from bs4 import BeautifulSoup
import re

def _parse_rows(html: str):
    """Convierte cualquier tabla <tr><td>label</td>...<td>value</td></tr> en pares (label, value)."""
    soup = BeautifulSoup(html, 'html.parser')
    rows = []
    for tr in soup.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) >= 2:
            label = tds[0].get_text(strip=True)
            value = tds[-1].get_text(strip=True)
            if label:
                rows.append((label.lower(), value))
    return rows

def _find(rows, include, exclude=None):
    """Primer valor cuya etiqueta contiene TODAS las palabras de include y NINGUNA de exclude."""
    exclude = exclude or []
    for label, value in rows:
        if all(k in label for k in include) and not any(k in label for k in exclude):
            return value
    return None

def _to_int(value):
    if not value:
        return None
    cleaned = re.sub(r'[^\d]', '', value)
    return int(cleaned) if cleaned else None

async def _get(client, url, timeout=4.0):
    try:
        resp = await client.get(url, timeout=timeout)
        if resp.status_code == 200:
            return resp
    except Exception:
        pass
    return None

async def get_printer_data(ip):
    results = {
        "ip": ip, "status": "Offline", "serial": "N/A", "location": "N/A",
        "page_count": 0, "copied_count": 0, "printed_count": 0,
        "two_sided_copied_count": 0, "two_sided_printed_count": 0,
        "toner_percent": 0, "toner_install_date": "N/A"
    }

    async with httpx.AsyncClient(verify=False, timeout=8.0, follow_redirects=True) as client:
        # 1. Info básica (probamos http, si falla https)
        resp = await _get(client, f"http://{ip}/stat/welcome.php")
        if not resp:
            resp = await _get(client, f"https://{ip}/stat/welcome.php")
        if resp:
            results["status"] = "Online"
            text = BeautifulSoup(resp.text, 'html.parser').get_text(separator=' | ')
            sn_m = re.search(r'(?:Serial Number|S/N|Serie)[:\s|]+([A-Z0-9]{6,})', text, re.I)
            if sn_m: results["serial"] = sn_m.group(1).strip()
            loc_m = re.search(r'(?:Location|Lugar|Ubicaci[oó]n)[:\s|]+([^|]+)', text, re.I)
            if loc_m: results["location"] = loc_m.group(1).strip()

        if results["status"] != "Online":
            return results  # sin conexión, no seguimos intentando

        # 2. Fecha de instalación de tóner
        resp = await _get(client, f"https://{ip}/stat/consumables_details.php")
        if resp:
            text = BeautifulSoup(resp.text, 'html.parser').get_text(separator=' | ')
            date_m = (re.search(r'(?:Cartucho de t[óo]ner|Toner Cartridge)[\s|]+([A-Za-z]{3}\s\d{1,2},\s\d{4}|[0-9]{1,4}[-/][0-9]{1,2}[-/][0-9]{1,4})', text, re.I)
                      or re.search(r'(?:Fecha de instalaci[óo]n|Installation Date)[:\s|]+([0-9]{1,4}[-/][0-9]{1,2}[-/][0-9]{1,4}|[A-Za-z]{3}\s\d{1,2},\s\d{4})', text, re.I))
            if date_m:
                results["toner_install_date"] = date_m.group(1)

        # 3. Nivel de tóner
        resp = await _get(client, f"https://{ip}/stat/consumables.php")
        if resp:
            text = BeautifulSoup(resp.text, 'html.parser').get_text(separator=' | ')
            tn_m = re.search(r'(?:Black|Negro|Toner).*?(\d{1,3})\s*%', text, re.I | re.S) or re.search(r'(\d{1,3})\s*%', text)
            if tn_m:
                results["toner_percent"] = int(tn_m.group(1))

        # 4. Contadores (aquí está el fix real, vía parseo de tabla)
        resp = await _get(client, f"https://{ip}/counters/usage.php")
        if resp:
            rows = _parse_rows(resp.text)

            copied = _find(rows, ['hojas', 'copiadas'], exclude=['dos caras']) \
                or _find(rows, ['black', 'copied', 'sheets'])
            printed = _find(rows, ['hojas', 'impresas'], exclude=['dos caras']) \
                or _find(rows, ['black', 'printed', 'sheets'])
            ts_copied = _find(rows, ['dos caras', 'copiadas']) \
                or _find(rows, ['2', 'sided', 'copied'])
            ts_printed = _find(rows, ['dos caras', 'impresas']) \
                or _find(rows, ['2', 'sided', 'printed'])
            total = _find(rows, ['total', 'impresiones']) \
                or _find(rows, ['total', 'impressions'])

            if copied is not None: results["copied_count"] = _to_int(copied) or 0
            if printed is not None: results["printed_count"] = _to_int(printed) or 0
            if ts_copied is not None: results["two_sided_copied_count"] = _to_int(ts_copied) or 0
            if ts_printed is not None: results["two_sided_printed_count"] = _to_int(ts_printed) or 0
            if total is not None: results["page_count"] = _to_int(total) or 0

    if results["page_count"] == 0:
        results["page_count"] = results["copied_count"] + results["printed_count"]

    return results
