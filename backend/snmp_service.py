import httpx
from bs4 import BeautifulSoup
import re

async def get_printer_data(ip):
    results = {
        "ip": ip,
        "status": "Offline",
        "serial": "N/A",
        "location": "N/A",
        "page_count": 0,
        "copied_count": 0,
        "printed_count": 0,
        "toner_percent": 0,
        "toner_install_date": "N/A"
    }

    async with httpx.AsyncClient(verify=False, timeout=8.0, follow_redirects=True) as client:
        # 1. Basic Info: Welcome Page
        try:
            welcome_url = f"http://{ip}/stat/welcome.php"
            resp = await client.get(welcome_url, timeout=4.0)
            if resp.status_code == 200:
                results["status"] = "Online"
                soup = BeautifulSoup(resp.text, 'html.parser')
                text = soup.get_text(separator=' | ')
                
                sn_m = re.search(r'(?:Serial Number|S/N|Serie)[:\s|]+([A-Z0-9]{6,})', text, re.I)
                if sn_m: results["serial"] = sn_m.group(1).strip()
                
                loc_m = re.search(r'(?:Location|Lugar|Ubicación)[:\s|]+([^|]+)', text, re.I)
                if loc_m: results["location"] = loc_m.group(1).strip()
        except:
            # Fallback to https just in case
            try:
                welcome_url = f"https://{ip}/stat/welcome.php"
                resp = await client.get(welcome_url, timeout=4.0)
                if resp.status_code == 200:
                    results["status"] = "Online"
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    text = soup.get_text(separator=' | ')
                    sn_m = re.search(r'(?:Serial Number|S/N|Serie)[:\s|]+([A-Z0-9]{6,})', text, re.I)
                    if sn_m: results["serial"] = sn_m.group(1).strip()
                    loc_m = re.search(r'(?:Location|Lugar|Ubicación)[:\s|]+([^|]+)', text, re.I)
                    if loc_m: results["location"] = loc_m.group(1).strip()
            except: pass

        # 2. Toner Installation Date
        try:
            cons_url = f"https://{ip}/stat/consumables_details.php"
            resp = await client.get(cons_url, timeout=4.0)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                text = soup.get_text(separator=' | ')
                # Buscamos 'Cartucho de tóner' seguido de la fecha
                date_match = re.search(r'(?:Cartucho de t[óo]ner|Toner Cartridge)[\s|]+([A-Za-z]{3}\s\d{1,2},\s\d{4}|[0-9]{1,4}[-/][0-9]{1,2}[-/][0-9]{1,4})', text, re.I)
                if date_match:
                    results["toner_install_date"] = date_match.group(1)
                else:
                    # Fallback general
                    fallback_date = re.search(r'(?:Fecha de instalaci[óo]n|Installation Date|Instalaci[óo]n)[:\s|]+([0-9]{1,4}[-/][0-9]{1,2}[-/][0-9]{1,4}|[A-Za-z]{3}\s\d{1,2},\s\d{4})', text, re.I)
                    if fallback_date:
                        results["toner_install_date"] = fallback_date.group(1)
        except: pass

        # 3. Toner Information (Percentage)
        try:
            cons_info_url = f"https://{ip}/stat/consumables.php"
            resp = await client.get(cons_info_url, timeout=4.0)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                text = soup.get_text(separator=' | ')
                tn_m = re.search(r'(?:Black|Negro|Toner).*?(\d{1,3})\s*%', text, re.I | re.S)
                if tn_m: 
                    results["toner_percent"] = int(tn_m.group(1))
                else:
                    tn_alt = re.search(r'(\d{1,3})\s*%', text)
                    if tn_alt:
                        results["toner_percent"] = int(tn_alt.group(1))
        except: pass

        # 4. Counters
        try:
            usage_url = f"https://{ip}/counters/usage.php"
            resp = await client.get(usage_url, timeout=4.0)
            print(resp.text)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                text = soup.get_text(separator=' | ')
                copied = re.search(r'(?:Hojas copiadas en negro|Black Copied Sheets)[\s|]+([\d,.]+)', text, re.I)
                if copied:
                    results["copied_count"] = int(copied.group(1).replace(',', '').replace('.', ''))
                else:
                    # Fallback just in case
                    copied_fallback = re.search(r'(?:Copiado|Copias|Copied)[:\s|]+([\d,.]+)', text, re.I)
                    if copied_fallback: results["copied_count"] = int(copied_fallback.group(1).replace(',', '').replace('.', ''))
                
                printed = re.search(r'(?:Hojas impresas en negro|Black Printed Sheets)[\s|]+([\d,.]+)', text, re.I)
                if printed:
                    results["printed_count"] = int(printed.group(1).replace(',', '').replace('.', ''))
                else:
                    printed_fallback = re.search(r'(?:Impreso|Impresiones|Printed)[:\s|]+([\d,.]+)', text, re.I)
                    if printed_fallback: results["printed_count"] = int(printed_fallback.group(1).replace(',', '').replace('.', ''))
                
                pc_m = re.search(r'(?:Total Impressions|Total|Contador)[:\s|]+([\d,.]+)', text, re.I)
                if pc_m: 
                    results["page_count"] = int(pc_m.group(1).replace(',', '').replace('.', ''))
        except: pass

    if results["page_count"] == 0:
        results["page_count"] = results["copied_count"] + results["printed_count"]

    return results
