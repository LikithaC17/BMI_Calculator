from flask import Flask, render_template, request, session

app = Flask(__name__)
app.secret_key = "bmi_secret_key"

@app.route("/", methods=["GET", "POST"])
def bmi():
    if request.method == "POST":
        weight = float(request.form["weight"])
        height_cm = float(request.form["height"])
        height_m = height_cm / 100

        bmi_value = round(weight / (height_m ** 2), 2)

        if bmi_value < 18.5:
            category = "Underweight"
        elif bmi_value < 24.9:
            category = "Normal weight"
        elif bmi_value < 29.9:
            category = "Overweight"
        else:
            category = "Obese"

        # Save values in session
        session["weight"] = weight
        session["height"] = height_cm
        session["bmi"] = bmi_value
        session["category"] = category

    return render_template(
        "index.html",
        weight=session.get("weight"),
        height=session.get("height"),
        bmi=session.get("bmi"),
        category=session.get("category")
    )

if __name__ == "__main__":
    app.run(debug=True)


