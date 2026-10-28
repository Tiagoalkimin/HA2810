"""Tela de apresentação. Os cálculos ficam em core/demo.py."""
import streamlit as st
from core.demo import QuickDemo
from core.energy import cost_projection


def br(value, digits=1):
    return f"{value:,.{digits}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def render_demo():
    st.markdown('''<style>
    .block-container {max-width:1180px;padding-top:1.25rem;padding-bottom:1rem;}
    [data-testid="stVerticalBlock"] {gap:.65rem;}
    .el-tag {color:#58dec1;letter-spacing:.14em;font-size:.75rem;font-weight:700;}
    .el-title {font-size:2.7rem;font-weight:750;line-height:1.15;margin:.4rem 0;}
    .el-sub {color:#adb8c8;margin-bottom:1.2rem;}
    .el-steps {display:flex;gap:10px;margin:1rem 0;}
    .el-step {flex:1;border:1px solid #344157;border-radius:10px;padding:10px 14px;color:#acb8cb;}
    .el-step.active {background:#173c36;border-color:#58dec1;color:#a6f3de;}
    .el-step small {display:block;font-size:.73rem;margin-top:3px;}
    .el-bars {border:1px solid #344157;border-radius:12px;padding:14px 18px;margin:8px 0;}
    .el-row {display:flex;justify-content:space-between;margin:5px 0;font-size:.9rem;}
    .el-bar {height:12px;border-radius:6px;margin:8px 0 12px;}
    .el-result {border:1px solid #58dec1;background:#14332d;border-radius:12px;padding:14px 18px;}
    .el-result strong {font-size:2.2rem;color:#90efd3;display:block;line-height:1.25;}
    [data-testid="stMetricValue"] {font-size:2rem;}
    [data-testid="stMetric"] {background:#172236;border:1px solid #344157;border-radius:12px;padding:14px;}
    div.stButton > button {min-height:46px;}
    @media(max-width:640px) {.el-title{font-size:2rem}.el-step{padding:8px;font-size:.8rem}.el-steps{gap:5px}}
    </style>''', unsafe_allow_html=True)
    if "quick_demo" not in st.session_state:
        st.session_state.quick_demo = QuickDemo()
    demo = st.session_state.quick_demo
    snap = demo.snapshot()
    power = snap["power"]["total_w"]
    month = cost_projection(power, demo.tariff)["30d"]
    stage = demo.stage
    index = {"normal": 0, "waste": 1, "optimized": 2}[stage]

    st.markdown('<div class="el-tag">ENERGYLENS · DEMONSTRAÇÃO CONTROLADA</div>', unsafe_allow_html=True)
    st.markdown('<div class="el-title">Mesma tarefa. Menos energia.</div>', unsafe_allow_html=True)
    st.markdown('<div class="el-sub">O consumo extra pode passar despercebido. O custo, não.</div>', unsafe_allow_html=True)
    steps = [("01 · Observar", "Uso comum do computador"),
             ("02 · Detectar", "Consumo fora do esperado"),
             ("03 · Otimizar", "Comparar o resultado")]
    html = '<div class="el-steps">'
    for i, (title, sub) in enumerate(steps):
        html += f'<div class="el-step {"active" if i == index else ""}">{title}<small>{sub}</small></div>'
    st.markdown(html + '</div>', unsafe_allow_html=True)
    st.caption("🖥️ PC intermediário · Navegador + documentos · Valores simulados, sem leitura ou alteração do hardware.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Potência elétrica", f"{br(power)} W")
    c2.metric("Temperatura estimada", f"{br(snap['temp'])} °C")
    c3.metric("Utilização CPU / GPU", f"{br(snap['cpu_util'], 0)} / {br(snap['gpu_util'], 0)} %")
    c4.metric("Custo mensal estimado", f"R$ {br(month['custo'], 2)}")

    if stage == "waste":
        st.error("Consumo acima do esperado. Verifique os processos em segundo plano.")
    elif stage == "optimized":
        st.success("Otimização simulada aplicada. Consumo extra removido; mesma carga útil de CPU e GPU.")
    else:
        st.info("Consumo dentro do esperado. Simule um processo desnecessário para revelar o desperdício.")

    # Os callbacks executam antes da renderização: os indicadores já chegam atualizados.
    a, b, c = st.columns([2, 2, 1])
    a.button("Simular desperdício", type="primary" if stage == "normal" else "secondary",
             disabled=stage != "normal", on_click=demo.inject_waste, use_container_width=True)
    b.button("Aplicar otimização", type="primary" if stage == "waste" else "secondary",
             disabled=stage != "waste", on_click=demo.optimize, use_container_width=True)
    def reset():
        st.session_state.quick_demo = QuickDemo(demo.tariff)
    c.button("Reiniciar", on_click=reset, use_container_width=True)

    result = demo.comparison()
    if result:
        left, right = st.columns([3, 2])
        with left:
            before_w, after_w = result["before_w"], result["after_w"]
            ratio = after_w / before_w * 100
            st.markdown(f'''<div class="el-bars">
            <div class="el-row"><b>Antes · com desperdício</b><b>{br(before_w)} W</b></div>
            <div class="el-bar" style="width:100%;background:#ff8c75"></div>
            <div class="el-row"><b>Depois · otimizado</b><b>{br(after_w)} W</b></div>
            <div class="el-bar" style="width:{ratio:.2f}%;background:#58dec1"></div>
            <div class="el-row"><span>Temperatura estimada</span><b>{br(result['before_temp'])} °C → {br(result['after_temp'])} °C</b></div>
            <div class="el-row"><span>Custo mensal</span><b>R$ {br(result['before_month']['custo'], 2)} → R$ {br(result['after_month']['custo'], 2)}</b></div>
            </div>''', unsafe_allow_html=True)
        with right:
            st.markdown(f'''<div class="el-result">Redução de consumo<strong>{br(result['reduction_pct'])}%</strong>
            Economia mensal estimada<strong>R$ {br(result['saved_brl'], 2)}</strong>
            {br(result['saved_kwh'], 2)} kWh a menos por mês</div>''', unsafe_allow_html=True)
    else:
        limit = snap["anomaly"]["esperado_max"] * 1.15
        st.caption(f"Referência da tarefa: {br(snap['anomaly']['esperado_min'])} a {br(snap['anomaly']['esperado_max'])} W. Alerta acima de {br(limit)} W.")

    st.caption(f"Projeção: 8 h/dia × 30 dias · Tarifa ilustrativa: R$ {br(demo.tariff, 2)}/kWh · Potência mantida durante o uso.")
    st.caption("Tempo térmico acelerado: cada cenário representa 3 minutos simulados, calculados sem espera. A temperatura não cai instantaneamente em um computador real.")
    with st.expander("Premissas e recursos completos"):
        st.write("O modelo adiciona 90 W de consumo extra sem alterar a carga útil. A otimização remove essa parcela usando a decisão de verificar processos já existente. Não encerra processos reais. A detecção usa o limite da tarefa com margem de 15%. A economia compara os mesmos 240 h de uso mensal, antes e depois, e não o tempo gasto na apresentação.")
        tariff = st.number_input("Tarifa ilustrativa (R$/kWh)", min_value=0.10, max_value=3.0,
                                 value=demo.tariff, step=0.05, key="demo_tariff")
        if tariff != demo.tariff:
            demo.tariff = tariff
            demo.sim.tarifa_kwh = tariff
            st.rerun()
        st.write("As telas educativas, seleção de computadores e tarefas, relatórios, teste de estresse e os oito experimentos continuam disponíveis no modo completo.")
        if st.button("Abrir modo completo"):
            st.session_state.screen = "intro_problema"
            st.rerun()
