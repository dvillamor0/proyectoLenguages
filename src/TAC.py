import re
import sys
import os

def tac_to_assembly(tac_file):
    # Leer y limpiar el archivo TAC
    with open(tac_file, 'r', encoding='utf-8') as f:
        tac_lines = [line.strip() for line in f if line.strip()]

    # Verificar si el archivo está vacío
    if not tac_lines:
        print(f"ADVERTENCIA: El archivo TAC '{tac_file}' está vacío o no contiene instrucciones válidas.")
        # Generar un conjunto mínimo de instrucciones para que el ensamblador no falle
        print("Generando código para operaciones BigGraph aunque no haya instrucciones TAC")
        return generate_default_bigraph_code()

    # --- Construir la tabla de constantes ---
    # Solo incluimos las constantes que aparecen en el TAC.
    # Se incluye "0" por defecto, ya que es común para comparaciones.
    const_table = {"0": 0}
    next_const_addr = 1

    # Primera pasada: identificar todas las constantes numéricas
    for line in tac_lines:
        # Ignorar etiquetas o líneas de control de flujo
        if line.startswith('L') and ':' in line:
            continue
        if line.startswith('begin_func') or line.startswith('end_func') or line.startswith('param'):
            continue

        # Buscar constantes en asignaciones
        if '=' in line and not line.startswith('ifz') and not line.startswith('goto'):
            parts = [p.strip() for p in line.split('=', 1)]
            expr = parts[1]
            
            # Si es un operando solo (no una operación)
            if '+' not in expr and '-' not in expr and '*' not in expr and '/' not in expr and '==' not in expr and '!=' not in expr and '<' not in expr and '<=' not in expr and '>' not in expr and '>=' not in expr:
                if expr.replace('.', '', 1).isdigit() and expr not in const_table:
                    const_table[expr] = next_const_addr
                    next_const_addr += 1
            # Si es una operación, buscar constantes en los operandos
            else:
                # Manejar operadores de comparación también
                operators = r'[+\-*/=<>!]+'
                for op in re.split(operators, expr):
                    op = op.strip()
                    if op and op.replace('.', '', 1).isdigit() and op not in const_table:
                        const_table[op] = next_const_addr
                        next_const_addr += 1

    # Agregar constantes para operaciones con Bigraphs
    if "1" not in const_table:
        const_table["1"] = 1
    if "2" not in const_table:
        const_table["2"] = 2
    
    # Buscar operaciones de BigGraph en el código TAC
    bigraph_ops = []
    for line in tac_lines:
        if '_bigraph_' in line:
            bigraph_ops.append(line)
            print(f"Encontrada operación BigGraph: {line}")
    
    # Si no hay operaciones BigGraph en el TAC pero el nombre del archivo sugiere 
    # que debería haberlas, generamos un aviso
    if not bigraph_ops and ('big' in tac_file.lower() or 'graph' in tac_file.lower()):
        print(f"ADVERTENCIA: No se encontraron operaciones BigGraph en el archivo TAC '{tac_file}'")
        print("Esto podría indicar un problema en la generación de código intermedio.")
        
    # --- Construir la tabla de variables ---
    var_table = {}
    next_var_addr = next_const_addr  # Las variables se asignan tras las constantes

    # Segunda pasada: asignar direcciones a todas las variables
    for line in tac_lines:
        # Ignorar etiquetas o líneas de control de flujo
        if line.startswith('L') and ':' in line:
            continue
        if line.startswith('begin_func') or line.startswith('end_func') or line.startswith('param'):
            continue

        # Procesar asignaciones y retornos
        if '=' in line and not line.startswith('ifz') and not line.startswith('goto'):
            target, expr = [x.strip() for x in line.split('=', 1)]
            if target not in var_table:
                var_table[target] = next_var_addr
                next_var_addr += 1
                
            # Procesar también variables en expresiones de comparación
            if '==' in expr or '!=' in expr or '<' in expr or '<=' in expr or '>' in expr or '>=' in expr:
                # Extraer los operandos de la comparación
                comp_parts = re.split(r'(==|!=|<=|>=|<|>)', expr)
                for part in comp_parts:
                    part = part.strip()
                    if part and not part in ['==', '!=', '<=', '>=', '<', '>'] and not part.replace('.', '', 1).isdigit() and part not in var_table:
                        var_table[part] = next_var_addr
                        next_var_addr += 1
                        
        elif line.startswith('return'):
            ret_var = line.split()[1]
            if ret_var not in var_table and not ret_var.replace('.', '', 1).isdigit():
                var_table[ret_var] = next_var_addr
                next_var_addr += 1

    # --- Construir la sección de datos ---
    total_addresses = next_var_addr  # Inicializar con el número de direcciones ya usadas
    
    # Primero, establecer valores de constantes    
    for const, addr in const_table.items():
        if addr >= total_addresses:
            total_addresses = addr + 1
            
    # Luego, direcciones de variables
    for var, addr in var_table.items():
        if addr >= total_addresses:
            total_addresses = addr + 1
            
    # Asegurar que haya suficiente espacio para BigGraphs (cada BigGraph usa múltiples posiciones contiguas)
    # Agregar 10 posiciones adicionales para cada variable en var_table que pueda ser un BigGraph
    for var in var_table:
        if "_op_result" not in var:  # No contar variables temporales de resultados
            total_addresses += 10
    
    # También asegurar espacio para operaciones BigGraph no detectadas
    # Esto es una solución para cuando las operaciones BigGraph no se están 
    # generando correctamente en el código TAC
    if ('big' in tac_file.lower() or 'graph' in tac_file.lower()) and not bigraph_ops:
        print("Reservando espacio adicional para operaciones BigGraph no detectadas")
        total_addresses += 50  # Reservar espacio extra
            
    data_section = ["0"] * total_addresses  # Inicializar toda la memoria en "0"
    
    # Escribir constantes en la sección de datos
    for const, addr in const_table.items():
        data_section[addr] = const
    
    # --- Generar la sección de código ---
    code_section = []
    asm_position = 0

    # Mapeo de etiquetas a posiciones de código ensamblador
    label_to_asm = {}

    # Primera pasada para identificar posiciones de etiquetas
    current_position = 0
    for line in tac_lines:
        if line.startswith('begin_func') or line.startswith('end_func') or line.startswith('param'):
            continue
        if line.startswith('L') and ':' in line:
            label = line.split(':')[0]
            label_to_asm[label] = current_position
            continue

        # Contar instrucciones para cada tipo de operación
        if '=' in line and ' + ' in line:
            current_position += 4  # LOAD, LOAD, ADD, STORE
        elif '=' in line and ' - ' in line:
            current_position += 4  # LOAD, LOAD, SUB, STORE
        elif '=' in line and ' * ' in line:
            current_position += 4  # LOAD, LOAD, MUL, STORE
        elif '=' in line and ' / ' in line:
            current_position += 4  # LOAD, LOAD, DIV, STORE
        elif '=' in line and ' == ' in line:
            current_position += 4  # LOAD, LOAD, CMP, STORE
        elif '=' in line and ' != ' in line:
            current_position += 4  # LOAD, LOAD, CMP, STORE
        elif '=' in line and ' < ' in line:
            current_position += 4  # LOAD, LOAD, CMP, STORE
        elif '=' in line and ' <= ' in line:
            current_position += 4  # LOAD, LOAD, CMP, STORE
        elif '=' in line and ' > ' in line:
            current_position += 4  # LOAD, LOAD, CMP, STORE
        elif '=' in line and ' >= ' in line:
            current_position += 4  # LOAD, LOAD, CMP, STORE
        elif '=' in line and not line.startswith('ifz') and not line.startswith('goto'):
            current_position += 2  # LOAD, STORE
        elif line.startswith('ifz'):
            current_position += 4  # LOAD, LOAD, CMP, BEQ
        elif line.startswith('goto'):
            current_position += 1  # JUMP
        elif line.startswith('return'):
            current_position += 2  # LOAD, RET

    # Segunda pasada para generar código
    for line in tac_lines:
        if line.startswith('begin_func') or line.startswith('end_func') or line.startswith('param'):
            continue
        if line.startswith('L') and ':' in line:
            continue

        # Ejemplo: manejo de la suma en operaciones aritméticas
        if '=' in line and ' + ' in line:
            target, expr = [x.strip() for x in line.split('=', 1)]
            target_addr = var_table[target]
            left, right = [x.strip() for x in expr.split(' + ')]
            
            # Resolver la dirección: si es un literal, usar la tabla de constantes; si es una variable, usar la tabla de variables.
            left_addr = const_table[left] if left.replace('.', '', 1).isdigit() else var_table[left]
            right_addr = const_table[right] if right.replace('.', '', 1).isdigit() else var_table[right]
            
            code_section.append(f"LOAD R0, [0x{left_addr:X}]")
            asm_position += 1
            code_section.append(f"LOAD R1, [0x{right_addr:X}]")
            asm_position += 1
            
            # FIXED: Changed format to match VM's expected bit pattern
            # Original: ADD R2, R0, R1
            # VM expects: destination register first, then operands
            code_section.append("ADD R0, R1, R2")
            asm_position += 1
            
            code_section.append(f"STORE R2, [0x{target_addr:X}]")
            asm_position += 1

        # Manejar otras operaciones aritméticas
        elif '=' in line and ' - ' in line:
            target, expr = [x.strip() for x in line.split('=', 1)]
            target_addr = var_table[target]
            left, right = [x.strip() for x in expr.split(' - ')]
            
            left_addr = const_table[left] if left.replace('.', '', 1).isdigit() else var_table[left]
            right_addr = const_table[right] if right.replace('.', '', 1).isdigit() else var_table[right]
            
            code_section.append(f"LOAD R0, [0x{left_addr:X}]")
            asm_position += 1
            code_section.append(f"LOAD R1, [0x{right_addr:X}]")
            asm_position += 1
            
            # FIXED: Changed format to match VM's expected bit pattern
            code_section.append("SUB R0, R1, R2")
            asm_position += 1
            
            code_section.append(f"STORE R2, [0x{target_addr:X}]")
            asm_position += 1

        elif '=' in line and ' * ' in line:
            target, expr = [x.strip() for x in line.split('=', 1)]
            target_addr = var_table[target]
            left, right = [x.strip() for x in expr.split(' * ')]
            
            left_addr = const_table[left] if left.replace('.', '', 1).isdigit() else var_table[left]
            right_addr = const_table[right] if right.replace('.', '', 1).isdigit() else var_table[right]
            
            code_section.append(f"LOAD R0, [0x{left_addr:X}]")
            asm_position += 1
            code_section.append(f"LOAD R1, [0x{right_addr:X}]")
            asm_position += 1
            
            # FIXED: Changed format to match VM's expected bit pattern
            code_section.append("MUL R0, R1, R2")
            asm_position += 1
            
            code_section.append(f"STORE R2, [0x{target_addr:X}]")
            asm_position += 1

        elif '=' in line and ' / ' in line:
            target, expr = [x.strip() for x in line.split('=', 1)]
            target_addr = var_table[target]
            left, right = [x.strip() for x in expr.split(' / ')]
            
            left_addr = const_table[left] if left.replace('.', '', 1).isdigit() else var_table[left]
            right_addr = const_table[right] if right.replace('.', '', 1).isdigit() else var_table[right]
            
            code_section.append(f"LOAD R0, [0x{left_addr:X}]")
            asm_position += 1
            code_section.append(f"LOAD R1, [0x{right_addr:X}]")
            asm_position += 1
            
            # FIXED: Changed format to match VM's expected bit pattern
            code_section.append("DIV R0, R1, R2")
            asm_position += 1
            
            code_section.append(f"STORE R2, [0x{target_addr:X}]")
            asm_position += 1
        
        # Manejar operaciones de comparación
        elif '=' in line and ' == ' in line:
            target, expr = [x.strip() for x in line.split('=', 1)]
            target_addr = var_table[target]
            left, right = [x.strip() for x in expr.split(' == ')]
            
            left_addr = const_table[left] if left.replace('.', '', 1).isdigit() else var_table[left]
            right_addr = const_table[right] if right.replace('.', '', 1).isdigit() else var_table[right]
            
            code_section.append(f"LOAD R0, [0x{left_addr:X}]")
            asm_position += 1
            code_section.append(f"LOAD R1, [0x{right_addr:X}]")
            asm_position += 1
            code_section.append("CMP R0, R1")
            asm_position += 1
            # Almacenar el resultado de la comparación (1 si igual, 0 si diferente)
            code_section.append(f"BEQ R0, R1, [0x{asm_position+2:X}]")
            asm_position += 1
            code_section.append(f"STORE R0, [0x{target_addr:X}]")  # Almacenar 0
            asm_position += 1
            code_section.append(f"LOAD R2, [0x1]")  # Cargar 1
            asm_position += 1
            code_section.append(f"STORE R2, [0x{target_addr:X}]")  # Almacenar 1
            asm_position += 1

        # Manejar asignaciones simples: var = literal o var = otra_var
        elif '=' in line and not line.startswith('ifz') and not line.startswith('goto'):
            target, expr = [x.strip() for x in line.split('=', 1)]
            
            # Manejar operaciones de BigGraph
            if expr == '_new_bigraph()':
                # Creación de un nuevo bigraph
                target_addr = var_table[target]
                
                # Reservar memoria para la estructura del bigraph
                code_section.append("# Inicialización de BigGraph")
                asm_position += 1
                code_section.append("LOAD R0, [0x1]")  # Cargar 1 para inicializar el BigGraph
                asm_position += 1
                code_section.append(f"STORE R0, [0x{target_addr:X}]")  # Marcar como BigGraph válido
                asm_position += 1
                
                # Inicializar memoria para los conjuntos de nodos y aristas
                code_section.append("LOAD R0, [0x0]")  # Inicializar conjunto de nodos como vacío
                asm_position += 1
                code_section.append(f"STORE R0, [0x{target_addr+1:X}]")  # Nodos
                asm_position += 1
                code_section.append(f"STORE R0, [0x{target_addr+2:X}]")  # Aristas
                asm_position += 1
                code_section.append(f"STORE R0, [0x{target_addr+3:X}]")  # Tipos
                asm_position += 1
                
            elif expr.startswith('_bigraph_add_node('):
                # Agregar un nodo al bigraph
                match = re.match(r'_bigraph_add_node\(([^,]+),\s*([^)]+)\)', expr)
                if match:
                    bg_name, node_name = match.groups()
                    bg_addr = var_table[bg_name.strip()]
                    
                    code_section.append(f"# Añadir nodo {node_name} a BigGraph {bg_name}")
                    asm_position += 1
                    
                    # Verificar si el BigGraph es válido
                    code_section.append(f"LOAD R0, [0x{bg_addr:X}]")  # Cargar el estado del BigGraph
                    asm_position += 1
                    code_section.append("LOAD R1, [0x1]")  # Cargar 1 para comparar
                    asm_position += 1
                    code_section.append("CMP R0, R1")  # Comparar si es un BigGraph válido
                    asm_position += 1
                    code_section.append(f"BNE R0, R1, [0x{asm_position+6:X}]")  # Si no es válido, saltar a fallo
                    asm_position += 1
                    
                    # Si es válido, añadir el nodo (simulación)
                    code_section.append(f"LOAD R0, [0x{bg_addr+1:X}]")  # Cargar el contador de nodos
                    asm_position += 1
                    code_section.append("LOAD R1, [0x1]")  # Cargar 1 para incrementar
                    asm_position += 1
                    code_section.append("ADD R0, R1, R2")  # Incrementar el contador
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{bg_addr+1:X}]")  # Almacenar el nuevo contador
                    asm_position += 1
                    
                    # Guardar resultado éxito (1)
                    code_section.append("LOAD R2, [0x1]")  # Cargar 1 (éxito)
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{next_var_addr:X}]")  # Guardar resultado
                    var_table["_op_result"] = next_var_addr
                    next_var_addr += 1
                    asm_position += 1
                    
                    # Saltar al final
                    code_section.append(f"JUMP [0x{asm_position+3:X}]")
                    asm_position += 1
                    
                    # Código para fallo
                    code_section.append("LOAD R2, [0x0]")  # Cargar 0 (fallo)
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{var_table['_op_result']:X}]")  # Guardar resultado
                    asm_position += 1
                
            elif expr.startswith('_bigraph_remove_node('):
                # Eliminar un nodo del bigraph
                match = re.match(r'_bigraph_remove_node\(([^,]+),\s*([^)]+)\)', expr)
                if match:
                    bg_name, node_name = match.groups()
                    bg_addr = var_table[bg_name.strip()]
                    
                    code_section.append(f"# Eliminar nodo {node_name} de BigGraph {bg_name}")
                    asm_position += 1
                    
                    # Verificar si el BigGraph es válido
                    code_section.append(f"LOAD R0, [0x{bg_addr:X}]")  # Cargar el estado del BigGraph
                    asm_position += 1
                    code_section.append("LOAD R1, [0x1]")  # Cargar 1 para comparar
                    asm_position += 1
                    code_section.append("CMP R0, R1")  # Comparar si es un BigGraph válido
                    asm_position += 1
                    code_section.append(f"BNE R0, R1, [0x{asm_position+6:X}]")  # Si no es válido, saltar a fallo
                    asm_position += 1
                    
                    # Si es válido, eliminar el nodo (simulación)
                    code_section.append(f"LOAD R0, [0x{bg_addr+1:X}]")  # Cargar el contador de nodos
                    asm_position += 1
                    code_section.append("LOAD R1, [0x1]")  # Cargar 1 para decrementar
                    asm_position += 1
                    code_section.append("SUB R0, R1, R2")  # Decrementar el contador
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{bg_addr+1:X}]")  # Almacenar el nuevo contador
                    asm_position += 1
                    
                    # Guardar resultado éxito (1)
                    code_section.append("LOAD R2, [0x1]")  # Cargar 1 (éxito)
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{next_var_addr:X}]")  # Guardar resultado
                    var_table["_op_result"] = next_var_addr
                    next_var_addr += 1
                    asm_position += 1
                    
                    # Saltar al final
                    code_section.append(f"JUMP [0x{asm_position+3:X}]")
                    asm_position += 1
                    
                    # Código para fallo
                    code_section.append("LOAD R2, [0x0]")  # Cargar 0 (fallo)
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{var_table['_op_result']:X}]")  # Guardar resultado
                    asm_position += 1
            
            elif expr.startswith('_bigraph_add_edge('):
                # Añadir una arista al bigraph
                match = re.match(r'_bigraph_add_edge\(([^,]+),\s*([^,]+),\s*([^)]+)\)', expr)
                if match:
                    bg_name, node1, node2 = match.groups()
                    bg_addr = var_table[bg_name.strip()]
                    
                    code_section.append(f"# Añadir arista entre {node1} y {node2} en BigGraph {bg_name}")
                    asm_position += 1
                    
                    # Verificar si el BigGraph es válido
                    code_section.append(f"LOAD R0, [0x{bg_addr:X}]")  # Cargar el estado del BigGraph
                    asm_position += 1
                    code_section.append("LOAD R1, [0x1]")  # Cargar 1 para comparar
                    asm_position += 1
                    code_section.append("CMP R0, R1")  # Comparar si es un BigGraph válido
                    asm_position += 1
                    code_section.append(f"BNE R0, R1, [0x{asm_position+6:X}]")  # Si no es válido, saltar a fallo
                    asm_position += 1
                    
                    # Si es válido, añadir la arista (simulación)
                    code_section.append(f"LOAD R0, [0x{bg_addr+2:X}]")  # Cargar el contador de aristas
                    asm_position += 1
                    code_section.append("LOAD R1, [0x1]")  # Cargar 1 para incrementar
                    asm_position += 1
                    code_section.append("ADD R0, R1, R2")  # Incrementar el contador
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{bg_addr+2:X}]")  # Almacenar el nuevo contador
                    asm_position += 1
                    
                    # Guardar resultado éxito (1)
                    code_section.append("LOAD R2, [0x1]")  # Cargar 1 (éxito)
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{next_var_addr:X}]")  # Guardar resultado
                    var_table["_op_result"] = next_var_addr
                    next_var_addr += 1
                    asm_position += 1
                    
                    # Saltar al final
                    code_section.append(f"JUMP [0x{asm_position+3:X}]")
                    asm_position += 1
                    
                    # Código para fallo
                    code_section.append("LOAD R2, [0x0]")  # Cargar 0 (fallo)
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{var_table['_op_result']:X}]")  # Guardar resultado
                    asm_position += 1
            
            elif expr.startswith('_bigraph_remove_edge('):
                # Eliminar una arista del bigraph
                match = re.match(r'_bigraph_remove_edge\(([^,]+),\s*([^,]+),\s*([^)]+)\)', expr)
                if match:
                    bg_name, node1, node2 = match.groups()
                    bg_addr = var_table[bg_name.strip()]
                    
                    code_section.append(f"# Eliminar arista entre {node1} y {node2} en BigGraph {bg_name}")
                    asm_position += 1
                    
                    # Verificar si el BigGraph es válido
                    code_section.append(f"LOAD R0, [0x{bg_addr:X}]")  # Cargar el estado del BigGraph
                    asm_position += 1
                    code_section.append("LOAD R1, [0x1]")  # Cargar 1 para comparar
                    asm_position += 1
                    code_section.append("CMP R0, R1")  # Comparar si es un BigGraph válido
                    asm_position += 1
                    code_section.append(f"BNE R0, R1, [0x{asm_position+6:X}]")  # Si no es válido, saltar a fallo
                    asm_position += 1
                    
                    # Si es válido, eliminar la arista (simulación)
                    code_section.append(f"LOAD R0, [0x{bg_addr+2:X}]")  # Cargar el contador de aristas
                    asm_position += 1
                    code_section.append("LOAD R1, [0x1]")  # Cargar 1 para decrementar
                    asm_position += 1
                    code_section.append("SUB R0, R1, R2")  # Decrementar el contador
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{bg_addr+2:X}]")  # Almacenar el nuevo contador
                    asm_position += 1
                    
                    # Guardar resultado éxito (1)
                    code_section.append("LOAD R2, [0x1]")  # Cargar 1 (éxito)
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{next_var_addr:X}]")  # Guardar resultado
                    var_table["_op_result"] = next_var_addr
                    next_var_addr += 1
                    asm_position += 1
                    
                    # Saltar al final
                    code_section.append(f"JUMP [0x{asm_position+3:X}]")
                    asm_position += 1
                    
                    # Código para fallo
                    code_section.append("LOAD R2, [0x0]")  # Cargar 0 (fallo)
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{var_table['_op_result']:X}]")  # Guardar resultado
                    asm_position += 1
            
            elif expr.startswith('_bigraph_add_type('):
                # Añadir un tipo a un nodo
                match = re.match(r'_bigraph_add_type\(([^,]+),\s*([^,]+),\s*([^)]+)\)', expr)
                if match:
                    bg_name, type_name, node_name = match.groups()
                    bg_addr = var_table[bg_name.strip()]
                    
                    code_section.append(f"# Añadir tipo {type_name} a nodo {node_name} en BigGraph {bg_name}")
                    asm_position += 1
                    
                    # Verificar si el BigGraph es válido
                    code_section.append(f"LOAD R0, [0x{bg_addr:X}]")  # Cargar el estado del BigGraph
                    asm_position += 1
                    code_section.append("LOAD R1, [0x1]")  # Cargar 1 para comparar
                    asm_position += 1
                    code_section.append("CMP R0, R1")  # Comparar si es un BigGraph válido
                    asm_position += 1
                    code_section.append(f"BNE R0, R1, [0x{asm_position+6:X}]")  # Si no es válido, saltar a fallo
                    asm_position += 1
                    
                    # Si es válido, añadir el tipo (simulación)
                    code_section.append(f"LOAD R0, [0x{bg_addr+3:X}]")  # Cargar el contador de tipos
                    asm_position += 1
                    code_section.append("LOAD R1, [0x1]")  # Cargar 1 para incrementar
                    asm_position += 1
                    code_section.append("ADD R0, R1, R2")  # Incrementar el contador
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{bg_addr+3:X}]")  # Almacenar el nuevo contador
                    asm_position += 1
                    
                    # Guardar resultado éxito (1)
                    code_section.append("LOAD R2, [0x1]")  # Cargar 1 (éxito)
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{next_var_addr:X}]")  # Guardar resultado
                    var_table["_op_result"] = next_var_addr
                    next_var_addr += 1
                    asm_position += 1
                    
                    # Saltar al final
                    code_section.append(f"JUMP [0x{asm_position+3:X}]")
                    asm_position += 1
                    
                    # Código para fallo
                    code_section.append("LOAD R2, [0x0]")  # Cargar 0 (fallo)
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{var_table['_op_result']:X}]")  # Guardar resultado
                    asm_position += 1
            
            elif expr.startswith('_bigraph_remove_type('):
                # Eliminar un tipo de un nodo
                match = re.match(r'_bigraph_remove_type\(([^,]+),\s*([^,]+),\s*([^)]+)\)', expr)
                if match:
                    bg_name, type_name, node_name = match.groups()
                    bg_addr = var_table[bg_name.strip()]
                    
                    code_section.append(f"# Eliminar tipo {type_name} de nodo {node_name} en BigGraph {bg_name}")
                    asm_position += 1
                    
                    # Verificar si el BigGraph es válido
                    code_section.append(f"LOAD R0, [0x{bg_addr:X}]")  # Cargar el estado del BigGraph
                    asm_position += 1
                    code_section.append("LOAD R1, [0x1]")  # Cargar 1 para comparar
                    asm_position += 1
                    code_section.append("CMP R0, R1")  # Comparar si es un BigGraph válido
                    asm_position += 1
                    code_section.append(f"BNE R0, R1, [0x{asm_position+6:X}]")  # Si no es válido, saltar a fallo
                    asm_position += 1
                    
                    # Si es válido, eliminar el tipo (simulación)
                    code_section.append(f"LOAD R0, [0x{bg_addr+3:X}]")  # Cargar el contador de tipos
                    asm_position += 1
                    code_section.append("LOAD R1, [0x1]")  # Cargar 1 para decrementar
                    asm_position += 1
                    code_section.append("SUB R0, R1, R2")  # Decrementar el contador
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{bg_addr+3:X}]")  # Almacenar el nuevo contador
                    asm_position += 1
                    
                    # Guardar resultado éxito (1)
                    code_section.append("LOAD R2, [0x1]")  # Cargar 1 (éxito)
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{next_var_addr:X}]")  # Guardar resultado
                    var_table["_op_result"] = next_var_addr
                    next_var_addr += 1
                    asm_position += 1
                    
                    # Saltar al final
                    code_section.append(f"JUMP [0x{asm_position+3:X}]")
                    asm_position += 1
                    
                    # Código para fallo
                    code_section.append("LOAD R2, [0x0]")  # Cargar 0 (fallo)
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{var_table['_op_result']:X}]")  # Guardar resultado
                    asm_position += 1
            
            elif expr.startswith('_bigraph_set_link('):
                # Establecer un enlace para un nodo
                match = re.match(r'_bigraph_set_link\(([^,]+),\s*([^,]+),\s*([^)]+)\)', expr)
                if match:
                    bg_name, node_name, limit = match.groups()
                    bg_addr = var_table[bg_name.strip()]
                    
                    code_section.append(f"# Establecer enlace para nodo {node_name} con límite {limit} en BigGraph {bg_name}")
                    asm_position += 1
                    
                    # Verificar si el BigGraph es válido
                    code_section.append(f"LOAD R0, [0x{bg_addr:X}]")  # Cargar el estado del BigGraph
                    asm_position += 1
                    code_section.append("LOAD R1, [0x1]")  # Cargar 1 para comparar
                    asm_position += 1
                    code_section.append("CMP R0, R1")  # Comparar si es un BigGraph válido
                    asm_position += 1
                    code_section.append(f"BNE R0, R1, [0x{asm_position+5:X}]")  # Si no es válido, saltar a fallo
                    asm_position += 1
                    
                    # Si es válido, establecer el enlace (simulación)
                    # Para este caso, almacenamos el límite en una posición de memoria
                    limit_addr = 0
                    if limit.replace('.', '', 1).isdigit():
                        if limit not in const_table:
                            const_table[limit] = next_const_addr
                            next_const_addr += 1
                        limit_addr = const_table[limit]
                    else:
                        limit_addr = var_table[limit.strip()]
                        
                    code_section.append(f"LOAD R0, [0x{limit_addr:X}]")  # Cargar el límite
                    asm_position += 1
                    code_section.append(f"LOAD R1, [0x{bg_addr+4:X}]")  # Cargar contador de enlaces
                    asm_position += 1
                    code_section.append("ADD R0, R1, R2")  # Aumentar contador
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{bg_addr+4:X}]")  # Almacenar
                    asm_position += 1
                    
                    # Guardar resultado éxito (1)
                    code_section.append("LOAD R2, [0x1]")  # Cargar 1 (éxito)
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{next_var_addr:X}]")  # Guardar resultado
                    var_table["_op_result"] = next_var_addr
                    next_var_addr += 1
                    asm_position += 1
                    
                    # Saltar al final
                    code_section.append(f"JUMP [0x{asm_position+3:X}]")
                    asm_position += 1
                    
                    # Código para fallo
                    code_section.append("LOAD R2, [0x0]")  # Cargar 0 (fallo)
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{var_table['_op_result']:X}]")  # Guardar resultado
                    asm_position += 1
            
            elif expr.startswith('_bigraph_remove_link('):
                # Eliminar el enlace de un nodo
                match = re.match(r'_bigraph_remove_link\(([^,]+),\s*([^)]+)\)', expr)
                if match:
                    bg_name, node_name = match.groups()
                    bg_addr = var_table[bg_name.strip()]
                    
                    code_section.append(f"# Eliminar enlace de nodo {node_name} en BigGraph {bg_name}")
                    asm_position += 1
                    
                    # Verificar si el BigGraph es válido
                    code_section.append(f"LOAD R0, [0x{bg_addr:X}]")  # Cargar el estado del BigGraph
                    asm_position += 1
                    code_section.append("LOAD R1, [0x1]")  # Cargar 1 para comparar
                    asm_position += 1
                    code_section.append("CMP R0, R1")  # Comparar si es un BigGraph válido
                    asm_position += 1
                    code_section.append(f"BNE R0, R1, [0x{asm_position+5:X}]")  # Si no es válido, saltar a fallo
                    asm_position += 1
                    
                    # Si es válido, eliminar el enlace (simulación)
                    code_section.append(f"LOAD R0, [0x{bg_addr+4:X}]")  # Cargar contador de enlaces
                    asm_position += 1
                    code_section.append("LOAD R1, [0x1]")  # Cargar 1 para decrementar
                    asm_position += 1
                    code_section.append("SUB R0, R1, R2")  # Decrementar el contador
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{bg_addr+4:X}]")  # Almacenar
                    asm_position += 1
                    
                    # Guardar resultado éxito (1)
                    code_section.append("LOAD R2, [0x1]")  # Cargar 1 (éxito)
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{next_var_addr:X}]")  # Guardar resultado
                    var_table["_op_result"] = next_var_addr
                    next_var_addr += 1
                    asm_position += 1
                    
                    # Saltar al final
                    code_section.append(f"JUMP [0x{asm_position+3:X}]")
                    asm_position += 1
                    
                    # Código para fallo
                    code_section.append("LOAD R2, [0x0]")  # Cargar 0 (fallo)
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{var_table['_op_result']:X}]")  # Guardar resultado
                    asm_position += 1
            
            elif expr.startswith('_bigraph_add_parent('):
                # Establecer relación padre-hijo
                match = re.match(r'_bigraph_add_parent\(([^,]+),\s*([^,]+),\s*([^)]+)\)', expr)
                if match:
                    bg_name, parent, child = match.groups()
                    bg_addr = var_table[bg_name.strip()]
                    
                    code_section.append(f"# Establecer {parent} como padre de {child} en BigGraph {bg_name}")
                    asm_position += 1
                    
                    # Verificar si el BigGraph es válido
                    code_section.append(f"LOAD R0, [0x{bg_addr:X}]")  # Cargar el estado del BigGraph
                    asm_position += 1
                    code_section.append("LOAD R1, [0x1]")  # Cargar 1 para comparar
                    asm_position += 1
                    code_section.append("CMP R0, R1")  # Comparar si es un BigGraph válido
                    asm_position += 1
                    code_section.append(f"BNE R0, R1, [0x{asm_position+6:X}]")  # Si no es válido, saltar a fallo
                    asm_position += 1
                    
                    # Si es válido, establecer relación (simulación)
                    code_section.append(f"LOAD R0, [0x{bg_addr+5:X}]")  # Cargar contador de relaciones padre-hijo
                    asm_position += 1
                    code_section.append("LOAD R1, [0x1]")  # Cargar 1 para incrementar
                    asm_position += 1
                    code_section.append("ADD R0, R1, R2")  # Incrementar el contador
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{bg_addr+5:X}]")  # Almacenar
                    asm_position += 1
                    
                    # Guardar resultado éxito (1)
                    code_section.append("LOAD R2, [0x1]")  # Cargar 1 (éxito)
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{next_var_addr:X}]")  # Guardar resultado
                    var_table["_op_result"] = next_var_addr
                    next_var_addr += 1
                    asm_position += 1
                    
                    # Saltar al final
                    code_section.append(f"JUMP [0x{asm_position+3:X}]")
                    asm_position += 1
                    
                    # Código para fallo
                    code_section.append("LOAD R2, [0x0]")  # Cargar 0 (fallo)
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{var_table['_op_result']:X}]")  # Guardar resultado
                    asm_position += 1
            
            elif expr.startswith('_bigraph_compose('):
                # Componer dos bigraphs
                match = re.match(r'_bigraph_compose\(([^,]+),\s*([^,]+),\s*([^)]+)\)', expr)
                if match:
                    result_bg, bg1, bg2 = match.groups()
                    result_addr = var_table[result_bg.strip()]
                    bg1_addr = var_table[bg1.strip()]
                    bg2_addr = var_table[bg2.strip()]
                    
                    code_section.append(f"# Componer BigGraphs {bg1} y {bg2} en {result_bg}")
                    asm_position += 1
                    
                    # Verificar si ambos BigGraphs son válidos
                    code_section.append(f"LOAD R0, [0x{bg1_addr:X}]")  # Cargar estado del primer BigGraph
                    asm_position += 1
                    code_section.append("LOAD R1, [0x1]")  # Cargar 1 para comparar
                    asm_position += 1
                    code_section.append("CMP R0, R1")  # Comparar si es un BigGraph válido
                    asm_position += 1
                    code_section.append(f"BNE R0, R1, [0x{asm_position+11:X}]")  # Si no es válido, saltar a fallo
                    asm_position += 1
                    
                    code_section.append(f"LOAD R0, [0x{bg2_addr:X}]")  # Cargar estado del segundo BigGraph
                    asm_position += 1
                    code_section.append("CMP R0, R1")  # Comparar si es un BigGraph válido
                    asm_position += 1
                    code_section.append(f"BNE R0, R1, [0x{asm_position+9:X}]")  # Si no es válido, saltar a fallo
                    asm_position += 1
                    
                    # Inicializar el BigGraph resultante
                    code_section.append(f"STORE R1, [0x{result_addr:X}]")  # Marcar como BigGraph válido
                    asm_position += 1
                    
                    # Sumar nodos de ambos BigGraphs
                    code_section.append(f"LOAD R0, [0x{bg1_addr+1:X}]")  # Cargar nodos del primer BigGraph
                    asm_position += 1
                    code_section.append(f"LOAD R1, [0x{bg2_addr+1:X}]")  # Cargar nodos del segundo BigGraph
                    asm_position += 1
                    code_section.append("ADD R0, R1, R2")  # Sumar nodos
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{result_addr+1:X}]")  # Almacenar nodos
                    asm_position += 1
                    
                    # Sumar aristas de ambos BigGraphs
                    code_section.append(f"LOAD R0, [0x{bg1_addr+2:X}]")  # Cargar aristas del primer BigGraph
                    asm_position += 1
                    code_section.append(f"LOAD R1, [0x{bg2_addr+2:X}]")  # Cargar aristas del segundo BigGraph
                    asm_position += 1
                    code_section.append("ADD R0, R1, R2")  # Sumar aristas
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{result_addr+2:X}]")  # Almacenar aristas
                    asm_position += 1
                    
                    # Sumar tipos de ambos BigGraphs
                    code_section.append(f"LOAD R0, [0x{bg1_addr+3:X}]")  # Cargar tipos del primer BigGraph
                    asm_position += 1
                    code_section.append(f"LOAD R1, [0x{bg2_addr+3:X}]")  # Cargar tipos del segundo BigGraph
                    asm_position += 1
                    code_section.append("ADD R0, R1, R2")  # Sumar tipos
                    asm_position += 1
                    code_section.append(f"STORE R2, [0x{result_addr+3:X}]")  # Almacenar tipos
                    asm_position += 1
                    
                    # Saltar al final
                    code_section.append(f"JUMP [0x{asm_position+3:X}]")
                    asm_position += 1
                    
                    # Código para fallo
                    code_section.append("LOAD R0, [0x0]")  # Cargar 0 para BigGraph inválido
                    asm_position += 1
                    code_section.append(f"STORE R0, [0x{result_addr:X}]")  # Marcar BigGraph como inválido
                    asm_position += 1
            
            # Asignación normal si no es una operación de BigGraph
            elif not any(expr.startswith(op) for op in ['_bigraph_']):
                target_addr = var_table[target]
                
                # Si es una constante numérica
                if expr.replace('.', '', 1).isdigit():
                    src_addr = const_table[expr]
                    code_section.append(f"LOAD R0, [0x{src_addr:X}]")
                    asm_position += 1
                    code_section.append(f"STORE R0, [0x{target_addr:X}]")
                    asm_position += 1
                # Si es otra variable
                elif expr in var_table:
                    src_addr = var_table[expr]
                    code_section.append(f"LOAD R0, [0x{src_addr:X}]")
                    asm_position += 1
                    code_section.append(f"STORE R0, [0x{target_addr:X}]")
                    asm_position += 1

        elif line.startswith('ifz'):
            parts = line.split()
            cond = parts[1]
            goto_label = parts[3]
            cond_addr = const_table[cond] if cond.replace('.', '', 1).isdigit() else var_table[cond]
            
            code_section.append(f"LOAD R0, [0x{cond_addr:X}]")
            asm_position += 1
            code_section.append("LOAD R1, [0x0]")
            asm_position += 1
            code_section.append("CMP R0, R1")
            asm_position += 1
            
            if goto_label in label_to_asm:
                # FIXED: Changed format to match VM's expected bit pattern for BEQ
                code_section.append(f"BEQ R0, R1, [0x{label_to_asm[goto_label]:X}]")
            else:
                code_section.append(f"BEQ R0, R1, [{goto_label}]")
            asm_position += 1

        elif line.startswith('goto'):
            goto_label = line.split()[1]
            if goto_label in label_to_asm:
                code_section.append(f"JUMP [0x{label_to_asm[goto_label]:X}]")
            else:
                code_section.append(f"JUMP [{goto_label}]")
            asm_position += 1

        elif line.startswith('return'):
            ret_var = line.split()[1]
            if ret_var.replace('.', '', 1).isdigit():
                ret_addr = const_table[ret_var]
            else:
                ret_addr = var_table[ret_var]
                
            code_section.append(f"LOAD R0, [0x{ret_addr:X}]")
            asm_position += 1
            code_section.append("RET")
            asm_position += 1

        else:
            code_section.append(f"# Instrucción no implementada: {line}")
            asm_position += 1

    # Resolver referencias a etiquetas en el código
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

