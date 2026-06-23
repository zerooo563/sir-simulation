from flask import Flask, request, jsonify, render_template
import numpy as np
from scipy.integrate import odeint
import json

app = Flask(__name__)

def sir_model(y, t, N, beta, gamma):
    S, I, R = y
    S = max(0.0, S)
    I = max(0.0, I)
    R = max(0.0, R)
    dSdt = -beta * S * I / N
    dIdt = (beta * S * I / N) - gamma * I
    dRdt = gamma * I
    return dSdt, dIdt, dRdt

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/simulate", methods=["POST"])
def simulate():
    data = request.get_json()
    N = int(data["N"])
    days = int(data["days"])
    beta = float(data["beta"])
    gamma = float(data["gamma"])
    I0 = int(data["I0"])

    R0_init = 0
    S0 = N - I0 - R0_init

    t = np.linspace(0, days, days * 10)
    y0 = S0, I0, R0_init
    ret = odeint(sir_model, y0, t, args=(N, beta, gamma))
    S, I, R = ret.T

    R_naught = beta / gamma if gamma > 0 else 0
    status = "epidemic" if R_naught > 1 else "decline"

    return jsonify({
        "t": t.tolist(),
        "S": S.tolist(),
        "I": I.tolist(),
        "R": R.tolist(),
        "initialSum": int(round((S + I + R)[0])),
        "finalSum": int(round((S + I + R)[-1])),
        "S0": int(S0),
        "I0": int(I0),
        "R0": int(R0_init),
        "minS": round(float(S.min()), 2),
        "minI": round(float(I.min()), 2),
        "minR": round(float(R.min()), 2),
        "R_naught": round(R_naught, 2),
        "status": status,
        "N": N
    })

if __name__ == "__main__":
    app.run(debug=True)
