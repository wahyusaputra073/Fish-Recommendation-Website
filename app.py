from flask import Flask, render_template, request
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from jinja2 import Environment, FileSystemLoader
import mysql.connector

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
    outputkab = outputkab.head(100)
    
    # Convert output to HTML table
    outputkab_html = outputkab.to_html(index=False)

    # Connect to MySQL
    cnx = mysql.connector.connect(
        user="panelteam01",
        password="pjLm.j)&5(39'`f8",
        host="34.101.58.55",
        database="panelteam01"
    )

    # Create table if not exists
    cursor = cnx.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clustering_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            KabKota VARCHAR(255),
            Jenis_Ikan VARCHAR(255),
            Status VARCHAR(255)
        )
    """)

    # Insert data into table
    for _, row in outputkab.iterrows():
        cursor.execute("""
            INSERT INTO clustering_results (KabKota, Jenis_Ikan, Status)
            VALUES (%s, %s, %s)
        """, (row['KabKota'], row['Jenis_Ikan'], row['Status']))
    
    # Commit the changes
    cnx.commit()

    # Close the cursor and connection
    cursor.close()
    cnx.close()

    return render_template('index.html', outputkab=outputkab)
    
if __name__ == '__main__':
    app.run(debug=True)
