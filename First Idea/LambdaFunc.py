import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import boto3
import io

def lambda_handler(event, context):
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

    pos = nx.spring_layout(G)
    edge_x = []
    edge_y = []

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=[node for node in G.nodes()],
        textposition='top center',
        hoverinfo='text',
        marker=dict(
            color='skyblue',
            size=10,
            line_width=2))

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40)))

    img_buffer = io.BytesIO()
    fig.write_image(img_buffer, format='png')
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
