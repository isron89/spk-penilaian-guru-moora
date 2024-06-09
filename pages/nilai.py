from dash import dcc,html, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import datetime as dt
from flask_login import current_user
import pandas as pd

from sqlalchemy import text
from src.config import engine
from datetime import datetime
from server import app

from sqlalchemy.exc import SQLAlchemyError
import traceback

def layout():
    nama = pd.read_sql_query("select uid, nama from profil where bidang_yang_diampu != 'Kepala Sekolah' and bidang_yang_diampu is not Null", con=engine)
    nama_opt = [{'label':f'{n}', 'value':m} for m,n in zip(nama['uid'],nama['nama'])]
    tahun = pd.read_sql_query("select tahun from nilai", con=engine)['tahun'].unique().tolist()
    if max(tahun)+1 == dt.datetime.today().year and dt.datetime.today().month == 12:
        tahun = tahun + [max(tahun)+1]
    thn_opt = [{'label':f'{n}', 'value':n} for n in tahun]
    kompetensi = pd.read_sql_query("select distinct kompetensi from kriteria", con=engine)['kompetensi'].values.tolist()
    return dbc.Container([
        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    id='nama-opt-nl',
                    options=nama_opt,
                    style={
                        # 'width': '135px',
                        'color': '#212121',
                        'background-color': '#FFFFFF',
                    }
                ), 
                md=4, style={'padding':20}
            ),
            dbc.Col(
                dcc.Dropdown(
                    id='thn-opt-nl',
                    options=thn_opt,
                    style={
                        # 'width': '135px',
                        'color': '#212121',
                        'background-color': '#FFFFFF',
                    }
                ),
                md=4, style={'padding':20}
            ),
            dbc.Col(
                dbc.Checklist(
                    options=[
                        {"label": "Edit", "value": True},
                    ],
                    value=False,
                    id="switches-edit-nl",
                    switch=True,
                    style={'text-align':'center'},
                ), md=4, style={'padding':20}
            )
        ], align='center',justify='center'),
        dbc.Container([
            dbc.Row([
                html.H3(html.B(k)),
                dbc.Container([
                    dbc.InputGroup([
                        html.Div(f"{m}", style={'width':'80vh', 'height':'auto', 'overflow-wrap':'break-word', 'font-size':'1vw', 'backgroundColor':'#303030', 'padding':'10px'}),
                        dbc.Select(
                            options=[{'label':y.values[1], 'value':x} for x,y in pd.read_sql_query("select * from skor", con=engine).iterrows()],
                            id=f"{n[0]}-field", style={'height':'auto', 'font-size':'1vw'}
                        ),
                    ],className="mb-3"  ) for m,n in zip(
                        pd.read_sql_query(f"select indikator from kriteria where kompetensi = '{k}'", con=engine)['indikator'].values.tolist(),
                        pd.read_sql_query(f"select indikator_id kompetensi from kriteria where kompetensi = '{k}'", con=engine).values.tolist()
                    )
                ], fluid=True)
            ]) for k in kompetensi], fluid=True),
        dbc.Row([
            dbc.Col(
                dbc.Button("Hapus",id="hapus-btn-nl"),
                align='center', md=4, style={'padding':20}
            ),
            dbc.Col(
                dbc.Button("Perbaharui",id="update-btn-nl"),
                align='center', md=4, style={'padding':20}
            ),
            dbc.Col(
                dbc.Button("Tambahkan",id="tambah-btn-nl"),
                align='center', md=4, style={'padding':20}
            )
        ], align='center',justify='center', style={'text-align':'center'}),
        html.Div(id='output')
    ], fluid=True)

@app.callback(
    [
        Output('update-btn-nl','disabled')
    ] + [Output(f"{n[0]}-field","disabled") for n in pd.read_sql_query("select indikator_id kompetensi from kriteria", con=engine).values.tolist()] + 
    [
        Output('hapus-btn-nl','disabled'),
        Output('tambah-btn-nl','disabled'),
        Output('switches-edit-nl','disabled')
    ],
    [
        Input('nama-opt-nl','value'),
        Input('thn-opt-nl','value'),
        Input('switches-edit-nl','value')
    ]
)
def disabled_nl(nm,th,sw):
    if nm is not None and th is not None:
        df = pd.read_sql_query(f"select * from nilai where uid = '{nm}' and tahun = {th}", con=engine)
    else:
        df = pd.DataFrame()
    if nm is None or th is None:
        return [True for n in range(pd.read_sql_query("select count(1) kompetensi from kriteria", con=engine).values[0][0] + 4)]
    elif df.empty:
        return [True] + [False for n in range(pd.read_sql_query("select count(1) kompetensi from kriteria", con=engine).values[0][0])] + [True, False, True]
    elif not df.empty and sw:
        return [False for n in range(pd.read_sql_query("select count(1) kompetensi from kriteria", con=engine).values[0][0] + 1)]  + [True,True,False]
    elif not df.empty and not sw:
        return [True for n in range(pd.read_sql_query("select count(1) kompetensi from kriteria", con=engine).values[0][0] + 1)]  + [False,True,False]
    else:
        return [True for n in range(pd.read_sql_query("select count(1) kompetensi from kriteria", con=engine).values[0][0] + 1)] + [True,True,True]

