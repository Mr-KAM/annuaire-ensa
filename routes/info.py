from flask import Blueprint, render_template

info_bp = Blueprint('info', __name__)

@info_bp.route('/info')
def info():
    """Render the info page"""
    return render_template('info/info.html')
