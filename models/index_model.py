import pandas

def get_client(conn):
    return pandas.read_sql('''

        SELECT * FROM client
    
    ''', conn)

def get_room_client(conn, client_id):
    return pandas.read_sql('''

        WITH get_room_types( room_id, room_types_name)
        AS(
            SELECT room_id, GROUP_CONCAT(room_type_name)
            FROM room_type JOIN room_room_type USING(room_type_id)
            GROUP BY room_id
        )
        SELECT title AS Адрес, room_types_name AS Тип_квартиры,
            enter_date AS Дата_заселения, exit_date AS Дата_выселения,
            room_client_id
        FROM
            client
            JOIN room_client USING(client_id)
            JOIN room USING(room_id)
            JOIN get_room_types USING(room_id)
        WHERE client.client_id = :id
        ORDER BY 3

    
    ''', conn, params={"id": client_id})

def get_new_client(conn, new_client):
    cur = conn.cursor()
    cur.execute('''

        insert into client (client_id, client_name) values (null, :new_client)

    ''', {"new_client": new_client})
    conn.commit()
    cur.close()
    
    return cur.lastrowid

def return_room(conn, room_client_id):
    cur = conn.cursor()
    
    cur.execute('''
                
        update room as A
        set available_amount = A.available_amount + 1
        from room as B join room_client using (room_id)   
        where room_client_id = :curr_room_client_id
        and A.room_id = B.room_id;
                
        
                                     
    ''', {"curr_room_client_id": room_client_id})

    cur.execute('''
                
        update room_client
        set exit_date = date('now', 'localtime')
        where room_client_id = :curr_room_client_id
                                     
    ''', {"curr_room_client_id": room_client_id})

    conn.commit()

    cur.close()
    
    return