from app import app
from flask import render_template, request, session, redirect, url_for
from utils import get_db_connection
from models.index_model import get_new_client

@app.route('/new_client', methods=["GET"])
def new_client():
    conn = get_db_connection()

    if request.values.get("cancel"):
        return redirect(url_for("index"))

    if request.values.get("add") and request.values.get("new_client"):
        new_client = request.values.get('new_client')
        session['client_id'] = get_new_client(conn, new_client)
        return redirect(url_for("index"))

    html = render_template(
        'new_client.html'
    )
    return html