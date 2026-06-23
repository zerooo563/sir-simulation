import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# إعدادات الصفحة
st.set_page_config(page_title="SIR Model Simulation", page_icon="🌊", layout="wide")

st.title("🌊 SIR Model Epidemic Simulation (RK4 Method)")
st.markdown("### المحاكاة الرقمية لانتشار الأوبئة باستخدام طريقة رونج-كوتا من الرتبة الرابعة")
st.write("تم تطوير هذا النموذج لمحاكاة حركة انتشار المرض بين الأفراد بدقة رياضية عالية.")

# القائمة الجانبية للمدخلات
st.sidebar.header("⚙️ معطيات النموذج والمحاكاة")

# حجم العينة الافتراضي 40 ليطابق الدراسة
N = st.sidebar.number_input("إجمالي عدد السكان (N)", min_value=10, max_value=100000, value=40)
I0 = st.sidebar.number_input("عدد المصابين الأولائي (I0)", min_value=1, max_value=N, value=1)
R0_init = st.sidebar.number_input("عدد المتعافين الأولي (R0)", min_value=0, max_value=N, value=0)
S0 = N - I0 - R0_init

st.sidebar.markdown("---")
beta = st.sidebar.slider("معدل انتقال العدوى (β)", 0.0, 2.0, 0.4, step=0.01)
gamma = st.sidebar.slider("معدل الشفاء (γ)", 0.0, 1.0, 0.1, step=0.01)
days = st.sidebar.slider("فترة المحاكاة بالكامل (الأيام)", 10, 200, 100)

# حساب عدد التكاثر الأساسي R0 الرياضي
r_zero = beta / gamma if gamma > 0 else 0
st.sidebar.metric(label="عدد التكاثر الأساسي (R₀)", value=f"{r_zero:.2f}")

# خوارزمية الحل العددي Runge-Kutta 4th Order (RK4)
def rk4_sir(S0, I0, R0, beta, gamma, N, days, dt=0.1):
    steps = int(days / dt)
    t = np.linspace(0, days, steps + 1)
    
    S = np.zeros(steps + 1)
    I = np.zeros(steps + 1)
    R = np.zeros(steps + 1)
    
    S[0], I[0], R[0] = S0, I0, R0
    
    for k in range(steps):
        # معادلات التفاضل لنموذج SIR
        def f_S(s, i): return - (beta * s * i) / N
        def f_I(s, i): return ((beta * s * i) / N) - (gamma * i)
        def f_R(i): return gamma * i
        
        # حساب معاملات K1
        k1_S = f_S(S[k], I[k])
        k1_I = f_I(S[k], I[k])
        k1_R = f_R(I[k])
        
        # حساب معاملات K2
        k2_S = f_S(S[k] + 0.5 * dt * k1_S, I[k] + 0.5 * dt * k1_I)
        k2_I = f_I(S[k] + 0.5 * dt * k1_S, I[k] + 0.5 * dt * k1_I)
        k2_R = f_R(I[k] + 0.5 * dt * k1_I)
        
        # حساب معاملات K3
        k3_S = f_S(S[k] + 0.5 * dt * k2_S, I[k] + 0.5 * dt * k2_I)
        k3_I = f_I(S[k] + 0.5 * dt * k2_S, I[k] + 0.5 * dt * k2_I)
        k3_R = f_R(I[k] + 0.5 * dt * k2_I)
        
        # حساب معاملات K4
        k4_S = f_S(S[k] + dt * k3_S, I[k] + dt * k3_I)
        k4_I = f_I(S[k] + dt * k3_S, I[k] + dt * k3_I)
        k4_R = f_R(I[k] + dt * k3_I)
        
        # تحديث القيم للخطوة القادمة بوزن نسبي متزن
        S[k+1] = S[k] + (dt / 6.0) * (k1_S + 2*k2_S + 2*k3_S + k4_S)
        I[k+1] = I[k] + (dt / 6.0) * (k1_I + 2*k2_I + 2*k3_I + k4_I)
        R[k+1] = N - S[k+1] - I[k+1] # للحفاظ على ثبات حجم المجتمع بدقة قانون الانحفاظ
        
    return t, S, I, R

# تشغيل المحاكاة
t, S, I, R = rk4_sir(S0, I0, R0_init, beta, gamma, N, days)

# إنشاء الرسم البياني التفاعلي بـ Plotly لمظهر فخم ومتناسق مع الوضع المظلم
fig = go.Figure()
fig.add_trace(go.Scatter(x=t, y=S, name='المعرضون للإصابة (Susceptible)', line=dict(color='#3b82f6', width=3)))
fig.add_trace(go.Scatter(x=t, y=I, name='المصابون (Infected)', line=dict(color='#ef4444', width=3)))
fig.add_trace(go.Scatter(x=t, y=R, name='المتعافون (Recovered)', line=dict(color='#10b981', width=3)))

fig.update_layout(
    title="منحنيات تطور الحالة الوبائية عبر الزمن",
    xaxis_title="الأيام",
    yaxis_title="عدد الأفراد",
    template="plotly_dark",
    background_color="rgba(0,0,0,0)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

# عرض الرسم البياني وجدول البيانات
col1, col2 = st.columns([3, 1])

with col1:
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 📊 ملخص البيانات")
    max_infected = int(np.max(I))
    peak_day = t[np.argmax(I)]
    st.metric("أعلى ذروة للمصابين", f"{max_infected} فرد")
    st.metric("يوم الوصول للذروة", f"اليوم {peak_day:.1f}")

    # عرض جدول سريع للنتائج
    df_data = pd.DataFrame({'اليوم': t[::10], 'المعرضين': S[::10], 'المصابين': I[::10], 'المتعافين': R[::10]})
    st.dataframe(df_data.round(1), hide_index=True)