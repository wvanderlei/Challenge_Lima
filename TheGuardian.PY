import requests
import pandas as pd
import pandas_gbq
import numpy as np
import google.cloud.exceptions
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

def mount_dataframe(response):
    res = []
    for i in response.json().get('response').get('results'):  
        res.append(i)
        df = pd.json_normalize(res)
        df = df.filter(["id","type","sectionId","sectionName","webPublicationDate","webTitle"])
    return df
       
url = "https://content.guardianapis.com/search?api-key=test"
 
project_id = "projectweb-380321"
table_id = 'news.tabela_theguardian'

response = requests.request("GET", url)


client = bigquery.Client(project_id)

sql = """
    SELECT * FROM `projectweb-380321.news.tabela_theguardian` limit 1000
"""
df = mount_dataframe(response)


try:
    client.get_table(table_id)  
    df2 = client.query(sql, project=project_id).to_dataframe()

    df3 = df.merge(df2, how='inner', on='id')
    df3.sort_values("id", inplace=True)
    df3.drop_duplicates(subset="id",keep=False, inplace=True)
    

    if df3  is not None:
        pandas_gbq.to_gbq(df, table_id, project_id=project_id,if_exists='replace')
except NotFound:
    pandas_gbq.to_gbq(df, table_id, project_id=project_id,if_exists='fail')
