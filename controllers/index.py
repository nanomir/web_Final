from app import app
from flask import render_template, request, session, redirect, url_for
from utils import get_db_connection
from models.index_model import get_client, get_room_client, return_room

@app.route('/', methods=["GET"])
def index():
    conn = get_db_connection()

    if request.values.get('client'):
        client_id = int(request.values.get('client'))
        session['client_id'] = client_id
    

    # elif request.values.get('noselect'):
    #     a = 1

    elif request.values.get('return_room'):
        return_room(conn, request.values.get('return_room'))
        return redirect(url_for('index'))

    elif "client_id" not in session:
        session['client_id'] = 1
        
    df_client = get_client(conn)
    df_room_client = get_room_client(conn, session['client_id'])


    html = render_template(
            'index.html',
            client_id = session['client_id'],
            combo_box = df_client,
            room_client = df_room_client,
            len = len
    )
    return html