# Data dictionary

## osm_churches_near_tsip.csv
One row per OpenStreetMap Christian place of worship (219,910 rows, 40 countries).

| Column | Description |
|---|---|
| `osm_id` | OpenStreetMap element id |
| `name` | Church name (OSM `name` tag, may be blank) |
| `denomination` | Raw OSM `denomination` tag (free text, often blank) |
| `lat`, `lon` | Church coordinates (WGS84) |
| `country` | Country |
| `denom_class` | Grouped denomination: Catholic / Anglican / Other Christian / Unspecified |
| `dist_km` | Great-circle distance (km) to the nearest TSIP contaminated site |
| `within_1km`, `within_5km` | 1 if `dist_km` ≤ 1 / ≤ 5, else 0 |
| `nearest_site` | Name of the nearest TSIP site |
| `pollutant` | Key pollutant of the nearest site (TSIP) |
| `site_industry` | Source-industry category of the nearest site (TSIP) |
| `site_id` | TSIP id of the nearest site |

## churches_near_sites_5km.xlsx / churches_near_sites_1km.xlsx
Filtered subsets — churches within 5 km / 1 km of a site.

## religious_schools_near_sites.xlsx / religious_schools_within_1km.xlsx
Catholic/Anglican **schools** within 5 km / 1 km, from the parent paper's
national school-census data.

| Column | Description |
|---|---|
| `country`, `school_name`, `location` | School identifiers |
| `denomination` | Catholic / Anglican / Anglican-Catholic |
| `mgmt` | Management type (from EMIS) |
| `enrollment` | Enrolment where recorded |
| `dist_km`, `within_1km` | Distance to nearest site; 1-km flag |
