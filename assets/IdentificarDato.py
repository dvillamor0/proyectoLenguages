import subprocess
import struct

def GetEntero(numero_binario):
    return int(numero_binario) * -1

def GetFloat(binary_str):
    if len(binary_str) != 21:
        raise ValueError("El binario debe tener exactamente 22 bits (1 signo, 8 exponente, 12 mantisa)")

    # Extraer partes
    sign = int(binary_str[0], 2)
    exponent = int(binary_str[1:9], 2)  # 8 bits de exponente
    mantissa_bits = binary_str[9:]  # 12 bits de mantisa

    # Ajustar el sesgo del exponente (bias = 127 para 8 bits)
    bias = 127
    exponent_unbiased = exponent - bias

    # Reconstruir la mantisa con bit implícito (1.xxxxx)
    mantissa = 1.0  # Bit implícito
    for i, bit in enumerate(mantissa_bits):
        mantissa += int(bit) * (2 ** -(i + 1))

    # Calcular el valor final
    float_value = ((-1) ** sign) * mantissa * (2 ** exponent_unbiased)

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

def FloatToBinary21(num):
    # Convertir a IEEE 754 estándar de 32 bits
    ieee_754_bin = struct.unpack('!I', struct.pack('!f', num))[0]

    # Extraer partes
    sign = (ieee_754_bin >> 31) & 0x1
    exponent_full = (ieee_754_bin >> 23) & 0xFF  # 8 bits de exponente IEEE 754

    # Ajustar el sesgo del exponente (bias = 127 en IEEE 754, nuevo bias = 127)
    exponent_adjusted = exponent_full  # Mantiene el bias de 127

    # Extraer la mantisa de 23 bits y reducirla a 12 bits
    mantissa_full = ieee_754_bin & 0x7FFFFF  # 23 bits de mantisa
    mantissa_reduced = mantissa_full >> 11  # Solo los 12 bits más significativos

    # Convertir a binario
    sign_bin = f"{sign:1b}"
    exponent_bin = f"{exponent_adjusted:08b}"  # 8 bits
    mantissa_bin = f"{mantissa_reduced:012b}"  # 12 bits

    return f"{sign_bin}{exponent_bin}{mantissa_bin}"

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
    