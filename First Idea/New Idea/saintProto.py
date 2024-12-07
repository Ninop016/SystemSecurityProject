import os
import multiprocessing

def identify_sensitive_elements():
    """Identify sensitive sources and sinks."""
    sensitive_sources = ['input', 'readLine', 'get', 'post']  # Common Groovy input methods
    sensitive_sinks = ['println', 'send', 'write']  # Common Groovy output methods
    return sensitive_sources, sensitive_sinks

def perform_static_analysis(source_file, sensitive_sources, sensitive_sinks):
    """Perform static analysis to track sensitive data flows."""
    with open(source_file, 'r', encoding='utf-8') as file:
        content = file.read()

    data_flow_paths = []
    for source in sensitive_sources:
        if source in content:
            for sink in sensitive_sinks:
                if sink in content:
                    data_flow_paths.append((source, sink))

    return data_flow_paths

def generate_report(data_flow_paths, report_file):
    """Generate a detailed report on potential data leaks."""
    with open(report_file, 'w', encoding='utf-8') as file:
        if data_flow_paths:
            file.write("Potential sensitive data flows detected:\n\n")
            for path in data_flow_paths:
                file.write(f"Source: {path[0]} -> Sink: {path[1]}\n")
                file.write(f"Potential Risk: Sensitive data read by {path[0]} could be exposed through {path[1]}\n\n")
        else:
            file.write("No sensitive data flows detected.\n")
    print(f"Report generated: {report_file}")

def process_file(source_file, report_folder):
    """Process a single IoT application file."""
    sensitive_sources, sensitive_sinks = identify_sensitive_elements()
    data_flow_paths = perform_static_analysis(source_file, sensitive_sources, sensitive_sinks)
    report_file = os.path.join(report_folder, os.path.basename(source_file).replace('.groovy', '_report.txt'))
    generate_report(data_flow_paths, report_file)

def main():
    source_folder = 'SystemSecurityProject\smartThings\smartThings-SainT\smartThings-SainT-sensitive-data-leaks-benchmark-apps'  # Replace with your source folder path
    report_folder = 'SystemSecurityProject\smartThings\smartThings-SainT\smartThings-SainT-sensitive-data-leaks-benchmark-apps\Reports'  # Replace with your report folder path

    # Create the report folder if it doesn't exist
    os.makedirs(report_folder, exist_ok=True)

    files = [os.path.join(source_folder, f) for f in os.listdir(source_folder) if f.endswith('.groovy')]

    with multiprocessing.Pool() as pool:
        pool.starmap(process_file, [(file, report_folder) for file in files])

if __name__ == "__main__":
    main()
