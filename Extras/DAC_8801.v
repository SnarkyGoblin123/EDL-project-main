module DAC(clk_50, rst, new_val, data, out_clk, out_csn, dac_din, complete);
  input wire clk_50, rst, new_val;
  input wire [13:0] data;
  output wire out_clk;
  output reg complete, out_csn;
  output wire dac_din;

  wire out_clk_pll;
  PLL_5 DAC_PLL(
		.clk_50   (clk_50),   //  clk_50.clk
		.clk_out  (out_clk_pll),  // clk_out.clk
		.rst_in   (rst)  //  rst_in.reset
	);
  reg [4:0] clk_cnt;

  always @(posedge(out_clk_pll)) begin
    clk_cnt = clk_cnt + 1;
  end

  assign out_clk = clk_cnt[4];

  reg [13:0] send_data;
  reg [3:0] counter;
  reg prev_new;

  always @(negedge(out_clk)) begin
    if(rst == 1'b1) begin
      prev_new <= 1'b0;
      complete <= 1'b0;
      out_csn <= 1'b1;
    end
    else begin
      if (new_val == 1'b1) begin
        if (prev_new == 1'b0) begin
          counter <= 4'b0000;
          send_data <= data;
          out_csn <= 1'b0;
        end
        else if (counter == 4'd13) begin
          complete <= 1'b1;
          out_csn <= 1'b1;
        end
        else begin
          counter <= counter + 1;
          send_data[13:1] <= send_data[12:0];
        end
      end
      else
        complete <= 1'b0;
    end

    prev_new <= new_val;
  end

  assign dac_din = send_data[13];
endmodule