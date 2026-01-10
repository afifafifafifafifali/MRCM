from myhdl import *
from mrcm_cpu import riscv_cpu_top

@block
def tb_recursion_demo():
    clk = Signal(bool(0))
    reset = ResetSignal(0, active=1, isasync=True)
    pc = Signal(intbv(0)[64:])

    test_program = [
        0x80000f13,  # addi x30, x0, 0x800  -> set stack pointer
        0x00300093,  # addi x1, x0, 3       -> load n=3
        0x00000113,  # addi x2, x0, 0       -> load 0 for comparison
        0x1c208063,  # beq x1, x2, 0x1c     -> if n==0, jump to base case
        0x001f2023,  # sw x1, 0(x30)        -> push n onto stack
        0xff8f0f13,  # addi x30, x30, -8    -> decrement stack pointer
        0xfff08093,  # addi x1, x1, -1      -> n = n - 1
        0x00800042,  # jmp 0x08             -> jump back to loop
        0x00000013,  # nop
        0x00000013,  # nop
        0x00100093,  # addi x1, x0, 1       -> base case: factorial(0) = 1
        0x00000013,  # nop                  -> infinite loop
    ]

    dut = riscv_cpu_top(clk, reset, pc, program=test_program)

    # clock generator
    @always(delay(5))
    def clkgen():
        clk.next = not clk

    @instance
    def stimulus():
        reset.next = 1
        yield delay(20)
        reset.next = 0

        print("starting recursion demo simulation...")
        print(f"time: {now()} - reset released, pc: 0x{int(pc.val):016x}")

        for i in range(20):
            yield clk.posedge
            print(f"cycle {i+1}: time: {now()}, pc: 0x{int(pc.val):016x}")

        print("recursion demo completed")
        raise StopSimulation

    return dut, clkgen, stimulus


if __name__ == '__main__':
    tb_inst = tb_recursion_demo()
    tb_inst.config_sim(trace=False)
    tb_inst.run_sim()