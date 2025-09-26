from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")  # save HTML as templates/index.html

@app.route("/simulate")
def simulate():
    oil_change = int(request.args.get("oil_change", 0))
    
    # Simple mock formula (can replace with AI/RAG pipeline)
    new_value = 100 + (oil_change * -0.8)  # e.g., portfolio drops 0.8% for every +1% oil
    return jsonify({"new_value": new_value})

if __name__ == "__main__":
    app.run(debug=True)
