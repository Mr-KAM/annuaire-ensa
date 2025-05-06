from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from markupsafe import Markup
from flask_login import login_required, current_user
from models import Discussion, Message, Like, User
from __init__ import db
import re

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

# Add nl2br filter for message content
@chat_bp.app_template_filter('nl2br')
def nl2br(value):
    if value:
        value = str(value)
        return Markup(value.replace('\n', '<br>'))
    return value

@chat_bp.route('/')
@login_required
def list_discussions():
    try:
        discussions = Discussion.query.order_by(Discussion.date_creation.desc()).all()
    except:
        discussions = []
    return render_template('chat/list.html', discussions=discussions)

@chat_bp.route('/<int:discussion_id>')
@login_required
def show_discussion(discussion_id):
    discussion = Discussion.query.get_or_404(discussion_id)
    messages = Message.query.filter_by(id_discussion=discussion_id).order_by(Message.date_ecriture).all()
    return render_template('chat/discussion.html', discussion=discussion, messages=messages)

@chat_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_discussion():
    if request.method == 'POST':
        subject = request.form.get('subject')
        if not subject:
            flash('Subject is required', 'error')
            return redirect(url_for('chat.new_discussion'))

        # Create a new discussion with only the fields that exist in the database
        discussion = Discussion(
            sujet=subject
        )
        # We'll set the user relationship directly instead of using auteur_id
        discussion.user = current_user
        db.session.add(discussion)
        db.session.commit()
        return redirect(url_for('chat.show_discussion', discussion_id=discussion.id_discussion))
    return render_template('chat/new.html')

@chat_bp.route('/<int:discussion_id>/message', methods=['POST'])
@login_required
def send_message(discussion_id):
    content = request.form.get('content')
    if not content:
        flash('Message content is required', 'error')
        return redirect(url_for('chat.show_discussion', discussion_id=discussion_id))

    message = Message(
        user_id=current_user.id,
        id_discussion=discussion_id,
        contenu=content
    )
    db.session.add(message)
    db.session.commit()
    return redirect(url_for('chat.show_discussion', discussion_id=discussion_id))

@chat_bp.route('/message/<int:message_id>/like', methods=['POST'])
@login_required
def like_message(message_id):
    message = Message.query.get_or_404(message_id)
    like = Like.query.filter_by(user_id=current_user.id, id_message=message_id).first()

    if like:
        db.session.delete(like)
        message.likes -= 1
    else:
        like = Like(user_id=current_user.id, id_message=message_id)
        db.session.add(like)
        message.likes += 1

    db.session.commit()
    return redirect(url_for('chat.show_discussion', discussion_id=message.id_discussion))
