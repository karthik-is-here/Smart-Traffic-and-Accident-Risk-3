import folium
import config


def _add_legend(m, colors, title):
    items = "".join(
        f'<div style="display:flex;align-items:center;gap:6px;margin:3px 0;">'
        f'<div style="width:12px;height:12px;border-radius:50%;background:{c};flex-shrink:0;"></div>'
        f'<span style="font-size:11px;color:#e0e0e0;">{level}</span></div>'
        for level, c in colors.items()
    )
    legend_html = (
        '<div style="position:absolute;bottom:20px;right:10px;z-index:9999;'
        'background:#111;border:1px solid #333;border-radius:8px;'
        'padding:10px 14px;min-width:130px;box-shadow:0 2px 12px rgba(0,0,0,0.5);">'
        f'<div style="font-size:10px;font-weight:700;color:#a3e635;'
        f'letter-spacing:1.5px;text-transform:uppercase;margin-bottom:7px;">{title}</div>'
        f'{items}</div>'
    )
    m.get_root().html.add_child(folium.Element(legend_html))


def create_congestion_map(predictions, area, tiles="CartoDB dark_matter"):
    if not predictions:
        lat, lon = 9.9975, 76.2900
    else:
        lat = sum(r["lat"] for r in predictions) / len(predictions)
        lon = sum(r["lon"] for r in predictions) / len(predictions)

    m = folium.Map(location=[lat, lon], zoom_start=14, tiles=tiles)

    for r in predictions:
        color  = config.CONGESTION_COLORS.get(r["congestion_level"], "#aaa")
        radius = {"Low":10,"Moderate":12,"High":15,"Very High":18}.get(r["congestion_level"], 10)

        popup_html = (
            '<div style="font-family:monospace;background:#111;color:#e0e0e0;'
            'padding:10px 12px;border-radius:6px;border:1px solid #333;min-width:180px;">'
            '<div style="font-size:12px;font-weight:700;color:#a3e635;margin-bottom:6px;">'
            + r["road_name"] +
            '</div>'
            '<div style="font-size:11px;line-height:1.8;">'
            'Level: <b style="color:' + color + '">' + r["congestion_level"] + '</b><br>'
            'Score: <b>' + str(r["congestion_score"]) + '%</b><br>'
            'Speed: <b>' + str(r["current_speed_kmph"]) + ' km/h</b><br>'
            'Type: ' + r["road_type"] + '<br>'
            'Limit: ' + str(r["speed_limit_kmph"]) + ' km/h'
            '</div></div>'
        )

        folium.CircleMarker(
            location=[r["lat"], r["lon"]],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            weight=2,
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"{r['road_name']} — {r['congestion_level']} ({r['congestion_score']}%)"
        ).add_to(m)

    _add_legend(m, config.CONGESTION_COLORS, "Congestion")
    return m


def create_risk_map(predictions, area, tiles="CartoDB dark_matter"):
    if not predictions:
        lat, lon = 9.9975, 76.2900
    else:
        lat = sum(r["lat"] for r in predictions) / len(predictions)
        lon = sum(r["lon"] for r in predictions) / len(predictions)

    m = folium.Map(location=[lat, lon], zoom_start=14, tiles=tiles)

    for r in predictions:
        color  = config.RISK_COLORS.get(r["accident_risk_level"], "#aaa")
        radius = {"Low":10,"Moderate":12,"High":15,"Very High":18}.get(r["accident_risk_level"], 10)

        popup_html = (
            '<div style="font-family:monospace;background:#111;color:#e0e0e0;'
            'padding:10px 12px;border-radius:6px;border:1px solid #333;min-width:180px;">'
            '<div style="font-size:12px;font-weight:700;color:#a3e635;margin-bottom:6px;">'
            + r["road_name"] +
            '</div>'
            '<div style="font-size:11px;line-height:1.8;">'
            'Risk: <b style="color:' + color + '">' + r["accident_risk_level"] + '</b><br>'
            'Score: <b>' + str(r["accident_risk_score"]) + '%</b><br>'
            'Rainfall: <b>' + str(r["rainfall_mm"]) + ' mm</b><br>'
            'Visibility: <b>' + str(r["visibility_m"]) + ' m</b><br>'
            'Weather: ' + r["weather_condition"]
            + '</div></div>'
        )

        folium.CircleMarker(
            location=[r["lat"], r["lon"]],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            weight=2,
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"{r['road_name']} — {r['accident_risk_level']} ({r['accident_risk_score']}%)"
        ).add_to(m)

    _add_legend(m, config.RISK_COLORS, "Risk Level")
    return m


def map_to_html(m):
    return m._repr_html_()
