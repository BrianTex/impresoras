import re

texts = [
    '\n | Hojas a dos caras copiadas en blanco y negro | 26 | \n',
    '2-Sided Black Copied Sheets | : | 1,024',
    'Hojas a dos caras impresas en blanco y negro | 184 |',
    'Copias a dos caras | 55',
]

for t in texts:
    c = re.search(r'(?:Hojas a dos caras copiadas|2-Sided.*?Copied|Copias a dos caras|Copiadas a dos caras)[^\d]+([\d,.]+)', t, re.I)
    if c:
        print("Copied:", c.group(1))
        
    p = re.search(r'(?:Hojas a dos caras impresas|2-Sided.*?Printed|Impresas a dos caras|Impresiones a dos caras)[^\d]+([\d,.]+)', t, re.I)
    if p:
        print("Printed:", p.group(1))

