# Operational Research & Logistics Toolkit

## Project Overview
This project has been developed as part of the **Operational Research and Logistics** course. It provides a comprehensive Python-based application for solving two fundamental problems in operations research: the **Critical Path Method (CPM)** for project management and the **Broker Problem** for transportation optimization. The application features an intuitive graphical user interface (GUI) to facilitate data input, analysis, and visualization of results.

## Features

### 1. Critical Path Method (CPM)
The CPM module provides robust project scheduling and management capabilities, including:

- **Time Calculations:**
  - Earliest Start (ES) and Earliest Finish (EF) times
  - Latest Start (LS) and Latest Finish (LF) times
  - Float/slack time calculations

- **Path Analysis:**
  - Critical path identification
  - Time reserve calculations for all activities

- **Visualization Tools:**
  - Activity-on-Node (AON) network diagrams
  - Activity-on-Arrow (AOA) network diagrams
  - Gantt chart representation

#### Input Formats:
The module accepts project data in two standard formats:

1. **Event Sequence Format:**
   - Activities defined by start and end events (e.g., '1-2')
   - Duration specifications for each activity
   
2. **Predecessor Format:**
   - Activities with explicit predecessor relationships
   - Duration specifications for each activity

#### Current Functionality:
- Complete implementation of the CPM algorithm
- Input validation and error handling
- Multiple visualization options with customizable displays
- User-friendly GUI for data input and analysis

### 2. Broker Problem
The Broker Problem module addresses transportation optimization in supplier-customer networks. When fully implemented, it will calculate:

- **Economic Metrics:**
  - Total transportation costs
  - Revenue potential
  - Broker profit optimization

- **Transportation Planning:**
  - Optimal distribution routes
  - Unit profit analysis
  - Supply and demand balancing

#### Current Status:
- Module framework established
- GUI components planned
- Implementation in progress

## Technologies

### Core Components:
- **Programming Language:** Python 3.11+

### Key Libraries:
- **Tkinter:** GUI development framework
- **Matplotlib:** Data visualization and charting
- **NetworkX:** Graph-based calculations and network visualization
- **Pillow:** Image processing for GUI elements

### Interface:
- Cross-platform desktop application
- Responsive window design
- User-friendly form inputs

## Project Structure
The codebase is organized into the following components:

- **`activity.py`**: Defines the `Activity` class and data parsing utilities
- **`cpm.py`**: Implements the CPM algorithm and visualization methods
- **`cpm_window.py`**: Handles the graphical user interface for the CPM module
- **`main_window.py`**: Provides the main application menu and navigation
- **`main.py`**: Application entry point with example implementations
- **`gui_paths.py`**: Manages asset and resource paths for the interface

## Installation & Usage

### Requirements:
- Python 3.11 or higher
- Required libraries (installable via pip)

### Setup:
1. Clone the repository to your local machine
    ```bash
    git clone https://github.com/WinterWollf/BOiL.git
    ```

2. Install dependencies:
   ```bash
   pip install matplotlib networkx pillow
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) License - see the [LICENSE](LICENSE.txt) file for details.

### Development Team
The project is being developed by:

<img alt="WinterWollf" src="https://img.shields.io/badge/GitHub-WinterWollf-181717?logo=github&amp;logoColor=white&amp;style=for-the-badge">

<img alt="reKOmo" src="https://img.shields.io/badge/GitHub-reKOmo-181717?logo=github&amp;logoColor=white&amp;style=for-the-badge">

<img alt="PawelS12" src="https://img.shields.io/badge/GitHub-PawelS12-181717?logo=github&amp;logoColor=white&amp;style=for-the-badge">