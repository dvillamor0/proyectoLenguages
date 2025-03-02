# import sys
# from Diseño_GUI import *
# from PyQt5.QtWidgets import QApplication

# app = QApplication(sys.argv)
# window = Ui_MainWindow()
# Form = QtWidgets.QMainWindow()
# window.setupUi(Form)
# Form.show()
# sys.exit(app.exec_())

import sys
import struct
import time
import tempfile
from assets.memoria import Memoria
from assets.IdentificarDato import GetEntero, GetFloat, GetNatural, GetBooleano, GetCaracterUtf16, int_to_bin16, float_to_bin16, ConvertirDatoBinario
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtWidgets import QApplication, QMainWindow
from vista.Diseno_GUI import *
from vista.prueba import *
import subprocess
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.cp = 0
        self.registro = [0] * 4
        self.carry = 0
        self.zero = 0
        self.negative = 0
        self.desbordamiento = 0
        self.config_input = {"text": "", "reg_input": 0, "Exxecute_all": False}
        self.set_REG_Values([0,0,0,0])
        self.setCarry(0)
        self.setZero(0)
        self.setNegative(0)
        self.setDesb(0)
        self.ui.input_button.setDisabled(True)
        self.memoria = Memoria(self.ui)
        self.ui.preprocesar_button.clicked.connect(self.Preprocesado)
        
        self.ui.Compilar_button.clicked.connect(self.Compilador)
        self.ui.ensamblador_button.clicked.connect(self.Ensamblador)
        self.ui.Linker_button.clicked.connect(self.EnlazadorCargador)
        self.ui.Read_Next_Instruction.clicked.connect(self.LeerInstruccion)
        self.ui.Exxecute_instructions.clicked.connect(self.LeerInstrucciones)
        self.ui.input_button.clicked.connect(self.getInput)
        self.ui.Charge_cp.clicked.connect(self.cargarCp)
        self.funciones = {
            "NOP" : self.NOP,
            "LOAD" : self.LOAD,
            "STORE" : self.STORE,
            "MOVE" : self.MOVE,
            "ADD" : self.ADD,
            "SUB" : self.SUB,
            "MUL" : self.MUL,
            "DIV" : self.DIV,
            "AND" : self.AND,
            "OR" : self.OR,
            "NOR" : self.NOR,
            "NOT" : self.NOT,
            "SHL" : self.SHL,
            "SHR" : self.SHR,
            "ROL" : self.ROL,
            "ROR" : self.ROR,
            "JUMP" : self.JUMP,
            "BEQ" : self.BEQ,
            "BNE" : self.BNE,
            "BLT" : self.BLT,
            "JLE" : self.JLE,
            "PUSH" : self.PUSH,
            "POP" : self.POP,
            "CALL" : self.CALL,
            "RET" : self.RET,
            "IN" : self.IN,
            "OUT" : self.OUT,
            "CMP" : self.CMP,
            "CLR" : self.CLR,
            "LOADR" : self.LOADR,
            "STORER" : self.STORER,
            "HALT" : self.HALT,
        }

    def cargarCp(self):
        valor = self.ui.CP_Set.toPlainText()
        try:
            valor = int(valor)
            self.setCp(valor)
        except ValueError as e:
            print(f"Error: '{valor}' no es un número válido.")
            self.ui.Output.setPlainText("[Error Enlazador]: "+ str(e))
             
    def getInput(self):
        valor = self.ui.Input.toPlainText()
        self.guardar_en_registro(self.config_input["reg_input"], float(valor))
        Llama_all = self.config_input['Exxecute_all']
        self.config_input = {"text": "", "reg_input": 0, "Exxecute_all": False}
        self.ui.Read_Next_Instruction.setDisabled(False)
        self.ui.Exxecute_instructions.setDisabled(False)
        self.ui.input_button.setDisabled(True)
        if(Llama_all):
            self.LeerInstrucciones()
        
    def setCp(self,new_cp):
        try:
            self.cp = new_cp
            self.ui.CP_Set.setPlainText(str(new_cp))
            self.memoria.mover_cp(int(new_cp))
        except ValueError as e:
            print(f"Error: '{new_cp}' no es un número válido.")
            self.ui.Output.setPlainText("[Error Enlazador]: "+ str(e))
            
    def setDir(self,new_dir):
        try:
            self.dir = new_dir
            self.ui.DIR.setPlainText(str(new_dir))
        except ValueError as e:
            print(f"Error: '{new_dir}' no es un número válido.")
            self.ui.Output.setPlainText("[Error Instruccion]: "+ str(e))
        
    def actualizarTablaMemoria(self):
        """ Actualiza la tabla de memoria en la interfaz. """
        self.ui.table_memoria.setRowCount(len(self.memoria))

        for i, (direccion, valor) in enumerate(self.memoria.items()):
            self.ui.table_memoria.setItem(i, 0, QtWidgets.QTableWidgetItem(str(valor)))
            item = self.ui.table_memoria(str(valor))
            # Resaltar la fila si es la dirección de `cp`
            if direccion == self.cp:
                item.setBackground(QColor(255, 255, 0))  # Amarillo
            else:
                item.setBackground(QColor(255, 255, 255))  # Blanco

            self.ui.table_memoria.setItem(i, 0, item)

        # 🔹 Mostrar los últimos 100 registros de la memoria en `table_pila`
        ultimas_100_direcciones = sorted(self.memoria.keys(), reverse=True)[:100]  # Obtener las últimas 100 direcciones
        self.ui.table_pila.setRowCount(len(ultimas_100_direcciones))  # Ajustar tamaño de la tabla

        for i, direccion in enumerate(ultimas_100_direcciones):
            valor = self.memoria[direccion]
            item = QtWidgets.QTableWidgetItem(str(valor))
            self.ui.table_pila.setItem(i, 0, item)
 
    def guardar_en_registro(self, indice, value):
        temp_reg = self.registro
        temp_reg[indice] = value
        self.set_REG_Values(temp_reg)
        
    def set_REG_Values(self,arreglo):
        self.registro[0] = arreglo[0]
        self.registro[1] = arreglo[1]
        self.registro[2] = arreglo[2]
        self.registro[3] = arreglo[3]
        self.ui.REG_A.setText(str(arreglo[0]))
        self.ui.REG_B.setText(str(arreglo[1]))
        self.ui.REG_C.setText(str(arreglo[2]))
        self.ui.REG_D.setText(str(arreglo[3]))
        
        def convertir_a_binario(valor):
            """Convierte un valor a binario según su tipo (int o float)."""
            if isinstance(valor, int):
                return int_to_bin16(valor)
            elif isinstance(valor, float):
                return float_to_bin16(valor)
            elif isinstance(valor, str):
                return float_to_bin16(bin(ord(valor))[2:].zfill(16))
            elif isinstance(valor, bool):
                if(valor):
                    return int_to_bin16(1)
                else:
                    return int_to_bin16(0)
            else:
                return "ERROR"  # Manejo de error en caso de tipo desconocido
        self.ui.BIN_A.setText(convertir_a_binario(arreglo[0]))
        self.ui.BIN_B.setText(convertir_a_binario(arreglo[1]))
        self.ui.BIN_C.setText(convertir_a_binario(arreglo[2]))
        self.ui.BIN_D.setText(convertir_a_binario(arreglo[3]))
      
    def setCarry(self,caryy):
        self.carry = caryy
        self.ui.REG_Carry.setText(str(caryy))
        self.ui.BIN_Carry.setText(int_to_bin16(caryy))
      
    def setZero(self,zero):
        self.zero = zero
        self.ui.REG_Zero.setText(str(zero))
        self.ui.BIN_Zero.setText(int_to_bin16(zero))
        
    def setNegative(self,negative):
        self.negative = negative
        self.ui.REG_Neg.setText(str(negativo))
        self.ui.BIN_Neg.setText(int_to_bin16(negativo))
        
    def setDesb(self,desbordamiento):
        self.desbordamiento = desbordamiento
        self.ui.REG_Desb.setText(str(desbordamiento))
        self.ui.BIN_Desb.setText(int_to_bin16(desbordamiento))
    
    def resetBanderas(self):
        self.setCarry(0)
        self.setZero(0)
        self.setNegative(0)
        self.setDesb(0)
        
    def Preprocesado(self):
        texto = self.ui.codigofuente_input.toPlainText()  # Obtener el texto del QTextEdit

        # Crear un archivo temporal para pasar el contenido al analizador Flex
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_file.write(texto.encode("utf-8"))
            temp_file_path = temp_file.name

        # Ejecutar el analizador léxico en Flex (asumiendo que ya compilaste el ejecutable)
        flex_executable = "./compilados/preprocesador"  # Asegúrate de que `scanner` es el ejecutable de Flex generado con `gcc`
        if os.name != 'posix':
            flex_executable += ".exe"
        try:
            result = subprocess.run(
                [flex_executable, temp_file_path],  # Ejecuta el scanner con el archivo temporal
                capture_output=True,
                text=True,
                check=True
            )
            output = result.stdout  # Obtener la salida del scanner
            self.ui.codigo_preprocesado_input.setPlainText(output)
        except Exception as e:
            self.ui.Output.setPlainText("[Error Preprocesado]: "+ str(e))
        
    def Compilador(self):
        def log_debug(message):
            """ Escribe en un archivo de depuración. """
            with open("debug.log", "a", encoding="utf-8") as debug_file:
                debug_file.write(message + "\n")
        # Obtener el código preprocesado de la UI
        codigo = self.ui.codigo_preprocesado_input.toPlainText()

        # Definir rutas absolutas para evitar problemas de ubicación
        compiler_executable = os.path.abspath("./compilados/compiler")
        if os.name != 'posix':
            compiler_executable += ".exe"
        output_file = "./archivos_salida/compilador.out"
        output_file_tac = "./archivos_salida/compilador.tac"
        output_file_asm = "./archivos_salida/compilador.asm"
        tac_script = os.path.abspath("./src/TAC.py")

        try:
            # Crear archivo temporal para la entrada
            with tempfile.NamedTemporaryFile(delete=False, suffix=".out", mode="w", encoding="utf-8") as temp_input:
                temp_input.write(codigo)
                temp_input.flush()  # Asegurar que se escribe antes de leer
                temp_input_path = temp_input.name  # Guardar la ruta del archivo
            
            with open(temp_input_path, "r", encoding="utf-8") as source_file:
                source_code = source_file.read()
            log_debug(f"🔹 Código fuente escrito en {temp_input_path}:\n{source_code}")
            
            # Crear archivo temporal para la salida
            with tempfile.NamedTemporaryFile(delete=False, suffix=".tac", mode="w", encoding="utf-8") as temp_output:
                temp_input_tac = temp_output.name  # Guardar la ruta del archivo
                temp_output_path = temp_input_tac.replace(".tac", ".out")  
                temp_asm_path = temp_input_tac.replace(".tac", ".asm")  

            log_debug(f"🔹 Archivos temporales creados:\nOUT: {temp_output_path}\nASM: {temp_asm_path}")

            # Ejecutar el compilador con archivos temporales
            result = subprocess.run(
                [compiler_executable, temp_input_path, temp_output_path],
                capture_output=True,  # Captura salida para depuración
                text=True
            )


            # Esperar a que se genere el archivo de salida (.tac)
            timeout = 5  # Tiempo máximo de espera en segundos
            start_time = time.time()

            while not os.path.exists(temp_input_tac):
                if time.time() - start_time > timeout:
                    self.ui.Output.setPlainText("[Error]: Tiempo de espera agotado. El compilador no generó el archivo .tac")
                    return
                time.sleep(0.1)  # Esperar 100ms antes de volver a comprobar
            
            with open(temp_input_tac, "r", encoding="utf-8") as source_file:
                source_code = source_file.read()
            log_debug(f"🔹 Contenido de {temp_input_tac}:\n{source_code}")
            
            with open(temp_input_tac, "r", encoding="utf-8") as source_file:
                source_code = source_file.read()
            log_debug(f"🔹 Contenido de {temp_input_tac}:\n{source_code}")
            
            # # Ejecutar TAC.py con el archivo de salida del compilador
            result_tac = subprocess.run(
                ["python", tac_script, temp_input_tac],
                capture_output=False,
                text=False
            )
            
            timeout = 5  # Tiempo máximo de espera en segundos
            start_time = time.time()

            while not os.path.exists(temp_asm_path):
                if time.time() - start_time > timeout:
                    self.ui.Output.setPlainText("[Error]: Tiempo de espera agotado. El compilador no generó el archivo .tac")
                    return
                time.sleep(0.1)  # Esperar 100ms antes de volver a comprobar

            # # Verificar si la conversión TAC → ASM fue exitosa
            if result_tac.returncode != 0:
                self.ui.Output.setPlainText(f"[Error TAC]: {result_tac.stderr}")
                return
            
            with open(temp_asm_path, "r", encoding="utf-8") as asm_file:
                asm_code = asm_file.read()
            log_debug(f"🔹 Contenido de {temp_asm_path}:\n{asm_code}")
            self.ui.assembler_input.setPlainText(asm_code)

        finally:
            # Limpiar archivo temporal de entrada si aún existe
            if os.path.exists(temp_input_path):
                try:
                    os.remove(temp_input_path)
                except Exception as e:
                    print(f"Error al eliminar archivo temporal: {e}")

        
    def Ensamblador(self):
        texto = self.ui.assembler_input.toPlainText()  # Obtener el texto del QTextEdit

        # Crear un archivo temporal para pasar el contenido al analizador Flex
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_file.write(texto.encode("utf-8"))
            temp_file_path = temp_file.name

        # Ejecutar el analizador léxico en Flex (asumiendo que ya compilaste el ejecutable)
        flex_executable = "./compilados/ensamblador"
        if os.name != 'posix':
            flex_executable += ".exe"
        try:
            result = subprocess.run(
                [flex_executable, temp_file_path],  # Ejecuta el scanner con el archivo temporal
                capture_output=True,
                text=True,
                check=True
            )
            output = result.stdout  # Obtener la salida del scanner
            self.ui.binary_input.setPlainText(output)
        except Exception as e:
            self.ui.Output.setPlainText("[Error Ensamblador]: "+ str(e))
        
    def EnlazadorCargador(self):
        direccion_referencia = self.ui.linker_input.toPlainText()
        try:
            direccion_referencia = int(direccion_referencia)
            # Lee el código reubicable desde la UI
            texto = self.ui.binary_input.toPlainText()
            texto_modificado = texto

            # Crear un archivo temporal para la entrada (similar a compilador.bin)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".bin", mode="w", encoding="utf-8") as temp_in:
                temp_in.write(texto_modificado)
                temp_in_path = temp_in.name

            # Crear un nombre de archivo temporal para la salida (similar a executable.bin)
            temp_out_path = tempfile.mktemp(suffix=".bin")

            # Definir el comando y agregar la extensión si es Windows
            comando = "./compilados/linkerloader"
            if os.name != 'posix':
                comando += ".exe"

            # Ejecutar el linkerloader pasando los tres parámetros:
            # 1. La dirección de referencia
            # 2. El archivo de entrada generado temporalmente
            # 3. El archivo de salida donde se almacenará el ejecutable
            proceso = subprocess.run(
                [comando, str(direccion_referencia), temp_in_path, temp_out_path],
                capture_output=True,
                text=True
            )

            # Si hay errores en stderr, mostrarlos en la UI
            if proceso.stderr:
                self.ui.Output.append("[Error Linker]: " + proceso.stderr)

            # Leer el contenido del archivo de salida generado
            if os.path.exists(temp_out_path):
                with open(temp_out_path, "r", encoding="utf-8") as out_file:
                    salida = out_file.read().strip()
                # Mostrar la salida en el campo de texto de la UI
                self.ui.binary_input.setPlainText(salida)

                # Escribir la salida en la memoria a partir de la dirección de referencia
                for i, linea in enumerate(salida.splitlines()):
                    direccion = direccion_referencia + i
                    if direccion < len(self.memoria):
                        self.memoria[direccion] = linea

                # Actualizar el contador de programa
                self.setCp(direccion_referencia)

            # Limpiar el archivo temporal de entrada
            if os.path.exists(temp_in_path):
                os.remove(temp_in_path)
            # Puedes optar por eliminar el archivo de salida si no lo necesitas después:
            # if os.path.exists(temp_out_path):
            #     os.remove(temp_out_path)

        except ValueError as e:
            self.ui.Output.setPlainText("[Error Enlazador]: " + str(e))

        
    def LeerDato(self,direccion):
        instruccion = self.memoria.leer_memoria(direccion)
        return self.EjecutarComando(instruccion)
        
    def LeerInstruccion(self):
        instruccion = self.memoria.leer_memoria(self.cp)
        self.config_input = {"text":"","reg_input":reg,"Exxecute_all":False} 
        try:
            self.EjecutarComando(instruccion)
            self.setCp(self.cp+1)      
        except ValueError as e:
            self.ui.Output.setPlainText("[Error Ejecutando]: "+ str(e))
            
    def LeerInstrucciones(self):
        instruccion = self.memoria.leer_memoria(self.cp)
        while(self.IdentificarComando(instruccion) != 'HALT' 
              and self.IdentificarComando(instruccion) != 'IN' 
              and self.memoria.leer_memoria(self.cp) != 0 ):
            self.LeerInstruccion()
        if(self.IdentificarComando(instruccion) == 'IN'):
            self.config_input = {"text":"","reg_input":reg,"Exxecute_all":True} 
            try:
                #Ejecuta instruccion
                self.EjecutarComando(instruccion)
                self.setCp(self.cp+1)      
            except ValueError as e:
                self.ui.Output.setPlainText("[Error Ejecutando]: "+ str(e))
        
    def EjecutarComando(self,instruccion):
        nombre_comando = self.IdentificarComando(instruccion)
        print("🚀 ~ nombre_comando:", nombre_comando)
        self.setDir(instruccion)
        funcion = self.funciones.get(nombre_comando)  # Obtener la función con el mismo nombre
            
        if funcion:
            try:
                # Asegurar que la instrucción se maneje como cadena binaria y tenga 32 bits
                binario = str(instruccion).zfill(32)  # Asegurar que tenga 32 bits, rellenando con ceros a la izquierda
                resto_instruccion = binario[5:]  # Convertir los 27 bits restantes a entero
                return funcion(resto_instruccion)
            except ValueError:
                print("Error: La funcion debe ser un número entero.")
        else:
            print(f"Error: La función {nombre_comando} no está definida.")

    def IdentificarComando(self,instruccion):
        commandos = [
            "NOP", "LOAD", "STORE", "MOVE", "ADD", "SUB", "MUL", "DIV", "AND", "OR", "NOR",
            "NOT", "SHL", "SHR", "ROL", "ROR", "JUMP", "BEQ", "BNE", "BLT", "JLE", "PUSH", 
            "POP", "CALL", "RET", "IN", "OUT", "CMP", "CLR", "LOADR", "STORER", "HALT"
        ]
        
        try:
            binario = str(instruccion).zfill(32)  # Asegurar que tenga 32 bits, llenando con ceros a la izquierda
            
            # Extraer los primeros 5 bits del binario
            opcode_binario = binario[:5]
            opcode = int(opcode_binario, 2)  # Convertir los primeros 5 bits a entero

            if 0 <= opcode < len(commandos):
                return commandos[opcode]
            else:
                print(f"Error: Código de instrucción fuera de rango ({opcode}).")
                return "ERROR"
        except ValueError:
            print("Error: El comando debe ser un número entero.")
            return "ERROR"

    def NOP(self,instruccion):
        type_dato = instruccion[:6]
        print("🚀 ~ instruccion:", instruccion)
        tipo_dato = int(type_dato, 2)
        print("🚀 ~ tipo_dato:", tipo_dato)
        
        # Determinar el tipo de dato según el valor de los primeros 6 bits
        if tipo_dato == 1:
            return GetBooleano(instruccion[6:])
        elif tipo_dato == 2:
            return GetNatural(instruccion[6:])
        elif tipo_dato == 3:
            return GetEntero(instruccion[6:])
        elif tipo_dato == 4:
            return GetFloat(instruccion[6:])
        elif tipo_dato == 5:
            return GetCaracterUtf16(instruccion[6:])
        else:
            print("Error: La data debe ser un número entero.")
            return "ERROR"
        
    def LOAD(self, instruccion):
        reg_destino = int(instruccion[:2], 2)
        dir_origen = int(instruccion[2:], 2)
        
        # Debug prints
        print(f"LOAD: Reading from memory address {dir_origen} value {self.LeerDato(dir_origen)}")
        print(f"LOAD: Will store into register {reg_destino}")
        
        # Make sure this actually loads into reg_destino, not some other register
        self.guardar_en_registro(reg_destino, self.LeerDato(dir_origen))
        
        # Verify after loading
        print(f"LOAD: Register {reg_destino} now has value {self.registro[reg_destino]}")
      
    def STORE(self, instruccion):
        reg_origen = int(instruccion[:2], 2)
        dir_destino = int(instruccion[2:], 2)
        
        print(f"STORE: Raw instruction bits: {instruccion}")
        print(f"STORE: Parsed reg_origen={reg_origen}, dir_destino={dir_destino}")
        print(f"STORE: Register {reg_origen} value = {self.registro[reg_origen]}")
        
        # Store the value from the specified register to memory
        self.memoria.escribir_memoria(dir_destino, ConvertirDatoBinario(self.registro[reg_origen]))
        return 0
        
    def MOVE(self,instruccion):
        reg_destino = int(instruccion[:2], 2)
        reg_origen = int(instruccion[2:4], 2)
        self.guardar_en_registro(reg_origen,self.LeerDato(reg_destino))
        return 0
        
    def ADD(self, instruccion):
        # Check these bit positions - they might be incorrect
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        reg_destino = int(instruccion[4:6], 2)
        
        # Debug prints
        print(f"ADD: Raw instruction bits: {instruccion}")
        print(f"ADD: Parsed reg_1={reg_1}, reg_2={reg_2}, reg_destino={reg_destino}")
        print(f"ADD: Register {reg_1} value = {self.registro[reg_1]}")
        print(f"ADD: Register {reg_2} value = {self.registro[reg_2]}")
        
        # Do the addition
        suma = self.registro[reg_1] + self.registro[reg_2]
        print(f"ADD: Sum result = {suma}, storing in Register {reg_destino}")
        
        # Store result
        self.guardar_en_registro(reg_destino, suma)
        
        # Set flags appropriately
        
        return 0
        
    def SUB(self,instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        reg_destino = int(instruccion[4:6], 2)
        resta = self.registro[reg_1] - self.registro[reg_2]
        if resta == 0:
            self.setZero(1)
        if resta < 0:
            self.setNegative(1)
        self.guardar_en_registro(reg_destino,resta)
        return 0
        
    def MUL(self,instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        reg_destino = int(instruccion[4:6], 2)
        multi = self.registro[reg_1] * self.registro[reg_2]
        if multi > 2097151:
            self.setDesb(1)
            self.setCarry(1)
        if multi == 0:
            self.setZero(1)
        self.guardar_en_registro(reg_destino,multi)
        return 0
        
    def DIV(self,instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        reg_destino = int(instruccion[4:6], 2)
        div = self.registro[reg_1] / self.registro[reg_2]
        if div == 0:
            self.setZero(1)
        self.guardar_en_registro(reg_destino,div)
        return 0
        
    def AND(self,instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        reg_destino = int(instruccion[4:6], 2)
        self.guardar_en_registro(reg_destino,int(self.registro[reg_1] & self.registro[reg_2]))
        return 0
        
    def OR(self,instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        reg_destino = int(instruccion[4:6], 2)
        self.guardar_en_registro(reg_destino,int(self.registro[reg_1] | self.registro[reg_2]))
        return 0
        
    def NOR(self,instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        reg_destino = int(instruccion[4:6], 2)
        self.guardar_en_registro(reg_destino,int(~(self.registro[reg_1] | self.registro[reg_2])))
        return 0
        
    def NOT(self,instruccion):
        reg_1 = int(instruccion[:2], 2)
        self.guardar_en_registro(reg_1,int(~(self.registro[reg_1])))
        return 0
        
    def SHL(self,instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        self.guardar_en_registro(reg_1,self.registro[reg_1] << self.registro[reg_2])
        return 0
        
    def SHR(self,instruccion):
        reg_1 = int(instruccion[:2], 2)  
        reg_2 = int(instruccion[2:4], 2) 
        self.guardar_en_registro(reg_1,self.registro[reg_1] >> self.registro[reg_2])
        return 0
        
    def ROL(self, instruccion):
        reg_1 = int(instruccion[:2], 2)  # Índice del registro destino
        reg_2 = int(instruccion[2:4], 2)  # Índice del registro que contiene el número de rotaciones

        tmp_reg = self.registro
        valor = tmp_reg[reg_1]  # Valor del registro a rotar
        n_bits = tmp_reg[reg_2]  # Número de bits a rotar

        BITS = 16
        n_bits %= BITS  # Asegurar que la rotación no exceda el tamaño del dato
        
        self.guardar_en_registro(reg_1,((valor << n_bits) & ((1 << BITS) - 1)) | (valor >> (BITS - n_bits)))
        return 0
        
    def ROR(self, instruccion):
        reg_1 = int(instruccion[:2], 2)  # Índice del registro destino
        reg_2 = int(instruccion[2:4], 2)  # Índice del registro que contiene el número de rotaciones

        tmp_reg = self.registro
        valor = tmp_reg[reg_1]  # Valor del registro a rotar
        n_bits = tmp_reg[reg_2]  # Número de bits a rotar

        BITS = 16
        n_bits %= BITS  # Asegurar que la rotación no exceda el tamaño del dato
        
        self.guardar_en_registro(reg_1,(valor >> n_bits) | ((valor & ((1 << n_bits) - 1)) << (BITS - n_bits)))
        return 0

    def JUMP(self,instruccion):
        dir_destino = int(instruccion, 2)        
        self.setCp(dir_destino)
        return 0

    def BEQ(self, instruccion):
        """
        Branch if Equal.
        
        In this design, BEQ assumes that a CMP instruction has already been executed
        so that the Zero flag reflects the equality of the two compared operands.
        
        The instruction is assumed to encode the branch target address in all its bits.
        If the Zero flag is 1 (i.e. the last CMP found the operands equal), the
        program counter is set to the target address.
        """
        # Convert the entire instruction to a branch target address.
        branch_target = int(instruccion, 2)
        
        print(f"BEQ: Zero flag = {self.zero}. Branch target = {branch_target}.")
        if self.zero == 1:
            self.setCp(branch_target)
            print(f"BEQ: Branch taken. CP set to {branch_target}.")
        else:
            print("BEQ: Branch not taken.")
        
        return 0

    def BNE(self, instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        dir_destino = int(instruccion[4:], 2)
        
        if self.registro[reg_1] != self.registro[reg_2]:
            self.setNegative(1)
            self.setCp(dir_destino)

    def BLT(self, instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        dir_destino = int(instruccion[4:], 2)
        
        if self.registro[reg_1] < self.registro[reg_2]:
            self.setNegative(1)
            self.setCp(dir_destino)

    def JLE(self, instruccion):
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        dir_destino = int(instruccion[4:], 2)
        
        if self.registro[reg_1] < self.registro[reg_2]:
            self.setNegative(1)            
        if self.registro[reg_1] == self.registro[reg_2]:
            self.setZero(1)
        
        if self.registro[reg_1] <= self.registro[reg_2]:
            self.setCp(dir_destino)

    def PUSH(self,instruccion):
        reg_index = int(instruccion[:2], 2)
        direccion = self.registro[reg_index]
        self.memoria.push_stack(direccion)
        return 0

    def POP(self,instruccion):
        reg_index = int(instruccion[:2], 2)
        direccion = self.memoria.pop_stack()
        self.guardar_en_registro(reg_index,direccion)
        return 0

    def CALL(self,instruccion):
        direccion = int(instruccion, 2)
        self.memoria.push_stack(self.cp)
        self.setCp(direccion)
        return 0

    def RET(self,instruccion):
        direccion = self.memoria.pop_stack()
        self.setCp(direccion-1)
        return 0

    def IN(self, instruccion):
        """Espera la entrada del usuario y la almacena en el registro correspondiente."""
        print("IN", instruccion)
        reg = int(instruccion[:2], 2)  # Obtener el índice del registro
        self.config_input = {"text":"","reg_input":reg,"Exxecute_all":self.config_input['Exxecute_all']}
        self.ui.input_button.setDisabled(False)
        self.ui.Read_Next_Instruction.setDisabled(True)
            
    def OUT(self,instruccion):
        reg_1 = int(instruccion[:2], 2)        
        self.ui.Output.setPlainText(str(self.registro[reg_1]))
        return 0

    def CMP(self, instruccion):
        """
        Compare the values in two registers.
        
        Assumes that the instruction encodes:
        - The first 2 bits: register index for operand 1
        - The next 2 bits: register index for operand 2
        It subtracts the second operand from the first, sets the zero flag
        if the result is zero, and the negative flag if the result is negative.
        """
        # Extract register indices from the first 4 bits.
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        
        value1 = self.registro[reg_1]
        value2 = self.registro[reg_2]
        result = value1 - value2

        # Set the Zero flag: 1 if result is zero, else 0.
        self.setZero(1 if result == 0 else 0)
        
        # Set the Negative flag: 1 if result is negative, else 0.
        self.setNegative(1 if result < 0 else 0)

        # Set the Carry flag: 1 if there is a carry, else 0.
        self.setCarry(1 if result < 0 else 0)

        # Set the Overflow flag: 1 if there is an overflow, else 0.
        self.setDesb(1 if result > 32767 or result < -32768 else 0)
        
        # (Optional: you could also set a carry flag if desired.)
        print(f"CMP: Comparing R{reg_1}({value1}) with R{reg_2}({value2}).")
        print(f"CMP: Result = {result}. Zero flag set to {self.zero}, Negative flag set to {self.negative}.")
        
        return 0

    def CLR(self,instruccion):
        print("CLR",instruccion)
        return 0

    def LOADR(self,instruccion):
        reg_destino = int(instruccion[:2], 2)
        reg_origen = int(instruccion[2:4], 2)
        self.registro[reg_destino] = self.registro[reg_origen]

    def STORER(self,instruccion):
        reg_origen = int(instruccion[:2], 2)
        dir_destino = int(instruccion[2:], 2)
        self.memoria.escribir_memoria(reg_origen,self.LeerDato(dir_destino))
        return 0

    def HALT(self,instruccion):
        return 0  
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())