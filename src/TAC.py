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
        # Saltar declaraciones de funciones y parámetros
        if line.startswith('begin_func') or line.startswith('end_func') or line.startswith('param'):
            continue
            
        # Registrar posiciones de etiquetas en ensamblador
        if line.startswith('L') and ':' in line:
            label = line.split(':')[0]
            label_to_asm[label] = asm_position
            continue
        
        # Manejar operaciones binarias (las comparaciones extra se implementan a continuación)
        if '=' in line and any(op in line.split('=', 1)[1] for op in [' + ', ' - ', ' * ', ' / ', ' < ', ' > ', ' <= ', ' >= ', ' == ', ' != ']):
            target, expr = [part.strip() for part in line.split('=', 1)]
            
            # Asegurar que el target tenga dirección
            if target not in variables:
                variables[target] = next_addr
                data_section.append("0")
                next_addr += 1
            
            target_addr = variables.get(target)
            
            # Si la operación involucra alguna comparación, aseguramos las constantes 0 y 1
            if any(op in expr for op in [' < ', ' > ', ' <= ', ' >= ', ' == ', ' != ']):
                zero_addr = 0  # Ya tenemos 0 en dirección 0
                one_addr = None
                for addr, val in memory_values.items():
                    if val == "1":
                        one_addr = addr
                        break
                if one_addr is None:
                    one_addr = next_addr
                    memory_values[next_addr] = "1"
                    data_section.append("1")
                    next_addr += 1
            
            # Operaciones aritméticas
            if ' + ' in expr:
                left, right = [part.strip() for part in expr.split(' + ')]
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")
                        next_addr += 1
                left_addr = variables.get(left)
                right_addr = variables.get(right)
                code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                asm_position += 1
                code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                asm_position += 1
                code_section.append("ADD R2, R0, R1")
                asm_position += 1
                code_section.append(f"STORE R2, [0x{target_addr:X}]")
                asm_position += 1
                
            elif ' - ' in expr:
                left, right = [part.strip() for part in expr.split(' - ')]
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")
                        next_addr += 1
                left_addr = variables.get(left)
                right_addr = variables.get(right)
                code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                asm_position += 1
                code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                asm_position += 1
                code_section.append("SUB R2, R0, R1")
                asm_position += 1
                code_section.append(f"STORE R2, [0x{target_addr:X}]")
                asm_position += 1
                
            elif ' * ' in expr:
                left, right = [part.strip() for part in expr.split(' * ')]
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")
                        next_addr += 1
                left_addr = variables.get(left)
                right_addr = variables.get(right)
                code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                asm_position += 1
                code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                asm_position += 1
                code_section.append("MUL R2, R0, R1")
                asm_position += 1
                code_section.append(f"STORE R2, [0x{target_addr:X}]")
                asm_position += 1
                
            elif ' / ' in expr:
                left, right = [part.strip() for part in expr.split(' / ')]
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")
                        next_addr += 1
                left_addr = variables.get(left)
                right_addr = variables.get(right)
                code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                asm_position += 1
                code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                asm_position += 1
                code_section.append("DIV R2, R0, R1")
                asm_position += 1
                code_section.append(f"STORE R2, [0x{target_addr:X}]")
                asm_position += 1
            
            # Operador menor que
            elif ' < ' in expr:
                left, right = [part.strip() for part in expr.split(' < ')]
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")
                        next_addr += 1
                left_addr = variables.get(left)
                right_addr = variables.get(right)
                code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                asm_position += 1
                code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                asm_position += 1
                code_section.append("CMP R0, R1")
                asm_position += 1
                code_section.append(f"LOAD R2, [0x{zero_addr:X}]")
                asm_position += 1
                jump_to_true = asm_position + 3
                jump_to_end = asm_position + 5
                code_section.append(f"BLT R0, R1, [0x{jump_to_true:X}]")
                asm_position += 1
                code_section.append(f"JUMP [0x{jump_to_end:X}]")
                asm_position += 1
                code_section.append(f"LOAD R2, [0x{one_addr:X}]")
                asm_position += 1
                code_section.append(f"STORE R2, [0x{target_addr:X}]")
                asm_position += 1

            # Operador mayor que: x > y  ===>  (y < x)
            elif ' > ' in expr:
                left, right = [part.strip() for part in expr.split(' > ')]
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")
                        next_addr += 1
                left_addr = variables.get(left)
                right_addr = variables.get(right)
                code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                asm_position += 1
                code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                asm_position += 1
                code_section.append("CMP R0, R1")
                asm_position += 1
                code_section.append(f"LOAD R2, [0x{zero_addr:X}]")
                asm_position += 1
                jump_to_true = asm_position + 3
                jump_to_end = asm_position + 5
                # For x > y, check if y < x.
                code_section.append(f"BLT R1, R0, [0x{jump_to_true:X}]")
                asm_position += 1
                code_section.append(f"JUMP [0x{jump_to_end:X}]")
                asm_position += 1
                code_section.append(f"LOAD R2, [0x{one_addr:X}]")
                asm_position += 1
                code_section.append(f"STORE R2, [0x{target_addr:X}]")
                asm_position += 1

            # Operador menor o igual: x <= y  ===>  NOT(x > y)
            elif ' <= ' in expr:
                left, right = [part.strip() for part in expr.split(' <= ')]
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")
                        next_addr += 1
                left_addr = variables.get(left)
                right_addr = variables.get(right)
                code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                asm_position += 1
                code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                asm_position += 1
                code_section.append("CMP R0, R1")
                asm_position += 1
                # Compute greater-than result into R3 (x > y)
                code_section.append(f"LOAD R3, [0x{zero_addr:X}]")
                asm_position += 1
                jump_to_gt_true = asm_position + 3
                jump_to_gt_end = asm_position + 5
                code_section.append(f"BLT R1, R0, [0x{jump_to_gt_true:X}]")
                asm_position += 1
                code_section.append(f"JUMP [0x{jump_to_gt_end:X}]")
                asm_position += 1
                code_section.append(f"LOAD R3, [0x{one_addr:X}]")
                asm_position += 1
                # Now result for (x > y) is in R3; x <= y = 1 - (x > y)
                code_section.append(f"LOAD R4, [0x{one_addr:X}]")
                asm_position += 1
                code_section.append("SUB R2, R4, R3")
                asm_position += 1
                code_section.append(f"STORE R2, [0x{target_addr:X}]")
                asm_position += 1

            # Operador mayor o igual: x >= y  ===>  NOT(x < y)
            elif ' >= ' in expr:
                left, right = [part.strip() for part in expr.split(' >= ')]
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")
                        next_addr += 1
                left_addr = variables.get(left)
                right_addr = variables.get(right)
                code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                asm_position += 1
                code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                asm_position += 1
                code_section.append("CMP R0, R1")
                asm_position += 1
                # Compute less-than result into R3 (x < y)
                code_section.append(f"LOAD R3, [0x{zero_addr:X}]")
                asm_position += 1
                jump_to_lt_true = asm_position + 3
                jump_to_lt_end = asm_position + 5
                code_section.append(f"BLT R0, R1, [0x{jump_to_lt_true:X}]")
                asm_position += 1
                code_section.append(f"JUMP [0x{jump_to_lt_end:X}]")
                asm_position += 1
                code_section.append(f"LOAD R3, [0x{one_addr:X}]")
                asm_position += 1
                # x >= y = 1 - (x < y)
                code_section.append(f"LOAD R4, [0x{one_addr:X}]")
                asm_position += 1
                code_section.append("SUB R2, R4, R3")
                asm_position += 1
                code_section.append(f"STORE R2, [0x{target_addr:X}]")
                asm_position += 1

            # Operador igualdad: x == y
            elif ' == ' in expr:
                left, right = [part.strip() for part in expr.split(' == ')]
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")
                        next_addr += 1
                left_addr = variables.get(left)
                right_addr = variables.get(right)
                code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                asm_position += 1
                code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                asm_position += 1
                code_section.append("CMP R0, R1")
                asm_position += 1
                code_section.append(f"LOAD R2, [0x{zero_addr:X}]")
                asm_position += 1
                jump_to_true = asm_position + 3
                jump_to_end = asm_position + 5
                code_section.append(f"BEQ R0, R1, [0x{jump_to_true:X}]")
                asm_position += 1
                code_section.append(f"JUMP [0x{jump_to_end:X}]")
                asm_position += 1
                code_section.append(f"LOAD R2, [0x{one_addr:X}]")
                asm_position += 1
                code_section.append(f"STORE R2, [0x{target_addr:X}]")
                asm_position += 1

            # Operador desigualdad: x != y  ===>  NOT(x == y)
            elif ' != ' in expr:
                left, right = [part.strip() for part in expr.split(' != ')]
                for op in [left, right]:
                    if op not in variables and not op.replace('.', '', 1).isdigit():
                        variables[op] = next_addr
                        data_section.append("0")
                        next_addr += 1
                left_addr = variables.get(left)
                right_addr = variables.get(right)
                code_section.append(f"LOAD R0, [0x{left_addr:X}]")
                asm_position += 1
                code_section.append(f"LOAD R1, [0x{right_addr:X}]")
                asm_position += 1
                code_section.append("CMP R0, R1")
                asm_position += 1
                # Para !=, asumimos true por defecto y cambiamos a false si son iguales.
                code_section.append(f"LOAD R2, [0x{one_addr:X}]")
                asm_position += 1
                jump_to_false = asm_position + 3
                jump_to_end = asm_position + 5
                code_section.append(f"BEQ R0, R1, [0x{jump_to_false:X}]")
                asm_position += 1
                code_section.append(f"JUMP [0x{jump_to_end:X}]")
                asm_position += 1
                code_section.append(f"LOAD R2, [0x{zero_addr:X}]")
                asm_position += 1
                code_section.append(f"STORE R2, [0x{target_addr:X}]")
                asm_position += 1
                
            else:
                code_section.append(f"# Unimplemented binary operation: {expr}")
                asm_position += 1
                
        # Manejar asignaciones de variables (var = algo)
        elif '=' in line and not line.startswith('ifz') and not line.startswith('goto'):
            target, expr = [part.strip() for part in line.split('=', 1)]
            if target not in variables:
                variables[target] = next_addr
                data_section.append("0")
                next_addr += 1
            target_addr = variables.get(target)
            
            # Array allocation: var = new_array size
            if 'new_array' in expr:
                size_match = re.search(r'new_array\s+(\w+)', expr)
                if size_match:
                    size_var = size_match.group(1)
                    if size_var.isdigit():
                        size = int(size_var)
                        base_addr = target_addr + 1
                        code_section.append(f"LOAD R0, [0x{base_addr:X}]")
                        asm_position += 1
                        code_section.append(f"STORE R0, [0x{target_addr:X}]")
                        asm_position += 1
                    else:
                        if size_var not in variables:
                            variables[size_var] = next_addr
                            data_section.append("0")
                            next_addr += 1
                        size_addr = variables[size_var]
                        code_section.append(f"LOAD R0, [0x{size_addr:X}]")
                        asm_position += 1
                        base_addr = target_addr + 1
                        code_section.append(f"LOAD R1, [0x{base_addr:X}]")
                        asm_position += 1
                        code_section.append(f"STORE R1, [0x{target_addr:X}]")
                        asm_position += 1
            
            # Array element access: var = array[index]
            elif '[' in expr and ']' in expr:
                array_access_match = re.search(r'(\w+)\[(\w+)\]', expr)
                if array_access_match:
                    array_var = array_access_match.group(1)
                    index_var = array_access_match.group(2)
                    if array_var not in variables:
                        variables[array_var] = next_addr
                        data_section.append("0")
                        next_addr += 1
                    array_addr = variables[array_var]
                    if index_var.isdigit():
                        index = int(index_var)
                        element_addr = array_addr + 1 + index
                        code_section.append(f"LOAD R0, [0x{element_addr:X}]")
                        asm_position += 1
                        code_section.append(f"STORE R0, [0x{target_addr:X}]")
                        asm_position += 1
                    else:
                        if index_var not in variables:
                            variables[index_var] = next_addr
                            data_section.append("0")
                            next_addr += 1
                        index_addr = variables[index_var]
                        code_section.append(f"LOAD R0, [0x{array_addr:X}]")
                        asm_position += 1
                        code_section.append(f"LOAD R1, [0x{index_addr:X}]")
                        asm_position += 1
                        one_addr = None
                        for addr, val in memory_values.items():
                            if val == "1":
                                one_addr = addr
                                break
                        if one_addr is None:
                            one_addr = next_addr
                            memory_values[next_addr] = "1"
                            data_section.append("1")
                            next_addr += 1
                        code_section.append(f"LOAD R2, [0x{one_addr:X}]")
                        asm_position += 1
                        code_section.append("ADD R1, R1, R2")
                        asm_position += 1
                        code_section.append("ADD R2, R0, R1")
                        asm_position += 1
                        code_section.append("LOAD R3, [0x0]")  # Placeholder for loaded element
                        asm_position += 1
                        code_section.append(f"STORE R3, [0x{target_addr:X}]")
                        asm_position += 1
                else:
                    code_section.append(f"# Invalid array access: {line}")
                    asm_position += 1
            
            # Numeric constants
            elif expr.replace('.', '', 1).isdigit():
                const_addr = None
                for addr, val in memory_values.items():
                    if val == expr:
                        const_addr = addr
                        break
                if const_addr is None:
                    const_addr = next_addr
                    memory_values[next_addr] = expr
                    data_section.append(expr)
                    next_addr += 1
                code_section.append(f"LOAD R0, [0x{const_addr:X}]")
                asm_position += 1
                code_section.append(f"STORE R0, [0x{target_addr:X}]")
                asm_position += 1
            
            # Función call: manejar llamadas a funciones
            elif expr.startswith("call "):
                # Ejemplo: "t73 = call factorial, 1"
                call_expr = expr[5:].strip()  # Quitar "call "
                parts = call_expr.split(',')
                func_name = parts[0].strip()
                num_args = parts[1].strip() if len(parts) > 1 else "0"
                # Suponemos que los parámetros ya se han cargado (líneas 'param')
                code_section.append(f"CALL {func_name}")
                asm_position += 1
                code_section.append(f"STORE R0, [0x{target_addr:X}]")
                asm_position += 1
            
            # Otras asignaciones: var = another_var
            else:
                if expr in variables:
                    source_addr = variables[expr]
                    code_section.append(f"LOAD R0, [0x{source_addr:X}]")
                    asm_position += 1
                    code_section.append(f"STORE R0, [0x{target_addr:X}]")
                    asm_position += 1
                else:
                    code_section.append(f"# Unrecognized expression: {expr}")
                    asm_position += 1
        
        # Manejar asignaciones a elementos de array: array[index] = value
        elif '[' in line and '=' in line and not line.startswith('ifz') and not line.startswith('goto'):
            array_assign_match = re.search(r'(\w+)\[(\w+)\]\s*=\s*(\w+)', line)
            if array_assign_match:
                array_var = array_assign_match.group(1)
                index_var = array_assign_match.group(2)
                value_var = array_assign_match.group(3)
                if array_var not in variables:
                    variables[array_var] = next_addr
                    data_section.append("0")
                    next_addr += 1
                array_addr = variables[array_var]
                if value_var not in variables and not value_var.isdigit():
                    variables[value_var] = next_addr
                    data_section.append("0")
                    next_addr += 1
                value_addr = variables.get(value_var)
                if value_var.isdigit():
                    for addr, val in memory_values.items():
                        if val == value_var:
                            value_addr = addr
                            break
                    if value_addr is None:
                        value_addr = next_addr
                        memory_values[next_addr] = value_var
                        data_section.append(value_var)
                        next_addr += 1
                if index_var.isdigit():
                    index = int(index_var)
                    element_addr = array_addr + 1 + index
                    code_section.append(f"LOAD R0, [0x{value_addr:X}]")
                    asm_position += 1
                    code_section.append(f"STORE R0, [0x{element_addr:X}]")
                    asm_position += 1
                else:
                    if index_var not in variables:
                        variables[index_var] = next_addr
                        data_section.append("0")
                        next_addr += 1
                    index_addr = variables[index_var]
                    code_section.append(f"LOAD R0, [0x{array_addr:X}]")
                    asm_position += 1
                    code_section.append(f"LOAD R1, [0x{index_addr:X}]")
                    asm_position += 1
                    one_addr = None
                    for addr, val in memory_values.items():
                        if val == "1":
                            one_addr = addr
                            break
                    if one_addr is None:
                        one_addr = next_addr
                        memory_values[next_addr] = "1"
                        data_section.append("1")
                        next_addr += 1
                    code_section.append(f"LOAD R2, [0x{one_addr:X}]")
                    asm_position += 1
                    code_section.append("ADD R1, R1, R2")
                    asm_position += 1
                    code_section.append("ADD R2, R0, R1")
                    asm_position += 1
                    code_section.append(f"LOAD R3, [0x{value_addr:X}]")
                    asm_position += 1
                    code_section.append("# Using calculated address in R2 to store from R3 - simulator should handle this")
                    asm_position += 1
                    code_section.append(f"STORE R3, [0x{array_addr+1:X}]  # Placeholder")
                    asm_position += 1
            else:
                code_section.append(f"# Invalid array assignment: {line}")
                asm_position += 1
        
        # Manejar saltos condicionales: ifz t1 goto L2
        elif line.startswith('ifz'):
            parts = line.split()
            condition_var = parts[1]
            goto_label = parts[3]
            if condition_var not in variables:
                variables[condition_var] = next_addr
                data_section.append("0")
                next_addr += 1
            condition_addr = variables.get(condition_var)
            code_section.append(f"LOAD R0, [0x{condition_addr:X}]")
            asm_position += 1
            code_section.append("LOAD R1, [0x0]")
            asm_position += 1
            code_section.append("CMP R0, R1")
            asm_position += 1
            if goto_label in label_to_asm:
                code_section.append(f"BEQ R0, R1, [0x{label_to_asm[goto_label]:X}]")
            else:
                code_section.append(f"BEQ R0, R1, [{goto_label}]")
            asm_position += 1
        
        # Manejar saltos incondicionales: goto L1
        elif line.startswith('goto'):
            goto_label = line.split()[1]
            if goto_label in label_to_asm:
                code_section.append(f"JUMP [0x{label_to_asm[goto_label]:X}]")
            else:
                code_section.append(f"JUMP [{goto_label}]")
            asm_position += 1
        
        # Manejar instrucciones return
        elif line.startswith('return'):
            return_var = line.split()[1]
            if return_var not in variables:
                variables[return_var] = next_addr
                data_section.append("0")
                next_addr += 1
            return_addr = variables.get(return_var)
            code_section.append(f"LOAD R0, [0x{return_addr:X}]")
            asm_position += 1
            code_section.append("RET")
            asm_position += 1
    
    # Última pasada: resolver referencias a etiquetas
    fixed_code_section = []
    for instr in code_section:
        if instr.startswith("#"):
            fixed_code_section.append(instr)
        else:
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
    output_file = tac_file.replace('.tac', '.asm')
    with open(output_file, 'w') as f:
        for data in data_section:
            f.write(f"{data}\n")
        for instr in code_section:
            f.write(f"{instr}\n")
    print(f"\nCódigo ensamblador escrito en {output_file}")

if __name__ == "__main__":
    main()
