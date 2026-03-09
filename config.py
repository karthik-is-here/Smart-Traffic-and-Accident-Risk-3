DAYS_OF_WEEK = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

WEATHER_OPTIONS = ["Clear","Cloudy","Light Rain","Heavy Rain","Fog"]

AREA_ROADS = {
    "Edappally": [
        "NH 66 Bypass","Edappally Junction","Seaport Airport Road",
        "Edappally Toll Junction","Rajagiri Road","Edappally North",
        "Konthuruthy Road","LuLu Mall Access Road"
    ],
    "Kakkanad": [
        "Kakkanad Main Road","Infopark Expressway","Infopark Road Phase 1",
        "Infopark Road Phase 2","Thrippunithura Road","CSEZ Road",
        "Kolenchery Road","High Court Road Kakkanad"
    ],
    "Fort Kochi": [
        "Beach Road Fort Kochi","Ridsdale Road","Calvathy Road","Tower Road",
        "Princess Street","Napier Street","Fort Kochi Ferry Road","Willingdon Island Road"
    ],
    "Mattancherry": [
        "Mattancherry Road","Jew Town Road","Bazaar Road","Pallipuram Road",
        "Dutch Cemetery Road","Thoppumpady Road","Mattancherry Palace Road","Harbour Road"
    ],
    "Vyttila": [
        "NH 66 Vyttila","Vyttila Junction","Kundannoor Bridge Road",
        "Vyttila Mobility Hub Road","Aroor Bypass","Chilavannoor Road",
        "Pachalam Road","SA Road Vyttila"
    ],
    "Palarivattom": [
        "Palarivattom Junction","NH 85 Palarivattom","Kaloor Palarivattom Rd",
        "Banerji Road","Vyttila Palarivattom Rd","Pullepady Road","Elamkulam Road"
    ],
    "Kadavanthra": [
        "Kadavanthra Junction","MG Road Kadavanthra","Shanmugham Road",
        "Sahodaran Ayyappan Road","Ravipuram Road","Chittoor Road",
        "Convent Road","Judges Avenue","Bristow Road","Kasturi Ranga Rd"
    ],
}

