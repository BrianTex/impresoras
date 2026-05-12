from bs4 import BeautifulSoup
import re

html_snippet = """
<tr class="odd"><td width="50%">Hojas a dos caras copiadas en blanco y negro</td><td style="text-align: center;">26</td></tr>
<tr class="even"><td width="50%">Hojas a dos caras impresas en blanco y negro</td><td style="text-align: center;">184</td></tr>
"""

soup = BeautifulSoup(html_snippet, 'html.parser')
text = soup.get_text(separator=' | ')
print("Extracted Text:", repr(text))

two_sided_copied = re.search(r'(?:Hojas a dos caras copiadas en blanco y negro)[\s|]+([\d,.]+)', text, re.I)
if two_sided_copied:
    print("Copied:", two_sided_copied.group(1))
else:
    print("Copied not found!")

two_sided_printed = re.search(r'(?:Hojas a dos caras impresas en blanco y negro)[\s|]+([\d,.]+)', text, re.I)
if two_sided_printed:
    print("Printed:", two_sided_printed.group(1))
else:
    print("Printed not found!")
