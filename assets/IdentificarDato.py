import subprocess
import struct
from fractions import Fraction

def GetEntero(numero_binario):
    return int(numero_binario) * -1

def GetFloat(binary_str):
    """Convierte un número binario de 21 bits (1 bit signo, 10 bits numerador, 10 bits denominador) en un flotante."""

    # 1️⃣ Verificar que la cadena binaria tenga exactamente 21 bits
    if len(binary_str) != 21:
        raise ValueError("El binario debe tener exactamente 21 bits (1 signo, 10 numerador, 10 denominador)")

    # 2️⃣ Extraer los bits individuales
    sign_bit = binary_str[0]  # 1 bit de signo
    numerator_bin = binary_str[1:11]  # 10 bits de numerador
    denominator_bin = binary_str[11:]  # 10 bits de denominador

    # 3️⃣ Convertir a enteros
    numerator = int(numerator_bin, 2)
    denominator = int(denominator_bin, 2)

    # 4️⃣ Si el denominador es 0, evitamos la división por 0 (lo tratamos como 1)
    if denominator == 0:
        denominator = 1

    # 5️⃣ Calcular el valor de la fracción
    fraction = Fraction(numerator, denominator)
    float_value = float(fraction)

    # 6️⃣ Aplicar el signo
    if sign_bit == '1':
        float_value *= -1

    return float_value

def GetNatural(numero_binario):
    return int(numero_binario, 2)

def GetBooleano(numero_binario):
    return True if int(numero_binario) == 1 else False

def GetCaracterUtf16(numero_binario):
    # Asegurarnos de que el número binario tenga una longitud adecuada para representar UTF-16
    # Convertir el número binario a un valor entero
    valor_entero = int(numero_binario, 2)
    
    # Verificar si el valor entero está dentro del rango de UTF-16
    if valor_entero <= 0x10FFFF:
        # Convertir el valor entero a un carácter correspondiente en UTF-16
        return chr(valor_entero)
    else:
        raise ValueError("El valor binario está fuera del rango UTF-16 válido.")

def FloatToBinary21(value):
    """Convierte un flotante a una fracción y luego lo representa en 21 bits (1 bit signo, 10 numerador, 10 denominador)."""

    # 1️⃣ Determinar el signo (1 bit)
    sign_bit = '0' if value >= 0 else '1'  # 0 para positivo, 1 para negativo
    value = abs(value)  # Trabajar con el valor absoluto

    # 2️⃣ Convertir el flotante a fracción
    frac = Fraction(value).limit_denominator(1023)  # Máximo denominador de 10 bits (1023)
    
    # 3️⃣ Obtener numerador y denominador en 10 bits
    numerator = frac.numerator & 0x3FF  # 10 bits para el numerador
    denominator = frac.denominator & 0x3FF  # 10 bits para el denominador

    # 4️⃣ Convertir a binario
    numerator_bin = format(numerator, '010b')  # 10 bits
    denominator_bin = format(denominator, '010b')  # 10 bits

    # 5️⃣ Concatenar los bits en un solo string binario
    binary_representation = sign_bit + numerator_bin + denominator_bin
    
    return binary_representation

def ConvertirDatoBinario(dato):
    # 1. Inicialización de los primeros 5 bits en 0
    binario = "00000"
    
    # 2. Determinar el tipo de dato y su código binario correspondiente
    tipo_dato_binario = ""
    if isinstance(dato, bool):
        tipo_dato_binario = "000001"  # Booleano
        binario_dato = "1" if dato else "0"  # Representación de un booleano
        binario_dato = f"{int(binario_dato):021b}"
    elif isinstance(dato, int) and dato >= 0:
        tipo_dato_binario = "000010"  # Natural
        binario_dato = f"{int(dato):021b}"
    elif isinstance(dato, int):
        tipo_dato_binario = "000011"  # Entero
        binario_dato = bin((1 << 21) + dato)[2:]  # Representación de complemento a dos para enteros negativos
        binario_dato = binario_dato.zfill(21)
    elif isinstance(dato, float):
        tipo_dato_binario = "000100"  # Carácter
        binario_dato = FloatToBinary21(dato)
    elif isinstance(dato, str) and len(dato) == 1:
        tipo_dato_binario = "000101"  # Carácter
        # Convertir el carácter a su código ASCII en binario
        binario_dato = bin(ord(dato))[2:].zfill(16)  # 16 bits para el carácter UTF-16
        binario_dato = "00000" + binario_dato
    else:
        raise ValueError("Tipo de dato no soportado o formato incorrecto.")
    
    # 3. Concatenar la cadena final
    # El binario debe ser de 5 bits (0s), seguido por los 6 bits del tipo de dato, y luego los bits del valor
    return binario + tipo_dato_binario + binario_dato

def int_to_bin16(numero):
    if numero < 0:
        numero = (1 << 16) + numero  # Convierte a complemento a dos si es negativo
    return format(numero & 0xFFFF, '016b')  # Asegura 16 bits

def float_to_bin16(value):
    """Convierte un flotante en su representación IEEE 754 de 16 bits (half precision)."""
    binary_21 = FloatToBinary21(value)
    binary_16 = binary_21[:16]

    return binary_16