@app.callback(
    [Output(f"{n[0]}-field","placeholder") for n in pd.read_sql_query("select indikator_id kompetensi from kriteria", con=engine).values.tolist()],
    [
        Input('nama-opt-nl','value'),
        Input('thn-opt-nl','value')
    ]
)
def field_val(nm,th):
    skor = pd.read_sql_query("select * from skor", con=engine)
    skor = skor.set_index("skor").to_dict()['keterangan']
    if nm is not None and th is not None:
        df = pd.read_sql_query(f"select * from nilai where uid = '{nm}' and tahun = {th}", con=engine).iloc[:,4:]
        if not df.empty:
            return [skor[n] for n in df.values.tolist()[0]]
        else:
            return ["" for n in range(pd.read_sql_query("select count(1) kompetensi from kriteria", con=engine).values[0][0])]
    else:
        return ["" for n in range(pd.read_sql_query("select count(1) kompetensi from kriteria", con=engine).values[0][0])]

@app.callback(
    Output('output','children'),
    [
        Input('nama-opt-nl','value'),
        Input('thn-opt-nl','value'),
        Input('tambah-btn-nl','n_clicks'),
        Input('update-btn-nl','n_clicks'),
        Input('hapus-btn-nl','n_clicks')
    ] 
    # + [Input(f'{n}-field','value') for n in pd.read_sql_query("PRAGMA table_info(nilai)", con=engine).name.values if n != 'pid'],
    + [Input(f"{n[0]}-field","value") for n in pd.read_sql_query("select indikator_id kompetensi from kriteria", con=engine).values.tolist()]
)

def tambah_nilai(nm,th,btn,btn2,btn3,a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z,aa,bb,cc,dd,ee,ff,gg,hh,ii,jj,kk,ll,mm,nn,oo,pp,qq,rr,ss,tt,uu,vv,ww,xx,yy,zz,aaa,bbb,ccc,ddd,eee,fff,ggg,hhh,iii,jjj,kkk,lll,mmm,nnn,ooo,ppp,qqq,rrr,sss,ttt,uuu,vvv,www,xxx,yyy,zzz):
# def tambah_nilai(nm,th,btn,list):
    trigger = callback_context.triggered[0]
    if trigger['prop_id'] == 'tambah-btn-nl.n_clicks':
        pid = f'p{int(pd.read_sql_query("select uid from nilai order by uid desc limit 1", con=engine).values.tolist()[0][0][1:])+1:03d}'
        col_sql = ','.join(pd.read_sql_query("select * from nilai order by uid asc limit 1", con=engine).columns.tolist())
        with engine.connect() as conn:
            ts = createDateTime()
            conn.execute(
                text(
                    f"insert into nilai (\
                        {col_sql}\
                    ) values (\
                        '{pid}','{nm}','{ts}',{th},{a},{b},{c},{d},{e},{f},{g},{h},{i},{j},{k},{l},{m},{n},{o},{p},{q},{r},{s},{t},{u},{v},{w},{x},{y},{z},{aa},{bb},{cc},{dd},{ee},{ff},{gg},{hh},{ii},{jj},{kk},{ll},{mm},{nn},{oo},{pp},{qq},{rr},{ss},{tt},{uu},{vv},{ww},{xx},{yy},{zz},{aaa},{bbb},{ccc},{ddd},{eee},{fff},{ggg},{hhh},{iii},{jjj},{kkk},{lll},{mmm},{nnn},{ooo},{ppp},{qqq},{rrr},{sss},{ttt},{uuu},{vvv},{www},{xxx},{yyy},{zzz}\
                    )"
                )
            )
            conn.commit()
        return f"Added nilai {pid}"
    elif trigger['prop_id'] == 'update-btn-nl.n_clicks':
        with engine.connect() as conn:
            ts = createDateTime()
            conn.execute(
                text(
                    f"UPDATE nilai SET tgl_penilaian='{ts}', A01={a}, A02={b}, A03={c}, A04={d}, A05={e}, A06={f}, B01={g}, B02={h}, B03={i}, B04={j}, B05={k}, B06={l}, C01={m}, C02={n}, C03={o}, C04={p}, D01={q}, D02={r}, D03={s}, D04={t}, D05={u}, D06={v}, D07={w}, D08={x}, D09={y}, D10={z}, D11={aa}, E01={bb}, E02={cc}, E03={dd}, E04={ee}, E05={ff}, E06={gg}, E07={hh}, F01={ii}, F02={jj}, F03={kk}, F04={ll}, F05={mm}, F06={nn}, G01={oo}, G02={pp}, G03={qq}, G04={rr}, G05={ss}, H01={tt}, H02={uu}, H03={vv}, H04={ww}, H05={xx}, I01={yy}, I02={zz}, I03={aaa}, I04={bbb}, I05={ccc}, J01={ddd}, J02={eee}, J03={fff}, J04={ggg}, J05={hhh}, J06={iii}, J07={jjj}, J08={kkk}, K01={lll}, K02={mmm}, K03={nnn}, L01={ooo}, L02={ppp}, L03={qqq}, M01={rrr}, M02={sss}, M03={ttt}, N01={uuu}, N02={vvv}, N03={www}, N04={xxx}, N05={yyy}, N06={zzz} WHERE uid='{nm}' and tahun={th};"
                )
            )
            conn.commit()
        return f"Updated nilai {nm} periode {th}"
    elif trigger['prop_id'] == 'hapus-btn-nl.n_clicks':
        query = f"delete from nilai where uid= '{nm}' and tahun= {th}"
        try :
            with engine.connect() as conn:
                conn.execute(
                    text(query)
                )
                conn.commit()
            return f"Deleted nilai {nm} periode {th}"
        except SQLAlchemyError as e:
            print(e)
            traceback.print_exc()
            return f"Nilai {nm} not found"
    print(trigger)
    return ""

def stringToDatetime(date_string):
    return datetime.strptime(date_string, '%Y-%m-%d')

def createDateTime():
    times = datetime.now()
    return times.replace(hour=0, minute=0, second=0, microsecond=0)