import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog, Button, Label, messagebox, Menu, Toplevel, Text, Scrollbar, END, simpledialog
import os
import json

# Function to load CSV file
def load_csv():
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    if file_path:
        try:
            data = pd.read_csv(file_path)
            if not {"Source", "Sink", "Flow Type"}.issubset(data.columns):
                raise ValueError("CSV must contain 'Source', 'Sink', and 'Flow Type' columns.")
            visualize_data_flows(data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file: {e}")

# Function to filter data
def filter_data(data):
    filter_window = Toplevel()
    filter_window.title("Filter Data")
    filter_window.geometry("400x200")

    Label(filter_window, text="Filter By:").pack(pady=5)
    Label(filter_window, text="Enter Source, Sink, or Flow Type:").pack(pady=5)
    filter_entry = Text(filter_window, height=2, width=30)
    filter_entry.pack(pady=5)

    def apply_filter():
        filter_value = filter_entry.get("1.0", END).strip()
        if filter_value:
            filtered_data = data[
                (data['Source'].str.contains(filter_value, case=False, na=False)) |
                (data['Sink'].str.contains(filter_value, case=False, na=False)) |
                (data['Flow Type'].str.contains(filter_value, case=False, na=False))
            ]
            visualize_data_flows(filtered_data)
        filter_window.destroy()

    Button(filter_window, text="Apply Filter", command=apply_filter, width=15).pack(pady=10)

# Function to save and load graph configurations
def save_graph_config(G):
    save_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
    )
    if save_path:
        nx.write_graphml(G, save_path)
        messagebox.showinfo("Success", f"Configuration saved as: {save_path}")

def load_graph_config():
    file_path = filedialog.askopenfilename(
        filetypes=[("GraphML Files", "*.graphml"), ("All Files", "*.*")]
    )
    if file_path:
        try:
            G = nx.read_graphml(file_path)
            plt.figure(figsize=(10, 6))
            pos = nx.spring_layout(G)
            nx.draw(G, pos, with_labels=True, node_size=2000, node_color="skyblue")
            edge_labels = nx.get_edge_attributes(G, 'flow_type')
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)
            plt.title("Loaded Data Flow Graph", fontsize=14, fontweight="bold")
            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {e}")

# Function to visualize data flows
def visualize_data_flows(dataframe):
    G = nx.DiGraph()  # Directed graph to show flow direction

    # Add nodes and edges with flow type as edge labels
    for idx, row in dataframe.iterrows():
        G.add_edge(row['Source'], row['Sink'], flow_type=row['Flow Type'])

    # Draw the graph
    pos = nx.spring_layout(G)  # Layout for better visualization
    plt.figure(figsize=(10, 6))
    nx.draw(
        G, pos, with_labels=True, node_size=2000, node_color="skyblue",
        font_size=10, font_weight="bold", edge_color="gray"
    )

    # Add edge labels
    edge_labels = {(row['Source'], row['Sink']): row['Flow Type'] for _, row in dataframe.iterrows()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)

    plt.title("Sensitive Data Flows in IoT Apps", fontsize=14, fontweight="bold")
    
    # Save the graph as an image
    save_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")]
    )
    if save_path:
        plt.savefig(save_path)
        messagebox.showinfo("Success", f"Graph saved as: {save_path}")
    plt.show()

# Function to display additional insights
def show_insights(data):
    insights = Toplevel()
    insights.title("Data Insights")
    insights.geometry("400x300")

    text_area = Text(insights, wrap='word', font=("Helvetica", 12))
    text_area.pack(expand=1, fill='both')
    scrollbar = Scrollbar(insights, command=text_area.yview)
    scrollbar.pack(side="right", fill="y")
    text_area['yscrollcommand'] = scrollbar.set

    # Generate insights
    most_common_source = data['Source'].mode().iloc[0]
    most_common_sink = data['Sink'].mode().iloc[0]
    most_common_flow = data['Flow Type'].mode().iloc[0]
    total_flows = len(data)

    insights_text = f"""
    Total Data Flows: {total_flows}
    Most Common Source: {most_common_source}
    Most Common Sink: {most_common_sink}
    Most Common Flow Type: {most_common_flow}
    """
    text_area.insert(END, insights_text)

# Function to search the graph
def search_graph(G):
    query = simpledialog.askstring("Search Graph", "Enter a node or flow type to search:")
    if query:
        matching_edges = [
            (u, v, data) for u, v, data in G.edges(data=True) if query in u or query in v or query in data.get('flow_type', '')
        ]
        if matching_edges:
            results = "\n".join([f"{u} -> {v}: {data['flow_type']}" for u, v, data in matching_edges])
            messagebox.showinfo("Search Results", f"Matching Flows:\n{results}")
        else:
            messagebox.showinfo("Search Results", "No matches found.")

# Function to add a help section
def show_help():
    help_window = Toplevel()
    help_window.title("Help")
    help_text = """
    1. Load a CSV file containing 'Source', 'Sink', and 'Flow Type' columns.
    2. Use the Filter Data option to filter by specific criteria.
    3. Save graph configurations for later use.
    4. Load previously saved graph configurations.
    5. Export the graph in JSON or GraphML formats.
    """
    Label(help_window, text="Help Section", font=("Helvetica", 16, "bold")).pack(pady=10)
    Text(help_window, wrap='word', height=10, width=50).pack(pady=5)

# Create the GUI
def create_gui():
    root = Tk()
    root.title("IoT Data Flow Visualizer")

    Label(root, text="IoT Data Flow Visualizer", font=("Helvetica", 16, "bold")).pack(pady=10)
    Label(root, text="Load a CSV file containing 'Source', 'Sink', and 'Flow Type' columns.").pack(pady=5)

    Button(root, text="Load CSV", command=load_csv, width=20, bg="lightblue").pack(pady=10)
    Button(root, text="Show Insights", command=lambda: show_insights(), width=20).pack(pady=5)
    Button(root, text="Search Graph", command=lambda: search_graph(), width=20).pack(pady=5)
    Button(root, text="Quit", command=root.quit, width=20, bg="lightcoral").pack(pady=10)

    root.geometry("400x200")
    root.mainloop()

# Run the GUI
if __name__ == "__main__":
    create_gui()
