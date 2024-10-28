import streamlit as st
import pandas as pd

# Carregar o dataset
df_validated = pd.read_csv('dataset_enhanced_analysis.csv')

# Converter 'entry_month' para datetime se necessário
df_validated['entry_month'] = pd.to_datetime(df_validated['entry_month'], errors='coerce')

# Sidebar com filtros condicionados e ordenados
st.sidebar.title("Filters")

# Filtro de país, ordenado
country_options = sorted(df_validated['country'].unique())
country_filter = st.sidebar.multiselect("Country", options=country_options)

# Aplicar filtro de país ao dataset
filtered_df = df_validated[df_validated['country'].isin(country_filter)] if country_filter else df_validated

# Filtro de Entry Month, ordenado e condicionado ao filtro anterior
entry_month_options = sorted(filtered_df['entry_month'].dt.strftime('%Y-%m').unique())
entry_month_filter = st.sidebar.multiselect("Entry Month", options=entry_month_options)
filtered_df = filtered_df[filtered_df['entry_month'].dt.strftime('%Y-%m').isin(entry_month_filter)] if entry_month_filter else filtered_df

# Filtro de Permanency, ordenado e condicionado aos filtros anteriores
permanency_options = sorted(filtered_df['permanency'].unique())
permanency_filter = st.sidebar.multiselect("Permanency", options=permanency_options)
filtered_df = filtered_df[filtered_df['permanency'].isin(permanency_filter)] if permanency_filter else filtered_df

# Filtro de Specialization Type, ordenado e condicionado aos filtros anteriores
specialization_type_options = sorted(filtered_df['specialization_type'].unique())
specialization_type_filter = st.sidebar.multiselect("Specialization Type", options=specialization_type_options)
filtered_df = filtered_df[filtered_df['specialization_type'].isin(specialization_type_filter)] if specialization_type_filter else filtered_df

# Filtro de Specialization, ordenado e condicionado aos filtros anteriores
specialization_options = sorted(filtered_df['specialization'].unique())
specialization_filter = st.sidebar.multiselect("Specialization", options=specialization_options)
filtered_df = filtered_df[filtered_df['specialization'].isin(specialization_filter)] if specialization_filter else filtered_df

# Filtro de Pricing, ordenado e condicionado aos filtros anteriores
pricing_options = sorted(filtered_df['pricing'].unique())
pricing_filter = st.sidebar.multiselect("Pricing", options=pricing_options)
filtered_df = filtered_df[filtered_df['pricing'].isin(pricing_filter)] if pricing_filter else filtered_df

# Filtro de Churning, com opções de "All", "Yes", "No" e condicionado aos filtros anteriores
churning_options = ["All", "Yes", "No"]
churning_filter = st.sidebar.selectbox("Will End Up Churning", options=churning_options)
if churning_filter != 'All':
    filtered_df = filtered_df[filtered_df['will_end_up_churning'] == (churning_filter == 'Yes')]

# Seletor de métrica amigável para o usuário
st.title("Patient Appointments Analysis by Entry Month and Contract Month")
st.write("This table shows the average values for the selected metric per month since the contract start, based on the entry cohort (Entry Month).")

# Mapear nomes amigáveis para métricas
metric_map = {
    'total_appointments': 'Total Appointments',
    'patient_appointments': 'Patient Appointments',
    'doctor_appointments': 'Doctor Appointments',
    'doctor_appointments_ratio': 'Doctor Appointments Ratio',
    'patient_appointments_ratio': 'Patient Appointments Ratio'
}

# Inverter o mapeamento para usar no código
metric_reverse_map = {v: k for k, v in metric_map.items()}

# Seletor de métrica com nomes amigáveis
selected_metric_name = st.selectbox("Select your metric", options=list(metric_map.values()))
selected_metric = metric_reverse_map[selected_metric_name]

# Filtrar apenas os primeiros 12 meses de contrato para cada safra
filtered_df = filtered_df[filtered_df['contract_month_order_from_sale'] <= 12]

# Criar a tabela dinâmica para a métrica selecionada
pivot_table = filtered_df.pivot_table(
    index='entry_month',
    columns='contract_month_order_from_sale',
    values=selected_metric,
    aggfunc='mean'
).fillna(0)

# Renomear as colunas para "Month +0", "Month +1", etc., corrigindo o deslocamento
pivot_table.columns = [f"Month +{int(col - 1)}" for col in pivot_table.columns]
pivot_table.index = pivot_table.index.to_series().dt.strftime('%Y-%m')
pivot_table.index.name = 'Entry Month'

# Aplicar gradiente de cor (heatmap) na tabela e formatar com uma casa decimal
styled_pivot_table = pivot_table.style.background_gradient(cmap="YlGnBu", axis=0).format("{:.1f}")

# Exibir a tabela e o heatmap no Streamlit
st.dataframe(styled_pivot_table)
