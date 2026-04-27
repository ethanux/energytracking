from flask import Flask, render_template, request, redirect, session
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)
app.secret_key = "secret123"


users = {}


def process_data():
    df = pd.read_csv("apple_data.csv")

    
    df.dropna(inplace=True)

   
    totals = df.groupby("Product")[["kWh", "CO2"]].sum()

    
    os.makedirs("static/graphs", exist_ok=True)

    
    for product in df["Product"].unique():
        product_data = df[df["Product"] == product]
        plt.figure()
        plt.plot(product_data["Year"], product_data["kWh"])
        plt.title(f"{product} Electricity Usage Over Time")
        plt.xlabel("Year")
        plt.ylabel("kWh")
        plt.savefig(f"static/graphs/{product}_trend.png")
        plt.close()

   
    plt.figure()
    plt.scatter(df["kWh"], df["CO2"])
    plt.xlabel("kWh")
    plt.ylabel("CO2")
    plt.title("kWh vs CO2 Relationship")
    plt.savefig("static/graphs/kwh_vs_co2.png")
    plt.close()

    return totals


totals = process_data()


@app.route("/")
def home():
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users[username] = password
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username] == password:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid login"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    graphs = os.listdir("static/graphs")

    return render_template("dashboard.html", graphs=graphs, totals=totals.to_dict())

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
