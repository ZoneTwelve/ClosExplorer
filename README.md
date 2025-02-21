# Clos network topology explorer

## Overview
Clos Network Topology Explorer is a web-based tool designed to generate and visualize Clos network topologies. It allows users to specify network parameters such as the number of servers, oversubscription ratio, bandwidth per server, and topology tiers, then generates possible network configurations based on available switch models.

<img src="https://github.com/user-attachments/assets/4043777e-b862-453e-95dc-df97ace0d93f" width="512" alt="Screenshot">

## Features
- **Dynamic Topology Generation:** Automatically computes optimal configurations for given network constraints.
- **Graph Visualization:** Generates network topology diagrams using Graphviz.
- **Cost Estimation:** Calculates total infrastructure costs based on switch selection.
- **Multi-Tier Support:** Supports 1-tier, 2-tier (Spine-Leaf), and 3-tier (Leaf-Spine-Superspine) architectures.
- **Web-Based Interface:** User-friendly form input and result display.

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3
- Flask (`pip install flask`)
- Graphviz (`pip install graphviz`)

### Setup
1. Clone this repository:
   ```bash
   git clone https://github.com/ZoneTwelve/clos-network-explorer.git
   cd clos-network-explorer
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Open a web browser and navigate to `http://127.0.0.1:5000/`

## Usage
1. Enter the required network parameters in the web interface.
2. Click **Generate Topologies**.
3. View generated network configurations along with cost estimation.
4. Download topology diagrams if needed.

## File Structure
```
clos-network-explorer/
│── app.py               # Main application logic
│── requirements.txt     # Dependencies list
│── static/              # Directory for storing generated topology images
│── templates/
│   └── index.html       # Web interface template
└── README.md            # Project documentation
```

## Contributing
Feel free to contribute by submitting issues or pull requests!

## License
This project is licensed under the Apache 2.0 License.
