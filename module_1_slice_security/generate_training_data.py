"""
generate_training_data.py
Generates synthetic 5G network slice traffic data (normal vs DDoS patterns)
for training the Slice Security DDoS classifier.

Run: python generate_training_data.py
Output: training_data.csv
"""

import numpy as np
import pandas as pd

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

N_NORMAL = 4000
N_DDOS = 1000


def generate_normal_traffic(n):
    """Normal 5G slice traffic: steady packet rate, moderate bandwidth,
    a reasonable spread of unique source IPs."""
    packet_rate = np.random.normal(loc=1200, scale=250, size=n).clip(min=50)
    bandwidth_mbps = np.random.normal(loc=80, scale=15, size=n).clip(min=5)
    unique_ips = np.random.normal(loc=300, scale=60, size=n).clip(min=10)
    syn_ratio = np.random.uniform(0.05, 0.25, size=n)  # normal SYN/total ratio
    avg_packet_size = np.random.normal(loc=512, scale=80, size=n).clip(min=64)
    label = np.zeros(n, dtype=int)
    return packet_rate, bandwidth_mbps, unique_ips, syn_ratio, avg_packet_size, label


def generate_ddos_traffic(n):
    """DDoS pattern: packet rate spikes, bandwidth saturates, fewer unique
    source IPs relative to volume (botnet amplification), high SYN ratio,
    smaller average packet size (flood packets)."""
    packet_rate = np.random.normal(loc=15000, scale=4000, size=n).clip(min=3000)
    bandwidth_mbps = np.random.normal(loc=480, scale=90, size=n).clip(min=150)
    unique_ips = np.random.normal(loc=120, scale=40, size=n).clip(min=5)
    syn_ratio = np.random.uniform(0.55, 0.95, size=n)
    avg_packet_size = np.random.normal(loc=96, scale=30, size=n).clip(min=40)
    label = np.ones(n, dtype=int)
    return packet_rate, bandwidth_mbps, unique_ips, syn_ratio, avg_packet_size, label


def main():
    normal = generate_normal_traffic(N_NORMAL)
    ddos = generate_ddos_traffic(N_DDOS)

    columns = ["packet_rate", "bandwidth_mbps", "unique_ips", "syn_ratio",
               "avg_packet_size", "label"]

    df_normal = pd.DataFrame(dict(zip(columns, normal)))
    df_ddos = pd.DataFrame(dict(zip(columns, ddos)))

    df = pd.concat([df_normal, df_ddos], ignore_index=True)
    df = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

    df.to_csv("training_data.csv", index=False)
    print(f"Generated {len(df)} rows -> training_data.csv")
    print(df["label"].value_counts().rename({0: "normal", 1: "ddos"}))


if __name__ == "__main__":
    main()
