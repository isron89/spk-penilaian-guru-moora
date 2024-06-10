from dash import dcc,html, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from flask_login import current_user
import pandas as pd

import sqlalchemy as db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from src.config import engine, DEV
from server import app

from datetime import datetime
import traceback

def layout():
    nama = pd.read_sql_query("select uid, nama from profil where bidang_yang_diampu != 'Kepala Sekolah' and bidang_yang_diampu is not Null", con=engine)
    nama_opt = [{'label':f'{n}', 'value':m} for m,n in zip(nama['uid'],nama['nama'])]
    field = pd.read_sql_query("PRAGMA table_info(profil)", con=engine)
    fn = ['UID', 'NIP', 'Karpeg','NUPTK','NRG','Nama','Tempat & Tgl. Lahir','Golongan','TMT','Mulai Bekerja di Sekolah','Pendidikan','Jenis Kelamin','Mata Pelajaran','Bidang yang Diampu']
    return dbc.Container([
        dbc.Row([
            dbc.Col(
               dcc.Dropdown(
                    id='nama-opt-kel',
                    options=nama_opt,
                    style={
                        # 'width': '135px',
                        'color': '#212121',
                        'background-color': '#FFFFFF',
                    },
                ), md=6, style={'padding':20}
            ),
            dbc.Col(
                dbc.Checklist(
                    options=[
                        {"label": "Edit", "value": True},
                    ],
                    value=False,
                    id="switches-edit",
                    switch=True,
                    style={'text-align':'center'},
                ), align='center', md=3, style={'padding':20}
            ),
            dbc.Col(
                dbc.Button("Perbaharui", id="update-btn"),
                align='center', md=3, style={'padding':20}
            )
        ], align='center',justify='center'),
        dbc.Container([
            dbc.InputGroup([
                dbc.InputGroupText(f"{m}", style={'width':'20vh'}),
                dbc.Input(id=f"{n}-field")
            ],className="mb-3") for m,n in zip(fn,field.name.values)], fluid=True
        ),
        dbc.Row([
            dbc.Col(
                dbc.Button("Hapus",id="hapus-btn"),
                align='center', md=5, style={'padding':20}
            ),
            dbc.Col(
                html.Div(id="output-kelola"),#,style={'display':'none'}
                align='center', md=2, style={'padding':20}
            ),
            dbc.Col(
                dbc.Button("Tambahkan",id="tambah-btn"),
                align='center', md=5, style={'padding':20}
            )
        ], align='center',justify='center', style={'text-align':'center', 'background-color':'#1c59b0cc'}, className="mb-3"),
    ], style={'background-color':'#1c59b0cc'}, fluid=True)

@app.callback(
    [Output(f'{n}-field','placeholder') for n in pd.read_sql_query("PRAGMA table_info(profil)", con=engine).name.values],
    Input('nama-opt-kel','value')
)
def kelola(nama):
    if nama != None:
        return pd.read_sql_query(f"select * from profil where uid='{nama}'", con=engine).values.tolist()[0]
    else:
        return ['.....' for n in range(len(pd.read_sql_query("PRAGMA table_info(profil)", con=engine).name.values))]

@app.callback(
    Output('switches-edit','options'),
    Input('url','pathname')
)
def disable_edit(url):
    try:
        if current_user.username == "kepsek":
            return [{"label": "Edit", "value": True, "disabled":True}]
        else:
            return [{"label": "Edit", "value": True, "disabled":False}]
    except:
        return [{"label": "Edit", "value": True, "disabled":False}]

@app.callback(
    [Output(f'{n}-field','disabled') for n in pd.read_sql_query("PRAGMA table_info(profil)", con=engine).name.values],
    Input('switches-edit','value')
)
def disable_edit(val):
    if val:
        return [True] + [False for n in range(len(pd.read_sql_query("PRAGMA table_info(profil)", con=engine).name.values)-1)]
    else:
        return [True for n in range(len(pd.read_sql_query("PRAGMA table_info(profil)", con=engine).name.values))]

@app.callback(
    [
        Output("hapus-btn",'disabled'),
        Output("tambah-btn",'disabled'),
        Output("update-btn",'disabled')
    ],
    [
        Input('nama-opt-kel','value'),
        Input('switches-edit','value')
    ]
)
def button_below(val,sw):
    if val == None and sw:
        return True, False, True
    elif (val == None and not sw):# or current_user.username == 'kepsek':
        return True, True, True
    elif val != None and sw:
        return True, True, False
    else:
        return False, True, True

