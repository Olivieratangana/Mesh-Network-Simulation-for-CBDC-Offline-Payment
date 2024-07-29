from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import random
import time
import matplotlib.pyplot as plt

def mesh_network(num_nodes):
    net = Mininet(controller=Controller, link=TCLink)
    
    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Adding hosts\n')
    hosts = [net.addHost(f'h{i}') for i in range(1, num_nodes + 1)]
    
    info('*** Creating links\n')
    for i in range(len(hosts)):
        for j in range(i + 1, len(hosts)):
            net.addLink(hosts[i], hosts[j], bw=10)
    
    info('*** Starting network\n')
    net.start()
    
    return net, hosts

def stop_network(net):
    info('*** Stopping network\n')
    net.stop()

def decrypt_and_verify(credential):
    # Simulate decryption and verification
    return random.choice([True, False])

def send_credentials(hosts, credential):
    results = {}
    for host in hosts:
        result = decrypt_and_verify(credential)
        results[host] = result
    return results

def consensus(results, threshold):
    accept_count = sum(results.values())
    return accept_count >= threshold

def run_experiment(num_nodes, thresholds, iterations):
    success_rates = []
    failure_rates = []
    avg_verification_times = []
    threshold_impact = []

    for threshold in thresholds:
        success_count = 0
        fail_count = 0
        total_verification_time = 0

        net, hosts = mesh_network(num_nodes)
        host_names = [f'h{i}' for i in range(1, num_nodes + 1)]

        for _ in range(iterations):
            credential = "encrypted_credential"
            
            start_time = time.time()
            results = send_credentials(host_names, credential)
            end_time = time.time()

            total_verification_time += (end_time - start_time)

            if consensus(results, threshold):
                success_count += 1
            else:
                fail_count += 1

        stop_network(net)
        
        success_rate = success_count / iterations
        failure_rate = fail_count / iterations
        avg_verification_time = total_verification_time / iterations

        success_rates.append(success_rate)
        failure_rates.append(failure_rate)
        avg_verification_times.append(avg_verification_time)
        threshold_impact.append((threshold, success_rate, failure_rate))

    return success_rates, failure_rates, avg_verification_times, threshold_impact

def plot_results(num_nodes, thresholds, success_rates, failure_rates, avg_verification_times, threshold_impact):
    plt.figure(figsize=(14, 8))

    # Success rate
    plt.subplot(2, 2, 1)
    plt.plot(thresholds, success_rates, marker='o')
    plt.title(f'Success Rate for {num_nodes} Nodes')
    plt.xlabel('Consensus Threshold')
    plt.ylabel('Success Rate')

    # Failure rate
    plt.subplot(2, 2, 2)
    plt.plot(thresholds, failure_rates, marker='o', color='red')
    plt.title(f'Failure Rate for {num_nodes} Nodes')
    plt.xlabel('Consensus Threshold')
    plt.ylabel('Failure Rate')

    # Average verification time
    plt.subplot(2, 2, 3)
    plt.plot(thresholds, avg_verification_times, marker='o', color='green')
    plt.title(f'Average Verification Time for {num_nodes} Nodes')
    plt.xlabel('Consensus Threshold')
    plt.ylabel('Verification Time (s)')

    # Impact of threshold on success/failure rates
    plt.subplot(2, 2, 4)
    success_rates = [rate for _, rate, _ in threshold_impact]
    failure_rates = [rate for _, _, rate in threshold_impact]
    plt.plot(thresholds, success_rates, label='Success Rate', marker='o')
    plt.plot(thresholds, failure_rates, label='Failure Rate', marker='x', color='red')
    plt.title(f'Impact of Consensus Threshold for {num_nodes} Nodes')
    plt.xlabel('Consensus Threshold')
    plt.ylabel('Rate')
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    setLogLevel('info')
    node_sizes = [10, 50, 100]
    thresholds = [3, 4, 5, 6, 7, 8]  # Example thresholds
    iterations = 100  # Number of iterations per configuration

    for num_nodes in node_sizes:
        success_rates, failure_rates, avg_verification_times, threshold_impact = run_experiment(num_nodes, thresholds, iterations)
        plot_results(num_nodes, thresholds, success_rates, failure_rates, avg_verification_times, threshold_impact)
