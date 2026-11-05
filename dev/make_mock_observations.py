"""Generate fake EarthRanger subject-group observations for mock-IO test runs.

The platform's built-in example return for ``get_subjectgroup_observations``
has no ``extra__subjectsource__*`` or ``extra__observation_details`` columns,
which this workflow's ``process_relocations`` step selects, so a mock-IO run
fails on it. This script writes a stand-in with every column the workflow
reads, shaped like a real ``include_details`` / ``include_subjectsource_details``
response.

What's in it (seeded, so reruns give identical output):

- Four collared animals in the Maasai Mara, one per 3D model subtype the
  workflow ships (elephant, lion, giraffe, wildebeest), with distinct colours.
- Hourly fixes from 2025-03-01 to 2025-03-14 (UTC); movement styles differ per
  species (lion rests by day and moves at night, wildebeest drifts north-east).
- Things the cleaning steps should remove:
  - a (0, 0) fix and a (1, 1) fix, which hit ``filter_point_coords``;
  - one fix flagged ``junk_status = True``;
  - a single 40 km GPS jump on the giraffe, which the test cases'
    ``max_speed_kmhr`` filter drops;
  - a 10-hour collar gap on the lion (left in, as real data has them).

Run from the repo root:

    pixi run --manifest-path ecoscope-workflows-animate-tracks-workflow/pixi.toml \
        python dev/make_mock_observations.py
"""

from __future__ import annotations

import uuid
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

OUT = Path(__file__).parent / "mock-io" / "get-subjectgroup-observations.example-return.parquet"

SEED = 20250301
START = pd.Timestamp("2025-03-01T00:00:00Z")
END = pd.Timestamp("2025-03-14T23:00:00Z")
TENANT = "5ae6c42f-1801-4206-baf9-dbfc11783173"
SERVER = "https://mep-dev.pamdas.org"

# Rough Maasai Mara box; tracks are kept inside it.
LON_MIN, LON_MAX = 34.90, 35.40
LAT_MIN, LAT_MAX = -1.65, -1.25

# name, subtype, sex, hex, start (lon, lat), mean step metres/hour, drift (east, north) m/h
SUBJECTS = [
    ("Kito", "elephant", "female", "#e41a1c", (35.05, -1.45), 450, (0, 0)),
    ("Olarro", "lion", "male", "#ff7f00", (35.15, -1.45), 0, (0, 0)),  # night-active, see _step
    ("Twiga", "giraffe", "female", "#4daf4a", (35.12, -1.38), 220, (0, 0)),
    ("Sopa", "wildebeest", "male", "#377eb8", (34.98, -1.58), 380, (60, 90)),
]

M_PER_DEG_LAT = 110_574.0


def _uuid(rng: np.random.Generator) -> str:
    return str(uuid.UUID(bytes=rng.bytes(16), version=4))


def _m_per_deg_lon(lat: float) -> float:
    return 111_320.0 * np.cos(np.radians(lat))


def _step(rng: np.random.Generator, subtype: str, hour: int, mean_m: float) -> float:
    if subtype == "lion":
        # Mostly resting in daylight, hunting/patrolling at night.
        return rng.gamma(2.0, 180.0) if hour >= 18 or hour < 6 else rng.gamma(1.0, 40.0)
    return rng.gamma(2.0, mean_m / 2.0)


def _track(rng: np.random.Generator, subtype: str, start: tuple[float, float], mean_m: float,
           drift: tuple[float, float], times: pd.DatetimeIndex) -> np.ndarray:
    lon, lat = start
    heading = rng.uniform(0, 2 * np.pi)
    pts = []
    for t in times:
        pts.append((lon, lat))
        heading += rng.normal(0, 0.6)  # correlated random walk
        d = _step(rng, subtype, t.hour, mean_m)
        de = d * np.sin(heading) + drift[0]
        dn = d * np.cos(heading) + drift[1]
        lon += de / _m_per_deg_lon(lat)
        lat += dn / M_PER_DEG_LAT
        # Bounce off the box edges so tracks stay in the Mara.
        if not LON_MIN < lon < LON_MAX:
            lon = float(np.clip(lon, LON_MIN, LON_MAX))
            heading = -heading
        if not LAT_MIN < lat < LAT_MAX:
            lat = float(np.clip(lat, LAT_MIN, LAT_MAX))
            heading = np.pi - heading
    return np.array(pts)


