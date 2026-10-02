# gnss-survey-to-autocad-dxf
A Python-based tool for processing GNSS/GPS survey data and automatically generating AutoCAD-compatible DXF files. It provides a user-friendly interface for classifying survey points, creating layers and polylines, and exporting accurate land survey maps.

The application provides a Persian-friendly graphical user interface (GUI) for importing GPS survey files, classifying survey points, organizing features into AutoCAD layers, creating polylines, and exporting the final survey drawing as a DXF file.

## Features

* Import GNSS/GPS survey data from:

  * CSV
  * TXT
  * Excel (`.xlsx`)
* Persian RTL graphical user interface
* Automatic preview of imported survey points
* Manual selection of coordinate columns:

  * Point ID
  * Easting / X
  * Northing / Y
  * Elevation / Z
  * Code / Description
* Survey-point classification based on GPS codes
* Support for common survey features:

  * Land boundary
  * Building
  * Road
  * Wall
  * Fence
  * Tree
  * Utility
  * Survey point
  * Contour
  * Other
* Automatic AutoCAD layer creation
* Automatic Point generation
* Automatic 3D Polyline generation
* Closed land-boundary generation
* Building polygon generation
* Preservation of X, Y, and Z coordinates
* Direct DXF generation using Python
* No AutoCAD installation required for DXF generation
* Downloadable DXF output
* Downloadable classified CSV data
* Suitable for GitHub Codespaces

## Workflow

```text
GNSS / GPS Survey
        |
        v
CSV / TXT / XLSX
        |
        v
Python Streamlit GUI
        |
        v
Column Identification
        |
        v
Point & Code Classification
        |
        v
Feature Organization
        |
        v
AutoCAD Layer Creation
        |
        v
Point / Polyline Generation
        |
        v
DXF File
        |
        v
AutoCAD / Civil 3D
```

## Technology Stack

* Python 3
* Streamlit
* Pandas
* OpenPyXL
* ezdxf
* GitHub Codespaces

## Project Structure

