module DAC(clk_50, rst, new_val, data, out_clk, out_fs, out_csn, dac_din, complete);
  input wire clk_50, rst, new_val;
  input wire[11:0] data;
  output wire out_clk, out_csn;
  output reg out_fs, complete;
  output wire dac_din;

  assign out_csn = 1'b0;

  wire out_clk_pll;
  PLL_5 DAC_PLL(
		.clk_50   (clk_50),   //  clk_50.clk
		.clk_out  (out_clk_pll),  // clk_out.clk
		.rst_in   (rst)  //  rst_in.reset
	);
  reg [10:0] clk_cnt;

  always @(posedge(out_clk_pll)) begin
    clk_cnt = clk_cnt + 1;
  end

  assign out_clk = clk_cnt[10];

  reg [15:0] send_data;
  reg [3:0] counter;
  reg prev_new;

  always @(posedge(out_clk)) begin
    if(rst == 1'b1) begin
      prev_new <= 1'b0;
      out_fs <= 1'b1;
      complete <= 1'b0;
    end
    else begin
      if (new_val == 1'b1) begin
        if (prev_new == 1'b0) begin
          counter <= 4'b0000;
          send_data <= {4'h4, data};
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
    end

    prev_new <= new_val;
  end

  assign dac_din = send_data[15];
endmodule