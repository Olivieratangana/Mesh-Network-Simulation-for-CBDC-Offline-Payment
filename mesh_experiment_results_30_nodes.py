# -*- coding: utf-8 -*-

from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import time
import random
import uuid
import hashlib
import csv
from prometheus_client import start_http_server, Summary, Counter, Gauge, REGISTRY

# Check if the metric is already registered to avoid duplication
def get_or_create_metric(metric_type, name, documentation, labelnames=(), namespace='', subsystem='', unit=''):
    if name not in REGISTRY._names_to_collectors:
        if metric_type == 'Summary':
            return Summary(name, documentation)
        elif metric_type == 'Counter':
            return Counter(name, documentation)
        elif metric_type == 'Gauge':
            return Gauge(name, documentation)
    return REGISTRY._names_to_collectors[name]

#  Prometheus metrics initialization
TRANSACTION_TIME = get_or_create_metric('Summary', 'transaction_processing_seconds', 'Time spent processing a transaction')
DOUBLE_SPENDING_TIME = get_or_create_metric('Summary', 'double_spending_detection_seconds', 'Time spent detecting double spending')
TRANSACTIONS = get_or_create_metric('Counter', 'transactions_total', 'Total number of transactions')
SUCCESSFUL_TRANSACTIONS = get_or_create_metric('Counter', 'successful_transactions_total', 'Total number of successful transactions')
FAILED_TRANSACTIONS = get_or_create_metric('Counter', 'failed_transactions_total', 'Total number of failed transactions')
DOUBLE_SPENDING_DETECTIONS = get_or_create_metric('Gauge', 'double_spending_detection_gauge', 'Double spending detection time per transaction')

class EnergyModel:
    def __init__(self, base_power, power_per_packet):
        self.base_power = base_power
       self.power_per_packet = power_per_packet

    def estimate_energy(self, num_packets, processing_time):
        return self.base_power * processing_time + self.power_per_packet * num_packets

#  UTXO and Transaction classes definition
class UTXO:
   def __init__(self, amount, owner_public_key, serial_number=None, is_spent=False):
        self.amount = amount
        self.owner_public_key = owner_public_key
        self.serial_number = serial_number or str(uuid.uuid4())
        self.is_spent = is_spent

class Transaction:
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs
        self.timestamp = time.time()
        self.tx_id = str(uuid.uuid4())
        self.signature = None

    def sign(self, private_key):
        self.signature = hashlib.sha256(private_key.encode() + str(self.inputs).encode() + str(self.outputs).encode()).hexdigest()

def generate_key_pair():
    return str(uuid.uuid4()), str(uuid.uuid4())

def issue_utxo(amount, owner_public_key):
    print("Issuing UTXO with amount:", amount, "and owner_public_key:", owner_public_key)  # Debugging line
    return UTXO(amount, owner_public_key)

def verify_double_spending(transaction, pending_transactions):
    input_serial_numbers = [utxo.serial_number for utxo in transaction.inputs]
    for tx in pending_transactions:
        for utxo in tx.inputs:
            if utxo.serial_number in input_serial_numbers:
                return False
    return True

@TRANSACTION_TIME.time()
def transfer_funds(from_private_key, from_public_key, to_public_key, amount, utxos, pending_transactions, transactions, energy_model):
    alice_utxos = [utxo for utxo in utxos if utxo.owner_public_key == from_public_key and not utxo.is_spent]
    total_available = sum(utxo.amount for utxo in alice_utxos)
    
    if total_available < amount:
        FAILED_TRANSACTIONS.inc()
        return False, 0, 0
    
    spent_utxos = []
    remaining_amount = amount
    for utxo in alice_utxos:
        if remaining_amount <= 0:
            break
        utxo.is_spent = True
        spent_utxos.append(utxo)
        remaining_amount -= utxo.amount
    
    outputs = [UTXO(amount, to_public_key)]
    if remaining_amount < 0:
        outputs.append(UTXO(-remaining_amount, from_public_key))
    
    transaction = Transaction(spent_utxos, outputs)
    transaction.sign(from_private_key)
    
    start_double_spending_check = time.time()
    double_spending_check = verify_double_spending(transaction, pending_transactions)
    end_double_spending_check = time.time()
    
    double_spending_detection_time = end_double_spending_check - start_double_spending_check
    DOUBLE_SPENDING_DETECTIONS.set(double_spending_detection_time)
    
    energy_consumed = energy_model.estimate_energy(num_packets=len(transaction.inputs) + len(transaction.outputs), processing_time=end_double_spending_check - start_double_spending_check)
    
    if not double_spending_check:
        FAILED_TRANSACTIONS.inc()
        return False, double_spending_detection_time, energy_consumed
    
    pending_transactions.append(transaction)
    transactions.append(transaction)
    utxos.extend(outputs)
    SUCCESSFUL_TRANSACTIONS.inc()
    
    return True, double_spending_detection_time, energy_consumed

