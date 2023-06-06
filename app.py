from flask import Flask, render_template, request, redirect
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from jinja2 import Environment, FileSystemLoader
from sklearn.cluster import DBSCAN, KMeans

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    # if request.method == 'POST':

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
    
    if search_query:
        outputkab = ikan[
            ikan['Jenis_Ikan'].str.contains(search_query, case=False) |
            ikan['KabKota'].str.contains(search_query, case=False)
        ]
    elif kota_query:
        outputkab = ikan[ikan['KabKota'].str.contains(kota_query, case=False)]
    else:
        outputkab = ikan.copy()


    # Take one Region
    outputkab = outputkab[['KabKota', 'Jenis_Ikan', 'Status']].copy()
    
    # Limit the output to a maximum of 10 rows
    outputkab = outputkab.head(100)    
    
    
#     =================================================================================================


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
    values = [
        'Boleh untuk ditangkap',
        'Sehat untuk ditangkap',
        'Jumlah terbatas',
        'Overfishing',
        'Aman'
    ]
    ikan['Status'] = np.select(condition, values)

    # Sort custom
    urutan = [
        (ikan['Status'] == 'Overfishing'),
        (ikan['Status'] == 'Sehat untuk ditangkap'),
        (ikan['Status'] == 'Overfishing'),
        (ikan['Status'] == 'Jumlah terbatas')
    ]
    values = [1, 2, 3, 4]
    ikan['temp'] = np.select(urutan, values)
    ikan = ikan.sort_values(by=['temp'])

    # Filter by search query
    search_query = request.args.get('search')
    kota_query = request.args.get('kota')
    
    if search_query:
        outputkab2 = ikan[
            ikan['Jenis_Ikan'].str.contains(search_query, case=False) |
            ikan['KabKota'].str.contains(search_query, case=False)
        ]
    elif kota_query:
        outputkab2 = ikan[ikan['KabKota'].str.contains(kota_query, case=False)]
    else:
        outputkab2 = ikan.copy()

        outputkab2 = outputkab[['KabKota', 'Jenis_Ikan', 'Status']].copy()   
    
    # Display
    outputkab2 = outputkab2.head(10)

    return render_template('index.html', outputkab=outputkab, outputkab2=outputkab2)

if __name__ == '__main__':
    app.run(debug=True)
