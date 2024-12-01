module DAC(clk_50, rst, new_val, data, out_clk, out_fs, dac_din, complete);
	input wire clk_50, rst, new_val;
	input wire[11:0] data;
	output wire out_clk;
	output reg out_fs, complete;
	output wire dac_din;

	wire out_clk_pll;
	PLL_1 DAC_PLL(
		.clk_in   (clk_50),   //  clk_50.clk
		.clk_out  (out_clk_pll),  // clk_out.clk
		.rst_in   (rst)  //  rst_in.reset
	);
  reg [4:0] clk_cnt;

  always @(posedge(out_clk_pll)) begin
    clk_cnt = clk_cnt + 1;
  end

  //Clock of 500MHz, since the DAC had to be
  //connected via jumpers.
  assign out_clk = clk_cnt[0];

  reg [15:0] send_data;
  reg [3:0] counter;
  reg prev_new;

/*
Refer to the Datasheet for MCP4921 
to understand the bit sequence that needs to
be sent over this SPI interface
*/
  always @(negedge(out_clk)) begin
	if (new_val) begin
		if (~prev_new) begin
			counter <= 4'b0000;
			send_data <= {4'b0011, data};
			out_fs <= 1'b0;
		end
		else if (counter == 4'd15) begin
			out_fs <= 1'b1;
			complete <= 1'b1;
		end
		else begin
			counter <= counter + 1;
			send_data[15:1] <= send_data[14:0];
		end
	end
	else
        complete <= 1'b0;

    prev_new <= new_val;
  end

  assign dac_din = send_data[15];
endmodule