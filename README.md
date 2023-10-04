# Factorio Resource Calculator

This repository contains a few scripts for calculating the number of assembling machines required to make items at a particular throughput.

## Installation on Linux

Make sure python (>= 3.9), graphviz and Qt are installed is installed: `sudo apt install python3 python3-venv python3-pip graphviz libgraphviz-dev qt5-default`, and clone this repository. From the root directory, make a virtual environment and install the requirements as follows:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

After that, you can run use `./amg.py`, which shows the assembling machine dependency tree required to make an item at a certain rate. Run `./amg.py -h` to read how it works.

To run the tests, install pytest using `pip install pytest`. Then run `pytest`.

## Installation on Windows and Mac

First, wipe your hard drive and install GNU/Linux. Then proceed to follow the instructions in the previous section.

Joking aside, you can probably get it working on Mac or Windows, but it hasn't been tested. The virtual environment should "just work", provided the python version is high enough, but graphviz and qt5 might require separate installation. Mac will probably work with some kind of brew install graphviz, and otherwise the same instructions as Linux above.




