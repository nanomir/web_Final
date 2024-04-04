import pandas

def get_room(conn, chosen_style = {}, chosen_room_type = {}, chosen_company = {}):
    if len(chosen_style) == 0 and len(chosen_room_type) == 0 and len(chosen_company) == 0:
        return pandas.read_sql('''
                            
            WITH get_room_types( room_id, room_types_name)
            AS(
                SELECT room_id, GROUP_CONCAT(room_type_name, ', ')
                FROM room_type JOIN room_room_type USING(room_type_id)
                GROUP BY room_id
            )

            select
                title as Адрес, 
                room_types_name as 'Тип_квартиры', 
                style_name as Стиль_квартиры,
                company_name as Компания,
                price as Цена_в_сутки,
                available_amount as Доступно,
                room_id
            from room join style using(style_id) 
            join company using(company_id) 
            join get_room_types using(room_id)

        ''', conn)
    else:
        cur = conn.cursor()

        df_style = pandas.DataFrame()
        for item in chosen_style:
            df_tmp = pandas.DataFrame(cur.execute('''
                
                select room_id from room
                where style_id = :item

            ''', {"item": int(chosen_style[item])}))

            df_style = pandas.concat([df_style, df_tmp])
        df_style.reset_index(inplace = True, drop= True)
        df_style = [df_style.loc[i, 0] for i in range(len(df_style))] if len(df_style) != 0 else []
            

        df_room_type = pandas.DataFrame()
        for item in chosen_room_type:
            df_tmp = pandas.DataFrame(cur.execute('''
                
                select room_id from room_room_type
                where room_type_id = :item

            ''', {"item": int(chosen_room_type[item])}))
                
            df_room_type = pandas.concat([df_room_type, df_tmp])
        df_room_type.reset_index(inplace = True, drop = True)
        df_room_type = [df_room_type.loc[i, 0] for i in range(len(df_room_type))] if len(df_room_type) != 0 else []


        df_company = pandas.DataFrame()
        for item in chosen_company:
            df_tmp = pandas.DataFrame(cur.execute('''
                
                select room_id from room
                where company_id = :item

            ''', {"item": int(chosen_company[item])}))
                
            df_company = pandas.concat([df_company, df_tmp])
        df_company.reset_index(inplace = True, drop = True)
        if len(df_style) != 0:
            df_company = [df_company.loc[i, 0] for i in range(len(df_company))] if len(df_company) != 0 else []


        index = df_style if len(df_style) != 0 else []
        index = df_room_type if len(df_room_type) != 0 else index
        index = df_company if len(df_company) != 0 else index
        index = list(set(index) & set(df_style)) if len(df_style) != 0 else index
        index = list(set(index) & set(df_room_type)) if len(df_room_type) != 0 else index
        index = list(set(index) & set(df_company)) if len(df_company) != 0 else index

        df = pandas.DataFrame()
        for item in index:

            df_tmp = pandas.read_sql('''
                            
                WITH get_room_types( room_id, room_types_name)
                AS(
                    SELECT room_id, GROUP_CONCAT(room_type_name, ', ')
                    FROM room_type JOIN room_room_type USING(room_type_id)
                    GROUP BY room_id
                )

                select
                    title as Адрес, 
                    room_types_name as 'Тип_квартиры', 
                    style_name as Стиль_квартиры,
                    company_name as Компания,
                    price as Цена_в_сутки,
                    available_amount as Доступно,
                    room_id
                from room join style using(style_id) 
                join company using(company_id) 
                join get_room_types using(room_id)
                where room_id = :item

            ''', conn, params = {"item": int(item)})  

            df = pandas.concat([df, df_tmp])

        df.reset_index(inplace = True, drop= True)
        return df
    
def get_style(conn):

    return pandas.read_sql('''
                           
        select distinct style.*, count() over(partition by room.style_id) as count from style join room using(style_id)

    ''', conn)

def get_room_type(conn):
    return pandas.read_sql('''
                           
        select distinct room_type.*, count() over(partition by room_room_type.room_type_id)
        as count from room_type join room_room_type using(room_type_id)

    ''', conn)

def get_company(conn):
    return pandas.read_sql('''
                           
        select distinct company.*, count() over(partition by company_id) 
        as count from company join room using(company_id)

    ''', conn)

def borrow_room(conn, room_id, client_id):
    cur = conn.cursor()

    cur.execute('''
        
        insert into room_client (room_client_id, room_id, client_id, enter_date, exit_date) values (null, :curr_room_id, :curr_client_id, date('now', 'localtime'), null)

    ''', {"curr_room_id": room_id, "curr_client_id": client_id})

    cur.execute('''
        
        update room
        set available_amount = available_amount - 1
        where room_id = :curr_room_id

    ''', {"curr_room_id": room_id})

    conn.commit()

    cur.close()

    return True