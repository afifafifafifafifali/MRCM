from mrcm_cpu import *
from myhdl import *



test_program = (
    0x00200113,
    0x00400041,
    0x00210193,
    0x00008043,
) + (0x00000013,) * 28  # Pad with NOPs to make 32 instructions total to make the tuple alive



clk = Signal(bool(0))
reset = ResetSignal(0, active=1, isasync=True)
pc = Signal(intbv(0)[64:])

dut = riscv_cpu_top(clk, reset, pc, program=test_program)

dut.convert(hdl="Verilog")

# THIS SYSTEM ANDCURRENT VERILOG CONVERSION IS ROM(READ ONLY MEMORY ONLY).WHICH IS FLASHED PERMANENTLY WHEN SYNTHASIZED
