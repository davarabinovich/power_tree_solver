![image](https://github.com/davarabinovich/power_tree_solver/assets/48604998/78d551d2-a72c-48a5-b32a-b643b08a2781)# Power Tree Solver
## Description
**Power Tree Solver** (**PTS**) is a graphic utility (based on PyQt) to calculation of power supply networks for PCB design or similar problems.
PTS allow you to build an electric network (in form of a forest, or set of trees, where every root is a global power supply input of your system, every leaf is an end-point consumer), set parameters for its nodes and display consumptions in every node.

The actual version supports the following features:
- Two types of end-point consumers - constant current and fixed resistance
- Two types of DC/DC voltage converters (as inner nodes of tree) - switching (with 100% efficiency) and linear

## Startup
To get PTS, do following:
1. Select the **release** branch of this repo
2. Download the pts.exe file to your local file system
3. Launch the pts.exe file

## Manual
### Networks
In terms of PTS, every electrical device you are designing (e. g. Print Circuit Board) has its own electric net. You can work with one net at the same time.
You can **create** new net, **load** an existing one from the file in your local file system, and **save** the currently edited net using commands in the app's main menu:
