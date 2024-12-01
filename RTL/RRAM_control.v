module RRAM_control (CLK_50, LED, DAC_CLK, DAC_FS, DAC_DIN, ADC_CLK, ADC_DIN, ADC_CS_N, ADC_DOUT, reset, control_BL, control_WL, control_R);
  input wire CLK_50, ADC_DOUT, reset;
  output reg [7:0] LED;//for debugging purposes
  output wire DAC_CLK, DAC_FS, DAC_DIN, ADC_CS_N, ADC_CLK, ADC_DIN; // SPI interface signals
  output reg [2:0] control_BL, control_WL; //Switch controls
  output reg [3:0] control_R; //Rsense control

  //state variables
  //Important: Consider these first whenever
  //there are bugs in the system
  reg ADC_ENABLE;
  reg new_val_DAC; 
  reg prev_read; //Used in pulse configuration to ensure that we don't read the same value twice
  reg ADC_stage; // 1 means we are sampling, 0 means we are waiting for User input through JTAG
  reg [6:0] ADC_samplecount; // Counts the number of samples taken
  reg [1:0] DAC_byte;// Tracks which byte we are recieving in the pulse configuration stage
  reg byte_no;// Tracks whether we are sending the first or second byte from the ADC

  //UART
  // Details on what these signals are will be found in the documentation
  reg uart_reg_select, pc_write_n, pc_read_n;
  wire [31:0] pc_readdata;
  reg [31:0] pc_senddata;

  wire waitreq, cs_uart;
  assign waitreq = 1'b0;
  assign cs_uart = 1'b1;
  jtag_uart PC_interface(
    .clk            (CLK_50),
    .rst_n          (!reset),
    .av_chipselect  (cs_uart),    
    .av_address     (uart_reg_select),
    .av_read_n      (!pc_write_n),
    .av_readdata    (pc_readdata),  
    .av_write_n     (pc_write_n),  
    .av_writedata   (pc_senddata),
    .av_waitrequest (waitreq),
    .av_irq         ()
  );

  //DAC module
  reg [11:0] DAC_data;
  wire DAC_DONE;
  DAC DAC_interface(
    .clk_50 (CLK_50),
    .rst    (reset),
    .new_val(new_val_DAC),
    .data   (DAC_data),
    .out_clk(DAC_CLK),
    .out_fs(DAC_FS),
    .dac_din(DAC_DIN),
    .complete(DAC_DONE)
  );

  // ADC module
  wire ADC_valid;
  wire [11:0] ADC_data;
  reg RST_N_ADC;
  ADC_SPI ADC_interface(
    .rst        (!RST_N_ADC), //The ADC needs a reset signal, which at the start is permanently high
    .enable     (ADC_ENABLE),
    .clk_50     (CLK_50),
    .cs_n       (ADC_CS_N),
    .adc_clk    (ADC_CLK),
    .adc_in     (ADC_DIN),
    .adc_out    (ADC_DOUT),
    .valid      (ADC_valid),
    .data       (ADC_data)
  );

//Drivers and FSM
always @(posedge(CLK_50)) begin
	//LED[3] <= ADC_CS_N;
	if (reset) begin 
		LED <= 0;
		pc_write_n <= 1'b0;
		pc_senddata <= 32'h00000400;
		DAC_byte <= 0;
		ADC_stage <= 0;
		byte_no <= 0;
		pc_read_n <= 1;
		ADC_samplecount <= 0;
		prev_read <= 1'b0;
		RST_N_ADC <= 1'b0;
	end
	// Pulse configuration stage
	else if (~ADC_stage) begin
		uart_reg_select <= 1'b0;
		pc_write_n <= 1'b1;
		pc_read_n <= 1'b0;

		if(pc_readdata[15] == 1'b1 && DAC_byte != 3) begin
			RST_N_ADC <= 1'b1;//Remove reset from ADC the first time the user sends data
			if (!prev_read) begin // If prev_read = 1, the UART will have the same data as in the previous cycle

				//LED[7:4] <= pc_readdata[7:4];
				ADC_samplecount[6] <= 1'b0; //To signify that the user has sent input data, AFTER the DAC output was set to 0
				prev_read <= 1'b1;

				// Read the bytes one by one, assign to switches/DAC inputs
				if (DAC_byte == 2) begin 
					//LED[2] <= 1;
					DAC_data[7:0] <= pc_readdata[7:0];
					new_val_DAC <= 1;
					DAC_byte <= 3;
				end
				else if (DAC_byte == 1) begin
					//LED[1] <= 1;
					control_BL <= pc_readdata[7:5];
					DAC_data[11:8] <= pc_readdata[3:0];
					DAC_byte <= 2;
				end
				else if (DAC_byte == 0) begin
					//LED[0] <= 1;
					control_R[2:0] <= pc_readdata[7:5];
					control_WL <= pc_readdata[3:1];
					DAC_byte <= 1;
				end
			end
			else
				prev_read <= 1'b0;
		end
		else if (DAC_DONE && ~ADC_samplecount[6]) begin //Advance to sampling stage
			pc_read_n <= 1'b1;
			DAC_byte <= 0;
			byte_no <= 0;
			new_val_DAC <= 1'b0;
			ADC_stage <= 1'b1;
			ADC_ENABLE <= 1'b1;
			ADC_samplecount <= 7'd0;
			prev_read <= 0;
			LED <= {8{1'b1}};
		end
	end
	else if (ADC_samplecount[6]) begin //Sampling completed
		uart_reg_select <= 1'b0;
		pc_write_n <= 1'b1;
		pc_read_n <= 1'b1;
		ADC_ENABLE <= 1'b0;

		// Finish the pulse - set DAC output to 0
		// Comment the below line out to send fixed values via GUI instead of pulses
		DAC_data <= 12'd0;

		if (~new_val_DAC)
			new_val_DAC <= 1'b1;
		else if (DAC_DONE) begin
			new_val_DAC <= 1'b0;
			ADC_stage <= 1'b0;
		end
	end
	else begin //Sampling stage
		if(~pc_write_n) begin //To send separate write requests, ensure read is not asserted in consecutive cycles
			pc_write_n <= 1'b1;
		end
		else if (byte_no) begin // byte_no = 1 means that we need to send 4 more bits
			LED[0] <= 0;
			pc_write_n <= 1'b0;
			pc_senddata <= {24'd0, ADC_data[7:0]};
			byte_no <= 1'b0;
			ADC_samplecount = ADC_samplecount + 1; //Increase number of samples sent
		end
		else if (ADC_valid) begin //Send first byte
			uart_reg_select <= 1'b0;
			pc_read_n <= 1'b1;
			pc_write_n <= 1'b0;
			pc_senddata <= {28'd0, ADC_data[11:8]}; //12-bit
			//pc_senddata <= {30'd0, ADC_data[9:8]}; //10-bit
			byte_no <= 1'b1;
		end
		else begin //Wait for valid data
			uart_reg_select <= 1'b1;
			pc_write_n <= 1'b1;
			pc_read_n <= 1'b0;
		end
	end
end

endmodule