import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="DEMONSTRAÇÃO - CONTROLE FINANCEIRO",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILIZAÇÃO CSS EXECUTIVA ---
st.markdown("""
<style>
    .block-container { padding-top: 1.2rem !important; padding-bottom: 3rem !important; max-width: 95% !important; }
    .stApp { background-color: #EAEFF5 !important; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important; border-radius: 12px !important; border: 1px solid #CBD5E1 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important; padding: 0px !important; overflow: hidden !important; margin-bottom: 35px !important; 
    }
    [data-testid="stVerticalBlockBorderWrapper"] > div { padding: 24px 28px !important; }
    .card-header-navy { background: linear-gradient(90deg, #0F172A 0%, #1E293B 100%); color: #FFFFFF; padding: 14px 24px; font-weight: 700; font-size: 1rem; text-transform: uppercase; margin: -24px -28px 24px -28px; }
    .card-header-orange { background: linear-gradient(90deg, #FF5722 0%, #E64A19 100%); color: #FFFFFF; padding: 14px 24px; font-weight: 700; font-size: 1rem; text-transform: uppercase; margin: -24px -28px 24px -28px; }
    .kpi-card-box { background: #F8FAFC; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border: 1px solid #E2E8F0; border-left: 6px solid #0F172A; }
    .kpi-card-orange { border-left-color: #FF5722; }
    .kpi-card-green { border-left-color: #10B981; }
    .kpi-card-blue { border-left-color: #0284C7; }
    .kpi-title { font-size: 0.85rem; font-weight: 700; color: #64748B; text-transform: uppercase; margin-bottom: 6px; }
    .kpi-value-main { font-size: 1.8rem !important; font-weight: 800 !important; line-height: 1.2 !important; }
    .kpi-subtext { font-size: 0.85rem; font-weight: 600; color: #64748B; margin-top: 4px; }
    .avatar-frame { width: 140px; height: 140px; border-radius: 50%; object-fit: cover; box-shadow: 0 4px 14px rgba(0,0,0,0.12); display: block; margin: 0 auto; }
    .speech-bubble { position: relative; background: #FFFFFF; border-radius: 14px; padding: 12px 18px; border: 2px solid #CBD5E1; font-size: 0.92rem; color: #1E293B; box-shadow: 0 4px 12px rgba(0,0,0,0.04); margin-top: 6px; display: inline-block; width: 100%; }
    .speech-bubble::after { content: ''; position: absolute; left: -10px; top: 22px; width: 0; height: 0; border-top: 8px solid transparent; border-bottom: 8px solid transparent; border-right: 10px solid #FFFFFF; }
    .speech-bubble::before { content: ''; position: absolute; left: -13px; top: 21px; width: 0; height: 0; border-top: 9px solid transparent; border-bottom: 9px solid transparent; border-right: 11px solid #CBD5E1; }
    div[data-testid="stRadio"] > div { flex-direction: row !important; flex-wrap: nowrap !important; gap: 2px !important; justify-content: flex-start !important; align-items: center !important; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label { background-color: #F8FAFC !important; border: 1px solid #CBD5E1 !important; padding: 3px 5px !important; border-radius: 6px !important; cursor: pointer !important; font-weight: 700 !important; font-size: 0.75rem !important; color: #334155 !important; white-space: nowrap !important; text-align: center !important; min-width: auto !important; margin: 0px !important; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child { display: none !important; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #0F172A !important; border-color: #0F172A !important; color: #FFFFFF !important; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] * { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

def fmt_brl(valor):
    try: return f"R$ {float(valor):,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.')
    except: return "R$ 0,00"

# =========================================================
# DADOS FICTÍCIOS (PARA DEMONSTRAÇÃO DO CLIENTE)
# =========================================================
df_entradas = pd.DataFrame({
    'Data': ['04/09/2026', '15/09/2026', '10/09/2026'],
    'Descrição': ['Salário', 'Adiantamento', 'Benefício Flash'],
    'Tipo de Pagamento': ['PIX', 'PIX', 'VR'],
    'Valor_Clean': [3800.00, 1500.00, 750.00]
})

df_saidas = pd.DataFrame({
    'Data': ['01/09/2026', '04/09/2026', '05/09/2026', '16/09/2026', '08/09/2026'],
    'Tipo de Gasto': ['Essenciais', 'Parcelamento', 'Mercado', 'Lazer', 'Gasolina'],
    'Parcelamento': ['-', '3/12', '-', '-', '-'],
    'Tipo de Pagamento': ['PIX', 'PIX', 'VR', 'PIX', 'PIX'],
    'Descrição do Gasto': ['Conta de Luz', 'Smartphone Novo', 'Supermercado', 'Cinema', 'Posto Gasolina'],
    'Valor_Clean': [180.00, 250.00, 450.00, 120.00, 150.00],
    'Dia': [1, 4, 5, 16, 8]
})

df_dividas_atrasadas = pd.DataFrame({
    'nome da dívida': ['Cartão de Crédito Banco XYZ', 'Empréstimo Rápido'],
    'credor': ['Banco XYZ', 'Financeira ABC'],
    'valor': [1250.00, 4500.00],
    'entrou em acordo': ['Não', 'Sim'],
    'parcelamento feito': ['-', '24x'],
    'quantidade': ['-', '24']
})

df_dividas_fixas = pd.DataFrame({
    'nome': ['Aluguel', 'Smartphone Novo'],
    'valor': [1200.00, 250.00],
    'tem parcelamento?': ['Não', 'Sim'],
    'quantidade de parcelas': ['-', '12x'],
    'inicio do pagamento': ['-', 'julho/26'],
    'finaliza em': ['-', 'junho/27'],
    'janela': ['Janela Salário', 'Janela Salário']
})

# --- CÁLCULOS DO DEMO ---
total_entradas_pix = df_entradas[df_entradas['Tipo de Pagamento'] == 'PIX']['Valor_Clean'].sum()
total_entradas_vr = df_entradas[df_entradas['Tipo de Pagamento'] == 'VR']['Valor_Clean'].sum()
entradas_salario_pix = 3800.00
entradas_adiantamento_pix = 1500.00
total_receita_conta = entradas_salario_pix + entradas_adiantamento_pix

total_saidas_pix = df_saidas[df_saidas['Tipo de Pagamento'] == 'PIX']['Valor_Clean'].sum()
saidas_salario_pix = df_saidas[(df_saidas['Tipo de Pagamento'] == 'PIX') & (df_saidas['Dia'] < 15)]['Valor_Clean'].sum()
saidas_adiantamento_pix = df_saidas[(df_saidas['Tipo de Pagamento'] == 'PIX') & (df_saidas['Dia'] >= 15)]['Valor_Clean'].sum()

gasto_gasolina_pix = 150.00
gasto_gasolina_vr = 0.0
gasto_lucca_pix = 0.0
gasto_lucca_vr = 0.0

sobra_liquida = total_entradas_pix - total_saidas_pix
sobra_salario = entradas_salario_pix - saidas_salario_pix
sobra_adiantamento = entradas_adiantamento_pix - saidas_adiantamento_pix

# --- SEMÁFORO DA ASSISTENTE ---
pct_gasto_total = (total_saidas_pix / total_entradas_pix) * 100 if total_entradas_pix > 0 else 100
dia_atual = datetime.now().day

if pct_gasto_total <= 60 and dia_atual <= 15:
    cor_semaforo = "#10B981"
    status_texto = "🟢 Mês sob controle!"
    assistente_expressao = "Tudo dentro do planejado! 😊"
else:
    cor_semaforo = "#10B981" # Mantemos verde para o cliente ver como funciona bem
    status_texto = "🟢 Mês sob controle!"
    assistente_expressao = "Tudo dentro do planejado! 😊"

avatar_src = "https://cdn-icons-png.flaticon.com/512/4140/4140048.png" # Avatar genérico executivo para demonstração

# --- HEADER DEMO ---
with st.container(border=True):
    col_av, col_content = st.columns([1.3, 7.7])
    with col_av:
        st.markdown(f"""<div style="display: flex; justify-content: center; align-items: center; height: 100%; padding-top: 5px;">
            <img src="{avatar_src}" class="avatar-frame" style="border: 5px solid {cor_semaforo};" alt="Avatar">
        </div>""", unsafe_allow_html=True)
    with col_content:
        st.markdown(f"""
        <h2 style='margin:0; padding-top:0px; font-size:1.65rem; font-weight:800; color:#0F172A;'>PAINEL DEMONSTRATIVO <span style='color:#FF5722;'>FINANCEIRO</span></h2>
        <div class="speech-bubble">
            <b style="color:{cor_semaforo}; font-size:1.0rem;">{status_texto}</b> <span style="font-size:0.85rem; color:#64748B;">{assistente_expressao}</span><br>
            <span style="font-size:0.85rem; color:#334155; display:inline-block; margin-top:2px;">Este é um modelo de vendas com dados 100% fictícios. Adquira sua versão personalizada!</span>
        </div>
        <div style='margin-top: 8px;'></div>
        """, unsafe_allow_html=True)
        c_ano, c_mes = st.columns([0.95, 8.05])
        with c_ano: st.selectbox("Ano", [2026], index=0, label_visibility="collapsed")
        with c_mes: st.radio("Mês", ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"], index=8, horizontal=True, label_visibility="collapsed")

# --- 1. RESUMO EXECUTIVO ---
with st.container(border=True):
    st.markdown('<div class="card-header-navy">📊 RESUMO EXECUTIVO GERAL</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="kpi-card-box kpi-card-blue"><div class="kpi-title">Total Entradas PIX</div><div class="kpi-value-main" style="color:#0284C7;">{fmt_brl(total_entradas_pix)}</div><div class="kpi-subtext">Salário + Adiantamento</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi-card-box kpi-card-blue"><div class="kpi-title">Total Entradas VR</div><div class="kpi-value-main" style="color:#0369A1;">{fmt_brl(total_entradas_vr)}</div><div class="kpi-subtext">Benefícios</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi-card-box kpi-card-orange"><div class="kpi-title">Total Saídas PIX</div><div class="kpi-value-main" style="color:#FF5722;">{fmt_brl(total_saidas_pix)}</div><div class="kpi-subtext">Todos os gastos</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="kpi-card-box kpi-card-green"><div class="kpi-title">Sobra do Mês</div><div class="kpi-value-main" style="color:#10B981;">{fmt_brl(sobra_liquida)}</div><div class="kpi-subtext">Saldo Real</div></div>', unsafe_allow_html=True)

# --- 2. DETALHAMENTO ---
with st.container(border=True):
    st.markdown('<div class="card-header-navy">📅 DETALHAMENTO POR JANELA DE PAGAMENTO</div>', unsafe_allow_html=True)
    cj1, cj2 = st.columns(2)
    with cj1:
        st.markdown(f"""<div style="background:#F8FAFC; padding:20px; border-radius:8px; border:1px solid #CBD5E1;">
            <div style="font-size:1.15rem; font-weight:800; color:#0F172A; margin-bottom:12px; border-bottom:1px solid #CBD5E1; padding-bottom:6px;">💳 Janela 1 (Dia 05)</div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#334155; font-weight:600;">Entrada (PIX):</span><span style="color:#0284C7; font-weight:800;">{fmt_brl(entradas_salario_pix)}</span></div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#334155; font-weight:600;">Gasto (PIX):</span><span style="color:#FF5722; font-weight:800;">- {fmt_brl(saidas_salario_pix)}</span></div>
            <div style="background-color:#CBD5E1; height:1px; width:100%; margin:12px 0;"></div>
            <div style="display:flex; justify-content:space-between; align-items:center;"><span style="color:#0F172A; font-weight:800; font-size:1.2rem;">💰 Sobra:</span><span style="color:#10B981; font-weight:800; font-size:1.5rem;">{fmt_brl(sobra_salario)}</span></div>
        </div>""", unsafe_allow_html=True)
    with cj2:
        st.markdown(f"""<div style="background:#F8FAFC; padding:20px; border-radius:8px; border:1px solid #CBD5E1;">
            <div style="font-size:1.15rem; font-weight:800; color:#0F172A; margin-bottom:12px; border-bottom:1px solid #CBD5E1; padding-bottom:6px;">💳 Janela 2 (Dia 15)</div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#334155; font-weight:600;">Entrada (PIX):</span><span style="color:#0284C7; font-weight:800;">{fmt_brl(entradas_adiantamento_pix)}</span></div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="color:#334155; font-weight:600;">Gasto (PIX):</span><span style="color:#FF5722; font-weight:800;">- {fmt_brl(saidas_adiantamento_pix)}</span></div>
            <div style="background-color:#CBD5E1; height:1px; width:100%; margin:12px 0;"></div>
            <div style="display:flex; justify-content:space-between; align-items:center;"><span style="color:#0F172A; font-weight:800; font-size:1.2rem;">💰 Sobra:</span><span style="color:#10B981; font-weight:800; font-size:1.5rem;">{fmt_brl(sobra_adiantamento)}</span></div>
        </div>""", unsafe_allow_html=True)

# --- 5. MAPEAMENTO DE DÍVIDAS: DEMO ---
with st.container(border=True):
    st.markdown('<div class="card-header-orange">⚠️ MAPEAMENTO DE DÍVIDAS: ATRASADAS</div>', unsafe_allow_html=True)
    
    html_card1 = f"""<div style="background:#F8FAFC; padding:18px; border-radius:8px; border:1px solid #CBD5E1; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
    <div style="flex: 1.2; min-width: 250px;"><span style="font-weight:800; font-size:1.1rem; color:#0F172A;">Cartão de Crédito Banco XYZ</span><br><span style="font-size:0.85rem; color:#64748B;">Credor: <b>Banco XYZ</b></span><br><span style="background:#FEE2E2; color:#FF5722; border:1px solid #FF5722; padding:2px 8px; border-radius:12px; font-weight:700; font-size:0.75rem;">Pendente</span></div>
    <div style="flex: 1; min-width: 150px; font-size:0.95rem; color:#334155;"><b>Valor Total:</b> <span style="color:#0F172A; font-weight:700;">R$ 1.250,00</span><br><span style="font-size:0.85rem; color:#64748B;">Acordo: -</span></div>
    <div style="flex: 2; min-width: 300px; font-size:0.95rem; color:#FF5722; font-weight:600;">Aguardando acordo / negociação para este credor.</div></div>"""
    
    html_card2 = f"""<div style="background:#F8FAFC; padding:18px; border-radius:8px; border:1px solid #CBD5E1; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
    <div style="flex: 1.2; min-width: 250px;"><span style="font-weight:800; font-size:1.1rem; color:#0F172A;">Empréstimo Rápido</span><br><span style="font-size:0.85rem; color:#64748B;">Credor: <b>Financeira ABC</b></span><br><span style="background:#E0F2FE; color:#0284C7; border:1px solid #0284C7; padding:2px 8px; border-radius:12px; font-weight:700; font-size:0.75rem;">Acordado / Parcelado</span></div>
    <div style="flex: 1; min-width: 150px; font-size:0.95rem; color:#334155;"><b>Valor Total:</b> <span style="color:#0F172A; font-weight:700;">R$ 4.500,00</span><br><span style="font-size:0.85rem; color:#64748B;">Acordo: 24x</span></div>
    <div style="flex: 1; min-width: 150px; font-size:0.95rem; color:#334155;"><b>Já pago:</b> 5 parcela(s)<br><span style="color:#10B981; font-weight:700;">R$ 937,50</span></div>
    <div style="flex: 1; min-width: 150px; font-size:0.95rem; color:#334155;"><b>Falta pagar:</b> 19 parcela(s)<br><span style="color:#FF5722; font-weight:700;">R$ 3.562,50</span></div></div>"""
    
    st.markdown(html_card1, unsafe_allow_html=True)
    st.markdown(html_card2, unsafe_allow_html=True)

# --- 6. CUSTOS ATIVOS DEMO ---
with st.container(border=True):
    st.markdown('<div class="card-header-navy">✅ CUSTOS / PARCELAMENTOS ATIVOS (POR JANELA)</div>', unsafe_allow_html=True)
    c_fix1, c_fix2 = st.columns(2)
    with c_fix1:
        st.markdown("<div style='font-size:1.1rem; font-weight:800; color:#0F172A; margin-bottom:12px; border-bottom:2px solid #10B981; padding-bottom:6px;'>💳 Pagamentos Janela 1</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.95rem; font-weight:700; color:#0F172A; background:#E2E8F0; padding:6px 10px; border-radius:6px; margin-bottom:10px;'>🔄 Custos Fixos Contínuos</div>", unsafe_allow_html=True)
        st.markdown("""<div style="background:#F8FAFC; padding:14px; border-radius:8px; border:1px solid #CBD5E1; margin-bottom:10px;">
        <div style="font-weight:800; font-size:1.05rem; color:#0F172A; margin-bottom:4px;">Aluguel</div>
        <div style="font-size:0.9rem; color:#334155; line-height:1.5;">• <b>Valor (R$):</b> <span style="color:#0F172A; font-weight:700;">R$ 1.200,00</span><br>• <b>Custo Fixo Contínuo</b> (Sem data final)</div></div>""", unsafe_allow_html=True)
        
        st.markdown("<div style='font-size:0.95rem; font-weight:700; color:#0F172A; background:#E2E8F0; padding:6px 10px; border-radius:6px; margin-bottom:10px; margin-top:15px;'>🔢 Parcelamentos Ativos</div>", unsafe_allow_html=True)
        st.markdown("""<div style="background:#F8FAFC; padding:14px; border-radius:8px; border:1px solid #CBD5E1; margin-bottom:10px;">
        <div style="font-weight:800; font-size:1.05rem; color:#0F172A; margin-bottom:4px;">Smartphone Novo</div>
        <div style="font-size:0.9rem; color:#334155; line-height:1.5;">• <b>Valor (R$):</b> <span style="color:#0F172A; font-weight:700;">R$ 250,00</span><br>• <b>Quantidade de Parcelas:</b> 12x<br>• <b>Início do Pagamento:</b> julho/26<br>• <b>Finaliza em:</b> junho/27<br>• <b>Status no Mês:</b> <span style='color:#10B981; font-weight:700;'>3 de 12 pagas (3/12)</span></div></div>""", unsafe_allow_html=True)

    with c_fix2:
        st.markdown("<div style='font-size:1.1rem; font-weight:800; color:#0F172A; margin-bottom:12px; border-bottom:2px solid #0284C7; padding-bottom:6px;'>💳 Pagamentos Janela 2</div>", unsafe_allow_html=True)
        st.write("Sem registros para esta janela neste exemplo.")

# --- 7. INSIGHTS DEMO ---
st.markdown('<div id="insights"></div>', unsafe_allow_html=True)
with st.container(border=True):
    st.markdown('<div class="card-header-navy">💡 INSIGHTS DA SUA ASSISTENTE PESSOAL</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#F8FAFC; padding:22px; border-radius:10px; border:1px solid #CBD5E1; border-left:6px solid #0F172A;">
        <div style="font-size:1.15rem; font-weight:800; color:#0F172A; margin-bottom:10px;">Aqui está sua análise financeira detalhada 🙋‍♀️</div>
        <div style="font-size:0.95rem; color:#334155; line-height:1.7;">
            Analisando suas movimentações até hoje, identifiquei que o seu maior volume de despesas está concentrado na categoria <b>Mercado</b>.<br><br>
            <b>Diagnóstico do Período:</b> 🟢 <b style='color:#10B981;'>Mês sob controle!</b> Estamos no início do mês e os gastos estão bem moderados. Excelente ritmo de economia!<br><br>
            <i style="color:#64748B; font-size:0.85rem;">Obs: Este é um modelo de vendas. Na versão final, esta análise se atualiza automaticamente lendo a sua planilha do Google Sheets.</i>
        </div>
    </div>
    """, unsafe_allow_html=True)