def mesh_network(num_nodes=30):
    net = Mininet(controller=RemoteController, link=TCLink)
    
    info('*** Adding controller\n')
    net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)

    info('*** Adding hosts\n')
    hosts = [net.addHost('h{}'.format(i)) for i in range(1, num_nodes + 1)]
    
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

def simulate_transactions(net, hosts):
    key_pairs = [generate_key_pair() for _ in hosts]
    print("Key pairs generated:", key_pairs)  # Debugging line
    utxos = [issue_utxo(1000, key_pairs[i][1]) for i in range(len(hosts))]
    pending_transactions = []
    transactions = []
    energy_model = EnergyModel(base_power=10, power_per_packet=0.05)

    success_count = 0
    fail_count = 0
    total_time = 0
    transaction_count = 100
    total_double_spending_detection_time = 0
    total_energy_consumed = 0

    for _ in range(transaction_count):
        from_host = random.choice(hosts)
        to_host = random.choice([host for host in hosts if host != from_host])
        from_private_key, from_public_key = key_pairs[hosts.index(from_host)]
        _, to_public_key = key_pairs[hosts.index(to_host)]
        
        start_time = time.time()
        success, double_spending_detection_time, energy_consumed = transfer_funds(from_private_key, from_public_key, to_public_key, random.randint(1, 50), utxos, pending_transactions, transactions, energy_model)
        end_time = time.time()
        
        total_time += (end_time - start_time)
        total_double_spending_detection_time += double_spending_detection_time
        total_energy_consumed += energy_consumed
        
        if success:
            success_count += 1
        else:
            fail_count += 1

    throughput = success_count / total_time
    latency = total_time / transaction_count
    average_double_spending_detection_time = total_double_spending_detection_time / transaction_count
    average_energy_consumed = total_energy_consumed / transaction_count

    print("Throughput: {} transactions/second".format(throughput))
    print("Latency: {} seconds/transaction".format(latency))
    print("Average Double Spending Detection Time: {} seconds".format(average_double_spending_detection_time))
    print("Average Energy Consumption: {} joules".format(average_energy_consumed))
    print("Success Rate: {}%".format(success_count / transaction_count * 100))
    print("Failure Rate: {}%".format(fail_count / transaction_count * 100))

    return success_count, fail_count, throughput, latency, average_double_spending_detection_time, average_energy_consumed

def save_results(results, filename):
    with open(filename, 'w') as csvfile:
        fieldnames = ["num_nodes", "success_count", "fail_count", "throughput", "latency", "average_double_spending_detection_time", "average_energy_consumed"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

if __name__ == '__main__':
    setLogLevel('info')
    start_http_server(8000)  # Start the HTTP server to expose Prometheus metrics
    results = []

    num_nodes = 30
    net, hosts = mesh_network(num_nodes)
    result = simulate_transactions(net, hosts)
    results.append({
        "num_nodes": num_nodes,
        "success_count": result[0],
        "fail_count": result[1],
        "throughput": result[2],
        "latency": result[3],
        "average_double_spending_detection_time": result[4],
        "average_energy_consumed": result[5]
    })
    stop_network(net)

    save_results(results, 'mesh_experiment_results_30_nodes.csv')