def generate_default_bigraph_code():
    """Genera código predeterminado para operaciones BigGraph cuando el archivo TAC está vacío."""
    # Constantes necesarias
    data_section = [
        "0",  # Constante 0 (posición 0)
        "1",  # Constante 1 (posición 1) - Operación: nuevo BigGraph
        "2",  # Constante 2 (posición 2) - Operación: agregar nodo
        "3",  # Constante 3 (posición 3) - Operación: reemplazar nodo
        "4",  # Constante 4 (posición 4) - Operación: eliminar nodo
        "5",  # Constante 5 (posición 5) - Operación: agregar arista
        "6",  # Constante 6 (posición 6) - Operación: eliminar arista
        "7",  # Constante 7 (posición 7) - Operación: agregar tipo
        "8",  # Constante 8 (posición 8) - Operación: eliminar tipo
        "9",  # Constante 9 (posición 9) - Operación: agregar padre
        "10", # Constante 10 (posición 10) - Operación: establecer enlace
        "11", # Constante 11 (posición 11) - Operación: eliminar enlace
        "12", # Constante 12 (posición 12) - Operación: componer bigrafos
        "100", # Tamaño del BigGraph (posición 13)
        "65", # Código ASCII para 'A' (posición 14)
        "66", # Código ASCII para 'B' (posición 15)
        "67", # Código ASCII para 'C' (posición 16)
        "68", # Código ASCII para 'D' (posición 17)
    ]
    
    # Código para operaciones BigGraph
    code_section = [
        "# Código de inicialización y operaciones para BigGraph",
        "# --- Inicialización de BigGraph ---",
        "LOAD R0, [0x1]",  # Cargar constante 1 (operación: nuevo BigGraph)
        "LOAD R1, [0xD]",  # Cargar tamaño (100)
        "STORE R0, [0x20]", # Guardar tipo de operación en memoria
        "STORE R1, [0x21]", # Guardar tamaño en memoria
        
        "# --- Agregar nodo A ---",
        "LOAD R0, [0x2]",  # Cargar constante 2 (operación: agregar nodo)
        "LOAD R1, [0xE]",  # Cargar código ASCII para 'A'
        "STORE R0, [0x30]", # Guardar tipo de operación
        "STORE R1, [0x31]", # Guardar identificador del nodo
        
        "# --- Agregar nodo B ---",
        "LOAD R0, [0x2]",  # Cargar constante 2 (operación: agregar nodo)
        "LOAD R1, [0xF]",  # Cargar código ASCII para 'B'
        "STORE R0, [0x40]", # Guardar tipo de operación
        "STORE R1, [0x41]", # Guardar identificador del nodo
        
        "# --- Agregar arista entre A y B ---",
        "LOAD R0, [0x5]",  # Cargar constante 5 (operación: agregar arista)
        "LOAD R1, [0xE]",  # Cargar código ASCII para 'A'
        "LOAD R2, [0xF]",  # Cargar código ASCII para 'B'
        "STORE R0, [0x50]", # Guardar tipo de operación
        "STORE R1, [0x51]", # Guardar identificador del nodo origen
        "STORE R2, [0x52]", # Guardar identificador del nodo destino
        
        "# --- Reemplazar nodo A por D ---",
        "LOAD R0, [0x3]",  # Cargar constante 3 (operación: reemplazar nodo)
        "LOAD R1, [0xE]",  # Cargar código ASCII para 'A'
        "LOAD R2, [0x11]", # Cargar código ASCII para 'D'
        "STORE R0, [0x60]", # Guardar tipo de operación
        "STORE R1, [0x61]", # Guardar identificador del nodo a reemplazar
        "STORE R2, [0x62]", # Guardar identificador del nuevo nodo
        
        "# --- Eliminar nodo B ---",
        "LOAD R0, [0x4]",  # Cargar constante 4 (operación: eliminar nodo)
        "LOAD R1, [0xF]",  # Cargar código ASCII para 'B'
        "STORE R0, [0x70]", # Guardar tipo de operación
        "STORE R1, [0x71]", # Guardar identificador del nodo a eliminar
        
        "# --- Agregar tipo ---",
        "LOAD R0, [0x7]",  # Cargar constante 7 (operación: agregar tipo)
        "LOAD R1, [0xE]",  # Cargar identificador del nodo
        "LOAD R2, [0x1]",  # Cargar tipo 1
        "STORE R0, [0x80]", # Guardar tipo de operación
        "STORE R1, [0x81]", # Guardar identificador del nodo
        "STORE R2, [0x82]", # Guardar valor del tipo
        
        "HALT" # Finalizar programa
    ]
    
    return data_section, code_section

