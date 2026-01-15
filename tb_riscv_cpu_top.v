module tb_riscv_cpu_top;

reg clk;
reg reset;
wire [63:0] pc_out;

initial begin
    $from_myhdl(
        clk,
        reset
    );
    $to_myhdl(
        pc_out
    );
end

riscv_cpu_top dut(
    clk,
    reset,
    pc_out
);

endmodule
