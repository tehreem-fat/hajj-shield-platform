"""
heatmap_generator.py
Generates a color-coded Folium heatmap of crowd density across Hajj zones
(Mataf, Masa'a, Jamarat, King Fahd Gate). Produces a standalone HTML file
that can be opened in any browser or embedded in the dashboard.
"""

import folium
import pandas as pd

from sensor_simulator import ZONES

RISK_COLORS = {
    "GREEN": "#2ecc71",
    "YELLOW": "#f1c40f",
    "RED": "#e74c3c",
}


def build_heatmap(zone_status: dict, output_path="haram_heatmap.html"):
    """
    zone_status: dict like
        {"Mataf": {"risk_level": "GREEN", "density_score": 76, "people_count": 3800}, ...}
    """
    center_lat = sum(z["lat"] for z in ZONES.values()) / len(ZONES)
    center_lon = sum(z["lon"] for z in ZONES.values()) / len(ZONES)

    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=17, tiles="CartoDB positron")

    for zone_name, meta in ZONES.items():
        status = zone_status.get(zone_name, {})
        risk = status.get("risk_level", "GREEN")
        color = RISK_COLORS.get(risk, "#3498db")
        density = status.get("density_score", 0)
        people = status.get("people_count", 0)

        popup_html = (
            f"<b>{zone_name.replace('_', ' ')}</b><br>"
            f"Risk: <b style='color:{color}'>{risk}</b><br>"
            f"Density score: {density}<br>"
            f"People count: {people}<br>"
            f"Capacity: {meta['capacity']}"
        )

        folium.Circle(
            location=[meta["lat"], meta["lon"]],
            radius=60 + (density * 1.2 if density else 60),
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.45,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{zone_name.replace('_', ' ')} — {risk}",
        ).add_to(fmap)

        folium.Marker(
            location=[meta["lat"], meta["lon"]],
            icon=folium.DivIcon(html=f"""<div style="font-size:11px;font-weight:600;
                color:#222;text-shadow:0 0 3px #fff;">{zone_name.replace('_', ' ')}</div>"""),
        ).add_to(fmap)

    legend_html = """
    <div style="position: fixed; bottom: 30px; left: 30px; z-index: 9999;
                background: white; padding: 10px 14px; border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.25); font-family: sans-serif; font-size: 13px;">
        <b>Zone Risk</b><br>
        <span style="color:#2ecc71;">●</span> Green — Safe<br>
        <span style="color:#f1c40f;">●</span> Yellow — Warning<br>
        <span style="color:#e74c3c;">●</span> Red — Critical
    </div>
    """
    fmap.get_root().html.add_child(folium.Element(legend_html))

    fmap.save(output_path)
    print(f"Heatmap saved -> {output_path}")
    return output_path


if __name__ == "__main__":
    # Example status snapshot (would normally come from anomaly_detector.py output)
    example_status = {
        "Mataf": {"risk_level": "GREEN", "density_score": 76, "people_count": 3800},
        "Masa_a": {"risk_level": "YELLOW", "density_score": 82, "people_count": 12300},
        "Jamarat": {"risk_level": "RED", "density_score": 108, "people_count": 8600},
        "King_Fahd_Gate": {"risk_level": "GREEN", "density_score": 60, "people_count": 1800},
    }
    build_heatmap(example_status)
