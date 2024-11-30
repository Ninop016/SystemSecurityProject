import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog, Button, Label, messagebox
import os

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

# Create the GUI
def create_gui():
    root = Tk()
    root.title("IoT Data Flow Visualizer")

    Label(root, text="IoT Data Flow Visualizer", font=("Helvetica", 16, "bold")).pack(pady=10)
    Label(root, text="Load a CSV file containing 'Source', 'Sink', and 'Flow Type' columns.").pack(pady=5)

    Button(root, text="Load CSV", command=load_csv, width=20, bg="lightblue").pack(pady=10)
    Button(root, text="Quit", command=root.quit, width=20, bg="lightcoral").pack(pady=10)

    root.geometry("400x200")
    root.mainloop()

# Run the GUI
if __name__ == "__main__":
    create_gui()
