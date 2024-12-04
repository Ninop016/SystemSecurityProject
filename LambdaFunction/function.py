import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx
import boto3
import io

def lambdahandler(event, context):
    data = event.get('data', [])
    if not data:
        return {
            'statusCode': 400,
            'body': 'No data provided for flow analysis.'
        }

    df = pd.DataFrame(data)

    G = nx.DiGraph()

    for idx, row in df.iterrows():
        G.add_edge(row['Source'], row['Sink'], flow_type=row['Flow Type'])

    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=12, font_weight="bold", edge_color="gray")

    edge_labels = {(row['Source'], row['Sink']): row['Flow Type'] for _, row in df.iterrows()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)

    s3 = boto3.client('s3')
    bucket_name = '4371projbucket'
    image_key = 'iot_data_flow.png'

    try:
        s3.upload_fileobj(img_buffer, bucket_name, image_key, ExtraArgs={'ACL': 'public-read'})
        img_url = f"https://4371projbucket.s3.amazonaws.com/iot_data_flow.png"
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error uploading to S3: {str(e)}"
        }

    return {
        'statusCode': 200,
        'body': f"Data flow analysis complete. View the graph: {img_url}"
    }