@app.callback(
    Output('output-kelola','children'),
    [
        Input('nama-opt-kel','value'),
        Input('tambah-btn','n_clicks'),
        Input('hapus-btn','n_clicks'),
        Input('update-btn','n_clicks')
    ] 
    + [Input(f'{n}-field','value') for n in pd.read_sql_query("PRAGMA table_info(profil)", con=engine).name.values if n != 'uid'],
    
)
def tambah_nilai(nm,btn1,btn2,btn3,b,c,d,e,f,g,h,i,j,k,l,m,n):
    trigger = callback_context.triggered[0]
    if trigger['prop_id']=='tambah-btn.n_clicks':
        uid = f'u{int(pd.read_sql_query("select uid from profil order by uid desc limit 1", con=engine).values.tolist()[0][0][1:])+1:03d}'
        col_sql = ','.join(pd.read_sql_query("select * from profil order by uid asc limit 1", con=engine).columns.tolist())
        with engine.connect() as conn:
            g = stringToDatetime(g)
            i = stringToDatetime(i)
            j = stringToDatetime(j)
            conn.execute(
                text(
                    f"insert into profil (\
                        {col_sql}\
                    ) values (\
                        '{uid}',{b},'{c}','{d}','{e}','{f}','{g}','{h}','{i}','{j}','{k}','{l}','{m}','{n}'\
                    )"
                )
            )
            conn.commit()
        return f"Added user {uid}"
    elif trigger['prop_id']=='update-btn.n_clicks':
        col_sql = ','.join(pd.read_sql_query("select * from profil order by uid asc limit 1", con=engine).columns.tolist())
        with engine.connect() as conn:
            if b:
                conn.execute(
                    text(
                        f"update profil set \
                            nip='{b}' \
                        where uid = '{nm}'"
                    )
                )
            if c:
                conn.execute(
                    text(
                        f"update profil set \
                            karpeg='{c}' \
                        where uid = '{nm}'"
                    )
                )
            if d:
                conn.execute(
                    text(
                        f"update profil set \
                            nuptk='{d}' \
                        where uid = '{nm}'"
                    )
                )
            if e:
                conn.execute(
                    text(
                        f"update profil set \
                            nrg='{e}' \
                        where uid = '{nm}'"
                    )
                )
            if f:
                conn.execute(
                    text(
                        f"update profil set \
                            nama='{f}' \
                        where uid = '{nm}'"
                    )
                )
            if g:
                g = stringToDatetime(g)
                conn.execute(
                    text(
                        f"update profil set \
                            ttl='{g}' \
                        where uid = '{nm}'"
                    )
                )
            if h:
                conn.execute(
                    text(
                        f"update profil set \
                            gol='{h}' \
                        where uid = '{nm}'"
                    )
                )
            if i:
                i = stringToDatetime(i)
                conn.execute(
                    text(
                        f"update profil set \
                            tmt='{i}' \
                        where uid = '{nm}'"
                    )
                )
            if j:
                j = stringToDatetime(j)
                conn.execute(
                    text(
                        f"update profil set \
                            mulai='{j}' \
                        where uid = '{nm}'"
                    )
                )
            if k:
                conn.execute(
                    text(
                        f"update profil set \
                            pendidikan='{k}' \
                        where uid = '{nm}'"
                    )
                )
            if l:
                conn.execute(
                    text(
                        f"update profil set \
                            gender='{l}' \
                        where uid = '{nm}'"
                    )
                )
            if m:
                conn.execute(
                    text(
                        f"update profil set \
                            mata_pelajaran='{m}' \
                        where uid = '{nm}'"
                    )
                )
            if n:
                conn.execute(
                    text(
                        f"update profil set \
                            bidang_yang_diampu='{n}' \
                        where uid = '{nm}'"
                    )
                )
            conn.commit()
        return f"Updated user {nm}"
    elif trigger['prop_id']=='hapus-btn.n_clicks':
        # query = db.text(f"delete from profil where uid = {nm}")
        query = f"delete from profil where uid= '{nm}'"
        try :
            with engine.connect() as conn:
                conn.execute(
                    text(query)
                )
                conn.commit()
            return f"Deleted user {nm}"
        except SQLAlchemyError as e:
            print(e)
            traceback.print_exc()
            return f"User {nm} not found"
    else:
        return ""

def stringToDatetime(date_string):
    return datetime.strptime(date_string, '%Y-%m-%d')