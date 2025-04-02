# Page Replacement Algorithm Simulator

## Overview
The **Page Replacement Algorithm Simulator** is a Python-based GUI application built using Tkinter that allows users to visualize and analyze different page replacement algorithms. It supports FIFO, LRU, and Clock algorithms, providing step-by-step execution details and performance comparisons.

## Features
- **Simulate Page Replacement Algorithms:** Supports FIFO, LRU, and Clock.
- **Graphical User Interface:** Built using Tkinter for an interactive experience.
- **Step-by-Step Execution:** Displays each step of the algorithm execution.
- **Performance Graphs:** Visual representation of page faults over time.
- **Algorithm Comparison:** Compare performance metrics of different algorithms.
- **File Operations:** Load page sequences from a file and save results.

## Technologies Used
- **Python** (Core language)
- **Tkinter** (GUI framework)
- **Matplotlib** (Graph plotting)
- **Collections (deque, OrderedDict)** (Efficient data structures)

## Installation
Ensure you have Python installed (Python 3.x recommended). Then, install the required dependencies:

```bash
pip install matplotlib
```

## Usage
1. **Run the Application:**
   ```bash
   python page_replacement_simulator.py
   ```
2. **Enter Page Sequence:** Provide a comma-separated list of page numbers.
3. **Set Number of Frames:** Specify the number of available frames.
4. **Choose Algorithm:** Select FIFO, LRU, or Clock from the dropdown.
5. **Run Simulation:** Click "Run" to see step-by-step execution.
6. **Compare Algorithms:** Click "Compare All" to analyze all three algorithms.
7. **View Performance Graph:** Click "Performance Graph" to visualize faults over time.
8. **Save & Load Files:** Use "Load" to import a page sequence and "Save" to export results.

## Screenshots
(Add screenshots of the application interface here)

## License
This project is open-source under the **MIT License**.

## Contributions
Feel free to fork this repository, improve the simulator, and submit pull requests!
