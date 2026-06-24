import xml.etree.ElementTree as ET
import csv, re, html, urllib.request
from datetime import datetime

XML_URL          = "https://www.msy.be/klr/pricelist/products.xml"
OUTPUT           = "zentrada_feed.csv"
MARKETPLACE      = "fr"
CURRENCY         = "EUR"
PIECES_PER_PACK  = 1
MIN_QTY          = 1
PRODUCER_NAME    = "MSY Invest"
PRODUCER_ADDRESS = "Belgium"
PRODUCT_EMAIL    = "info@msy.be"
AVAILABLE_LANGS  = "FR, NL, DE, EN"

COLUMNS = [
  "Attributionplacedemarche","Referencearticle","code_barre_ean","ean_ve",
  "Titreannonce","Descriptionarticle","Descriptiondetailleearticle","MotclefMarque",
  "Photo","Photo2","Photo3","Photo4","Photo5","Photo6","Photo7","Photo8","Photo9","Photo10",
  "Monnaie","TVAenpourcent",
  "Nombre_de_piece_par_unite_demballage","Quantite_minimale_en_unite_demballage",
  "Prixnet_par_piece","rabais_promotion",
  "Volumedegressif1","Prixdegressif1","Volumedegressif2","Prixdegressif2",
  "Volumedegressif3","Prixdegressif3",
  "Quantite_disponible_en_unite_demballage","Recommandation_de_prix",
  "Boutique_Identificateurproduit1","Boutique_Identificateurproduit2",
  "Boutique_Identificateurproduit3","Echeance_le","Poids",
  "collection","statistical_number","country_of_origin","dangerous_goods",
  "energyEfficiency","energyEffImage",
  "weightNetPcP","weightGrossPcP","volumeGrossPcP",
  "lengthPU","widthPU","heightPU","lengthPc","widthPc","heightPc",
  "puPallet","puLayerPallet","hazardCode","hazardName","flashPoint",
  "electroClassification","isBatterieIncluded","isLithium",
  "VocPerc","isFood","color","material","charge","mhd",
  "GPSRIsRequired","certificate_CE","certificate_additional",
  "availableLanguages","producerName","producerAddress","productManagerEMail",
  "operatingInstructions","instructionsDocument1","instructionsDocument2","instructionsDocument3",
  "warningNote","warningNote1","warningNote2","warningNote3",
]

def clean(text):
    if not text: return ""
    text = re.sub(r'&lt;[^&]*&gt;', ' ', text)
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'[\r\n\t]+', ' ', text)
    return re.sub(r'\s{2,}', ' ', text).strip()

def trunc(text, n):
    if len(text) <= n: return text
    return text[:n-1].rsplit(' ',1)[0]

def f(n):
    try: return float(n)
    except: return None

def map_item(item):
    g = lambda t: (item.findtext(t) or "").strip()
    desc = trunc(clean(g("description")), 1000)
    price = f(g("price")); prec = f(g("price_recommended"))
    vol = f(g("volume")); stock = int(f(g("stock")) or 0)
    w = g("weight")
    photos = [g(f"photo_{n}") for n in range(1,6)]
    row = {c:"" for c in COLUMNS}
    row.update({
      "Attributionplacedemarche": MARKETPLACE,
      "Referencearticle": g("article_num"),
      "code_barre_ean": g("ean"),
      "Titreannonce": g("name")[:50],
      "Descriptionarticle": desc,
      "Descriptiondetailleearticle": desc,
      "MotclefMarque": g("brand")[:40],
      "Photo": photos[0],"Photo2": photos[1],"Photo3": photos[2],
      "Photo4": photos[3],"Photo5": photos[4],
      "Monnaie": CURRENCY,
      "TVAenpourcent": g("vat_rate"),
      "Nombre_de_piece_par_unite_demballage": PIECES_PER_PACK,
      "Quantite_minimale_en_unite_demballage": MIN_QTY,
      "Prixnet_par_piece": f"{price:.2f}" if price else "",
      "Quantite_disponible_en_unite_demballage": stock,
      "Recommandation_de_prix": f"{prec:.2f}" if prec else "",
      "Boutique_Identificateurproduit1": g("cat"),
      "Boutique_Identificateurproduit2": g("scat"),
      "Poids": w,"weightNetPcP": w,"weightGrossPcP": w,
      "volumeGrossPcP": f"{vol*1000:.3f}" if vol else "",
      "lengthPU": g("length"),"widthPU": g("width"),"heightPU": g("height"),
      "lengthPc": g("length"),"widthPc": g("width"),"heightPc": g("height"),
      "statistical_number": g("hs_code"),
      "country_of_origin": g("country_of_origin"),
      "dangerous_goods": "0","isFood": "0","GPSRIsRequired": "1",
      "availableLanguages": AVAILABLE_LANGS,
      "producerName": PRODUCER_NAME,
      "producerAddress": PRODUCER_ADDRESS,
      "productManagerEMail": PRODUCT_EMAIL,
    })
    return row

print(f"Fetching {XML_URL}...")
req = urllib.request.Request(XML_URL, headers={"User-Agent":"MSY-Zentrada/1.0"})
with urllib.request.urlopen(req, timeout=60) as r:
    root = ET.fromstring(r.read())

items = list(root)
print(f"Products: {len(items)}")
rows = [map_item(i) for i in items]

with open(OUTPUT, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=COLUMNS, delimiter=";", quoting=csv.QUOTE_ALL)
    w.writeheader()
    w.writerows(rows)

print(f"Done — {len(rows)} rows written to {OUTPUT}")
