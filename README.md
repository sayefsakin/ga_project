# CSC 537 Geometric Algorithm Project

----

## Exploiting KD-Tree for designing interactive gantt-chart visualization of task based time-series data
## Sayef Azad Sakin

## Introduction
Runtime parallel program analysts generate trace data, event logs of historical program execution, and visualize their programs to analyze its performance. Gantt chart is an effective visual analytical tool for analyzing such distributed parallel programs. Longer running distributed programs generally generate large amount of data (millions) in the trace data. In this project, my plan is to exploit KD-tree to store the execution data, enable faster range queries, and visualize in a gantt chart. The developed visualization interface will support faster interactivity (zooming, panning, etc.) with minimal (un-noticeable) visual latency.

##

To parse a OTF2 file, [otf2](https://www.vi-hps.org/projects/score-p/) needs to be installed and its binaries need to be in your PATH. At first, place the 
OTF2 files in `data/<program_name>/OTF2_archive/APEX.OTF2` location. To convert the OTF2 file into plain text file, run the following,
```shell
python3 data_store.py <path to otf2 file>
```
This will create a file named `converted` inside `data` directory. Then to visualize it run
```shell
python3 visualize.py
```
This will show the tasks as a Gantt View in tkinter window.