ROAD_COORDINATES = {
    # ── Edappally ── (verified: Edappally Junction = 10.02455, 76.30805 via Wikipedia)
    "NH 66 Bypass":              (10.0246, 76.3081),  # NH66 at Edappally Junction
    "Edappally Junction":        (10.0246, 76.3081),  # Wikipedia verified
    "Seaport Airport Road":      (10.0189, 76.3215),  # runs NE toward airport from Edappally
    "Edappally Toll Junction":   (10.0304, 76.3045),  # toll booth ~500m north on bypass
    "Rajagiri Road":             (10.0196, 76.3058),  # near Rajagiri college, west of bypass
    "Edappally North":           (10.0331, 76.3067),  # Kunnumpuram Jn, north of Edappally
    "Konthuruthy Road":          (10.0224, 76.3001),  # west of bypass toward backwaters
    "LuLu Mall Access Road":     (10.0257, 76.3115),  # LuLu Mall is just east of Edappally Jn

    # ── Kakkanad ── (Infopark ~10km east, near 10.022, 76.352)
    "Kakkanad Main Road":        (10.0217, 76.3402),  # Kakkanad civil station area
    "Infopark Expressway":       (10.0189, 76.3322),  # 4-lane road connecting SA Road to Infopark
    "Infopark Road Phase 1":     (10.0230, 76.3508),  # Phase 1 campus entrance
    "Infopark Road Phase 2":     (10.0302, 76.3574),  # Phase 2 campus, further NE
    "Thrippunithura Road":       (10.0089, 76.3398),  # toward Tripunithura from Kakkanad
    "CSEZ Road":                 (10.0248, 76.3452),  # Cochin SEZ, north of Infopark Ph1
    "Kolenchery Road":           (10.0142, 76.3361),  # south Kakkanad toward Kolenchery
    "High Court Road Kakkanad":  (10.0172, 76.3418),  # near District Court Kakkanad

    # ── Fort Kochi ── (peninsula, ~9.964, 76.243)
    "Beach Road Fort Kochi":     (9.9653,  76.2432),  # along waterfront, Fort Kochi beach
    "Ridsdale Road":             (9.9638,  76.2451),  # inland from beach
    "Calvathy Road":             (9.9621,  76.2463),  # near Calvathy church area
    "Tower Road":                (9.9668,  76.2418),  # near Chinese fishing nets
    "Princess Street":           (9.9643,  76.2446),  # main heritage street Fort Kochi
    "Napier Street":             (9.9631,  76.2458),  # parallel to Princess St
    "Fort Kochi Ferry Road":     (9.9675,  76.2404),  # near Fort Kochi ferry terminal
    "Willingdon Island Road":    (9.9598,  76.2675),  # Willingdon Island, SE of Fort Kochi

    # ── Mattancherry ── (~9.957, 76.259)
    "Mattancherry Road":         (9.9577,  76.2594),  # main road through Mattancherry
    "Jew Town Road":             (9.9561,  76.2603),  # Paradesi Synagogue street
    "Bazaar Road":               (9.9591,  76.2579),  # spice market area
    "Pallipuram Road":           (9.9538,  76.2617),  # south Mattancherry
    "Dutch Cemetery Road":       (9.9573,  76.2568),  # near Dutch cemetery
    "Thoppumpady Road":          (9.9514,  76.2648),  # toward Thoppumpady bridge
    "Mattancherry Palace Road":  (9.9556,  76.2592),  # Dutch Palace / Mattancherry Palace
    "Harbour Road":              (9.9604,  76.2557),  # along harbour north of Mattancherry

    # ── Vyttila ── (verified: Junction = 9°58'6"N 76°19'5"E = 9.96833, 76.31806)
    "NH 66 Vyttila":             (9.9683,  76.3181),  # NH66 at Vyttila flyover
    "Vyttila Junction":          (9.9683,  76.3181),  # Wikimapia verified
    "Kundannoor Bridge Road":    (9.9628,  76.3098),  # toward Kundannoor bridge, SW of Vyttila
    "Vyttila Mobility Hub Road": (9.9692,  76.3211),  # Hub is NE of junction (verified ~9°58'8"N 76°19'16"E)
    "Aroor Bypass":              (9.9541,  76.3065),  # NH66 south toward Aroor
    "Chilavannoor Road":         (9.9748,  76.3052),  # Chilavannoor backwaters area, NW of Vyttila
    "Pachalam Road":             (9.9771,  76.2981),  # Pachalam, west of Vyttila
    "SA Road Vyttila":           (9.9721,  76.3028),  # SA Road eastern end near Vyttila

    # ── Palarivattom ── (on NH66 bypass, between Edappally & Vyttila; ~10.002, 76.307)
    "Palarivattom Junction":     (10.0019, 76.3071),  # NH66 bypass signal junction
    "NH 85 Palarivattom":        (10.0022, 76.3089),  # NH85 starts here toward Kakkanad
    "Kaloor Palarivattom Rd":    (9.9973,  76.3002),  # road from Kaloor to Palarivattom
    "Banerji Road":              (9.9934,  76.2921),  # major arterial, central Ernakulam
    "Vyttila Palarivattom Rd":   (9.9851,  76.3036),  # connecting Vyttila to Palarivattom
    "Pullepady Road":            (9.9912,  76.2958),  # Pullepady junction area
    "Elamkulam Road":            (9.9871,  76.2946),  # Elamkulam metro station area

    # ── Kadavanthra ── (SA Road / Kaloor-Kadavanthra intersection ~9.9755, 76.2900)
    "Kadavanthra Junction":      (9.9757,  76.2901),  # Kadavanthra metro station junction
    "MG Road Kadavanthra":       (9.9813,  76.2884),  # MG Road near Ernakulam South
    "Shanmugham Road":           (9.9826,  76.2741),  # Marine Drive / Shanmugham Road
    "Sahodaran Ayyappan Road":   (9.9752,  76.2897),  # SA Road at Kadavanthra
    "Ravipuram Road":            (9.9795,  76.2863),  # Ravipuram, near Ernakulam Jn
    "Chittoor Road":             (9.9843,  76.2868),  # Chittoor Rd, central Ernakulam
    "Convent Road":              (9.9768,  76.2878),  # near Sacred Heart convent
    "Judges Avenue":             (9.9834,  76.2852),  # near High Court
    "Bristow Road":              (9.9781,  76.2831),  # near Ernakulam South station
    "Kasturi Ranga Rd":          (9.9818,  76.2909),  # near GCDA lawns
}

