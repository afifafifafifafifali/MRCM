from myhdl import *
from mrcm_cpu import riscv_cpu_top
from mrcm_cpu import movl, callq, jmp, ret


@block
def tb():
    clk = Signal(bool(0))
    reset = ResetSignal(0, active=1, isasync=True)
    pc = Signal(intbv(0)[64:])

    test_program = [
    0x00200113,
    0x00400041,
    0x00210193,
    0x00008043,
]
    dut = riscv_cpu_top(clk, reset, pc, program=test_program)

    @always(delay(5))
    def clkgen():
        clk.next = not clk

    @instance
    def stimulus():
        reset.next = 1
        yield delay(20)
        reset.next = 0

        print("starting cpu simulation...")
        print(f"time: {now()} - reset released, pc: 0x{int(pc.val):016x}")

        for i in range(20):
            yield clk.posedge
            print(f"cycle {i+1}: time: {now()}, pc: 0x{int(pc.val):016x}")

        print("test completed")
        raise StopSimulation

    return dut, clkgen, stimulus

if __name__ == '__main__':
    tb_inst = tb()
    tb_inst.config_sim(trace=False)
    tb_inst.run_sim()