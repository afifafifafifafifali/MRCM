"""
@brief: Register File for 64-bit RISC CPU
Implements 32 general-purpose 64-bit registers
"""

from myhdl import *


@block
def regfile(clk, we, rs1, rs2, rd, wd, r1, r2):
    """
    @brief: Register File with 32 64-bit registers
    @param clk: Clock signal
    @param we: Write enable
    @param rs1: Read port 1 address
    @param rs2: Read port 2 address
    @param rd: Write address
    @param wd: Write data
    @param r1: Read port 1 data
    @param r2: Read port 2 data
    """
    regs = [Signal(intbv(0)[64:]) for _ in range(32)]

    @always_comb
    def read():
        r1.next = 0 if rs1 == 0 else regs[int(rs1)]
        r2.next = 0 if rs2 == 0 else regs[int(rs2)]

    @always_seq(clk.posedge, reset=None)
    def write():
        if we and rd != 0:
            regs[int(rd)].next = wd
            #print(f"WRITE x{int(rd)} = {int(wd)}")
            print("WRITE x",int(rd), " = ", int(wd))

    return read, write