ROAD_PROPERTIES = {
    "NH 66 Bypass":              {"road_type": "Highway",  "lanes": 4, "speed_limit_kmph": 80},
    "Edappally Junction":        {"road_type": "Arterial", "lanes": 3, "speed_limit_kmph": 50},
    "Seaport Airport Road":      {"road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 60},
    "Edappally Toll Junction":   {"road_type": "Highway",  "lanes": 4, "speed_limit_kmph": 80},
    "Rajagiri Road":             {"road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    "Edappally North":           {"road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    "Konthuruthy Road":          {"road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    "LuLu Mall Access Road":     {"road_type": "Arterial", "lanes": 3, "speed_limit_kmph": 50},
    "Kakkanad Main Road":        {"road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 50},
    "Infopark Expressway":       {"road_type": "Arterial", "lanes": 3, "speed_limit_kmph": 60},
    "Infopark Road Phase 1":     {"road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 40},
    "Infopark Road Phase 2":     {"road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 40},
    "Thrippunithura Road":       {"road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 50},
    "CSEZ Road":                 {"road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    "Kolenchery Road":           {"road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    "High Court Road Kakkanad":  {"road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 50},
    "Beach Road Fort Kochi":     {"road_type": "Local",    "lanes": 2, "speed_limit_kmph": 30},
    "Ridsdale Road":             {"road_type": "Local",    "lanes": 1, "speed_limit_kmph": 30},
    "Calvathy Road":             {"road_type": "Local",    "lanes": 1, "speed_limit_kmph": 30},
    "Tower Road":                {"road_type": "Local",    "lanes": 1, "speed_limit_kmph": 30},
    "Princess Street":           {"road_type": "Local",    "lanes": 1, "speed_limit_kmph": 30},
    "Napier Street":             {"road_type": "Local",    "lanes": 1, "speed_limit_kmph": 30},
    "Fort Kochi Ferry Road":     {"road_type": "Local",    "lanes": 2, "speed_limit_kmph": 30},
    "Willingdon Island Road":    {"road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 50},
    "Mattancherry Road":         {"road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 40},
    "Jew Town Road":             {"road_type": "Local",    "lanes": 1, "speed_limit_kmph": 20},
    "Bazaar Road":               {"road_type": "Local",    "lanes": 2, "speed_limit_kmph": 30},
    "Pallipuram Road":           {"road_type": "Local",    "lanes": 2, "speed_limit_kmph": 30},
    "Dutch Cemetery Road":       {"road_type": "Local",    "lanes": 1, "speed_limit_kmph": 20},
    "Thoppumpady Road":          {"road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 40},
    "Mattancherry Palace Road":  {"road_type": "Local",    "lanes": 1, "speed_limit_kmph": 20},
    "Harbour Road":              {"road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 40},
    "NH 66 Vyttila":             {"road_type": "Highway",  "lanes": 4, "speed_limit_kmph": 70},
    "Vyttila Junction":          {"road_type": "Arterial", "lanes": 3, "speed_limit_kmph": 50},
    "Kundannoor Bridge Road":    {"road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 50},
    "Vyttila Mobility Hub Road": {"road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 40},
    "Aroor Bypass":              {"road_type": "Highway",  "lanes": 4, "speed_limit_kmph": 80},
    "Chilavannoor Road":         {"road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    "Pachalam Road":             {"road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    "SA Road Vyttila":           {"road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 50},
    "Palarivattom Junction":     {"road_type": "Arterial", "lanes": 3, "speed_limit_kmph": 50},
    "NH 85 Palarivattom":        {"road_type": "Highway",  "lanes": 4, "speed_limit_kmph": 70},
    "Kaloor Palarivattom Rd":    {"road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 50},
    "Banerji Road":              {"road_type": "Arterial", "lanes": 3, "speed_limit_kmph": 50},
    "Vyttila Palarivattom Rd":   {"road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 50},
    "Pullepady Road":            {"road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    "Elamkulam Road":            {"road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    "Kadavanthra Junction":      {"road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 50},
    "MG Road Kadavanthra":       {"road_type": "Arterial", "lanes": 3, "speed_limit_kmph": 50},
    "Shanmugham Road":           {"road_type": "Arterial", "lanes": 3, "speed_limit_kmph": 50},
    "Sahodaran Ayyappan Road":   {"road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 40},
    "Ravipuram Road":            {"road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    "Chittoor Road":             {"road_type": "Arterial", "lanes": 2, "speed_limit_kmph": 50},
    "Convent Road":              {"road_type": "Local",    "lanes": 1, "speed_limit_kmph": 30},
    "Judges Avenue":             {"road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    "Bristow Road":              {"road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
    "Kasturi Ranga Rd":          {"road_type": "Local",    "lanes": 2, "speed_limit_kmph": 40},
}

CONGESTION_COLORS = {
    "Low":       "#00e676",
    "Moderate":  "#ffea00",
    "High":      "#ff6d00",
    "Very High": "#ff1744",
}

RISK_COLORS = {
    "Low":       "#00e676",
    "Moderate":  "#ffea00",
    "High":      "#ff6d00",
    "Very High": "#ff1744",
}

MODEL_DIR = "models"