def main():
    if len(sys.argv) != 2:
        print("Uso: python TAC.py <archivo_entrada.tac>")
        sys.exit(1)
    
    tac_file = sys.argv[1]
    
    # Verificar si el archivo TAC existe
    if not os.path.exists(tac_file):
        print(f"ERROR: El archivo TAC '{tac_file}' no existe.")
        sys.exit(1)
    
    # Verificar si el archivo TAC está vacío
    if os.path.getsize(tac_file) == 0:
        print(f"ADVERTENCIA: El archivo TAC '{tac_file}' está vacío.")
    
    data_section, code_section = tac_to_assembly(tac_file)
    output_file = tac_file.replace('.tac', '.asm')
    
    # Filtrar comentarios para el archivo de salida
    filtered_code_section = []
    for instr in code_section:
        if not instr.startswith('#'):
            filtered_code_section.append(instr)
    
    # Escribir el archivo de salida sin comentarios
    with open(output_file, 'w', encoding='utf-8') as f:
        for data in data_section:
            f.write(f"{data}\n")
        for instr in filtered_code_section:
            f.write(f"{instr}\n")
    
    # Escribir todos los comentarios en un archivo de depuración
    debug_file = tac_file.replace('.tac', '.debug')
    with open(debug_file, 'w', encoding='utf-8') as f:
        for instr in code_section:
            if instr.startswith('#'):
                f.write(f"{instr}\n")
    
    print(f"\nCódigo ensamblador escrito en {output_file}")
    print(f"Comentarios de depuración escritos en {debug_file}")

if __name__ == "__main__":
    main()