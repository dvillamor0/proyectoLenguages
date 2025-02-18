from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QColor


class Memoria:
    def __init__(self, ui):
        self.ui = ui  # Referencia a la interfaz gráfica
        self.memoria = {i: 0 for i in range(1000)}
        self.cp = 0  # Inicializamos el Contador de Programa
        self.stack_size = 100  # Los últimos 30 registros son parte de la pila
        self.stack_start = len(self.memoria) - self.stack_size

        # Configurar la tabla en la UI
        self.ui.table_memoria.setColumnCount(1)
        self.ui.table_memoria.setHorizontalHeaderLabels(["Contenido"])
        self.ui.table_memoria.horizontalHeader().setStretchLastSection(True)

    def __len__(self):
        return len(self.memoria)
    
    def __setitem__(self, key, value):
        self.escribir_memoria(key, value)
    
    def items(self):
        return self.memoria.items()  # Devuelve un iterable de pares clave-valor
    
    def actualizar_memoria_ui(self):
        self.ui.table_memoria.setRowCount(len(self.memoria))

        for fila, (direccion, valor) in enumerate(sorted(self.memoria.items())):
            self.ui.table_memoria.setItem(fila, 0, QTableWidgetItem(str(valor)))
            item = QTableWidgetItem(str(valor))
            # Resaltar la fila si es la dirección de `cp`
            if direccion == self.cp:
                item.setBackground(QColor(255, 255, 0))  # Amarillo
            else:
                item.setBackground(QColor(255, 255, 255))  # Blanco

            self.ui.table_memoria.setItem(fila, 0, item)

    def escribir_memoria(self, direccion, valor):
        """Escribe un valor en la memoria, no puede escribir en la pila."""
        if 0 <= direccion < self.stack_start:  # Si no es parte de la pila
            if valor == 0 and direccion in self.memoria:
                del self.memoria[direccion]  # Elimina si vuelve a 0 para ahorrar espacio
            else:
                self.memoria[direccion] = valor
            self.actualizar_memoria_ui()  # Refresca la tabla en la UI
        else:
            print(f"Error: No se puede escribir en la pila en la dirección {direccion}")

    def leer_memoria(self, direccion):
        """Lee un valor de la memoria."""
        return self.memoria.get(direccion, 0)  # Devuelve 0 si no está guardado

    
    def mover_cp(self,new_cp):
        if 0 <= new_cp < len(self.memoria):
            self.cp = new_cp
            self.actualizar_memoria_ui()
    
    def push_stack(self, valor):
        """Agrega un valor a la pila (últimas 30 direcciones)."""
        # Verifica que haya espacio en la pila
        print("🚀 ~ valor:", valor)
        print("🚀 ~ valor:", valor)
        for i in range(self.stack_start, len(self.memoria)):
            if self.memoria[i] == 0:  # Si la dirección está vacía
                self.memoria[i] = valor
                self.actualizar_memoria_ui()
                return
        print("Error: La pila está llena, no se puede hacer push.")
    
    def pop_stack(self):
        """Elimina un valor de la pila (últimas 30 direcciones)."""
        for i in range(len(self.memoria) - 1, self.stack_start - 1, -1):  # Comienza desde el final
            if i in self.memoria:
                valor = self.memoria.pop(i)
                self.actualizar_memoria_ui()
                return valor
        print("Error: La pila está vacía, no se puede hacer pop.")
        return None