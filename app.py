from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Données d'exemple pour l'autocomplétion
suggestions = ["Apple", "Banana", "Orange", "Grape", "Pineapple"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('query', '').lower()
    results = [item for item in suggestions if query in item.lower()]
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
