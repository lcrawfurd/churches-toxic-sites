"""
proximity.py — the core nearest-site method used to build the dataset.

This documents (and lets you re-run) the step that turns raw church
coordinates + contaminated-site coordinates into the per-church distance and
within-1km / within-5km flags in data/osm_churches_near_tsip.csv.

The bundled CSV is the precomputed output of this function. Re-running the full
pipeline from scratch additionally requires:
  - the OpenStreetMap church download (Overpass API; see README "Methods"), and
  - the Pure Earth TSIP contaminated-site coordinates (obtain from Pure Earth;
    not redistributed here).

Method matches the parent paper's proximity computation: a KD-tree for fast
nearest-neighbour lookup on cosine-latitude-projected coordinates, refined with
exact haversine distance.
"""
import numpy as np
from scipy.spatial import cKDTree

EARTH_RADIUS_KM = 6371.0088


def haversine_km(lat1, lon1, lat2, lon2):
    """Vectorised great-circle distance in km."""
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def nearest_site(churches, sites, radii=(1, 5),
                 lat_col="lat", lon_col="lon",
                 site_lat="latitude", site_lon="longitude"):
    """Add nearest-site distance and within-radius flags to `churches`.

    Parameters
    ----------
    churches : DataFrame with church lat/lon columns
    sites    : DataFrame with site lat/lon columns (e.g. TSIP sites)
    radii    : thresholds (km) for which to add within_<r>km indicator columns

    Returns a copy of `churches` with: dist_km, nearest_idx, and within_<r>km.
    """
    mean_lat = sites[site_lat].mean()
    cos_lat = np.cos(np.radians(mean_lat))

    site_xy = np.column_stack([sites[site_lat].values,
                               sites[site_lon].values * cos_lat])
    ch_xy = np.column_stack([churches[lat_col].values,
                             churches[lon_col].values * cos_lat])

    tree = cKDTree(site_xy)
    _, idx = tree.query(ch_xy, k=1)

    nearest = sites.iloc[idx]
    dist = haversine_km(churches[lat_col].values, churches[lon_col].values,
                        nearest[site_lat].values, nearest[site_lon].values)

    out = churches.copy()
    out["nearest_idx"] = idx
    out["dist_km"] = dist
    for r in radii:
        out[f"within_{r}km"] = (dist <= r).astype(int)
    return out


if __name__ == "__main__":
    print(__doc__)
