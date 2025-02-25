def tac_to_assembly(tac_file):
    """
    Convert a TAC (Three-Address Code) file to assembly code for the custom CPU.
    
    Args:
        tac_file (str): Path to the TAC file
        
    Returns:
        list: List of assembly instructions
    """
    # Read the TAC file
    with open(tac_file, 'r') as f:
        tac_lines = f.readlines()
    
    # Remove leading/trailing whitespace and empty lines
    tac_lines = [line.strip() for line in tac_lines if line.strip()]
    
    # Initialize data structures
    assembly = []          # The final assembly code
    temp_vars = {}         # Maps temporary variables to registers
    variables = {}         # Maps program variables to memory addresses
    memory_values = {}     # Tracks actual values at memory locations
    label_positions = {}   # Maps labels to positions in the TAC
    label_to_asm = {}      # Maps labels to positions in the assembly
    
    # Initialize standard constants
    assembly.append("0")   # Address 0: Constant 0
    assembly.append("1")   # Address 1: Constant 1
    assembly.append("2")   # Address 2: Constant 2
    memory_values[0] = "0"
    memory_values[1] = "1" 
    memory_values[2] = "2"
    
    # Memory allocation starts at address 3
    next_addr = 3
    
    # First pass: identify all variables and assign memory addresses
    for i, line in enumerate(tac_lines):
        if line.startswith('L') and ':' in line:
            # It's a label (L1:, L2:, etc.)
            label = line.split(':')[0]
            label_positions[label] = i
        elif '=' in line and not line.startswith('ifz') and not line.startswith('goto'):
            # Variable assignment
            target = line.split('=', 1)[0].strip()
            expr = line.split('=', 1)[1].strip()
            
            # Add non-temporary variables to our mapping
            if not target.startswith('t') and target not in variables:
                variables[target] = next_addr
                next_addr += 1
            
            # If it's a numeric constant, add it to our constants
            if expr.replace('.', '', 1).isdigit() and expr not in memory_values.values():
                memory_values[next_addr] = expr
                assembly.append(expr)
                next_addr += 1
    
    # Debug: Print variable mapping
    print("# Variables and their memory addresses:")
    for var, addr in variables.items():
        print(f"# {var}: address {addr}")
    
    # Second pass: Add initial values to memory
    for var_addr in range(3, next_addr):
        if var_addr not in memory_values:
            # This is a variable that doesn't have an initial value yet
            # We'll fill it with zeros for now
            assembly.append("0.0")  # Default value
    
    # Third pass: Generate assembly code
    asm_position = len(assembly)  # Start after constants and initial values
    
    for i, line in enumerate(tac_lines):
        # Skip function declarations and endings
        if line.startswith('begin_func') or line.startswith('end_func'):
            continue
            
        # Record label positions in assembly
        if line.startswith('L') and ':' in line:
            label = line.split(':')[0]
            label_to_asm[label] = asm_position
            continue
        
        # Handle variable assignments (var = something)
        if '=' in line and not line.startswith('ifz') and not line.startswith('goto'):
            target, expr = [part.strip() for part in line.split('=', 1)]
            
            # Handle different types of expressions
            if expr.replace('.', '', 1).isdigit():  # It's a numeric constant
                # Find where the constant is stored
                const_addr = None
                for addr, val in memory_values.items():
                    if val == expr:
                        const_addr = addr
                        break
                
                if const_addr is None:
                    # Add the constant to memory
                    const_addr = next_addr
                    memory_values[next_addr] = expr
                    assembly.append(expr)
                    next_addr += 1
                    asm_position += 1
                
                # Load the constant into a register
                r0 = 0  # Use R0 for constants
                assembly.append(f"LOAD R{r0}, [{const_addr}]")
                asm_position += 1
                
                # If it's a program variable, store it
                if not target.startswith('t'):
                    target_addr = variables[target]
                    assembly.append(f"STORE R{r0}, [{target_addr}]")
                    asm_position += 1
                
                # Keep track of which register has the value
                temp_vars[target] = r0
            
            elif '!=' in expr:  # Not equal comparison
                operands = expr.split('!=')
                left = operands[0].strip()
                right = operands[1].strip()
                
                # Load the left operand
                r0 = 0
                if left in variables:
                    left_addr = variables[left]
                    assembly.append(f"LOAD R{r0}, [{left_addr}]")
                    asm_position += 1
                elif left in temp_vars:
                    r0 = temp_vars[left]
                
                # Load the right operand
                r1 = 1
                if right in variables:
                    right_addr = variables[right]
                    assembly.append(f"LOAD R{r1}, [{right_addr}]")
                    asm_position += 1
                elif right in temp_vars:
                    r1 = temp_vars[right]
                
                # Compare the values
                assembly.append(f"CMP R{r0}, R{r1}")
                asm_position += 1
                
                # The result of != is the opposite of equality
                # Store 1 in a register to indicate they're not equal
                # This will be used with BEQ in the ifz instruction
                r2 = 2
                assembly.append(f"BNE R{r0}, R{r1}, [SKIP1]")
                asm_position += 1
                
                # If we get here, they were equal (result = 0)
                assembly.append(f"LOAD R{r2}, [0]")  # Load 0 (false)
                asm_position += 1
                assembly.append(f"JUMP [SKIP2]")
                asm_position += 1
                
                # SKIP1: They were not equal (result = 1)
                label_to_asm["SKIP1"] = asm_position
                assembly.append(f"LOAD R{r2}, [1]")  # Load 1 (true)
                asm_position += 1
                
                # SKIP2: Continue with the next instruction
                label_to_asm["SKIP2"] = asm_position
                
                # The comparison result is in r2
                temp_vars[target] = r2
            
            elif '/' in expr:  # Division operation
                operands = expr.split('/')
                left = operands[0].strip()
                right = operands[1].strip()
                
                # Load the left operand
                r0 = 0
                if left in variables:
                    left_addr = variables[left]
                    assembly.append(f"LOAD R{r0}, [{left_addr}]")
                    asm_position += 1
                elif left in temp_vars:
                    r0 = temp_vars[left]
                
                # Load the right operand
                r1 = 1
                if right in variables:
                    right_addr = variables[right]
                    assembly.append(f"LOAD R{r1}, [{right_addr}]")
                    asm_position += 1
                elif right in temp_vars:
                    r1 = temp_vars[right]
                elif right == "2":  # Special case for division by 2
                    assembly.append(f"LOAD R{r1}, [2]")  # Load constant 2
                    asm_position += 1
                
                # Perform the division
                r2 = 2  # Result goes in R2
                assembly.append(f"DIV R{r2}, R{r0}, R{r1}")
                asm_position += 1
                
                # If it's a program variable, store the result
                if not target.startswith('t'):
                    target_addr = variables[target]
                    assembly.append(f"STORE R{r2}, [{target_addr}]")
                    asm_position += 1
                
                # Keep track of which register has the value
                temp_vars[target] = r2
            
            elif '+' in expr:  # Addition operation
                operands = expr.split('+')
                left = operands[0].strip()
                right = operands[1].strip()
                
                # Load the left operand
                r0 = 0
                if left in variables:
                    left_addr = variables[left]
                    assembly.append(f"LOAD R{r0}, [{left_addr}]")
                    asm_position += 1
                elif left in temp_vars:
                    r0 = temp_vars[left]
                
                # Load the right operand
                r1 = 1
                if right in variables:
                    right_addr = variables[right]
                    assembly.append(f"LOAD R{r1}, [{right_addr}]")
                    asm_position += 1
                elif right in temp_vars:
                    r1 = temp_vars[right]
                
                # Perform the addition
                r3 = 3  # Result goes in R3
                assembly.append(f"ADD R{r3}, R{r0}, R{r1}")
                asm_position += 1
                
                # If it's a program variable, store the result
                if not target.startswith('t'):
                    target_addr = variables[target]
                    assembly.append(f"STORE R{r3}, [{target_addr}]")
                    asm_position += 1
                
                # Keep track of which register has the value
                temp_vars[target] = r3
            
            else:  # Simple variable assignment (target = var)
                # Find the value we're assigning from
                src_reg = None
                if expr in variables:
                    src_addr = variables[expr]
                    r0 = 0
                    assembly.append(f"LOAD R{r0}, [{src_addr}]")
                    asm_position += 1
                    src_reg = r0
                elif expr in temp_vars:
                    src_reg = temp_vars[expr]
                
                # If it's a program variable, store the value
                if not target.startswith('t') and src_reg is not None:
                    target_addr = variables[target]
                    assembly.append(f"STORE R{src_reg}, [{target_addr}]")
                    asm_position += 1
                
                # Keep track of which register has the value
                if src_reg is not None:
                    temp_vars[target] = src_reg
        
        # Handle conditional jumps (ifz t1 goto L2)
        elif line.startswith('ifz'):
            parts = line.split()
            condition_var = parts[1]
            goto_label = parts[3]
            
            # The condition should already be in a register from a previous comparison
            condition_reg = None
            if condition_var in temp_vars:
                condition_reg = temp_vars[condition_var]
            
            # If it's not, we need to load it
            if condition_reg is None:
                r0 = 0
                if condition_var in variables:
                    condition_addr = variables[condition_var]
                    assembly.append(f"LOAD R{r0}, [{condition_addr}]")
                    asm_position += 1
                    condition_reg = r0
            
            # Load 0 for comparison (since ifz means "if zero")
            r1 = 1
            assembly.append(f"LOAD R{r1}, [0]")
            asm_position += 1
            
            # Add the branch instruction with a placeholder for the target
            if goto_label in label_to_asm:
                target_addr = label_to_asm[goto_label]
                assembly.append(f"BEQ R{condition_reg}, R{r1}, [{target_addr:X}]")
            else:
                assembly.append(f"BEQ R{condition_reg}, R{r1}, [PLACEHOLDER_{goto_label}]")
            asm_position += 1
        
        # Handle unconditional jumps (goto L1)
        elif line.startswith('goto'):
            goto_label = line.split()[1]
            
            # Add the jump instruction with a placeholder for the target
            if goto_label in label_to_asm:
                target_addr = label_to_asm[goto_label]
                assembly.append(f"JUMP [{target_addr:X}]")
            else:
                assembly.append(f"JUMP [PLACEHOLDER_{goto_label}]")
            asm_position += 1
        
        # Handle return statements
        elif line.startswith('return'):
            return_var = line.split()[1]
            
            # Load the return value into a register
            r0 = 0
            if return_var in variables:
                return_addr = variables[return_var]
                assembly.append(f"LOAD R{r0}, [{return_addr}]")
                asm_position += 1
            elif return_var in temp_vars:
                r0 = temp_vars[return_var]
            
            # Store to the designated return location
            assembly.append(f"STORE R{r0}, [0x14]")
            asm_position += 1
            
            # End the program
            assembly.append("HALT")
            asm_position += 1
    
    # Final pass: resolve label references
    for i, instr in enumerate(assembly):
        if "PLACEHOLDER_" in instr:
            for label, pos in label_to_asm.items():
                placeholder = f"PLACEHOLDER_{label}"
                if placeholder in instr:
                    assembly[i] = instr.replace(f"[{placeholder}]", f"[{pos:X}]")
        elif "SKIP1" in instr or "SKIP2" in instr:
            for label, pos in label_to_asm.items():
                if label in instr:
                    assembly[i] = instr.replace(f"[{label}]", f"[{pos:X}]")
    
    return assembly

def main():
    """Main function to run the TAC to assembly converter."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python tac_to_assembly.py <input_file.tac>")
        sys.exit(1)
    
    tac_file = sys.argv[1]
    asm_instructions = tac_to_assembly(tac_file)
    
    # Print the generated assembly
    for instruction in asm_instructions:
        print(instruction)
    
    # Also write to a file
    output_file = tac_file.replace('.tac', '.asm')
    with open(output_file, 'w') as f:
        for instruction in asm_instructions:
            f.write(f"{instruction}\n")
    
    print(f"\nAssembly code written to {output_file}")

if __name__ == "__main__":
    main()