def build() -> gpd.GeoDataFrame:
    rng = np.random.default_rng(SEED)
    times = pd.date_range(START, END, freq="1h")
    created = pd.Timestamp("2025-03-15T08:00:00Z")
    rows = []

    for name, subtype, sex, hex_, start, mean_m, drift in SUBJECTS:
        subject_id = _uuid(rng)
        source_id = _uuid(rng)
        pts = _track(rng, subtype, start, mean_m, drift, times)
        keep = np.ones(len(times), dtype=bool)
        junk = np.zeros(len(times), dtype=bool)

        if subtype == "lion":
            keep[150:160] = False  # 10-hour collar gap
        if subtype == "giraffe":
            pts[200] = pts[200] + [0.36, 0.0]  # ~40 km east and straight back: a GPS jump
        if subtype == "elephant":
            pts[90] = [0.0, 0.0]  # null-island fix
            pts[91] = [1.0, 1.0]  # placeholder fix
        if subtype == "wildebeest":
            junk[120] = True

        last = pts[keep][-1]
        last_t = times[keep][-1]
        subject = {
            "extra__subject__content_type": "observations.subject",
            "extra__subject__id": subject_id,
            "extra__subject__name": name,
            "extra__subject__subject_type": "wildlife",
            "extra__subject__subject_subtype": subtype,
            "extra__subject__common_name": None,
            "extra__subject__created_at": pd.Timestamp("2024-11-02T09:15:00+03:00"),
            "extra__subject__updated_at": pd.Timestamp("2025-03-15T11:00:00+03:00"),
            "extra__subject__is_active": True,
            "extra__subject__user": None,
            "extra__subject__tracks_available": True,
            "extra__subject__image_url": f"/static/{subtype}-black.svg",
            "extra__subject__last_position_status": {
                "last_voice_call_start_at": None, "radio_state": "na", "radio_state_at": None,
            },
            "extra__subject__last_position_date": last_t,
            "extra__subject__last_position": {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [float(last[0]), float(last[1])]},
                "properties": {"DateTime": last_t.isoformat(), "title": name},
            },
            "extra__subject__device_status_properties": None,
            "extra__subject__url": f"{SERVER}/api/v1.0/subject/{subject_id}",
            "extra__subject__hex": hex_,
            "extra__subject__sex": sex,
            "extra__subjectsource__id": _uuid(rng),
            "extra__subjectsource__assigned_range": {
                "lower": "2024-11-02T00:00:00+00:00", "upper": "2026-11-02T00:00:00+00:00",
            },
            "extra__subjectsource__source": source_id,
            "extra__subjectsource__subject": subject_id,
            "extra__subjectsource__additional": {"collar_model": "GPS Plus 2"},
        }

        for i, t in enumerate(times):
            if not keep[i]:
                continue
            lon, lat = map(float, pts[i])
            obs_id = _uuid(rng)
            rows.append({
                "id": obs_id,
                "extra__id": obs_id,
                "extra__location": {"latitude": lat, "longitude": lon},
                "extra__recorded_at": t,
                "extra__created_at": created,
                "extra__exclusion_flags": 0.0,
                "extra__das_tenant_id": TENANT,
                "extra__source": source_id,
                "extra__subject_id": subject_id,
                "extra__observation_details": {
                    "battery_v": round(float(3.9 - 0.002 * i + rng.normal(0, 0.01)), 3),
                    "temperature_c": round(float(22 + 8 * np.sin((t.hour - 9) / 24 * 2 * np.pi)
                                                 + rng.normal(0, 1)), 1),
                    "hdop": round(float(rng.uniform(0.7, 2.5)), 1),
                },
                "geometry": Point(lon, lat),
                **subject,
                "groupby_col": subject_id,
                "fixtime": t,
                "junk_status": bool(junk[i]),
            })

    gdf = gpd.GeoDataFrame(rows, geometry="geometry", crs="EPSG:4326").set_index("id")
    return gdf


def main() -> None:
    gdf = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(OUT)
    counts = gdf.groupby("extra__subject__name").size().to_dict()
    print(f"Wrote {len(gdf)} fixes for {counts} to {OUT}")
    print(f"Time span: {gdf['fixtime'].min()} to {gdf['fixtime'].max()}")


if __name__ == "__main__":
    main()
