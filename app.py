import streamlit as st
import numpy as np
import json
import os

# 1. إعدادات الشاشة الكاملة وإخفاء هوامش Streamlit لتظهر واجهتك المخصصة فقط
st.set_page_config(page_title="SIR Model Simulation & Portfolio", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    body {margin: 0; padding: 0; background-color: #000000;}
    .stApp {background-color: #000000;}
    </style>
""", unsafe_allow_html=True)

# 2. المحرك الرياضي (RK4) لحساب انتشار الوباء لنموذج SIR (أساس مشروع تخرجك)
def rk4_sir(S0, I0, R0, beta, gamma, N, days, dt=0.1):
    steps = int(days / dt)
    t = np.linspace(0, days, steps + 1)
    
    S = np.zeros(steps + 1)
    I = np.zeros(steps + 1)
    R = np.zeros(steps + 1)
    
    S[0], I[0], R[0] = S0, I0, R0
    
    for k in range(steps):
        # المعادلات التفاضلية للنموذج
        def f_S(s, i): return - (beta * s * i) / N
        def f_I(s, i): return ((beta * s * i) / N) - (gamma * i)
        
        # حساب معاملات K1 لـ S و I
        k1_S = f_S(S[k], I[k])
        k1_I = f_I(S[k], I[k])
        
        # حساب معاملات K2
        k2_S = f_S(S[k] + 0.5 * dt * k1_S, I[k] + 0.5 * dt * k1_I)
        k2_I = f_I(S[k] + 0.5 * dt * k1_S, I[k] + 0.5 * dt * k1_I)
        
        # حساب معاملات K3
        k3_S = f_S(S[k] + 0.5 * dt * k2_S, I[k] + 0.5 * dt * k2_I)
        k3_I = f_I(S[k] + 0.5 * dt * k2_S, I[k] + 0.5 * dt * k2_I)
        
        # حساب معاملات K4
        k4_S = f_S(S[k] + dt * k3_S, I[k] + dt * k3_I)
        k4_I = f_I(S[k] + dt * k3_S, I[k] + dt * k3_I)
        
        # تحديث القيم للخطوة التالية
        S[k+1] = S[k] + (dt / 6.0) * (k1_S + 2*k2_S + 2*k3_S + k4_S)
        I[k+1] = I[k] + (dt / 6.0) * (k1_I + 2*k2_I + 2*k3_I + k4_I)
        R[k+1] = N - S[k+1] - I[k+1] # الحفاظ على ثبات حجم المجتمع (N=40)
        
    return t.tolist(), S.tolist(), I.tolist(), R.tolist()

# تشغيل الحسابات الرياضية وتثبيت حجم العينة على 40 فرد ليطابق دراستك العلمية
t_res, S_res, I_res, R_res = rk4_sir(S0=39, I0=1, R0=0, beta=0.4, gamma=0.1, N=40, days=100)

# تحويل مصفوفات الحل العددي إلى صيغة JSON لكي يقرأها ملف الجافا سكريبت المخصص لديك
simulation_json = json.dumps({
    "time": t_res,
    "susceptible": S_res,
    "infected": I_res,
    "recovered": R_res
})

# 3. قراءة كافة الملفات الجمالية وحقن البيانات الرياضية داخلها
def render_full_app(data_to_inject):
    html_file = "templates/index.html"
    css_file = "static/style.css"
    js_file = "static/script.js"
    
    # التأكد من أن جميع الملفات متواجدة في مساراتها الصحيحة كما في صور الـ Explorer
    if os.path.exists(html_file) and os.path.exists(css_file) and os.path.exists(js_file):
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()
        with open(css_file, "r", encoding="utf-8") as f:
            css_content = f.read()
        with open(js_file, "r", encoding="utf-8") as f:
            js_content = f.read()
            
        # إنشاء متغير جافا سكريبت عالمي (Global Variable) يحمل نتائج حسابات الـ SIR الرياضية
        javascript_data_bridge = f"<script>window.sirSimulationData = {data_to_inject};</script>"
        
        # دمج الستاين والبيانات الرياضية داخل الـ Head
        full_html = html_content.replace(
            "</head>", f"<style>{css_content}</style>{javascript_data_bridge}</head>"
        ).replace(
            "</body>", f"<script>{js_content}</script></body>"
        )
        
        # تشغيل التطبيق بالكامل بكافة مؤثراته البصرية (الروبوت والتموجات) وحجم شاشة كامل 100%
        st.components.v1.html(full_html, height=1000, scrolling=True)
    else:
        st.error("يوجد نقص في ملفات المشروع! تأكد من وجود مجلد templates ومجلد static بجانب ملف app.py مباشرة.")

# استدعاء وبناء التطبيق المتكامل أونلاين
render_full_app(simulation_json)