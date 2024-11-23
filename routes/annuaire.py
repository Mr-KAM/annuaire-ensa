from app import app

@app.route('/annuaire')
def annuaire():
    return render_template('ui/annuaire.html')