# scripts/generate_data.py
import pandas as pd
import random
from datetime import datetime, timedelta
import os

# --- Produits de parapharmacie avec prix en dinars tunisiens (TND) ---
produits = [
    ("Crème hydratante NUXE", "Soin du visage", 80.000),
    ("Shampoing sec Klorane", "Cheveux", 45.500),
    ("Sérum anti-âge La Roche-Posay", "Soin du visage", 130.000),
    ("Gel douche doux Uriage", "Hygiène", 32.000),
    ("Patchs yeux Bio", "Soin du visage", 60.000),
    ("Brumisateur d'eau thermale", "Soin du visage", 48.000),
    ("Crème mains nourrissante", "Soin corps", 28.500),
    ("Déodorant sans alcool", "Hygiène", 35.000),
    ("Complément alimentaire sommeil", "Bien-être", 75.000),
    ("Masque capillaire nourrissant", "Cheveux", 52.000),
    ("Dentifrice Sensigel", "Hygiène", 22.000),
    ("Huile d'argan marocaine", "Cheveux", 95.000),
    ("Lotion nettoyante Bioderma", "Soin du visage", 78.000),
    ("Savon d'Alep bio", "Hygiène", 18.000),
    ("Gel anti-douleur musculaire", "Santé", 40.000),
    ("croquette ships chat","croquette",6.000), 
    ("croquette chien","croquette",6.000),
    ("litiere chat cats ways","litiere",12.000),
    ("litiere naturel","litiere",10.000),
    


]

# --- Génération des données ---
data = []
start = datetime(2024, 1, 1)
end = datetime(2025, 3, 31)
current = start

while current <= end:
    nb_ventes = random.randint(15, 50)  # Volume adapté
    for _ in range(nb_ventes):
        prod, cat, prix = random.choice(produits)
        quantite = random.choice([1, 1, 1, 2])  # majorité 1, quelques 2
        data.append({
            "date": current.strftime("%Y-%m-%d"),
            "produit": prod,
            "categorie": cat,
            "prix_unitaire": round(prix, 3),  # Précision en TND (millimes)
            "quantite": quantite,
            "ca": round(prix * quantite, 3)  # Chiffre d'affaires en TND
        })
    current += timedelta(days=1)

# --- Sauvegarde dans data/ventes.csv ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
data_dir = os.path.join(project_root, "data")
data_file = os.path.join(data_dir, "ventes.csv")

os.makedirs(data_dir, exist_ok=True)

df = pd.DataFrame(data)
df.to_csv(data_file, index=False)

print(f"✅ Données générées avec succès : {data_file}")
print(f"📊 {len(df):,} ventes générées entre 2024-01-01 et 2025-03-31")
print(f"💵 Chiffre d'affaires total simulé : {df['ca'].sum():,.3f} TND")