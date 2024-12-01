module ADC_SPI (rst, enable, clk_50, cs_n, adc_clk, adc_in, adc_out, valid, data);
  input wire enable, clk_50, rst;
  input wire adc_out;
  output reg cs_n;
  output reg [11:0] data;
  output wire adc_in, adc_clk;
  output reg valid;

  wire out_clk_pll;
  PLL_1_5 ADC_PLL(
		.clk_in(clk_50),   // clk_50.clk
		.clk_out(out_clk_pll),  // rst_in.reset
		.rst_in(rst)
	);

  /*
  // Example for how to get slower clocks from PLL
  reg [4:0] clk_cnt;
  always @(posedge(out_clk_pll)) begin
    clk_cnt = clk_cnt + 1;
  end
  //assign adc_clk = clk_cnt[0];
  */

  assign adc_clk = out_clk_pll;

  reg [3:0] adc_counter;
  reg [11:0] data_int;

  reg prev_counter_MSB;

  //sync the valid signal to the 50 MHz clock
  always @(posedge(clk_50)) begin
    if ((prev_counter_MSB) & (~adc_counter[3])) begin
      valid <= 1'b1;
      data <= data_int;
    end
    else
	  valid <= 1'b0;

	prev_counter_MSB <= adc_counter[3];
  end

/*
See the datasheet for understanding the bit sequence that needs to be sent
We are samping from Analog input 2 and 7, as shown in the schematic.
*/
  reg prev_en, channel_no;
  reg [5:0] send_control;
  always @(posedge(adc_clk)) begin
    if(rst == 1'b1) begin
      cs_n <= 1'b1;
	  send_control <= 4;
	  channel_no <= 1;
    end
    else if(~prev_en && enable) begin
      adc_counter <= 4'b0000;
      cs_n <= 1'b0;
	  send_control <= 4;
	  channel_no <= 1;
    end
    else if(~cs_n) begin
      if (adc_counter == 15) begin
		if (~enable)
    		cs_n <= 1'b1;

		if (channel_no)
			send_control <= 14;
		else
			send_control <= 4;

		channel_no <= ~channel_no;
	  end
	  else
	  	send_control[5:1] <= send_control[4:0];

      adc_counter <= adc_counter + 1;
    end
    prev_en <= enable;
    
    data_int[11:1] <= data_int[10:0];
    data_int[0] <= adc_out;
  end

  assign adc_in = send_control[5];

endmodule