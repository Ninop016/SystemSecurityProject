import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def evaluate_security(flow_type, source, sink):
    score = 0
    if flow_type in ['Type1', 'Type2']:
        score += 5
    else:
        score += 2
    
    trusted_sources = ['TrustedSource1', 'TrustedSource2']
    trusted_sinks = ['TrustedSink1', 'TrustedSink2']
    
    if source in trusted_sources:
        score += 3
    else:
        score += 1
    
    if sink in trusted_sinks:
        score += 3
    else:
        score += 1
    
    return score

def lambda_handler(event, context):
    file_path = event.get('file_path', '')

    if not file_path:
        return {
            'statusCode': 400,
            'body': 'No file path provided for data retrieval.'
        }

    try:
        print("Loading data from file...")
        data = pd.read_csv(file_path)
        print("Data loaded successfully.")
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error loading data from file: {str(e)}"
        }

    if data.empty:
        return {
            'statusCode': 400,
            'body': 'No data available for flow analysis.'
        }

    # Group by flow type and count the number of unique devices
    grouped_data = data.groupby('Flow Type').agg(
        num_devices=('Source', 'nunique'),
        example_source=('Source', 'first'),
        example_sink=('Sink', 'first')
    ).reset_index()

    G = nx.DiGraph()

    for _, row in grouped_data.iterrows():
        flow_type = row['Flow Type']
        example_source = row['example_source']
        example_sink = row['example_sink']
        security_score = evaluate_security(flow_type, example_source, example_sink)
        G.add_edge(example_source, example_sink, flow_type=flow_type, security_score=security_score)

    print("Graph created, generating layout...")
    pos = nx.spring_layout(G)

    edge_colors = []
    for edge in G.edges(data=True):
        score = edge[2]['security_score']
        if score > 5:
            edge_colors.append('green')
        elif score >= 3:
            edge_colors.append('orange')
        else:
            edge_colors.append('red')

    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, node_size=5000, node_color="skyblue", font_size=14, font_weight="bold", edge_color=edge_colors)
    edge_labels = {(edge[0], edge[1]): f"{edge[2]['flow_type']} ({edge[2]['security_score']})" for edge in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)

    try:
        print("Saving figure as image...")
        plt.savefig('iot_data_flow.png')
        plt.close()
        print("Image saved successfully.")
        img_url = 'iot_data_flow.png'
    except Exception as e:
        print(f"Error saving image: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Error saving image locally: {str(e)}"
        }

    # Print the grouped data for reference
    print("Grouped data:")
    print(grouped_data)

    return {
        'statusCode': 200,
        'body': f"Data flow analysis complete. View the graph: {img_url}",
        'grouped_data': grouped_data.to_dict(orient='records')
    }

def main():
    event = {
        'file_path': 'dataset.csv'  # Ensure this file exists locally
    }

    result = lambda_handler(event, None)
    print(result)
    # Print the summarized information
    for item in result['grouped_data']:
        print(f"Flow Type: {item['Flow Type']}, Example Device: {item['example_source']} -> {item['example_sink']}, Number of Devices: {item['num_devices']}")

if __name__ == "__main__":
    main()
