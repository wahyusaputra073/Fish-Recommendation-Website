from flask import Flask, render_template, request
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from jinja2 import Environment, FileSystemLoader

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
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
    outputkab = outputkab.head(10)
    
    # Convert output to HTML table
    outputkab_html = outputkab.to_html(index=False)

    return render_template('index.html', outputkab=outputkab)
    
    # return render_template('index2.html')

if __name__ == '__main__':
    app.run(debug=True)
