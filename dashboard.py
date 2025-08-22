# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration
st.set_page_config(page_title="💊 Pharmavie - Dashboard", layout="wide")
st.title("📊 Tableau de bord - Parapharmacie Pharmavie (Tunisie)")

# Chargement des données
@st.cache_data
def load_data():
    df = pd.read_csv("data/ventes.csv")
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# Filtres
st.sidebar.header("🔍 Filtres")
min_date = df['date'].min().date()
max_date = df['date'].max().date()
start_date = st.sidebar.date_input("Date de début", min_date)
end_date = st.sidebar.date_input("Date de fin", max_date)

categories = ["Toutes"] + sorted(df['categorie'].unique().tolist())
selected_cat = st.sidebar.selectbox("Catégorie", categories)

# Filtrer
mask = (df['date'] >= pd.Timestamp(start_date)) & (df['date'] <= pd.Timestamp(end_date))
if selected_cat != "Toutes":
    mask &= (df['categorie'] == selected_cat)
filtered = df[mask]

# KPI (en TND)
st.header("📈 Indicateurs clés")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Chiffre d'affaires", f"{filtered['ca'].sum():,.3f} TND")
col2.metric("Nombre de ventes", len(filtered))
col3.metric("Quantité vendue", int(filtered['quantite'].sum()))
col4.metric("Panier moyen", f"{filtered['ca'].mean():,.3f} TND")

# Graphiques
st.subheader("Évolution du chiffre d'affaires")
daily = filtered.groupby('date')['ca'].sum().reset_index()
fig1 = px.line(daily, x='date', y='ca', title="Chiffre d'affaires par jour (TND)")
fig1.update_layout(yaxis_title="CA (TND)")
st.plotly_chart(fig1, use_container_width=True)

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

# Données brutes
if st.checkbox("Afficher les données brutes"):
    st.write(filtered)