"""
@brief: Register File for 64-bit RISC CPU
Implements 32 general-purpose 64-bit registers
"""

from myhdl import *


@block
def regfile(clk, we, rs1, rs2, rd, wd, r1, r2, monitor_addr1=None, monitor_addr2=None, monitor_data1=None, monitor_data2=None):
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
    @param monitor_addr1: Optional monitoring address 1
    @param monitor_addr2: Optional monitoring address 2
    @param monitor_data1: Optional monitoring data 1
    @param monitor_data2: Optional monitoring data 2
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
            print(f"WRITE x{int(rd)} = {int(wd)}")

    # Optional monitoring logic - always define if all monitor signals are provided
    @always_comb
    def monitor():
        if monitor_addr1 is not None and monitor_addr2 is not None and monitor_data1 is not None and monitor_data2 is not None:
            monitor_data1.next = 0 if int(monitor_addr1) == 0 else regs[int(monitor_addr1)]
            monitor_data2.next = 0 if int(monitor_addr2) == 0 else regs[int(monitor_addr2)]

    return read, write