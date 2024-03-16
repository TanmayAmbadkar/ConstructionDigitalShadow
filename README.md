# Construction Digital Shadow

## Overview
Construction Digital Shadow is a project that aims to create a digital shadow for steel structure construction. It generates a graph data model using the IFC data schema to map the IFC entities into a directed graph, which holds the steel structure member entities and the relations between them based on structural connections and schedule preferences. This serves as a virtual replica of a steel structure that can be used for planning and monitoring purposes.

## Features
1. Generate load path graph from ifc files for visualization and planning of construction sequence
2. Check if construction sequence follows load path to ensure no problems during construction
3. Consistent and clear naming scheme of beams and columns
4. Web app to monitor progress of construction
5. Generate an IFC file to mimic construction for shadowing construction in a digital environment (VR/AR)

## Requirements
- NetworkX
- IfcOpenShell
- Streamlit
- pandas
- NumPy

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/construction-digital-shadow.git
    cd construction-digital-shadow
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
### Planning Phase
1. Set the `config.py` file, where the flag must be set to `False` to run the script in the planning phase.
2. Run `ifc_parser.py` to create the load path graph:
    ```bash
    python ifc_parser.py
    ```
3. Visualize the graph by running the Streamlit web app in `progress_check.py`:
    ```bash
    streamlit run progress_check.py
    ```

### Construction Phase
1. Set the `config.py` flag to `True` to enable the construction phase.
2. The contractor provides a sequence using Primavera software, which is converted to a CSV and placed in the root folder.
3. Run `ifc_parser.py` again to create the progress monitoring graph.
4. Run the Streamlit web app to monitor progress:
    ```bash
    streamlit run progress_check.py
    ```

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License
This project is licensed under the [MIT License](LICENSE).
