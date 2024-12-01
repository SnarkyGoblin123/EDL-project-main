# RRAM characterization docs

This documentation contains directions on how to use the device that we have created as part of our EDL project, as well as a clear explanation of all the files provided, so as to guide anyone attempting to improve upon/modify this project.

### Using the device
After making the required connections, use quartus to compile the given Quartus Project and download it into your De0-Nano board. After this, run the python file Gui.py and you are all set!

### RTL design
There is verilog code in the folder named ```RTL```, which was programmed on a De0-Nano board to be used as a controller and to interface with the PC. There is detailed documentation of the verilog code inside this folder, given in a readme in folder ```RTL```. 

### PC software
The GUI was implemented using PyQt6 and PyQt designer, and there is plenty of documentation available online to work with this library. The interfacing with FPGA was handled by the python library ```intel_jtag_uart```, as explained above. We have provided a ```.ui``` file for quick modification of the GUI (In PyQt designer), in the folder ```Extras```.

We are sending three bytes of info to the FPGA, which contains information regarding what bitline and wordline the user wants to select, and the strength of the pulse we want to send. 
To scale up with a larger crossbar, we just have to send more bytes as the circuit demands. The GUI will also need to be modified to accomodate larger input options.

The bits sent to the DAC are also decided here. For example:

In our final circuit, the strength of the pulse sent to the crossbar is ```5x-16```, where ```x``` is the output of the DAC. The output of the DAC itself scales from 0 to 5 linearly with the 12 bits we send.
If the user wants the pulse strength to be ```y```, the output of the DAC should be ```(y+16)/5```. Thus, the bit sequence sent is:

$\frac{2^{12}-1}{5}\times\frac{y+16}{5}$

The analog input data also needs to be adjusted accordingly before plotting.

## Analog Design

This part involves all the analog circuitry required to send the voltage pulse across a selected resistance in the crossbar. We will briefly describe what individual components in the circuit do:

- MCP4921 : This is the DAC that converts the input from FPGA to analog pulse.
- TL071 : This opamp performs the function y = -x where x is the output of DAC.
- LM6172 : Now, we want pulses of amplitude -5 to 5, so it scales the input of TL071 appropriately. The 2nd opamp in the IC is write buffer. For its use refer the paper.
- CD4066 : This is a CMOS switch that selects which $R_{sense}$ should be selected. The control signals are sent from FPGA.
- ADG436 : These are MUX switches that select a resistance from the crossbar array. The control signals are sent from FPGA.
- TL071: This is the read buffer opamp, for its use see the paper.
- LMH6715: Now, again to send data to ADC, we need to scale it appropriately so that it matches with input range of ADC. This opamp scales appropriately the $V_{source}$ and $V_{bias}$ voltages.

We will discuss the working in brief. The circuit is essentially a voltage divider, with a known resistance $R_{sense}$ and an unknown one which we want ot measure. Now, if measure the voltages across the $R_{sense}$, lets call them $V_{source}$ and $V_{bias}$, then we can get the value of unknown resistance by the formula 
$\frac{V_{bias}}{V_{source} - V_{bias}}*R_{sense}$. This is the method we use to measure resistances in the crossbar. 
