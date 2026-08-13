"""
sensor_simulator.py
Simulates 5G-connected IoT sensor readings (crowd density, movement speed)
across key Hajj zones around the Haram.
"""

import numpy as np
import pandas as pd

RANDOM_SEED = 7
np.random.seed(RANDOM_SEED)

ZONES = {
    "Mataf": {"lat": 21.4225, "lon": 39.8262, "capacity": 5000},
    "Masa_a": {"lat": 21.4227, "lon": 39.8268, "capacity": 15000},
    "Jamarat": {"lat": 21.4240, "lon": 39.8300, "capacity": 8000},
    "King_Fahd_Gate": {"lat": 21.4210, "lon": 39.8240, "capacity": 3000},
}


def _density_score(people_count, capacity):
    """0-100 score based on occupancy ratio, clipped."""
    ratio = people_count / capacity
    return float(np.clip(ratio * 100, 0, 130))


def generate_baseline_readings(n_per_zone=200):
    """Normal, gently fluctuating crowd levels — 60-85% of capacity."""
    rows = []
    for zone, meta in ZONES.items():
        occupancy_ratio = np.random.uniform(0.55, 0.85, size=n_per_zone)
        people_count = (occupancy_ratio * meta["capacity"]).astype(int)
        movement_speed = np.random.normal(loc=0.9, scale=0.15, size=n_per_zone).clip(min=0.2)
        for pc, ms in zip(people_count, movement_speed):
            rows.append({
                "zone": zone,
                "people_count": int(pc),
                "movement_speed_avg": round(float(ms), 2),
                "density_score": round(_density_score(pc, meta["capacity"]), 1),
            })
    return pd.DataFrame(rows)


def generate_surge_event(zone="Jamarat", n=15):
    """A sudden crowd surge: occupancy exceeds capacity, movement slows to a crawl."""
    meta = ZONES[zone]
    occupancy_ratio = np.random.uniform(1.05, 1.35, size=n)
    people_count = (occupancy_ratio * meta["capacity"]).astype(int)
    movement_speed = np.random.uniform(0.1, 0.35, size=n)
    rows = []
    for pc, ms in zip(people_count, movement_speed):
        rows.append({
            "zone": zone,
            "people_count": int(pc),
            "movement_speed_avg": round(float(ms), 2),
            "density_score": round(_density_score(pc, meta["capacity"]), 1),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    baseline = generate_baseline_readings()
    surge = generate_surge_event()
    all_data = pd.concat([baseline, surge], ignore_index=True)
    all_data.to_csv("sensor_data.csv", index=False)
    print(f"Generated {len(all_data)} sensor readings -> sensor_data.csv")
    print(all_data.groupby("zone")["density_score"].describe())
