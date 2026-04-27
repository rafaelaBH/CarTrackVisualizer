
# DECISIONS.md

## 1. UI Framework Choice

I chose to use Dash together with Plotly for the visualisation layer

### Rationale:

- I chose Dash because it works well with Python and lets me build interactive visuals without needing frontend (JavaScript/HTML) knowledge
- It provides built-in support for interactive elements like buttons, sliders, and callbacks, which made it easier to control the animation
- It works well with Plotly, especially for map-based visualizations, which was a core part of this project
- It has a simple setup

### Alternatives considered:

* Matplotlib – simpler but not suitable for interactive animation
* JavaScript-based mapping libraries – more powerful but significantly more complex and outside the project scope

---

## 2. Key Design Decisions

### 2.1 Separation of Concerns

The system is structured into three main components:

* **Loader** – responsible for parsing and validating raw CSV input
* **Processor** – responsible for computing derived metrics and anomaly detection
* **Visualizer** – responsible for interactive UI rendering

This improves modularity, readability, and maintainability.

### 2.2 Anomaly Detection

Anomalies are detected based on:

* Unrealistic speed between consecutive points
* Altitude values outside a plausible physical range

### Rationale:

* Directly addresses data quality requirements
* Provides meaningful insight into corrupted or invalid GPS traces

---

### 2.3 UI Feature Selection

The following features were implemented:

* **Playback speed control (1×, 2×, 5×)** – high usability with minimal complexity
* **Timeline slider** – enables precise navigation and debugging of time-based data
* **Live data panel (time, speed, altitude)** – turns the tool into a data exploration system rather than a static visualisation
* **Anomaly highlighting** – makes data quality issues immediately visible

---

### 2.4 Excluded Feature: Heading

Although heading can be computed from consecutive points, I chose not to include it because the direction of movement is already visually apparent from the trajectory and there was no requirement for precise angular accuracy

---

## 3. Use of AI Tools

AI tools were used as development and learning aids throughout the project:

* ChatGPT

    * Assisted in structuring documentation (README.md and DECISIONS.md)
    * Helped improve written explanations
    * Supported trade-off analysis

* Claude

    * Helped generate the Mermaid architecture diagram
    * Supported implementation of the Visualizer component, particularly due to limited prior familiarity with Dash and Plotly
    * Assisted in correctly implementing the Haversine formula and Python logging usage, due to limited prior familiarity with these concepts

All AI-generated content was reviewed and adapted before integration into the final implementation.

---

## 4. What I Would Improve With More Time

* Add unit tests for Loader and Processor components
* Add UI controls such as toggle anomaly visibility, Color-coded speed: Colouring the track line by speed (green → red) and more
* Visualization of multiple vehicles simultaneously

---
