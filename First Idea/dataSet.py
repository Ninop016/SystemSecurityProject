import pandas as pd
import random

# Define parameters
num_records = 1000  # Number of data flow records
sources = [f"Device{i}" for i in range(1, 51)]  # 50 devices
sinks = [f"Service{i}" for i in range(1, 31)]  # 30 services
flow_types = ['Type1', 'Type2', 'Type3', 'Type4', 'Type5']

# Generate random data flows
data = []
for _ in range(num_records):
    source = random.choice(sources)
    sink = random.choice(sinks)
    flow_type = random.choice(flow_types)
    data.append({'Source': source, 'Sink': sink, 'Flow Type': flow_type})

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('dataset.csv', index=False)
print("Dataset created and saved as large_dataset.csv")
