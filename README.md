# GPS Track Visualiser

An interactive web-based tool for visualising GPS trajectory data over time.
The application loads a CSV file containing GPS records, processes the data, and displays an animated track on a map.

---

## Features

* **Interactive map visualisation** using Plotly & Dash
* **Playback controls** (Play / Pause + speed selection: 1×, 2×, 5×)
* **Timeline slider** for manual navigation through the track
* **Live data display**:

  * Time
  * Speed (km/h)
  * Altitude
* **Anomaly detection & highlighting**:

  * Unrealistic speeds
  * Out-of-range altitude values

---

## Project Structure

```
project/
  SPEC.md
  DECISIONS.md
  requirements.txt
  README.md
  src/
    main.py
    loader.py
    processor.py
    visualizer.py
    point.py
```

---

## Installation

1. Clone the repository:

```bash
git clone <your-repo-url>
cd project
```

2. (Recommended) Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

Run the application:

```bash
python src/main.py
```

Optional arguments:

```bash
python src/main.py <csv_path> --port 8050 --debug
```

### Arguments:

* `csv` (optional): Path to CSV file (default: `car_track.csv`)
* `--port`: Port for the web server (default: 8050)
* `--debug`: Enable Dash debug mode

---

## Access the App

Once running, open your browser at:

```
http://localhost:8050
```

---

## Input Format

The CSV file must include the following columns:

```
time, lat, lon, alt
```

### Example:

```
time,lat,lon,alt
0.0,32.0853,34.7818,10
1.0,32.0854,34.7819,12
```

---

## Data Handling

* Rows with missing or invalid values are skipped
* Latitude/longitude are validated against physical bounds
* Duplicate timestamps are removed
* At least **2 valid records** are required

---

## Processing Logic

* Speed is computed between consecutive points using the **Haversine formula**
* The final point inherits the previous speed
* A point is flagged as **anomalous** if:

  * Speed exceeds a plausible threshold (250 km/h)
  * Altitude is outside [-500, 9000] meters

---

## Design Notes

* The system is divided into clear components:

  * `Loader` – data ingestion & validation
  * `Processor` – derived metrics & anomaly detection
  * `Visualizer` – UI & interaction

* The focus was on:

  * Clarity of architecture
  * Separation of concerns
  * Minimal but meaningful UI

---
