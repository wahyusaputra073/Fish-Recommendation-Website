from flask import Flask, render_template, request
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from jinja2 import Environment, FileSystemLoader
import mysql.connector
from sklearn.cluster import DBSCAN, KMeans

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/index', methods=['GET', 'POST'])
def index():
    return tampil_halaman(1)

@app.route('/halaman/<int:halaman>')
def tampil_halaman(halaman):
    JUMLAH_PER_HALAMAN = 15

    # Load Data
    data_cluster = pd.read_csv("https://storage.googleapis.com/tim_panel1/DataCobaNew.csv")
    data_cluster = data_cluster[['Volume_Produksi','Konsumsi']]
    
    # Feature Scaling
    sc_data_cluster = StandardScaler()
    data_cluster_std = sc_data_cluster.fit_transform(data_cluster.astype(float))
    
    # Clustering with KMeans
    kmeans = KMeans(n_clusters=5, random_state=42).fit(data_cluster_std)
    labels = kmeans.labels_
    

    # Add labels to a new column
    ikan = pd.read_csv("https://storage.googleapis.com/tim_panel1/DataCobaNew.csv")
    ikan['Cluster'] = labels
    
    # Data Frame Manipulation
    condition = [
        (ikan['Cluster'] == 0),
        (ikan['Cluster'] == 1),
        (ikan['Cluster'] == 2),
        (ikan['Cluster'] == 3),
        (ikan['Cluster'] == 4)
    ]
    values = [
        'Kurang disarankan untuk ditangkap/dibudidaya', 
        'Bisa ditangkap/dibudidaya',
        'Disarankan untuk ditangkap/dibudidaya',
        'Sangat disarankan untuk ditangkap/dibudidaya',
        'Kurang disarankan untuk ditangkap/dibudidaya'
    ]
    ikan['Status'] = np.select(condition, values)
    
    # Filter by search query
    search_query = request.args.get('search')
    kota_query = request.args.get('kota')
    
    if search_query and kota_query:
        outputkab = ikan[
        (ikan['Jenis_Ikan'].str.contains(search_query, case=False, na=False) | ikan['KabKota'].str.contains(search_query, case=False)) &
        ikan['KabKota'].str.contains(kota_query, case=False, na=False)
    ] 

    if search_query:
        outputkab = ikan[
            (ikan['Jenis_Ikan'].str.contains(search_query, case=False, na=False)) &
            (ikan['KabKota'].str.contains(kota_query, case=False, na=False))
        ]
    elif kota_query:
        outputkab = ikan[ikan['KabKota'].str.contains(kota_query, case=False, na=False)]
    else:
        outputkab = ikan.copy()
       
    # Apply pagination
    awal = (halaman-1) * JUMLAH_PER_HALAMAN
    akhir = awal + JUMLAH_PER_HALAMAN
    outputkab = outputkab[awal:akhir]

    return render_template(
        'index.html', 
        table=outputkab.to_dict(orient='records'), 
        page=halaman, 
        JUMLAH_PER_HALAMAN=JUMLAH_PER_HALAMAN,
        search_query=search_query, kota_query=kota_query)




@app.route('/result', methods=['GET', 'POST'])
def index2():
    return tampil_halaman2(1)

@app.route('/halaman2/<int:halaman2>', methods=['GET', 'POST'])
def tampil_halaman2(halaman2):
    JUMLAH_PER_HALAMAN = 15
    # Melakukan proses clustering
    df = pd.read_csv("https://storage.googleapis.com/tim_panel1/DataCobaNew.csv")
    df = df[['Volume_Produksi', 'Konsumsi']]
    data = StandardScaler().fit_transform(df.astype(float))

    # Clustering menggunakan DBSCAN
    db = DBSCAN(eps=0.18, min_samples=2).fit(data)
    labels_dbscan = db.labels_

    # Clustering menggunakan K-means
    kmeans = KMeans(n_clusters=5, random_state=0)
    labels_kmeans = kmeans.fit_predict(data)

    # Menambahkan kolom label ke DataFrame
    df['Cluster_DBSCAN'] = labels_dbscan
    df['Cluster_KMeans'] = labels_kmeans

    # Menyimpan hasil clustering
    labels = labels_kmeans
    # Load Data
    ikan = pd.read_csv("https://storage.googleapis.com/tim_panel1/DataCobaNew.csv")
    ikan['Cluster'] = labels

    # Data Frame Manipulation
    condition = [
        (ikan['Cluster'] == 0),
        (ikan['Cluster'] == 1),
        (ikan['Cluster'] == 2),
        (ikan['Cluster'] == 3),
        (ikan['Cluster'] == 4)
    ]
    
    values = ['Sehat untuk ditangkap', 
              'Lebih baik dibatasi',
              'Overfishing',
              'Boleh dilebihkan',
              'Aman']
    ikan['Status'] = np.select(condition, values)

    # Sort custom
    urutan = [
            (ikan['Status'] == 'Sehat untuk ditangkap'),
            (ikan['Status'] == 'Lebih baik dibatasi'),
            (ikan['Status'] == 'Overfishing'),
            (ikan['Status'] == 'Boleh dilebihkan'),
            (ikan['Status'] == 'Aman'),
            ]
    values = [1, 2, 3, 4, 5]
    ikan['temp'] = np.select(urutan, values)
    ikan = ikan.sort_values(by=['temp'])

    # Filter by search query
    search_query = request.args.get('search')
    kota_query = request.args.get('kota')


    if search_query and kota_query:
        outputkab2 = ikan[
        (ikan['Jenis_Ikan'].str.contains(search_query, case=False, na=False) | ikan['KabKota'].str.contains(search_query, case=False)) &
        ikan['KabKota'].str.contains(kota_query, case=False, na=False)
    ]

    if search_query:
        outputkab2 = ikan[
            (ikan['Jenis_Ikan'].str.contains(search_query, case=False, na=False)) &
            (ikan['KabKota'].str.contains(kota_query, case=False, na=False))
        ]
    elif kota_query:
        outputkab2 = ikan[ikan['KabKota'].str.contains(kota_query, case=False, na=False)]
    else:
        outputkab2 = ikan.copy()
        
    outputkab2 = outputkab2[['KabKota', 'Jenis_Ikan', 'Status']].copy()   
    

    # Display
    outputkab2 = outputkab2.head(70)   
    
    awal = (halaman2-1) * JUMLAH_PER_HALAMAN
    akhir = awal + JUMLAH_PER_HALAMAN
    outputkab2 = outputkab2[awal:akhir]   

    return render_template(
        'index2.html', 
        table=outputkab2.to_dict(orient='records'), 
        page=halaman2, 
        JUMLAH_PER_HALAMAN=JUMLAH_PER_HALAMAN)
    

if __name__ == '__main__':
    app.run(debug=True)
