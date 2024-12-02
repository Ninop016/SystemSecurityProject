import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog, Button, Label, messagebox, Toplevel, Text, Scrollbar, END, simpledialog

# Global variables to hold the loaded data and graph
loaded_data = None
current_graph = None

# Function to load CSV file
def load_csv():
    global loaded_data, current_graph
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    if file_path:
        try:
            loaded_data = pd.read_csv(file_path)
            if not {"Source", "Sink", "Flow Type"}.issubset(loaded_data.columns):
                raise ValueError("CSV must contain 'Source', 'Sink', and 'Flow Type' columns.")
            visualize_data_flows(loaded_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file: {e}")

# Function to visualize data flows
def visualize_data_flows(dataframe):
    global current_graph
    current_graph = nx.DiGraph()  # Directed graph to show flow direction

    # Add nodes and edges with flow type as edge labels
    for idx, row in dataframe.iterrows():
        current_graph.add_edge(row['Source'], row['Sink'], flow_type=row['Flow Type'])

    # Use a layout with a larger scale
    pos = nx.spring_layout(current_graph, scale=3, k=0.5)  # Increase scale and spacing with k

    # Draw the graph with increased figure size
    plt.figure(figsize=(14, 10))  # Larger figure size for better visualization
    nx.draw(
        current_graph, pos, with_labels=True, node_size=2000, font_size=12, node_color="skyblue",
        font_weight="bold", edge_color="gray"
    )

    # Add edge labels with extra padding
    edge_labels = nx.get_edge_attributes(current_graph, 'flow_type')
    nx.draw_networkx_edge_labels(
        current_graph, pos, edge_labels=edge_labels, font_size=10, label_pos=0.6, rotate=False
    )

    plt.title("Sensitive Data Flows in IoT Apps", fontsize=16, fontweight="bold")
    plt.show()

# Function to display additional insights
def show_insights():
    global loaded_data
    if loaded_data is None:
        messagebox.showerror("Error", "No data loaded. Please load a CSV file first.")
        return

    insights = Toplevel()
    insights.title("Data Insights")
    insights.geometry("400x300")

    text_area = Text(insights, wrap='word', font=("Helvetica", 12))
    text_area.pack(expand=1, fill='both')
    scrollbar = Scrollbar(insights, command=text_area.yview)
    scrollbar.pack(side="right", fill="y")
    text_area['yscrollcommand'] = scrollbar.set

    # Generate insights
    most_common_source = loaded_data['Source'].mode().iloc[0]
    most_common_sink = loaded_data['Sink'].mode().iloc[0]
    most_common_flow = loaded_data['Flow Type'].mode().iloc[0]
    total_flows = len(loaded_data)

    insights_text = f"""
    Total Data Flows: {total_flows}
    Most Common Source: {most_common_source}
    Most Common Sink: {most_common_sink}
    Most Common Flow Type: {most_common_flow}
    """
    text_area.insert(END, insights_text)

# Function to search the graph
def search_graph():
    global current_graph
    if current_graph is None:
        messagebox.showerror("Error", "No graph data available. Please load and visualize data first.")
        return

    query = simpledialog.askstring("Search Graph", "Enter a node or flow type to search:")
    if query:
        matching_edges = [
            (u, v, data) for u, v, data in current_graph.edges(data=True) if query in u or query in v or query in data.get('flow_type', '')
        ]
        if matching_edges:
            results = "\n".join([f"{u} -> {v}: {data['flow_type']}" for u, v, data in matching_edges])
            messagebox.showinfo("Search Results", f"Matching Flows:\n{results}")
        else:
            messagebox.showinfo("Search Results", "No matches found.")

# Function to detect anomalies
def detect_anomalies(dataframe):
    anomalies = []

    for idx, row in dataframe.iterrows():
        source = row['Source']
        sink = row['Sink']
        flow_type = row['Flow Type']

        # Rule 1: Unexpected Source-Sink combinations
        if source.lower().startswith("untrusted") and sink.lower().startswith("sensitive"):
            anomalies.append(f"Anomaly: Data from untrusted source '{source}' to sensitive sink '{sink}'.")

        # Rule 2: Sensitive data transmitted in plaintext
        if "plaintext" in flow_type.lower() and "sensitive" in sink.lower():
            anomalies.append(f"Anomaly: Sensitive data transmitted in plaintext from '{source}' to '{sink}'.")

    return anomalies

# Function to show anomalies
def show_anomalies(dataframe):
    if dataframe is None:
        messagebox.showerror("Error", "No data loaded. Please load a CSV file first.")
        return

    anomalies = detect_anomalies(dataframe)

    if not anomalies:
        messagebox.showinfo("No Anomalies", "No anomalies detected in the data.")
        return

    # Display anomalies in a new window
    anomalies_window = Toplevel()
    anomalies_window.title("Detected Anomalies")
    anomalies_window.geometry("400x300")

    text_area = Text(anomalies_window, wrap='word', font=("Helvetica", 12))
    text_area.pack(expand=1, fill='both')
    scrollbar = Scrollbar(anomalies_window, command=text_area.yview)
    scrollbar.pack(side="right", fill="y")
    text_area['yscrollcommand'] = scrollbar.set

    for anomaly in anomalies:
        text_area.insert(END, f"{anomaly}\n\n")

    Button(anomalies_window, text="Close", command=anomalies_window.destroy).pack(pady=10)

# Create the GUI
def create_gui():
    root = Tk()
    root.title("IoT Data Flow Visualizer")

    Label(root, text="IoT Data Flow Visualizer", font=("Helvetica", 16, "bold")).pack(pady=10)
    Label(root, text="Load a CSV file containing 'Source', 'Sink', and 'Flow Type' columns.").pack(pady=5)

    Button(root, text="Load CSV", command=load_csv, width=20, bg="lightblue").pack(pady=10)
    Button(root, text="Show Insights", command=show_insights, width=20).pack(pady=5)
    Button(root, text="Search Graph", command=search_graph, width=20).pack(pady=5)
    Button(root, text="Detect Anomalies", 
           command=lambda: show_anomalies(loaded_data) if loaded_data is not None else messagebox.showerror("Error", "No data loaded."), 
           width=20, bg="orange").pack(pady=5)
    Button(root, text="Quit", command=root.quit, width=20, bg="lightcoral").pack(pady=10)

    root.geometry("400x200")
    root.mainloop()

# Run the GUI
if __name__ == "__main__":
    create_gui()
