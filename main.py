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
    """
    Clase principal que implementa una máquina virtual con capacidades de compilación,
    ensamblado, enlazado y ejecución de instrucciones de bajo nivel.
    Proporciona una interfaz gráfica para interactuar con todas estas funcionalidades.
    """
    def __init__(self):
        """
        Inicializa la ventana principal, configurando la interfaz gráfica y
        estableciendo el estado inicial de la máquina virtual (registros, banderas, etc.).
        También configura los manejadores de eventos para los botones de la interfaz.
        """
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.cp = 0  # Contador de programa
        self.registro = [0] * 4  # Registros de propósito general (A, B, C, D)
        self.carry = 0  # Bandera de acarreo
        self.zero = 0  # Bandera de cero
        self.negative = 0  # Bandera de negativo
        self.desbordamiento = 0  # Bandera de desbordamiento
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
        # Diccionario que mapea nombres de instrucciones a sus implementaciones correspondientes
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
        """
        Carga un nuevo valor para el contador de programa (CP) desde la interfaz.
        Verifica que el valor sea un entero válido antes de actualizarlo.
        """
        valor = self.ui.CP_Set.toPlainText()
        try:
            valor = int(valor)
            self.setCp(valor)
        except ValueError as e:
            print(f"Error: '{valor}' no es un número válido.")
            self.ui.Output.setPlainText("[Error Enlazador]: "+ str(e))
             
    def getInput(self):
        """
        Procesa la entrada del usuario desde la interfaz gráfica y la almacena en el registro
        especificado por config_input["reg_input"]. Si "Exxecute_all" está establecido,
        continúa la ejecución de instrucciones después de recibir la entrada.
        """
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
        """
        Actualiza el contador de programa (CP) con el nuevo valor proporcionado
        y refleja este cambio en la interfaz gráfica. También actualiza la
        visualización de la memoria según el nuevo CP.
        
        Args:
            new_cp (int): Nuevo valor para el contador de programa
        """
        try:
            self.cp = new_cp
            self.ui.CP_Set.setPlainText(str(new_cp))
            self.memoria.mover_cp(int(new_cp))
        except ValueError as e:
            print(f"Error: '{new_cp}' no es un número válido.")
            self.ui.Output.setPlainText("[Error Enlazador]: "+ str(e))
            
    def setDir(self,new_dir):
        """
        Actualiza el registro de dirección con el nuevo valor proporcionado
        y actualiza la interfaz gráfica correspondiente.
        
        Args:
            new_dir (int): Nuevo valor para el registro de dirección
        """
        try:
            self.dir = new_dir
            self.ui.DIR.setPlainText(str(new_dir))
        except ValueError as e:
            print(f"Error: '{new_dir}' no es un número válido.")
            self.ui.Output.setPlainText("[Error Instruccion]: "+ str(e))
        
    def actualizarTablaMemoria(self):
        """ 
        Actualiza la visualización de la tabla de memoria en la interfaz.
        Resalta la fila correspondiente al CP actual y muestra los últimos
        100 registros de la memoria en la tabla de pila.
        """
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
        """
        Almacena un valor en el registro especificado y actualiza la 
        visualización de los registros en la interfaz.
        
        Args:
            indice (int): Índice del registro (0-3 para A, B, C, D)
            value: Valor a almacenar en el registro
        """
        temp_reg = self.registro
        temp_reg[indice] = value
        self.set_REG_Values(temp_reg)
        
    def set_REG_Values(self,arreglo):
        """
        Actualiza todos los registros con los valores proporcionados en el arreglo
        y actualiza sus representaciones tanto en formato decimal como binario en la interfaz.
        
        Args:
            arreglo (list): Lista de 4 valores para los registros A, B, C y D
        """
        self.registro[0] = arreglo[0]
        self.registro[1] = arreglo[1]
        self.registro[2] = arreglo[2]
        self.registro[3] = arreglo[3]
        self.ui.REG_A.setText(str(arreglo[0]))
        self.ui.REG_B.setText(str(arreglo[1]))
        self.ui.REG_C.setText(str(arreglo[2]))
        self.ui.REG_D.setText(str(arreglo[3]))
        
        def convertir_a_binario(valor):
            """
            Convierte un valor a su representación binaria de 16 bits dependiendo de su tipo.
            
            Args:
                valor: Valor a convertir (int, float, str, bool)
            
            Returns:
                str: Representación binaria del valor en 16 bits
            """
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
        """
        Actualiza el valor de la bandera de acarreo y su visualización en la interfaz.
        
        Args:
            caryy (int): Nuevo valor para la bandera de acarreo (0 o 1)
        """
        self.carry = caryy
        self.ui.REG_Carry.setText(str(caryy))
        self.ui.BIN_Carry.setText(int_to_bin16(caryy))
      
    def setZero(self,zero):
        """
        Actualiza el valor de la bandera de cero y su visualización en la interfaz.
        
        Args:
            zero (int): Nuevo valor para la bandera de cero (0 o 1)
        """
        self.zero = zero
        self.ui.REG_Zero.setText(str(zero))
        self.ui.BIN_Zero.setText(int_to_bin16(zero))
        
    def setNegative(self,negative):
        """
        Actualiza el valor de la bandera de negativo y su visualización en la interfaz.
        
        Args:
            negative (int): Nuevo valor para la bandera de negativo (0 o 1)
        """
        self.negative = negative
        self.ui.REG_Neg.setText(str(negativo))
        self.ui.BIN_Neg.setText(int_to_bin16(negativo))
        
    def setDesb(self,desbordamiento):
        """
        Actualiza el valor de la bandera de desbordamiento y su visualización en la interfaz.
        
        Args:
            desbordamiento (int): Nuevo valor para la bandera de desbordamiento (0 o 1)
        """
        self.desbordamiento = desbordamiento
        self.ui.REG_Desb.setText(str(desbordamiento))
        self.ui.BIN_Desb.setText(int_to_bin16(desbordamiento))
    
    def resetBanderas(self):
        """
        Reinicia todas las banderas (carry, zero, negative, desbordamiento) a 0.
        Útil después de ciertas operaciones para limpiar el estado de las banderas.
        """
        self.setCarry(0)
        self.setZero(0)
        self.setNegative(0)
        self.setDesb(0)
        
    def Preprocesado(self):
        """
        Realiza el preprocesamiento del código fuente utilizando un ejecutable externo (flex).
        Lee el código fuente desde la interfaz, lo escribe en un archivo temporal,
        ejecuta el preprocesador y muestra el resultado en la interfaz.
        """
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
        """
        Ejecuta el proceso de compilación del código preprocesado.
        Utiliza un ejecutable externo para compilar el código y generar
        un archivo de código TAC (Three-Address Code), que luego se convierte
        a ensamblador mediante otro script Python.
        
        Maneja archivos temporales para la entrada/salida y muestra el resultado
        en la interfaz gráfica.
        """
        def log_debug(message):
            """ 
            Escribe mensajes de depuración en un archivo de log.
            Útil para rastrear el proceso de compilación.
            
            Args:
                message (str): Mensaje a registrar en el archivo de depuración
            """
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
        """
        Ejecuta el proceso de ensamblado del código en lenguaje ensamblador.
        Toma el código ensamblador de la interfaz, lo escribe en un archivo temporal,
        ejecuta el ensamblador externo y muestra el código binario resultante en la interfaz.
        """
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
        """
        Ejecuta el proceso de enlazado y carga del código binario en la memoria.
        Toma la dirección de referencia y el código binario de la interfaz,
        ejecuta el enlazador-cargador externo y carga el código resultante en la
        memoria de la máquina virtual a partir de la dirección de referencia.
        
        También actualiza el contador de programa para apuntar a la dirección inicial del programa.
        """
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
        """
        Lee un dato almacenado en la dirección de memoria especificada.
        Útil para instrucciones que requieren acceder a valores en memoria.
        
        Args:
            direccion (int): Dirección de memoria a leer
            
        Returns:
            El valor almacenado en la dirección de memoria, procesado según 
            su tipo de dato (entero, float, booleano, etc.)
        """
        instruccion = self.memoria.leer_memoria(direccion)
        return self.EjecutarComando(instruccion)
        
    def LeerInstruccion(self):
        """
        Lee y ejecuta la instrucción ubicada en la dirección actual del contador de programa.
        Después de la ejecución, incremente el CP para apuntar a la siguiente instrucción.
        
        Es utilizada para la ejecución paso a paso del programa cargado en memoria.
        """
        instruccion = self.memoria.leer_memoria(self.cp)
        self.config_input = {"text":"","reg_input":reg,"Exxecute_all":False} 
        try:
            self.EjecutarComando(instruccion)
            self.setCp(self.cp+1)      
        except ValueError as e:
            self.ui.Output.setPlainText("[Error Ejecutando]: "+ str(e))
            
    def LeerInstrucciones(self):
        """
        Lee y ejecuta instrucciones desde la dirección actual del CP hasta encontrar
        una instrucción HALT, IN o un valor 0 en memoria.
        
        Es utilizada para la ejecución continua del programa cargado en memoria.
        Si encuentra una instrucción IN, pausa la ejecución y espera la entrada del usuario.
        """
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
        """
        Identifica y ejecuta el comando representado por la instrucción binaria.
        Extrae el código de operación (opcode) y llama a la función correspondiente
        pasando los bits restantes de la instrucción como parámetros.
        
        Args:
            instruccion: Instrucción binaria a ejecutar
            
        Returns:
            El resultado de la ejecución de la instrucción
        """
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
        """
        Identifica el tipo de comando/instrucción a partir de su representación binaria.
        Extrae los primeros 5 bits de la instrucción para determinar el código de operación
        y devuelve el nombre del comando correspondiente.
        
        Args:
            instruccion: Instrucción binaria a identificar
            
        Returns:
            str: Nombre del comando identificado, o "ERROR" si no se puede identificar
        """
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
        """
        Implementa la instrucción NOP (No Operation).
        En esta implementación, NOP se utiliza para interpretar y devolver
        un valor de datos según su tipo (booleano, natural, entero, float o carácter).
        
        Args:
            instruccion (str): Bits de la instrucción que contienen información del dato
            
        Returns:
            El valor del dato según su tipo identificado
        """
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
        """
        Implementa la instrucción LOAD que carga un valor desde la memoria a un registro.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen el registro destino
                            y la dirección de memoria origen
        
        Returns:
            int: 0 para indicar éxito
        """
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
        """
        Implementa la instrucción STORE que almacena el valor de un registro en la memoria.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen el registro origen
                            y la dirección de memoria destino
        
        Returns:
            int: 0 para indicar éxito
        """
        reg_origen = int(instruccion[:2], 2)
        dir_destino = int(instruccion[2:], 2)
        
        print(f"STORE: Raw instruction bits: {instruccion}")
        print(f"STORE: Parsed reg_origen={reg_origen}, dir_destino={dir_destino}")
        print(f"STORE: Register {reg_origen} value = {self.registro[reg_origen]}")
        
        # Store the value from the specified register to memory
        self.memoria.escribir_memoria(dir_destino, ConvertirDatoBinario(self.registro[reg_origen]))
        return 0
        
    def MOVE(self,instruccion):
        """
        Implementa la instrucción MOVE que copia el valor de un registro a otro.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen los registros
                            origen y destino
        
        Returns:
            int: 0 para indicar éxito
        """
        reg_destino = int(instruccion[:2], 2)
        reg_origen = int(instruccion[2:4], 2)
        self.guardar_en_registro(reg_origen,self.LeerDato(reg_destino))
        return 0
        
    def ADD(self, instruccion):
        """
        Implementa la instrucción ADD que suma los valores de dos registros
        y almacena el resultado en un tercero.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen los registros
                            operandos y el registro destino
        
        Returns:
            int: 0 para indicar éxito
        """
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
        """
        Implementa la instrucción SUB que resta el valor del segundo registro del primero
        y almacena el resultado en un tercero. También actualiza las banderas Zero y Negative.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen los registros
                            operandos y el registro destino
        
        Returns:
            int: 0 para indicar éxito
        """
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
        """
        Implementa la instrucción MUL que multiplica los valores de dos registros
        y almacena el resultado en un tercero. Actualiza las banderas de Desbordamiento,
        Carry y Zero según corresponda.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen los registros
                            operandos y el registro destino
        
        Returns:
            int: 0 para indicar éxito
        """
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
        """
        Implementa la instrucción DIV que divide el valor del primer registro entre el segundo
        y almacena el resultado en un tercero. Actualiza la bandera Zero si el resultado es cero.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen los registros
                            operandos y el registro destino
        
        Returns:
            int: 0 para indicar éxito
        """
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        reg_destino = int(instruccion[4:6], 2)
        div = self.registro[reg_1] / self.registro[reg_2]
        if div == 0:
            self.setZero(1)
        self.guardar_en_registro(reg_destino,div)
        return 0
        
    def AND(self,instruccion):
        """
        Implementa la instrucción AND que realiza la operación lógica AND bit a bit
        entre los valores de dos registros y almacena el resultado en un tercero.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen los registros
                            operandos y el registro destino
        
        Returns:
            int: 0 para indicar éxito
        """
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        reg_destino = int(instruccion[4:6], 2)
        self.guardar_en_registro(reg_destino,int(self.registro[reg_1] & self.registro[reg_2]))
        return 0
        
    def OR(self,instruccion):
        """
        Implementa la instrucción OR que realiza la operación lógica OR bit a bit
        entre los valores de dos registros y almacena el resultado en un tercero.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen los registros
                            operandos y el registro destino
        
        Returns:
            int: 0 para indicar éxito
        """
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        reg_destino = int(instruccion[4:6], 2)
        self.guardar_en_registro(reg_destino,int(self.registro[reg_1] | self.registro[reg_2]))
        return 0
        
    def NOR(self,instruccion):
        """
        Implementa la instrucción NOR que realiza la operación lógica NOR bit a bit
        entre los valores de dos registros y almacena el resultado en un tercero.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen los registros
                            operandos y el registro destino
        
        Returns:
            int: 0 para indicar éxito
        """
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        reg_destino = int(instruccion[4:6], 2)
        self.guardar_en_registro(reg_destino,int(~(self.registro[reg_1] | self.registro[reg_2])))
        return 0
        
    def NOT(self,instruccion):
        """
        Implementa la instrucción NOT que invierte bit a bit el valor del registro especificado.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen el registro a invertir
        
        Returns:
            int: 0 para indicar éxito
        """
        reg_1 = int(instruccion[:2], 2)
        self.guardar_en_registro(reg_1,int(~(self.registro[reg_1])))
        return 0
        
    def SHL(self,instruccion):
        """
        Implementa la instrucción SHL (Shift Left) que desplaza a la izquierda los bits
        del primer registro tantas posiciones como indique el valor del segundo registro.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen los registros operandos
        
        Returns:
            int: 0 para indicar éxito
        """
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        self.guardar_en_registro(reg_1,self.registro[reg_1] << self.registro[reg_2])
        return 0
        
    def SHR(self,instruccion):
        """
        Implementa la instrucción SHR (Shift Right) que desplaza a la derecha los bits
        del primer registro tantas posiciones como indique el valor del segundo registro.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen los registros operandos
        
        Returns:
            int: 0 para indicar éxito
        """
        reg_1 = int(instruccion[:2], 2)  
        reg_2 = int(instruccion[2:4], 2) 
        self.guardar_en_registro(reg_1,self.registro[reg_1] >> self.registro[reg_2])
        return 0
        
    def ROL(self, instruccion):
        """
        Implementa la instrucción ROL (Rotate Left) que rota a la izquierda los bits
        del primer registro tantas posiciones como indique el valor del segundo registro.
        A diferencia de SHL, los bits desplazados fuera del registro se vuelven a insertar por la derecha.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen los registros operandos
        
        Returns:
            int: 0 para indicar éxito
        """
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
        """
        Implementa la instrucción ROR (Rotate Right) que rota a la derecha los bits
        del primer registro tantas posiciones como indique el valor del segundo registro.
        A diferencia de SHR, los bits desplazados fuera del registro se vuelven a insertar por la izquierda.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen los registros operandos
        
        Returns:
            int: 0 para indicar éxito
        """
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
        """
        Implementa la instrucción JUMP que realiza un salto incondicional a la dirección especificada.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen la dirección destino del salto
        
        Returns:
            int: 0 para indicar éxito
        """
        dir_destino = int(instruccion, 2)        
        self.setCp(dir_destino)
        return 0

    def BEQ(self, instruccion):
        """
        Implementa la instrucción BEQ (Branch if Equal) que realiza un salto condicional
        a la dirección especificada si la bandera Zero está activa (resultado de una comparación previa).
        
        Args:
            instruccion (str): Bits de la instrucción que contienen la dirección destino del salto
        
        Returns:
            int: 0 para indicar éxito
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
        """
        Implementa la instrucción BNE (Branch if Not Equal) que realiza un salto condicional
        si los valores de los dos registros especificados son diferentes.
        También actualiza la bandera Negative.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen los registros a comparar
                            y la dirección destino del salto
        
        Returns:
            int: 0 para indicar éxito
        """
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        dir_destino = int(instruccion[4:], 2)
        
        if self.registro[reg_1] != self.registro[reg_2]:
            self.setNegative(1)
            self.setCp(dir_destino)

    def BLT(self, instruccion):
        """
        Implementa la instrucción BLT (Branch if Less Than) que realiza un salto condicional
        si el valor del primer registro es menor que el del segundo registro.
        También actualiza la bandera Negative.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen los registros a comparar
                            y la dirección destino del salto
        
        Returns:
            int: 0 para indicar éxito
        """
        reg_1 = int(instruccion[:2], 2)
        reg_2 = int(instruccion[2:4], 2)
        dir_destino = int(instruccion[4:], 2)
        
        if self.registro[reg_1] < self.registro[reg_2]:
            self.setNegative(1)
            self.setCp(dir_destino)

    def JLE(self, instruccion):
        """
        Implementa la instrucción JLE (Jump if Less or Equal) que realiza un salto condicional
        si el valor del primer registro es menor o igual que el del segundo registro.
        Actualiza las banderas Negative y Zero según corresponda.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen los registros a comparar
                            y la dirección destino del salto
        
        Returns:
            int: 0 para indicar éxito
        """
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
        """
        Implementa la instrucción PUSH que guarda el valor del registro especificado
        en la pila de la máquina virtual.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen el registro origen
        
        Returns:
            int: 0 para indicar éxito
        """
        reg_index = int(instruccion[:2], 2)
        direccion = self.registro[reg_index]
        self.memoria.push_stack(direccion)
        return 0

    def POP(self,instruccion):
        """
        Implementa la instrucción POP que recupera un valor de la pila
        y lo almacena en el registro especificado.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen el registro destino
        
        Returns:
            int: 0 para indicar éxito
        """
        reg_index = int(instruccion[:2], 2)
        direccion = self.memoria.pop_stack()
        self.guardar_en_registro(reg_index,direccion)
        return 0

    def CALL(self,instruccion):
        """
        Implementa la instrucción CALL que guarda la dirección de retorno (CP actual)
        en la pila y salta a la subrutina ubicada en la dirección especificada.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen la dirección de la subrutina
        
        Returns:
            int: 0 para indicar éxito
        """
        direccion = int(instruccion, 2)
        self.memoria.push_stack(self.cp)
        self.setCp(direccion)
        return 0

    def RET(self,instruccion):
        """
        Implementa la instrucción RET que recupera la dirección de retorno de la pila
        y establece el CP a dicha dirección (menos 1, para compensar el incremento posterior).
        
        Args:
            instruccion (str): Bits de la instrucción (no utilizados en esta instrucción)
        
        Returns:
            int: 0 para indicar éxito
        """
        direccion = self.memoria.pop_stack()
        self.setCp(direccion-1)
        return 0

    def IN(self, instruccion):
        """
        Implementa la instrucción IN que solicita una entrada al usuario
        y la almacena en el registro especificado. Configura la interfaz para
        esperar la entrada del usuario antes de continuar la ejecución.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen el registro destino
        
        Returns:
            int: 0 para indicar éxito
        """
        print("IN", instruccion)
        reg = int(instruccion[:2], 2)  # Obtener el índice del registro
        self.config_input = {"text":"","reg_input":reg,"Exxecute_all":self.config_input['Exxecute_all']}
        self.ui.input_button.setDisabled(False)
        self.ui.Read_Next_Instruction.setDisabled(True)
            
    def OUT(self,instruccion):
        """
        Implementa la instrucción OUT que muestra el valor del registro especificado
        en la salida de la interfaz gráfica.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen el registro origen
        
        Returns:
            int: 0 para indicar éxito
        """
        reg_1 = int(instruccion[:2], 2)        
        self.ui.Output.setPlainText(str(self.registro[reg_1]))
        return 0

    def CMP(self, instruccion):
        """
        Implementa la instrucción CMP que compara los valores de dos registros
        y establece las banderas Zero y Negative según el resultado de la comparación.
        Esta instrucción es útil antes de ejecutar instrucciones de salto condicional.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen los registros a comparar
        
        Returns:
            int: 0 para indicar éxito
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
        
        # (Optional: you could also set a carry flag if desired.)
        print(f"CMP: Comparing R{reg_1}({value1}) with R{reg_2}({value2}).")
        print(f"CMP: Result = {result}. Zero flag set to {self.zero}, Negative flag set to {self.negative}.")
        
        return 0

    def CLR(self,instruccion):
        """
        Implementa la instrucción CLR (Clear) que pone a cero un registro o una posición de memoria.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen el registro o dirección a limpiar
        
        Returns:
            int: 0 para indicar éxito
        """
        print("CLR",instruccion)
        return 0

    def LOADR(self,instruccion):
        """
        Implementa la instrucción LOADR (Load Register) que copia el valor
        de un registro a otro sin acceder a memoria.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen los registros
                            destino y origen
        
        Returns:
            int: 0 para indicar éxito
        """
        reg_destino = int(instruccion[:2], 2)
        reg_origen = int(instruccion[2:4], 2)
        self.registro[reg_destino] = self.registro[reg_origen]

    def STORER(self,instruccion):
        """
        Implementa la instrucción STORER (Store Register) que almacena en memoria
        el valor de un registro en la dirección especificada por otro registro.
        
        Args:
            instruccion (str): Bits de la instrucción que contienen los registros
                            origen y dirección
        
        Returns:
            int: 0 para indicar éxito
        """
        reg_origen = int(instruccion[:2], 2)
        dir_destino = int(instruccion[2:], 2)
        self.memoria.escribir_memoria(reg_origen,self.LeerDato(dir_destino))
        return 0

    def HALT(self,instruccion):
        """
        Implementa la instrucción HALT que detiene la ejecución del programa.
        
        Args:
            instruccion (str): Bits de la instrucción (no utilizados en esta instrucción)
        
        Returns:
            int: 0 para indicar éxito
        """
        return 0  
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())