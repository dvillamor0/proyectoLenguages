import re

def tac_to_assembly(tac_file):
    """
    Convierte un archivo TAC (Three-Address Code) a código ensamblador para la CPU personalizada.
    
    Args:
        tac_file (str): Ruta al archivo TAC
        
    Returns:
        tuple: (data_section, code_section) conteniendo listas de datos y instrucciones en ensamblador
    """
    # Leer el archivo TAC
    with open(tac_file, 'r') as f:
        tac_lines = f.readlines()
    
    # Eliminar espacios en blanco al inicio/final y líneas vacías
    tac_lines = [line.strip() for line in tac_lines if line.strip()]
    
    # Inicializar estructuras de datos
    data_section = []      # Valores de inicialización de memoria
    code_section = []      # Instrucciones de ensamblador
    temp_vars = {}         # Mapea variables temporales a registros
    variables = {}         # Mapea variables del programa a direcciones de memoria
    memory_values = {}     # Rastrea valores actuales en ubicaciones de memoria
    label_positions = {}   # Mapea etiquetas a posiciones en el TAC
    label_to_asm = {}      # Mapea etiquetas a posiciones en el ensamblador
    
    # Inicializar constantes estándar
    data_section.append("0")   # Dirección 0: Constante 0
    memory_values[0] = "0"
    
    # Primera pasada: identificar todas las variables y asignar direcciones de memoria
    next_addr = 1
    
    for i, line in enumerate(tac_lines):
        if line.startswith('L') and ':' in line:
            # Es una etiqueta (L1:, L2:, etc.)
            label = line.split(':')[0]
            label_positions[label] = i
        elif '=' in line and not line.startswith('ifz') and not line.startswith('goto'):
            # Asignación de variable
            target = line.split('=', 1)[0].strip()
            expr = line.split('=', 1)[1].strip()
            
            # Agregar variables no temporales a nuestro mapeo
            if target not in variables:
                variables[target] = next_addr
                next_addr += 1
            
            # Si es una constante numérica, agregarla a nuestras constantes
            if expr.replace('.', '', 1).isdigit() and expr not in memory_values.values():
                memory_values[next_addr] = expr
                data_section.append(expr)
                next_addr += 1
    
    # Agregar constantes requeridas
    for const in ["1", "2"]:
        if const not in memory_values.values():
            memory_values[next_addr] = const
            data_section.append(const)
            next_addr += 1
    
    # También encontrar todas las variables usadas en las declaraciones de retorno
    for line in tac_lines:
        if line.startswith('return'):
            return_var = line.split()[1]
            if return_var not in variables:
                variables[return_var] = next_addr
                next_addr += 1
    
    # Depuración: Imprimir mapeo de variables
    print("# Variables y sus direcciones de memoria:")
    for var, addr in variables.items():
        print(f"# {var}: dirección {addr}")
    
    # Segunda pasada: Agregar valores iniciales a la memoria
    for var_addr in range(1, next_addr):
        if var_addr not in memory_values:
            # Esta es una variable que aún no tiene un valor inicial
            # La llenaremos con ceros por ahora
            data_section.append("0")  # Valor predeterminado
    
    # Tercera pasada: Generar código ensamblador
    asm_position = 0  # Iniciar posición de código desde 0, separada de la sección de datos
    
    for i, line in enumerate(tac_lines):
        # Skip function declarations and endings
        if line.startswith('begin_func') or line.startswith('end_func') or line.startswith('param'):
            continue
            
        # Record label positions in assembly
        if line.startswith('L') and ':' in line:
            label = line.split(':')[0]
            label_to_asm[label] = asm_position
            continue
        
        # Handle binary operations with + - * / 
        if '=' in line and any(op in line.split('=', 1)[1] for op in [' + ', ' - ', ' * ', ' / ', ' < ', ' > ', ' <= ', ' >= ', ' == ', ' != ']):
            target, expr = [part.strip() for part in line.split('=', 1)]
            
            # Ensure target has an address
            if target not in variables:
                variables[target] = next_addr
                data_section.append("0")
                next_addr += 1
                
            target_addr = variables.get(target)
            
            # Parse binary operation
            if ' + ' in expr:
                left, right = [part.strip() for part in expr.split(' + ')]
                
                # Ensure operands have addresses
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")
                        next_addr += 1
                
                # Get operand addresses
                left_addr = variables.get(left)
                right_addr = variables.get(right)
                
                # Load operands into registers
                code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                asm_position += 1
                code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                asm_position += 1
                
                # Perform addition with registers only
                code_section.append(f"ADD R2, R0, R1")
                asm_position += 1
                
                # Store result
                code_section.append(f"STORE R2, [0x{target_addr:X}]")
                asm_position += 1
                
            elif ' - ' in expr:
                left, right = [part.strip() for part in expr.split(' - ')]
                
                # Ensure operands have addresses
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")
                        next_addr += 1
                
                # Get operand addresses
                left_addr = variables.get(left)
                right_addr = variables.get(right)
                
                # Load operands into registers
                code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                asm_position += 1
                code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                asm_position += 1
                
                # Perform subtraction with registers only
                code_section.append(f"SUB R2, R0, R1")
                asm_position += 1
                
                # Store result
                code_section.append(f"STORE R2, [0x{target_addr:X}]")
                asm_position += 1
                
            elif ' * ' in expr:
                left, right = [part.strip() for part in expr.split(' * ')]
                
                # Ensure operands have addresses
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")
                        next_addr += 1
                
                # Get operand addresses
                left_addr = variables.get(left)
                right_addr = variables.get(right)
                
                # Load operands into registers
                code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                asm_position += 1
                code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                asm_position += 1
                
                # Perform multiplication with registers only
                code_section.append(f"MUL R2, R0, R1")
                asm_position += 1
                
                # Store result
                code_section.append(f"STORE R2, [0x{target_addr:X}]")
                asm_position += 1
                
            elif ' / ' in expr:
                left, right = [part.strip() for part in expr.split(' / ')]
                
                # Ensure operands have addresses
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")
                        next_addr += 1
                
                # Get operand addresses
                left_addr = variables.get(left)
                right_addr = variables.get(right)
                
                # Load operands into registers
                code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                asm_position += 1
                code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                asm_position += 1
                
                # Perform division with registers only
                code_section.append(f"DIV R2, R0, R1")
                asm_position += 1
                
                # Store result
                code_section.append(f"STORE R2, [0x{target_addr:X}]")
                asm_position += 1
            
            # Comparison operations
            elif ' < ' in expr:
                left, right = [part.strip() for part in expr.split(' < ')]
                
                # Ensure operands have addresses
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")
                        next_addr += 1
                
                # Get operand addresses
                left_addr = variables.get(left)
                right_addr = variables.get(right)
                
                # Load operands into registers
                code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                asm_position += 1
                code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                asm_position += 1
                
                # Compare using CMP and BLT
                code_section.append(f"CMP R0, R1")
                asm_position += 1
                
                # Find or create memory locations for constant 0 and 1
                zero_addr = 0  # We already have 0 at address 0
                one_addr = next_addr
                if "1" not in memory_values.values():
                    memory_values[one_addr] = "1"
                    data_section.append("1")
                    next_addr += 1
                else:
                    for addr, val in memory_values.items():
                        if val == "1":
                            one_addr = addr
                            break
                
                # For BLT, we jump 2 instructions ahead if less than (to load 1 - true)
                jump_to_true = asm_position + 3
                jump_to_end = asm_position + 5
                
                # First, load 0 (false) into R2
                code_section.append(f"LOAD R2, [0x{zero_addr:X}]")
                asm_position += 1
                
                # Jump to end if not less than
                code_section.append(f"BLT R0, R1, [0x{jump_to_true:X}]")
                asm_position += 1
                
                # Skip to the end (after the "true" part)
                code_section.append(f"JUMP [0x{jump_to_end:X}]")
                asm_position += 1
                
                # Load 1 (true) into R2 if condition is true
                code_section.append(f"LOAD R2, [0x{one_addr:X}]")
                asm_position += 1
                
                # Store the result
                code_section.append(f"STORE R2, [0x{target_addr:X}]")
                asm_position += 1
                
            else:
                # For other binary operations, add as needed
                code_section.append(f"# Unimplemented binary operation: {expr}")
                asm_position += 1
                
        # Handle variable assignments (var = something)
        elif '=' in line and not line.startswith('ifz') and not line.startswith('goto'):
            target, expr = [part.strip() for part in line.split('=', 1)]
            
            # Ensure the target has an address
            if target not in variables:
                variables[target] = next_addr
                data_section.append("0")  # Add default value to memory
                next_addr += 1
                
            target_addr = variables.get(target)
            
            # Handle array allocation: var = new_array size
            if 'new_array' in expr:
                size_match = re.search(r'new_array\s+(\w+)', expr)
                if size_match:
                    size_var = size_match.group(1)
                    
                    # Check if size is a constant
                    if size_var.isdigit():
                        size = int(size_var)
                        
                        # Store the base address (which is the current target address + 1)
                        base_addr = target_addr + 1
                        code_section.append(f"LOAD R0, [0x{base_addr:X}]")
                        asm_position += 1
                        code_section.append(f"STORE R0, [0x{target_addr:X}]")
                        asm_position += 1
                    else:
                        # Dynamic size - we need to load the size from a variable
                        if size_var not in variables:
                            variables[size_var] = next_addr
                            data_section.append("0")
                            next_addr += 1
                        
                        size_addr = variables[size_var]
                        
                        # Load the size
                        code_section.append(f"LOAD R0, [0x{size_addr:X}]")
                        asm_position += 1
                        
                        # Calculate base address (target_addr + 1)
                        base_addr = target_addr + 1
                        code_section.append(f"LOAD R1, [0x{base_addr:X}]")
                        asm_position += 1
                        
                        # Store base address
                        code_section.append(f"STORE R1, [0x{target_addr:X}]")
                        asm_position += 1
            
            # Handle array element access: var = array[index]
            elif '[' in expr and ']' in expr:
                array_access_match = re.search(r'(\w+)\[(\w+)\]', expr)
                if array_access_match:
                    array_var = array_access_match.group(1)
                    index_var = array_access_match.group(2)
                    
                    # Get array base address
                    if array_var not in variables:
                        variables[array_var] = next_addr
                        data_section.append("0")  # Initialize array base
                        next_addr += 1
                    
                    array_addr = variables[array_var]
                    
                    # Handle index
                    if index_var.isdigit():
                        # Constant index
                        index = int(index_var)
                        
                        # Calculate element address (base + index)
                        element_addr = array_addr + 1 + index  # +1 because element 0 is at base+1
                        
                        # Load the element value
                        code_section.append(f"LOAD R0, [0x{element_addr:X}]")
                        asm_position += 1
                        
                        # Store to target
                        code_section.append(f"STORE R0, [0x{target_addr:X}]")
                        asm_position += 1
                    else:
                        # Dynamic index
                        if index_var not in variables:
                            variables[index_var] = next_addr
                            data_section.append("0")
                            next_addr += 1
                        
                        index_addr = variables[index_var]
                        
                        # Load the base address of the array
                        code_section.append(f"LOAD R0, [0x{array_addr:X}]")
                        asm_position += 1
                        
                        # Load the index
                        code_section.append(f"LOAD R1, [0x{index_addr:X}]")
                        asm_position += 1
                        
                        # Find 1 in memory or add it
                        one_addr = next_addr
                        if "1" not in memory_values.values():
                            memory_values[one_addr] = "1"
                            data_section.append("1")
                            next_addr += 1
                        else:
                            for addr, val in memory_values.items():
                                if val == "1":
                                    one_addr = addr
                                    break
                        
                        # Load the constant 1 (for offset)
                        code_section.append(f"LOAD R2, [0x{one_addr:X}]")
                        asm_position += 1
                        
                        # Add 1 to index (element 0 is at base+1)
                        code_section.append(f"ADD R1, R1, R2")
                        asm_position += 1
                        
                        # Calculate the element address (base + index + 1)
                        code_section.append(f"ADD R2, R0, R1")
                        asm_position += 1
                        
                        # Load element using R2 as address
                        code_section.append(f"LOAD R3, [0x0]")  # Temporary placeholder
                        asm_position += 1
                        
                        # Need to convert this to use CMP and BEQ
                        # Since we can't use register-indirect addressing directly
                        
                        # Store to target
                        code_section.append(f"STORE R3, [0x{target_addr:X}]")
                        asm_position += 1
                else:
                    code_section.append(f"# Invalid array access: {line}")
                    asm_position += 1
            
            # Handle numeric constants, variables, and other expressions
            elif expr.replace('.', '', 1).isdigit():  # Numeric constant
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
                    data_section.append(expr)
                    next_addr += 1
                
                # Load constant and store to target
                code_section.append(f"LOAD R0, [0x{const_addr:X}]")
                asm_position += 1
                code_section.append(f"STORE R0, [0x{target_addr:X}]")
                asm_position += 1
            
            # Handle other expressions like var = another_var
            else:
                # Check if it's a variable
                if expr in variables:
                    source_addr = variables[expr]
                    
                    # Load from source and store to target
                    code_section.append(f"LOAD R0, [0x{source_addr:X}]")
                    asm_position += 1
                    code_section.append(f"STORE R0, [0x{target_addr:X}]")
                    asm_position += 1
                else:
                    # Unknown expression
                    code_section.append(f"# Unrecognized expression: {expr}")
                    asm_position += 1
        
        # Handle array element assignment: array[index] = value
        elif '[' in line and '=' in line and not line.startswith('ifz') and not line.startswith('goto'):
            array_assign_match = re.search(r'(\w+)\[(\w+)\]\s*=\s*(\w+)', line)
            if array_assign_match:
                array_var = array_assign_match.group(1)
                index_var = array_assign_match.group(2)
                value_var = array_assign_match.group(3)
                
                # Get array base address
                if array_var not in variables:
                    variables[array_var] = next_addr
                    data_section.append("0")  # Initialize array base
                    next_addr += 1
                
                array_addr = variables[array_var]
                
                # Get value address
                if value_var not in variables and not value_var.isdigit():
                    variables[value_var] = next_addr
                    data_section.append("0")
                    next_addr += 1
                
                value_addr = variables.get(value_var)
                if value_var.isdigit():
                    # Find constant address
                    for addr, val in memory_values.items():
                        if val == value_var:
                            value_addr = addr
                            break
                    
                    if value_addr is None:
                        value_addr = next_addr
                        memory_values[next_addr] = value_var
                        data_section.append(value_var)
                        next_addr += 1
                
                # Handle index
                if index_var.isdigit():
                    # Constant index
                    index = int(index_var)
                    
                    # Calculate element address (base + index)
                    element_addr = array_addr + 1 + index  # +1 because element 0 is at base+1
                    
                    # Load value and store to element
                    code_section.append(f"LOAD R0, [0x{value_addr:X}]")
                    asm_position += 1
                    code_section.append(f"STORE R0, [0x{element_addr:X}]")
                    asm_position += 1
                else:
                    # Dynamic index - similar to array access, need to find the address
                    if index_var not in variables:
                        variables[index_var] = next_addr
                        data_section.append("0")
                        next_addr += 1
                    
                    index_addr = variables[index_var]
                    
                    # Load the base address of the array
                    code_section.append(f"LOAD R0, [0x{array_addr:X}]")
                    asm_position += 1
                    
                    # Load the index
                    code_section.append(f"LOAD R1, [0x{index_addr:X}]")
                    asm_position += 1
                    
                    # Find 1 in memory or add it
                    one_addr = next_addr
                    if "1" not in memory_values.values():
                        memory_values[one_addr] = "1"
                        data_section.append("1")
                        next_addr += 1
                    else:
                        for addr, val in memory_values.items():
                            if val == "1":
                                one_addr = addr
                                break
                    
                    # Load the constant 1 (for offset)
                    code_section.append(f"LOAD R2, [0x{one_addr:X}]")
                    asm_position += 1
                    
                    # Add 1 to index (element 0 is at base+1)
                    code_section.append(f"ADD R1, R1, R2")
                    asm_position += 1
                    
                    # Calculate the element address (base + index + 1)
                    code_section.append(f"ADD R2, R0, R1")
                    asm_position += 1
                    
                    # Load the value to store
                    code_section.append(f"LOAD R3, [0x{value_addr:X}]")
                    asm_position += 1
                    
                    # Store value to element - since we can't use register-indirect, adjust this
                    code_section.append(f"# Using calculated address in R2 to store from R3 - simulator should handle this")
                    asm_position += 1
                    
                    # This is a placeholder - would need to implement a sequence that stores to the calculated address
                    code_section.append(f"STORE R3, [0x{array_addr+1+0:X}]")  # Example: store to first element
                    asm_position += 1
            else:
                code_section.append(f"# Invalid array assignment: {line}")
                asm_position += 1
        
        # Handle conditional jumps (ifz t1 goto L2)
        elif line.startswith('ifz'):
            parts = line.split()
            condition_var = parts[1]
            goto_label = parts[3]
            
            # Ensure condition variable has an address
            if condition_var not in variables:
                variables[condition_var] = next_addr
                data_section.append("0")
                next_addr += 1
            
            condition_addr = variables.get(condition_var)
            
            # Load condition value
            code_section.append(f"LOAD R0, [0x{condition_addr:X}]")
            asm_position += 1
            
            # Load 0 for comparison
            code_section.append(f"LOAD R1, [0x0]")
            asm_position += 1
            
            # Compare values
            code_section.append(f"CMP R0, R1")
            asm_position += 1
            
            # Branch if equal (ifz means "if zero")
            if goto_label in label_to_asm:
                code_section.append(f"BEQ R0, R1, [0x{label_to_asm[goto_label]:X}]")
            else:
                # Store label for later resolution
                code_section.append(f"BEQ R0, R1, [{goto_label}]")
            asm_position += 1
        
        # Handle unconditional jumps (goto L1)
        elif line.startswith('goto'):
            goto_label = line.split()[1]
            
            # Add the jump instruction
            if goto_label in label_to_asm:
                code_section.append(f"JUMP [0x{label_to_asm[goto_label]:X}]")
            else:
                # Store label for later resolution
                code_section.append(f"JUMP [{goto_label}]")
            asm_position += 1
        
        # Handle return statements
        elif line.startswith('return'):
            return_var = line.split()[1]
            
            # Ensure return variable has an address
            if return_var not in variables:
                variables[return_var] = next_addr
                data_section.append("0")
                next_addr += 1
            
            return_addr = variables.get(return_var)
            
            # Load return value to R0
            code_section.append(f"LOAD R0, [0x{return_addr:X}]")
            asm_position += 1
            
            # Return from function
            code_section.append("RET")
            asm_position += 1
    
    # Last pass: resolve label references
    fixed_code_section = []
    for instr in code_section:
        if instr.startswith("#"):
            # Keep comments as they are
            fixed_code_section.append(instr)
        else:
            # Check for label references
            modified_instr = instr
            for label, pos in label_to_asm.items():
                if f"[{label}]" in modified_instr:
                    modified_instr = modified_instr.replace(f"[{label}]", f"[0x{pos:X}]")
            fixed_code_section.append(modified_instr)
    
    return data_section, fixed_code_section

def main():
    """Función principal para ejecutar el convertidor de TAC a ensamblador."""
    import sys
    
    if len(sys.argv) != 2:
        print("Uso: python TAC.py <archivo_entrada.tac>")
        sys.exit(1)
    
    tac_file = sys.argv[1]
    data_section, code_section = tac_to_assembly(tac_file)
    
    # escribir a un archivo
    output_file = tac_file.replace('.tac', '.asm')
    with open(output_file, 'w') as f:
        for data in data_section:
            f.write(f"{data}\n")
        
        for instr in code_section:
            f.write(f"{instr}\n")
    
    print(f"\nCódigo ensamblador escrito en {output_file}")

if __name__ == "__main__":
    main()