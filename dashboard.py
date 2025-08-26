# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np  # ← Ajouté pour les prévisions

# Configuration
st.set_page_config(page_title="💊 Pharmavie - Dashboard", layout="wide")
st.title("📊 Tableau de bord - Parapharmacie Pharmavie (Tunisie)")

# --- Chargement des données ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/ventes.csv")
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# --- Filtres dans la barre latérale ---
st.sidebar.header("🔍 Filtres")
min_date = df['date'].min().date()
max_date = df['date'].max().date()
start_date = st.sidebar.date_input("Date de début", min_date)
end_date = st.sidebar.date_input("Date de fin", max_date)

categories = ["Toutes"] + sorted(df['categorie'].unique().tolist())
selected_cat = st.sidebar.selectbox("Catégorie", categories)

# --- Appliquer les filtres → Créer 'filtered' ---
mask = (df['date'] >= pd.Timestamp(start_date)) & (df['date'] <= pd.Timestamp(end_date))
if selected_cat != "Toutes":
    mask &= (df['categorie'] == selected_cat)
filtered = df[mask]

# --- KPI (Indicateurs clés) ---
st.header("📈 Indicateurs clés")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Chiffre d'affaires", f"{filtered['ca'].sum():,.3f} TND")
col2.metric("Nombre de ventes", len(filtered))
col3.metric("Quantité vendue", int(filtered['quantite'].sum()))
col4.metric("Panier moyen", f"{filtered['ca'].mean():,.3f} TND")

# --- Graphique : Évolution du chiffre d'affaires ---
st.subheader("Évolution du chiffre d'affaires")
daily = filtered.groupby('date')['ca'].sum().reset_index()
fig1 = px.line(daily, x='date', y='ca', title="Chiffre d'affaires par jour (TND)")
fig1.update_layout(yaxis_title="CA (TND)")
st.plotly_chart(fig1, use_container_width=True)

# --- Top 10 produits et Répartition par catégorie ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("Top 10 des produits")
    top_prod = filtered.groupby('produit')['ca'].sum().nlargest(10)
    fig2 = px.bar(top_prod, x=top_prod.values, y=top_prod.index, orientation='h',
                  labels={'x': 'CA (TND)', 'y': 'Produit'},
                  title="Top 10 par chiffre d'affaires")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("Répartition par catégorie")
    cat_data = filtered.groupby('categorie')['ca'].sum()
    fig3 = px.pie(cat_data, values='ca', names=cat_data.index,
                  title="Part de marché par catégorie",
                  labels={'ca': 'CA (TND)'})
    st.plotly_chart(fig3, use_container_width=True)

# --- 🔮 PRÉVISION DES VENTES (IA légère) ---
st.subheader("📈 Prévision des ventes sur 7 prochains jours")

# Agréger les ventes par jour (sur les données filtrées)
daily_ca = filtered.groupby('date')['ca'].sum().reset_index()
daily_ca = daily_ca.sort_values('date')

# Remplir les trous de dates (si certains jours n'ont pas de vente)
date_range = pd.date_range(start=daily_ca['date'].min(), end=daily_ca['date'].max(), freq='D')
daily_ca = daily_ca.set_index('date').reindex(date_range).fillna(0).rename_axis('date').reset_index()

# Prendre les 30 derniers jours
last_30_days = daily_ca['ca'].tail(30).values

# Si moins de 30 jours, prendre ce qu'on a
if len(last_30_days) == 0:
    st.warning("Pas assez de données pour la prévision.")
else:
    # Prédiction : moyenne mobile pondérée (poids croissants vers le présent)
    weights = np.arange(1, len(last_30_days) + 1)  # Poids 1, 2, ..., 30
    predicted_ca = np.sum(weights * last_30_days) / np.sum(weights)

    # Créer les dates futures
    future_dates = pd.date_range(start=daily_ca['date'].max() + pd.Timedelta(days=1), periods=7)

    # Créer le DataFrame de prévision
    forecast = pd.DataFrame({
        'date': future_dates,
        'ca': [predicted_ca] * 7
    })

    # Fusionner historique et prévision
    historical = daily_ca[['date', 'ca']].copy()
    historical['type'] = 'Historique'
    forecast['type'] = 'Prévision'

    combined = pd.concat([historical, forecast], ignore_index=True)

    # Graphique
    fig_forecast = px.line(
        combined,
        x='date',
        y='ca',
        color='type',
        title="Évolution du CA : Historique et Prévision (7 jours)",
        labels={'ca': 'Chiffre d\'affaires (TND)', 'date': 'Date'},
        color_discrete_map={'Historique': 'blue', 'Prévision': 'orange'}
    )
    fig_forecast.update_traces(line=dict(dash="dot"), selector=dict(name="Prévision"))
    st.plotly_chart(fig_forecast, use_container_width=True)

    # Afficher la valeur prévue
    st.info(f"💰 Prévision moyenne : **{predicted_ca:,.3f} TND/jour** sur les 7 prochains jours")

# --- Données brutes ---
if st.checkbox("Afficher les données brutes"):
    st.write(filtered)






# --- 💡 RECOMMANDATION DE PRODUITS (IA légère) ---
st.subheader("💡 Recommandation de produits")

# Créer des "paniers" : regrouper les achats par date et produit
# On suppose qu'un client achète plusieurs produits le même jour = même panier
baskets = filtered.groupby(['date', 'produit']).agg({'quantite': 'sum'}).reset_index()

# Pivoter pour avoir des paniers (chaque ligne = un jour, colonnes = produits)
basket_table = baskets.pivot_table(index='date', columns='produit', values='quantite', fill_value=0)

# Binariser : 1 si acheté, 0 sinon
basket_table = basket_table.applymap(lambda x: 1 if x > 0 else 0)

# Liste des produits populaires
popular_products = filtered['produit'].value_counts().head(10).index.tolist()

# Sélectionner un produit pour recommander
selected_product = st.selectbox("Choisissez un produit pour voir les recommandations :", popular_products)

# Trouver les produits souvent achetés ensemble
product_data = basket_table[basket_table[selected_product] > 0]  # Lignes où le produit est acheté
support = product_data.sum() / len(product_data)  # Fréquence d'achat des autres produits

# Trier et prendre les 3 produits les plus fréquents (exclure le produit lui-même)
recommendations = support.drop(selected_product).sort_values(ascending=False).head(3)

# Afficher les recommandations
st.write(f"👉 Les clients qui ont acheté **{selected_product}** ont aussi souvent acheté :")
for i, (prod, score) in enumerate(recommendations.items(), 1):
    st.write(f"{i}. **{prod}** (taux d'association : {score:.1%})")
