# RRAM RTL
This is documentation for all of the verilog code submitted as part of the project.
The design has 4 main components:

#### JTAG - UART
There is a file for the jtag-uart IP. This file can be generated using Intel's Platform designer. This file SHOULD not be altered, so there is really no need for re-generating it.

To actually use this IP, the user has to have familiarity with the Avalon interface. We recommend reading through the [docs](https://www.intel.com/content/www/us/en/docs/programmable/683091/22-3/introduction-to-the-interface-specifications.html), specifically section 3 on Memory-Mapped Interfaces.

On the PC side, you will need a driver to interface with the UART, which is a problem thankfully solved already by Tom Verbuere in his [blog](https://tomverbeure.github.io/2021/05/02/Intel-JTAG-UART.html). This allows us to interface with the JTAG UART in python, instead of Intel's own very limiting Nios-II terminal.

Lastly, you will have to read through the JTAG UART documentation IP to actually know what to write into the interface, which is provided in the ```datasheets``` folder. Read from page 5-9, the _Register Map_ section.

Reading the above, along with the heavily commented RTL given in the module ```RRAM_control``` should give the reader sufficient expertise as to how the entire system works.

#### DAC driver
Most DACs are controlled using an SPI interface, and normally require 3 signals to drive (There is usually a fourth input, but it can be almost always set to high or low).

The interface we have implemented is simple:
- There are clock and reset inputs.
- Three outputs to send to the DAC - clock, actual data, and some signal to synchronize the FPGA and DAC.
- A register input ```data``` that holds the new value to be sent to the DAC. This value is recieved from the UART interface.
- An input (```new_val```) to notify to the DAC that a new value should be sent to the DAC. This signal remains high until the driver sends the signal ```complete```, which signifies that the new value has been transmitted to the DAC.

This allows us to change DACs if needed, while only having to change the SPI interface within the driver slightly to adjust to a different DAC's timing requirements. In fact, the drivers for dac8801 and TLV5616, which we had at some point considered, are also provided in the folder ```Extras```.


#### ADC driver
This is very similar to the DAC, as we still need to control an SPI interface. The differences are as follows:
- The SPI 'data' signal is now an input
- The register 'data' signal is now an output
- There is a ```valid``` signal which signifies that the current value in the ```data``` register is correct and should be sent to the PC, and
- There is an ```enable``` input which remains high until the required number of samples are collected.

Again, care has been taken that any ADC that supports an SPI interface can be painlessly integrated. Unfortunately, we do not have examples of such alternatives, as the on-board ADC128S022 worked well for us since the start.

#### PLLs
We can instantiate up to 4 Phase Locked Loops in De0-Nano, which are quite usefull for providing the slower clocks the ADCs or DACs might need. PLLs for a specific frequency can again be produced using Intel's Platform designer or IP tools. We have provided files to both instantiate a 1MHz PLL clock and a 5MHz PLL clock. These can be used to generate slower clocks using a counter.

When writing the ADC and DAC drivers, do remember that you are dealing with different clock domains, and very hard-to-track bugs can arise from this.

Note: If you want to generate a PLL for a different frequency, Intel's PLL generation wizard works on Windows only, not Linux.


With this, and the RTL code provided, we hope that anyone with UG-level knowledge of verilog and Quartus Tools can modify the given project.