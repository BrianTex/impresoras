import re

text = '\n | Hojas a dos caras copiadas en blanco y negro | 26 | \n | Hojas a dos caras impresas en blanco y negro | 184 | \n'

two_sided_copied = re.search(r'(?:Hojas a dos caras copiadas|2-Sided.*Copied)[^|]*[\s|]+([\d,.]+)', text, re.I)
if two_sided_copied:
    print("Copied:", two_sided_copied.group(1))
else:
    print("Copied fallback")
    ts_copied_fallback = re.search(r'(?:Copiadas a dos caras|Copias a dos caras|Copied 2-Sided)[^|]*[\s|]+([\d,.]+)', text, re.I)
    if ts_copied_fallback:
        print("Copied FB:", ts_copied_fallback.group(1))

two_sided_printed = re.search(r'(?:Hojas a dos caras impresas|2-Sided.*Printed)[^|]*[\s|]+([\d,.]+)', text, re.I)
if two_sided_printed:
    print("Printed:", two_sided_printed.group(1))
else:
    print("Printed fallback")
    ts_printed_fallback = re.search(r'(?:Impresas a dos caras|Impresiones a dos caras|Printed 2-Sided)[^|]*[\s|]+([\d,.]+)', text, re.I)
    if ts_printed_fallback:
        print("Printed FB:", ts_printed_fallback.group(1))
