import re
import base64
import os
import json

html_file = "index.html"
output_dir = "slike"

os.makedirs(output_dir, exist_ok=True)

with open(html_file, "r", encoding="utf-8") as f:
    html = f.read()

# Izvuci popis biljaka iz JS arraya da znamo nazive
products_match = re.search(r'const products\s*=\s*(\[.*?\]);', html, re.DOTALL)
if not products_match:
    # Fallback: ukloni base64 pa traži
    html_temp = re.sub(r'"img":"data:image/[^;]+;base64,[A-Za-z0-9+/=]+"', '"img":"REMOVED"', html)
    products_match = re.search(r'const products\s*=\s*(\[.*?\]);', html_temp, re.DOTALL)

# Napravi mapu: redni_broj -> naziv datoteke
# Čitamo proizvode bez img polja
html_temp = re.sub(r'"img":"data:image/[^;]+;base64,[A-Za-z0-9+/=]+"', '"img":"REMOVED"', html)
products_match2 = re.search(r'const products\s*=\s*(\[.*?\]);', html_temp, re.DOTALL)

products = []
if products_match2:
    try:
        products = json.loads(products_match2.group(1).replace('"img":"REMOVED"', '"img":""'))
    except:
        pass

def make_filename(idx, product):
    """Napravi ime datoteke od šifre i naziva"""
    sifra = product.get("id", f"biljka-{idx}").replace(" ", "-")
    naziv = product.get("name", f"biljka-{idx}").lower()
    naziv = re.sub(r'[^a-z0-9]', '-', naziv)
    naziv = re.sub(r'-+', '-', naziv).strip('-')
    return f"{sifra}-{naziv}.jpg"

# Pronađi sve base64 JPEG slike i zamijeni ih
counter = 0
img_map = {}  # redni_broj -> filename

def replace_base64(match):
    global counter
    mime = match.group(1)  # jpeg ili png itd.
    b64_data = match.group(2)
    
    # Određi ekstenziju
    ext = "jpg" if "jpeg" in mime else mime.split("/")[-1]
    
    # Dohvati naziv iz popisa biljaka
    if counter < len(products):
        product = products[counter]
        sifra = product.get("id", f"biljka-{counter+1}").replace(" ", "-")
        naziv = product.get("name", f"biljka-{counter+1}").lower()
        naziv = re.sub(r'[^a-z0-9]', '-', naziv)
        naziv = re.sub(r'-+', '-', naziv).strip('-')
        filename = f"{sifra}-{naziv}.{ext}"
    else:
        filename = f"slika-{counter+1:02d}.{ext}"
    
    filepath = os.path.join(output_dir, filename)
    
    # Spremi sliku
    try:
        img_data = base64.b64decode(b64_data)
        with open(filepath, "wb") as img_file:
            img_file.write(img_data)
        print(f"✓ Spremljeno: {filepath} ({len(img_data)//1024} KB)")
    except Exception as e:
        print(f"✗ Greška za sliku {counter+1}: {e}")
    
    counter += 1
    return f'slike/{filename}'

# Zamijeni sve base64 slike (i JPEG i SVG i ostalo)
pattern = r'data:image/([^;]+);base64,([A-Za-z0-9+/=]+)'
new_html = re.sub(pattern, replace_base64, html)

# Spremi novi HTML
output_html = "index_novi.html"
with open(output_html, "w", encoding="utf-8") as f:
    f.write(new_html)

print(f"\n✅ Gotovo!")
print(f"   - {counter} slika izvučeno u mapu '{output_dir}/'")
print(f"   - Novi HTML spremljen kao '{output_html}'")
print(f"\nSljedeći koraci:")
print(f"   1. Provjeri mapu 'slike/' — tamo su sve slike")
print(f"   2. Uploadaj mapu 'slike/' na GitHub repozitorij")
print(f"   3. Zamijeni index.html s index_novi.html")
print(f"   4. Veličina novog HTML-a trebala bi biti < 50 KB umjesto 15 MB")
