# Example assembly program to calculate ((5+13)*2)/2
ADDI x1, x0, 5     # Load 5 into x1
ADDI x2, x0, 13    # Load 13 into x2
ADD x3, x1, x2     # x3 = x1 + x2 = 18
SLLI x4, x3, 1     # x4 = x3 << 1 = 36 (multiply by 2)
SRLI x5, x4, 1     # x5 = x4 >> 1 = 18 (divide by 2)
NOP                # No operation (infinite loop)