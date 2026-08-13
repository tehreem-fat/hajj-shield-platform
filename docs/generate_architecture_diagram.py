"""
generate_architecture_diagram.py
Generates docs/architecture.png — a clean box diagram of the HAJJ-SHIELD
6-module architecture, matching the README's ASCII diagram.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

BG = "#0A1210"
PANEL = "#132420"
LINE = "#2E9C6E"
SAND = "#C9A84C"
TEXT = "#EDEFEA"
TEXT_MID = "#9FB0A9"

fig, ax = plt.subplots(figsize=(12, 7.5), facecolor=BG)
ax.set_facecolor(BG)
ax.set_xlim(0, 12)
ax.set_ylim(0, 8)
ax.axis("off")

# Outer container
outer = FancyBboxPatch((0.3, 0.3), 11.4, 7.2, boxstyle="round,pad=0.02,rounding_size=0.15",
                        linewidth=1.5, edgecolor=SAND, facecolor="none")
ax.add_patch(outer)
ax.text(6, 7.15, "HAJJ-SHIELD PLATFORM", ha="center", fontsize=16, color=SAND,
        fontweight="bold", family="monospace")

modules = [
    ("Module 1\n5G Slice\nSecurity", 0.9),
    ("Module 2\nAI Crowd\nAnomaly Detector", 3.2),
    ("Module 3\nEmergency Alert\nValidator", 5.5),
    ("Module 4\nPilgrim\nPrivacy Shield", 7.8),
]

box_w, box_h, box_y = 2.0, 1.5, 4.7

for label, x in modules:
    box = FancyBboxPatch((x, box_y), box_w, box_h, boxstyle="round,pad=0.02,rounding_size=0.1",
                          linewidth=1.3, edgecolor=LINE, facecolor=PANEL)
    ax.add_patch(box)
    ax.text(x + box_w / 2, box_y + box_h / 2, label, ha="center", va="center",
            fontsize=10, color=TEXT, family="sans-serif", fontweight="medium")

# Central Dashboard box
dash_x, dash_y, dash_w, dash_h = 4.6, 1.6, 2.8, 1.4
dash = FancyBboxPatch((dash_x, dash_y), dash_w, dash_h, boxstyle="round,pad=0.02,rounding_size=0.1",
                       linewidth=1.6, edgecolor=SAND, facecolor="#1A2E27")
ax.add_patch(dash)
ax.text(dash_x + dash_w / 2, dash_y + dash_h / 2 + 0.15, "Central Dashboard",
        ha="center", va="center", fontsize=11, color=SAND, fontweight="bold")
ax.text(dash_x + dash_w / 2, dash_y + dash_h / 2 - 0.22, "(Grafana / HTML)",
        ha="center", va="center", fontsize=9, color=TEXT_MID, family="monospace")

# Connector lines from each module down to the dashboard
for label, x in modules:
    mod_center_x = x + box_w / 2
    mod_bottom_y = box_y
    dash_top_y = dash_y + dash_h
    dash_center_x = dash_x + dash_w / 2
    ax.plot([mod_center_x, mod_center_x, dash_center_x, dash_center_x],
            [mod_bottom_y, mod_bottom_y - 0.35, dash_top_y + 0.35, dash_top_y],
            color=LINE, linewidth=1.1, alpha=0.7)

# Module 6 demo scenario note at bottom
ax.text(6, 0.75, "Module 6 — Demo Scenario: Hajj Day 3 Emergency Drill (ties all modules together)",
        ha="center", fontsize=9.5, color=TEXT_MID, family="monospace", style="italic")

plt.tight_layout()
plt.savefig("architecture.png", dpi=180, facecolor=BG, bbox_inches="tight")
print("Saved architecture.png")
