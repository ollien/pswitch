# PSwitch

A Python script to switch all Pulse Audio inputs/outputs to a single source/sink.

![Icon](https://raw.githubusercontent.com/ollien/pswitch/master/icon.png)

### Installation
Simply run `pip install --user .`

### Dependencies

* pulseaudio
* python3

### Usage

If you don't wish to install pulse switch, replace `pswitch` with `python -m pswitch`

`pswitch o[utput]`

Opens a menu of all available sinks, allowing you to change all outputs to it.

`pswitch i[nput]`

Opens a menu of all available sources, allowing you to change all inputs to it.

`pswitch o[utput] n`

Changes all outputs to sink with index n.


`pswitch i[nput] n`

Changes all inputs to source with index n.
