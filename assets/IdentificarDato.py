import subprocess
import struct

def GetEntero(numero_binario):
    return int(numero_binario) * -1

def GetFloat(binary_str):
    
    # Desglosamos los 21 bits en signo, exponente y mantisa
    sign_bit = int(binary_str[0], 2)  # Bit de signo
    exponent_bits = binary_str[1:9]  # Bits del exponente (8 bits)
    mantissa_bits = binary_str[9:]   # Bits de la mantisa (12 bits)

    # Convertimos el exponente de binario a entero
    exponent = int(exponent_bits, 2) - 127  # Restamos el sesgo de 127

    # Convertimos la mantisa de binario a número flotante
    mantissa = 1  # El valor base de la mantisa es 1 (como en IEEE 754)
    for i in range(len(mantissa_bits)):
        if mantissa_bits[i] == '1':
            mantissa += 1 / (2 ** (i + 1))  # Sumamos la fracción correspondiente
    
    # Calculamos el valor final
    value = mantissa * (2 ** exponent)
    
    # Aplicamos el signo
    if sign_bit == 1:
        value = -value

    return value

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

# def ConvertirDatoBinario(dato):
    