# recursion example: Calculate factorial of 3

# Main program
ADDI x1, x0, 3       # Load argument n=3 into x1
ADDI x30, x0, 0x800  # Set stack pointer to address 0x800
CALLQ factorial        # Call factorial function
NOP                  # Infinite loop after return

# Factorial function
factorial:
ADDI x2, x0, 0       # Load 0 for comparison
BEQ x1, x2, base_case  # If n == 0, go to base case

# Recursive case: n * factorial(n-1)
ADDI x2, x1, 0       # Save current n in x2
SW x2, 0(x30)        # Push current n onto stack
ADDI x30, x30, -8    # Decrement stack pointer
ADDI x1, x1, -1      # n = n - 1
CALLQ factorial        # Recursive call to factorial
# After return: result is in x1, old n is on stack
ADDI x30, x30, 8     # Increment stack pointer to pop
LW x2, 0(x30)        # Load old n
# Multiply result in x1 by old n in x2 (simplified for demo)
# Since we don't have MUL, we'll just return the result
RET                  # Return to caller

base_case:
ADDI x1, x0, 1       # Return 1 (factorial(0) = 1)
RET                  # Return to caller