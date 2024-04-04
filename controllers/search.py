from app import app
from flask import render_template, request, session, redirect, url_for
from utils import get_db_connection
from models.search_model import get_room, borrow_room, get_style, get_room_type, get_company

@app.route('/search', methods=["GET"])
def search():
    conn = get_db_connection()

    if request.values.get('borrow_room'):
        room_id = int(request.values.get('borrow_room'))
        borrow_room(conn, room_id, session['client_id'])
        return redirect(url_for("index"))
    
    
    
    if request.values.get('search') and len(request.values.to_dict()) > 1:
    
        filter_dict = dict(filter(lambda item: item[0] not in ('search'), dict(request.values).items()))
        
        chosen_style = {}
        chosen_room_type = {}
        chosen_company = {}
        
        df_style = get_style(conn)
        df_room_type = get_room_type(conn)
        df_company = get_company(conn)

        for i in range(len(df_style)):
            if df_style.loc[i, 'style_name'] in filter_dict:
                chosen_style[df_style.loc[i, 'style_name']] = df_style.loc[i, 'style_id']

        for i in range(len(df_room_type)):
            if df_room_type.loc[i, 'room_type_name'] in filter_dict:
                chosen_room_type[df_room_type.loc[i, 'room_type_name']] = df_room_type.loc[i, 'room_type_id']

        for i in range(len(df_company)):
            if df_company.loc[i, 'company_name'] in filter_dict:
                chosen_company[df_company.loc[i, 'company_name']] = df_company.loc[i, 'company_id']

        df_room = get_room(conn, chosen_style, chosen_room_type, chosen_company)

        html = render_template(
            'search.html',
            room = df_room,
            style = df_style,
            room_type = df_room_type,
            company = df_company,
            chosen_style = chosen_style,
            chosen_room_type = chosen_room_type,
            chosen_company = chosen_company,
            len = len
        )
        

    else:
        df_room = get_room(conn)
        df_style = get_style(conn)
        df_room_type = get_room_type(conn)
        df_company = get_company(conn)

        html = render_template(
                'search.html',
                room = df_room,
                style = df_style,
                room_type = df_room_type,
                company = df_company,
                len = len
        )
        
    return html