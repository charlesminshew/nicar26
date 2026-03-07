# 🗺️ From Spreadsheet to Map in 60 Minutes

**NICAR 2026 · Saturday, March 7 · 10:15 a.m.**

Jennifer LaFleur, UC Berkeley School of Journalism
Charles Minshew, The Atlanta Journal-Constitution

## Session goal

Participants will follow along step-by-step in QGIS to turn a spreadsheet with latitude and longitude coordinates into a styled map with geographic context.

You'll leave knowing three common newsroom mapping workflows:

1. Mapping coordinates from a spreadsheet
2. Joining spreadsheet data to geographic boundaries
3. Summarizing points within geographic areas

This session is designed as a guided exercise with minimal lecture and constant hands-on work.

## What you'll need

- A laptop with QGIS installed
- Sample data on the machines in the lab

## Files

| File | Used in |
|------|---------|
| `waffle_house_locations_090525.csv` | Exercise 1, Bonus |
| `tl_2023_us_state.shp` | Exercise 1 |
| `tl_2023_us_county.shp` | Exercise 2, Bonus |
| `medinc_county.csv` | Exercise 2 |

---

## 0–5 min · Setup and framing

**Workflow overview:** Spreadsheet → Points → Context → Analysis

Open QGIS, locate the class data folder, and confirm everyone has the files.

**Dataset introduction:** We'll map Waffle House locations across the United States (about 2,000 stores). The spreadsheet includes latitude, longitude, city, state, and address.

Many newsroom datasets come exactly like this — a spreadsheet with coordinates that needs to be quickly turned into a map.

---

## Exercise 1: Mapping coordinates (≈25–30 min)

### Step 1 — Add geographic context

Add the U.S. states shapefile (`tl_2023_us_state.shp`).

Quick styling adjustments: light or no fill, thin gray outlines.

### Step 2 — Import the spreadsheet

Add the CSV using **Layer → Add Layer → Add Delimited Text Layer**.

Settings:

- X field: `longitude`
- Y field: `latitude`
- Geometry definition: Point Coordinates

You should now see Waffle House locations mapped across the United States.

### Step 3 — Style the points

Adjust symbol size, change color, and ensure points are visible at a national scale.

**Optional:** Categorize points using the `state` field.

### Outcome

You've created a national point map of Waffle House locations.

Common newsroom uses for point maps: crash locations, restaurant inspections, police incidents, campaign stops, business locations.

---

## Exercise 2: Joining data to geography (≈15–20 min)

### Step 1 — Set up the layers

1. Add the U.S. counties shapefile (`tl_2023_us_county.shp`)
2. Import the median income CSV (`medinc_county.csv`)
3. Join the CSV to counties using the `GEOID` field

### Step 2 — Create a choropleth map

Style counties using **Graduated** colors on the median household income field.

Choose a color ramp and adjust the classification method.

### Outcome

You've learned how to attach spreadsheet data to geographic boundaries and create a thematic map.

---

## Bonus: Counting Waffle Houses by county (≈10 min)

Use the **Count Points in Polygon** tool:

**Processing Toolbox → Count Points in Polygon**

- Polygon layer: `tl_2023_us_county`
- Points layer: `waffle_house_locations`

The output layer will include a field counting how many Waffle Houses fall inside each county.

### Explore the results

Style counties by Waffle House count and compare patterns with median income.

Discussion prompts: Where are Waffle Houses most concentrated? How does that pattern compare to income levels or regional geography?

---

## Wrap-up

Three mapping workflows covered today:

1. Mapping coordinates from a spreadsheet
2. Joining tabular data to geographic boundaries
3. Counting points within geographic areas

**Sources for geographic data:** Census TIGER shapefiles, state GIS portals, city open data portals.

## Contact

Charles Minshew · [charles.minshew@ajc.com](mailto:charles.minshew@ajc.com)
