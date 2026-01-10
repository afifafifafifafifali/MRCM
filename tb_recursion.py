from myhdl import *
from mrcm_cpu import riscv_cpu_top

@block
def tb_recursion():
    clk = Signal(bool(0))
    reset = ResetSignal(0, active=1, isasync=True)
    pc = Signal(intbv(0)[64:])

    test_program = [
        0x00300093,  # addi x1, x0, 3       -> load argument n=3 into x1
        0x80000f13,  # addi x30, x0, 0x800  -> set stack pointer to address 0x800
        0x00800042,  # jmp 0x08             -> jump to sum function
        0x00000013,  # nop                  -> after sum returns, result is in x1
        0x00000113,  # addi x2, x0, 0       -> load 0 for comparison
        0x14208063,  # beq x1, x2, 0x14     -> if n == 0, jump to base case
        0x00008113,  # addi x2, x1, 0       -> save current n in x2
        0xfff08093,  # addi x1, x1, -1      -> n = n - 1
        0x00800042,  # jmp 0x08             -> recursive call to sum
        0x002080b3,  # add x1, x1, x2       -> x1 = sum(n-1) + n
        0x00400042,  # jmp 0x04             -> jump back to end
        0x00000093,  # addi x1, x0, 0       -> return 0 (base case)
        0x00400042,  # jmp 0x04             -> jump back to end
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

        print("starting recursion example simulation...")
        print(f"time: {now()} - reset released, pc: 0x{int(pc.val):016x}")

        for i in range(30):
            yield clk.posedge
            print(f"cycle {i+1}: time: {now()}, pc: 0x{int(pc.val):016x}")

        print("recursion example completed")
        raise StopSimulation

    return dut, clkgen, stimulus


if __name__ == '__main__':
    tb_inst = tb_recursion()
    tb_inst.config_sim(trace=False)
    tb_inst.run_sim()