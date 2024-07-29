# MeshCoin-Project

Project Overview

The primary objective of this simulation is to provide insights into how mesh networks can support offline CBDC transactions, ensuring secure, efficient, and reliable payment processing without continuous internet connectivity.

Features

- Consensus Threshold Analysis: Evaluate the impact of different consensus thresholds on transaction success rates and verification times.
- Node Configuration Testing: Simulate network configurations with varying numbers of nodes to understand scalability and performance.
- Latency and Throughput Measurement: Measure the transaction latency and throughput to assess network performance under different conditions.
- Double Spending Detection: Analyze the efficiency of double spending detection mechanisms in offline scenarios.
- Energy Consumption Analysis: Evaluate the energy consumption of nodes during transaction processing to ensure sustainable operations.
- 
Simulation Scripts

- mesh_experiment.py: Main script to set up and run the mesh network simulation.
- mesh_experiment_results_10_nodes.py: Script containing results and analysis for a 10-node configuration.
Getting Started
Prerequisites
- Python 3.x
- Mininet
- Required Python libraries: numpy, matplotlib, networkx

Installation
1- Clone the repository:
git clone https://github.com/yourusername/mesh-network-simulation.git
cd mesh-network-simulation

2-Install Mininet:
Follow the official Mininet installation guide:https://mininet.org/ 

3-Install the required Python libraries:

pip install numpy matplotlib networkx

Running the Simulation
To run the main simulation script: 

sudo python mesh_experiment.py
To view the results for the 10-node configuration:
python mesh_experiment_results_10_nodes.py

Note: Running the Mininet simulations requires sudo privileges.
Results
The results of the simulation include detailed analysis of transaction success rates, verification times, double spending detection efficiency, and energy consumption metrics. The findings are visualized using graphs and charts to provide a clear understanding of the network performance.

Contribution
Contributions to the project are welcome. If you have any suggestions, improvements, or bug fixes, please feel free to open an issue or submit a pull request.

License
This project is licensed under the MIT License. 
Contact
For any questions or inquiries, please contact olivieratangana57@gmail.com.
