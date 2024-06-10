from re import template
from dash import dcc,html
#import dash_core_components as dcc
#import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
import plotly.express as px

import numpy as np
import pandas as pd

from server import app
from src.config import engine
from src.utils import moora, bobot

def layout():
    tahun = pd.read_sql_query("select tahun from nilai", con=engine)['tahun'].unique()
    thn_opt = [{'label':f'{n}', 'value':n} for n in tahun]
    nama = pd.read_sql_query("select nama from profil where bidang_yang_diampu != 'Kepala Sekolah' and bidang_yang_diampu is not Null", con=engine)['nama'].unique()
    nama_opt = [{'label':f'{n}', 'value':n} for n in nama]
    return dbc.Container([
        dbc.Row([
            dbc.Col(
                dcc.Dropdown(
                    id='thn-opt',
                    options=thn_opt,
                    style={
                        # 'width': '135px',
                        'color': '#212121',
                        'background-color': '#FFFFFF',
                    },
                    value=max(tahun),
                    clearable=False
                ),
            ),
            dbc.Col(
                dcc.Dropdown(
                    id='nama-opt',
                    options=nama_opt,
                    style={
                        # 'width': '135px',
                        'color': '#212121',
                        'background-color': '#FFFFFF',
                    },
                    multi=True
                ), md=6, style={'padding':20}
            )
        ], justify='center',align='center'),
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        html.Div(id='chart'), style={'height':'100%'})
                ), style={'padding':20}
            )
        ),
        html.Div(id='dataview', style={'padding':20, 'background-color':'#212121'})
    ], style={'background-color':'#212121'}, fluid=True)

@app.callback(
    [
        Output('dataview','children'),
        Output('chart','children'),
    ],
    [
        Input('thn-opt','value'),
        Input('nama-opt','value')
    ]
)
def dataview(thn,nm):

    df, dx = moora(thn)

    df['Peringkat'] = df['Peringkat'].astype(int) + 1
    # df['Rekomendasi'] = df['Peringkat'].astype(str).replace('1','Naik jabatan').replace('2','Bonus gajian').replace('3','Pengangkatan sebagai wali kelas').replace('4','Penilaian ulang')
    # for x in range(df['Rekomendasi'].size+1):
    #     if x > 4:
    #         df['Rekomendasi'] = df['Rekomendasi'].replace(str(x),'-')


    for x in range(df['Rekomendasi'].size):
        numb = float(df['Skor'].get(x))
        if abs(numb) >= abs(float(4)):
            df['Rekomendasi'][x] = 'Naik jabatan'
        elif abs(numb) < abs(float(4)) and abs(numb) >= abs(float(3.5)):
            df['Rekomendasi'][x] = 'Bonus gajian'
        elif abs(numb) < abs(float(3.5)) and abs(numb) >= abs(float(3)):
            df['Rekomendasi'][x] = 'Pengangkatan sebagai wali kelas'
        else:
            df['Rekomendasi'][x] = 'Bimbingan penilaian'
        
    fig = px.line_polar(
        pd.DataFrame(dx.iloc[:,4:].mean()).reset_index().rename(columns={'index':'Kompetensi',0:'Nilai'}), 
        r='Nilai', theta='Kompetensi', line_close=True)
    dx_mean = pd.DataFrame(dx.iloc[:,4:].mean()).reset_index().rename(columns={'index':'Kompetensi',0:'Nilai'})
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=dx_mean.Nilai.values.tolist(),
        theta=dx_mean.Kompetensi.values.tolist(),
        fill='toself',
        name='Rata-rata'
    ))
    if nm == [] or nm is None:
        pass
    else:
        for nama in nm:
            nilai = pd.read_sql_query(
                f"select * from nilai nl\
                join (\
                    select * from profil\
                ) prf on nl.uid=prf.uid\
                where prf.nama = '{nama}'\
                    and nl.tahun = '{thn}'",
                con=engine).iloc[:,4:82]
            nilai = nilai.transpose().reset_index().rename(columns={'index':'indikator',0:'nilai'})
            nilai['kriteria'] = nilai['indikator'].str[0]
            dn = nilai.groupby('kriteria')['nilai'].sum().reset_index().copy()
            dn['maks'] = (nilai.groupby('kriteria')['nilai'].count()*2).values
            dn['bobot'] = (dn['nilai']/dn['maks']) * 100
            dn['bobot'] = dn['bobot'].apply(lambda x: bobot(x))
            fig.add_trace(go.Scatterpolar(
                r=dn.bobot.values.tolist(),
                theta=dx_mean.Kompetensi.values.tolist(),
                fill='toself',
                name=nama
            ))

    fig.update_layout(
        template='plotly_dark',
        hovermode="x",
        paper_bgcolor='rgba(21, 89, 176, 0.8)',
        plot_bgcolor='rgba(21, 89, 176, 0.8)',
        # title='Radar Chart <b>Kompetensi Guru</b>'
        title={
            'text': 'Radar Chart <b>Kompetensi Guru</b>',
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    return html.Div(
        dbc.Row(
            dbc.Table.from_dataframe(
                df, striped=True, bordered=True, hover=True, index=False, dark=True, responsive=True
            )
        ), style={'background-color':'#212121'}
    ), html.Div(
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    figure=fig
                )
            )
        ), style={'background-color':'#212121'}
    )