```text
gnss-survey-to-autocad-dxf/
│
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

### 1. Clone the repository

```bash
git clone (https://github.com/Ghorbanpoor/gnss-survey-to-autocad-dxf.git)
```

Move into the project directory:

```bash
cd gnss-survey-to-autocad-dxf
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

The application will be available through the Streamlit interface.

## GitHub Codespaces

This project is designed to run directly in GitHub Codespaces.

After opening the repository in Codespaces:

```bash
pip install -r requirements.txt
```

Then run:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Open port `8501` in the Codespaces interface.

No local AutoCAD installation is required to process the GPS data or generate the DXF file.

## Input Data

The application expects survey data containing coordinates.

A typical input file may look like:

```text
Point,X,Y,Z,Code
101,523456.214,4023456.832,124.52,BND
102,523489.631,4023458.217,124.71,BND
103,523491.115,4023421.904,124.36,BND
104,523458.927,4023419.512,124.18,BND
201,523470.100,4023440.200,124.50,BLDG
202,523480.100,4023440.200,124.55,BLDG
203,523480.100,4023430.200,124.40,BLDG
204,523470.100,4023430.200,124.45,BLDG
```

The exact column names do not have to match these names because the application allows the user to select the appropriate columns through the GUI.

## Coordinate Data

The application supports three-dimensional survey coordinates:

```text
X = Easting
Y = Northing
Z = Elevation
```

For example:

```text
Point: 101
X: 523456.214
Y: 4023456.832
Z: 124.52
```

The coordinate values are preserved when creating the DXF file.

## Survey Code Classification

GPS/GNSS surveyors commonly use codes to identify different types of field features.

Examples:

| GPS Code | Feature       |
| -------- | ------------- |
| BND      | Land Boundary |
| BLDG     | Building      |
| ROAD     | Road          |
| WALL     | Wall          |
| FENCE    | Fence         |
| TREE     | Tree          |
| UTIL     | Utility       |

The application allows the user to map each GPS code to a survey feature through the GUI.

For example:

```text
BND  → Land Boundary
BLDG → Building
ROAD → Road
WALL → Wall
TREE → Tree
```

## AutoCAD Layers

The generated DXF uses separate layers for different survey features.

Typical layers include:

```text
LAND_BOUNDARY
BUILDING
ROAD
WALL
FENCE
TREE
UTILITY
SURVEY_POINTS
CONTOUR
OTHER
```

This makes it easier to manage the resulting drawing in AutoCAD or Civil 3D.

## DXF Generation

The application uses the `ezdxf` Python library to create the DXF file directly.

The basic process is:

```text
Survey Coordinates
        ↓
Feature Classification
        ↓
Layer Assignment
        ↓
Point Creation
        ↓
Polyline Creation
        ↓
DXF Export
```

AutoCAD is not required during this process.

The resulting file can later be opened in compatible CAD software.

## Boundary Generation

When survey points are classified as:

```text
BND
```

the application can create a closed polyline representing the land boundary.

For example:

```text
P101 ───────── P102
 │               │
 │               │
P104 ───────── P103
```

The order of the survey points is important because the application uses the order of the input data when creating polylines.

## Building Generation

Building survey points can be classified as:

```text
BLDG
```

and converted into a closed polyline.

For example:

```text
P201 ───────── P202
 │               │
 │   BUILDING    │
 │               │
P204 ───────── P203
```

## Important Survey Data Requirement

The application does not invent missing survey information.

If a file contains only:

```text
X
Y
Z
```

without feature codes or a reliable point sequence, the software cannot automatically determine with certainty whether a group of points represents:

* a building
* a boundary
* a road
* a wall
* or another feature

Therefore, using meaningful survey codes and a logical point collection order is strongly recommended.

## Accuracy

The application preserves the numerical X, Y, and Z values provided by the GPS/GNSS file.

It does not automatically improve the accuracy of the original GNSS survey.

The final map accuracy therefore depends on:

* GNSS receiver accuracy
* RTK correction quality
* Coordinate reference system
* Datum
* Field observation procedure
* Antenna height
* Survey control points
* Multipath and satellite conditions
* Quality of the original survey data

The generated DXF should be checked against survey-control information before being used for legal, cadastral, construction, or engineering purposes.

## Coordinate Reference System

The current application assumes that the input coordinates are already in a suitable projected coordinate system.

For example:

```text
UTM
```

If the GPS file uses geographic coordinates such as:

```text
Latitude
Longitude
```

additional coordinate transformation should be performed before creating a metric CAD drawing.

Future versions may include automatic CRS and datum transformation.

## Outputs

The application can generate:

### DXF

```text
GPS_Survey.dxf
```

### Classified CSV

```text
GPS_Classified_Points.csv
```

### JSON

```text
GPS_Points.json
```

The DXF file is the main CAD output.

## Example Output

A typical generated drawing may contain:

```text
LAND_BOUNDARY
    └── Closed Polyline

BUILDING
    └── Building Polyline

ROAD
    └── Road Polyline

SURVEY_POINTS
    └── Survey Points

TREE
    └── Tree Points
```

## Why AutoCAD Is Not Required

The application generates the DXF file directly with Python.

The process is:

```text
GPS File
   ↓
Python
   ↓
ezdxf
   ↓
DXF
```

AutoCAD is only required if you want to open, edit, annotate, or further process the generated drawing using AutoCAD.

## Limitations

The current version is intentionally focused on basic GPS/GNSS-to-DXF processing.

It does not automatically perform:

* Survey network adjustment
* RTK correction
* Datum transformation
* Automatic cadastral boundary interpretation
* Automatic feature recognition from raw coordinates
* Professional terrain modeling
* Advanced contour interpolation
* Automatic orthophoto generation
* Legal cadastral validation

The application should therefore be considered a survey-data processing and CAD-generation tool rather than a replacement for professional surveying procedures.

## Future Development

Possible future features include:

* Direct GNSS receiver integration
* NMEA support
* RTK data processing
* UTM coordinate transformation
* EPSG/CRS selection
* Datum transformation
* Interactive map preview
* Manual point connection
* Point editing
* Drag-and-drop feature classification
* Automatic contour generation
* Digital Terrain Model (DTM)
* Surface generation
* DXF block generation
* AutoCAD annotation
* Dimension generation
* North arrow
* Scale bar
* Survey report generation
* PDF map export
* GeoJSON export
* Shapefile export
* KML/KMZ export
* Integration with GIS software
* 3D terrain visualization

## Recommended Survey Workflow

For professional land surveying, the recommended workflow is:

```text
1. Establish survey control
        ↓
2. Collect GNSS/RTK observations
        ↓
3. Assign meaningful field codes
        ↓
4. Export survey data
        ↓
5. Upload GPS file to the application
        ↓
6. Verify X/Y/Z columns
        ↓
7. Verify feature codes
        ↓
8. Review point classification
        ↓
9. Generate DXF
        ↓
10. Open and inspect in CAD software
        ↓
11. Perform professional survey/CAD quality control
```

## Example

Input:

```text
101,523456.214,4023456.832,124.52,BND
102,523489.631,4023458.217,124.71,BND
103,523491.115,4023421.904,124.36,BND
104,523458.927,4023419.512,124.18,BND
```

Classification:

```text
BND → LAND_BOUNDARY
```

Output:

```text
LAND_BOUNDARY
└── Closed 3D Polyline
```

The resulting DXF can then be opened in AutoCAD or another compatible CAD application.

## License

This project can be released under the MIT License.

If you use this project for commercial surveying or engineering work, verify the generated CAD data against the original survey observations and applicable professional requirements.

## Disclaimer

This software is intended to assist with GNSS/GPS survey-data processing and CAD generation.

It does not replace a licensed land surveyor, professional survey procedures, official cadastral systems, or required quality-control processes.

Always verify the generated drawing against the original field observations and survey-control data before using it for legal, construction, cadastral, or engineering purposes.

## Author

Developed as a Python-based GNSS/GPS surveying and AutoCAD DXF automation project.

Contributions, improvements, and feature requests are welcome.
