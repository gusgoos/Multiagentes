# MultiAgents Smart Intersection

## Description

This project is a college proyect for the CIIIA, which simulates a traffic 4-way intersection in Unity based in the coordinates over time given by a mesa framework Python simulation.

## Requirements

### Python

## Pip installs
To run the Python portion of this project, you'll need to install the following Python packages:

- [Flask](https://pypi.org/project/Flask/): A micro web framework for Python.
    ```
    pip install Flask
    ```

- [Mesa](https://pypi.org/project/mesa/): A library for agent-based modeling.
    ```
    pip install mesa
    ```

- [Matplotlib](https://pypi.org/project/matplotlib/): A plotting library for Python.
    ```
    pip install matplotlib
    ```

- [Numpy](https://pypi.org/project/numpy/): A library for numerical computations in Python.
    ```
    pip install numpy
    ```
### Unity

To set up the Unity part of the project you need to drag and drop the package `EscenaCiudad.unitypackage` into a new project's scenes to install it. You'll also need to install the following package:

- [Newtonsoft.Json-for-Unity](https://github.com/jilleJr/Newtonsoft.Json-for-Unity/wiki/Install-official-via-UPM): A JSON serialization library for Unity. To install, follow these steps:
    1. Open the Unity Package Manager (Window -> Package Manager).
    2. Add a new extension by package name 
    3. Enter `com.unity.nuget.newtonsoft-json` as the package name.
    4. Enter `3.2.1` as the version (or the latest available version).
    5. Click the "Add" button to install the package.

Make sure to follow the provided link for more detailed installation instructions for Newtonsoft.Json-for-Unity.

## Usage

### Python

1. Clone this repository to your local machine.

2. Navigate to the Python project directory.

3. Run the Python script using the following command:

    ```
    python Server.py
    ```

### Json generation
To run the simulation in Unity you can either use the generated jsons in the package or create your own using the files `Semaforo.py` and `Semaforo_SMART.py` which will generate a new simulation file with a preview using matplotlib.

### Unity

1. Open Unity and load the Unity project from the project directory.

2. Ensure that you've installed the `Newtonsoft.Json-for-Unity` package following the instructions in the "Requirements" section.

3. To switch between the Normal and the Smart Light you can switch the URL in the controller object in Unity
