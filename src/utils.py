import pandas as pd
import math
import numpy as np
from src.config import engine
import dash_bootstrap_components as dbc
import pyDecision.algorithm as mcdma

w = [
    1/(14*6), 1/(14*6), 1/(14*6), 1/(14*6), 1/(14*6), 1/(14*6),
    1/(14*6), 1/(14*6), 1/(14*6), 1/(14*6), 1/(14*6), 1/(14*6),
    1/(14*4), 1/(14*4), 1/(14*4), 1/(14*4), 
    1/(14*11), 1/(14*11), 1/(14*11), 1/(14*11), 1/(14*11), 1/(14*11), 1/(14*11), 1/(14*11), 1/(14*11), 1/(14*11), 1/(14*11), 
    1/(14*7), 1/(14*7), 1/(14*7), 1/(14*7), 1/(14*7), 1/(14*7), 1/(14*7), 
    1/(14*6), 1/(14*6), 1/(14*6), 1/(14*6), 1/(14*6), 1/(14*6),
    1/(14*5), 1/(14*5), 1/(14*5), 1/(14*5), 1/(14*5), 
    1/(14*5), 1/(14*5), 1/(14*5), 1/(14*5), 1/(14*5), 
    1/(14*5), 1/(14*5), 1/(14*5), 1/(14*5), 1/(14*5), 
    1/(14*8), 1/(14*8), 1/(14*8), 1/(14*8), 1/(14*8), 1/(14*8), 1/(14*8), 1/(14*8), 
    1/(14*3), 1/(14*3), 1/(14*3), 
    1/(14*3), 1/(14*3), 1/(14*3), 
    1/(14*3), 1/(14*3), 1/(14*3), 
    1/(14*6), 1/(14*6), 1/(14*6), 1/(14*6), 1/(14*6), 1/(14*6),
]

c = ["max" for i in range(len(w))]

def normalization(matrix):
    # Transpose Decision Matrix
    matrix = matrix.transpose()
    row_values = []
    norm_matrix = []
    
    for i in range(matrix.shape[0]): # Looping per baris (kriteria)
        # Menghitung sum tiap x_{ij}^2
        sum_row = sum([pow(x,2) for x in matrix[i]])
        
        for j in range(matrix[i].shape[0]): # Looping per kolom (alternatif)
            # membangi nilai asli x_{ij} dengan hasil akar
            r_value = matrix[i][j] / math.sqrt(sum_row)
            
            # Masukkan hasil normalisasi ke list tiap baris
            row_values.append(r_value)
        
        #Masukkan hasil normalisasi per baris ke matrix normalisasi
        norm_matrix.append(row_values)
        
        #Kosongkan list normalisasi perbaris
        row_values = []
            
    # Ubah dalam bentuk numpy array
    norm_matrix = np.asarray(norm_matrix)
    
    # Return dalam bentuk transporse agar kembali ke format awal
    return norm_matrix.transpose()

# Implementasi Menghitung Nilai 
def optimize_value(w_matrix):
    y_values = []
    
    for i in range(w_matrix.shape[0]):
        max_val = []
        min_val = []
        
        for j in range(w_matrix[i].shape[0]):
            max_val.append(w_matrix[i][j])
        
        y = sum(max_val) - sum(min_val)
        y_values.append(y)
    
    return np.asarray(y_values)

def bobot(nilai):
    if nilai <=25:
        return 1
    elif nilai >25 and nilai <=50:
        return 2
    elif nilai >50 and nilai <=75:
        return 3
    else:
        return 4

def moora(tahun):
    nilai = pd.read_sql_query(
        f"select * from nilai where tahun = {tahun}",
        con=engine
    )

    kriteria = pd.read_sql_query(
        "select * from kriteria",
        con=engine
    )

    profil = pd.read_sql_query(
        "select * from profil",
        con=engine
    )

    recommendation = [
        'Naik gaji', 'Baik, pertahankan', 'Cukup, tingkatkan', 'Kurang, perbaiki', '-','-'
    ]

    df = nilai.iloc[:,:4].copy()
    for m in  kriteria['indikator_id'].str[0].unique():
        df[m] = pd.DataFrame(nilai[[n for n in nilai.columns if n.startswith("A")]].sum(axis=1)*100/(len([n for n in nilai.columns if n.startswith("A")])*2), columns=['A']).apply(lambda x: bobot(x.values[0]), axis=1)
    return df.iloc[:,:4].join(pd.DataFrame(optimize_value(normalization(df.iloc[:,4:].values)),columns=['skor'])).sort_values(by='skor',ascending=False).set_index('uid').join(pd.DataFrame(recommendation,columns=["rekomendasi"])).join(profil.set_index('uid')).reset_index()[['nip','nama','gol','mata_pelajaran','skor','rekomendasi']].reset_index().rename(columns={
        'index':'Peringkat','nip':'NIP','nama':'Nama','gol':'Golongan','mata_pelajaran':'Mata Pelajaran','skor':'Skor','rekomendasi':'Rekomendasi'
    }), df.rename(columns={n:kriteria[kriteria['indikator_id'].str[0]==n]['kompetensi'].unique()[0] for n in kriteria['indikator_id'].str[0].unique()})

CONTENT_STYLE = {
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

nav = dbc.Navbar([
    dbc.Nav(
        [
            dbc.NavItem(dbc.NavLink("Home", href="/main", active="exact")),
            dbc.NavItem(dbc.NavLink("Berikan Penilaian", id='nilai-btn', href="/nilai", active="exact")),
            dbc.NavItem(dbc.NavLink("Kelola Daftar Guru", href="/kelola", active="exact")),
            dbc.NavItem(dbc.NavLink("Logout", href="/logout", active="exact")),
        ],
        pills=True,
    ),
],color="dark")