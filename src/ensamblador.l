%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h> 

#define TRUE 1
#define FALSE 0

void print_binary(int num) {
    unsigned int mask = 1 << 20; // Máscara para el bit más significativo (bit 20, el bit más a la izquierda en 21 bits)
    
    // Imprimir los 21 bits
    for (int i = 0; i < 21; i++) {
        if (num & mask) {
            printf("1");
        } else {
            printf("0");
        }
        mask >>= 1;  // Desplazamos la máscara para el siguiente bit
    }
}

float binary_to_float_21_bits(const char *binary_str) {
    if (strlen(binary_str) != 21) {
        fprintf(stderr, "El binario debe tener 21 bits.\n");
        return 0;
    }
    
    // Desglosamos los 21 bits en signo, exponente y mantisa
    int sign_bit = binary_str[0] - '0';  // Bit de signo
    char exponent_bits[9];  // 8 bits para el exponente
    char mantissa_bits[13]; // 12 bits para la mantisa
    
    strncpy(exponent_bits, binary_str + 1, 8);
    strncpy(mantissa_bits, binary_str + 9, 12);
    exponent_bits[8] = '\0';
    mantissa_bits[12] = '\0';

    // Convertimos el exponente de binario a entero
    int exponent = strtol(exponent_bits, NULL, 2) - 127;  // Restamos el sesgo de 127

    // Convertimos la mantisa de binario a número flotante
    float mantissa = 1.0;  // El valor base de la mantisa es 1 (como en IEEE 754)
    for (int i = 0; i < 12; ++i) {
        if (mantissa_bits[i] == '1') {
            mantissa += 1.0 / (1 << (i + 1));  // Sumamos la fracción correspondiente
        }
    }

    // Calculamos el valor final
    float value = mantissa * (1 << exponent);
    
    // Aplicamos el signo
    if (sign_bit == 1) {
        value = -value;
    }

    return value;
}

char* GetBinarioCommand(const char *command, int esRegistro) {
    static char binary[6];
    const char *commands[] = {
        "NOP", "LOAD", "STORE", "MOVE", "ADD", "SUB", "MUL", "DIV", "AND", "OR", "NOR",
        "NOT", "SHL", "SHR", "ROL", "ROR", "JUMP", "BEQ", "BNE", "BLT", "JLE", "PUSH", 
        "POP", "CALL", "RET", "IN", "OUT", "CMP", "CLR", "ERROR", "ERROR", "HALT"
    };
    const int num_commands = sizeof(commands) / sizeof(commands[0]);

    if (esRegistro && (strcmp(command, "LOAD") == 0 || strcmp(command, "STORE") == 0)) {
        if (strcmp(command, "LOAD") == 0) {
            strcpy(binary, "11101");
        } else {
            strcpy(binary, "11110");
        }
        return binary;
    }

    for (int i = 0; i < num_commands; i++) {
        if (strcmp(command, commands[i]) == 0) {
            for (int j = 0; j < 5; j++) {
                binary[4 - j] = (i & (1 << j)) ? '1' : '0';
            }
            binary[5] = '\0';  // Agregar el terminador nulo

            return binary;
        }
    }
    strcpy(binary, "00000");
    return binary;
}

char* GetBinarioRegistro(const char *reg){
    static char binary[3];

    if (reg[0] == 'R' && reg[1] >= '0' && reg[1] <= '3' && reg[2] == '\0') {
        int regNumber = reg[1] - '0'; // Convertir el caracter del número a un valor entero

        // Convertir el número del registro a binario
        switch (regNumber) {
            case 0:
                strcpy(binary, "00");
                break;
            case 1:
                strcpy(binary, "01");
                break;
            case 2:
                strcpy(binary, "10");
                break;
            case 3:
                strcpy(binary, "11");
                break;
            default:
                strcpy(binary, "00"); 
                break;
        }
    }
    return binary;
}

char* GetRelativeDirection(const char *reg){
    static char result[20];

    if (reg == NULL || strlen(reg) < 5) {
        return "Formato Incorrecto Relative";
    }

    size_t len = strlen(reg);

    if (reg[0] == '[' && reg[len - 1] == ']' && strncmp(reg + 1, "0x", 2) == 0) {
        char hexValue[10]; // Para almacenar el número hexadecimal
        strncpy(hexValue, reg + 3, len - 4); // Extraer solo los dígitos hexadecimales
        hexValue[len - 4] = '\0'; // Terminar la cadena

        long decimalValue = strtol(hexValue, NULL, 16); // Convertir a decimal

        snprintf(result, sizeof(result), "(%ld)", decimalValue);
        return result;
    } else {
        return "Formato Incorrecto Relative";
    }
}

char* ConcatenarDireccion(const char *numero, const char *direccion) {
    static char resultado[32];
    int numero_len = strlen(numero);
    int size_to_fill = 32 - numero_len - 8;  // 32 menos el largo de numero y los 8 bits para la dirección
    resultado[0] = '\0';
    /*
    for (int i = 0; i < size_to_fill; i++) {
        strcat(resultado, "0");
    }
    */
    strcat(resultado, direccion);
    return resultado;
}

char* GetBinarioSecondRegistro(const char *reg, const char *numero) {
    static char result[32];
    char limpio[32];

    sscanf(reg, "%s", limpio);  // O usa otra opción de limpieza

    int esRegistro = (limpio[0] == 'R') ? TRUE : FALSE;
    if (esRegistro) {
        strcpy(result, GetBinarioRegistro(limpio));
    } else {
        strcpy(result, ConcatenarDireccion(numero, GetRelativeDirection(limpio)));
    }
    return result;
}

int contieneParentesis(const char *str) {
    while (*str != '\0') {  // Mientras no lleguemos al final de la cadena
        if (*str == '(') {   // Si encontramos '('
            return 1;         // Retornamos 1
        }
        str++;  // Avanzamos al siguiente carácter
    }
    return 0;  // Si no se encontró '('
}

char* CompletarCeros(const char *numero){
    static char resultado[32];
    int numero_len = strlen(numero);
    int size_to_fill = 32 - numero_len;
    resultado[0] = '\0';

    for (int i = 0; i < size_to_fill; i++) {
        strcat(resultado, "0");
    }
    return resultado;
}

void GenerarBinarioParams(const char *command, const char *reg1, const char *reg2, const char *reg3) {
    //printf("Comando: %s\n", command);
    int esRegistro2 = (reg2[0] == 'R') ? TRUE : FALSE;
    char numero[32] = "";
    strcat(numero,GetBinarioCommand(command, esRegistro2));
    int esRegistro1 = (reg1[0] == 'R') ? TRUE : FALSE;
    if(!esRegistro1){
        strcat(numero,"000000");
    }
    if (strcmp(reg1, "") != 0){
        strcat(numero, GetBinarioSecondRegistro(reg1,numero));
    }
    if(!esRegistro2 && esRegistro1){
        strcat(numero,"0000");
    }
    if (strcmp(reg2, "") != 0){
        strcat(numero, GetBinarioSecondRegistro(reg2,numero));
    }
    int esRegistro3 = (reg3[0] == 'R') ? TRUE : FALSE;
    if(!esRegistro3 && esRegistro1 && esRegistro2){
        strcat(numero,"00");
    }
    if (strcmp(reg3, "") != 0){
        strcat(numero, GetBinarioSecondRegistro(reg3,numero));
    }
    if(strlen(numero) < 32 && !contieneParentesis(numero)){
        strcat(numero,CompletarCeros(numero));
    }
    printf("%s", numero);
    printf("\n"); 
}

void printAscii(const char *str) {
    printf("ASCII: ");
    for (int i = 0; str[i] != '\0'; i++) {
        printf("[%d]", str[i]);
    }
    printf("\n");
}

%}

%option noyywrap

delim       [ \t\n]+
spaces      [" "]
R_REGISTER  "R"[0-3]
HEX_ADDRESS \[0x[0-9A-F]+\]
digits       [0-9]+
boolean     ((F|f)(A|a)(L|l)(S|s)(E|e)|(T|t)(R|r)(U|u)(E|e))

%%

(ADD|SUB|MUL|DIV|AND|OR|NOR){spaces}+{R_REGISTER},{spaces}*{R_REGISTER},{spaces}*{R_REGISTER}{spaces}* {
    //printf("Reconocido 3 R : %s\n", yytext);

    char command[10];  // Para guardar el comando (ADD, SUB, etc.)
    char reg1[10], reg2[10], reg3[10];  // Para guardar los registros
    
    if (sscanf(yytext, "%9s %[^,], %[^,], %9s", command, reg1, reg2, reg3) == 4) {
        GenerarBinarioParams(command, reg1, reg2, reg3);
    } else {
        //printf("Error al analizar la instrucción: %s\n", yytext);
    }
}
(BEQ|BNE|BLT|JLE){spaces}+{R_REGISTER},{spaces}*{R_REGISTER},{spaces}*{HEX_ADDRESS}{spaces}* {
    //printf("Reconocido 3 R : %s\n", yytext);

    char command[10];  // Para guardar el comando (ADD, SUB, etc.)
    char reg1[10], reg2[10], reg3[10];  // Para guardar los registros

    if (sscanf(yytext, "%9s %[^,], %[^,], %9s", command, reg1, reg2, reg3) == 4) {
        GenerarBinarioParams(command, reg1, reg2, reg3);
    } else {
        //printf("Error al analizar la instrucción: %s\n", yytext);
    }
}
(LOAD|STORE){spaces}+({R_REGISTER}|{HEX_ADDRESS}),{spaces}*({R_REGISTER}|{HEX_ADDRESS}){spaces}* {
    //printf("Reconocido 1 R 1 H: %s\n", yytext);

    char command[10];  // Para guardar el comando (LOAD, STORE, etc.)
    char reg1[10], reg2[15];  // Para guardar los registros
    if (sscanf(yytext, "%9s %[^,], %[^,]", command, reg1, reg2) == 3) {
        GenerarBinarioParams(command, reg1, reg2, "");
    } else {
        printf("Error al analizar la instrucción: %s\n", yytext);
    }
}
(JUMP|CALL){spaces}{HEX_ADDRESS}{spaces}* {
    //printf("Reconocido 1 R 1 H: %s\n", yytext);

    char command[10];  // Para guardar el comando (LOAD, STORE, etc.)
    char reg1[10];  // Para guardar los registros

    if (sscanf(yytext, "%9s %[^,], %[^,]", command, reg1) == 2) {
        GenerarBinarioParams(command, reg1, "", "");
    } else {
        //printf("Error al analizar la instrucción: %s\n", yytext);
    }
}
(IN){spaces}+{HEX_ADDRESS}{spaces}* {
    //printf("Reconocido 1 R 1 H: %s\n", yytext);

    char command[10];  // Para guardar el comando (LOAD, STORE, etc.)
    char reg1[10];  // Para guardar los registros

    if (sscanf(yytext, "%9s %[^,], %[^,]", command, reg1) == 2) {
        GenerarBinarioParams(command, reg1, "", "");
    } else {
        //printf("Error al analizar la instrucción: %s\n", yytext);
    }
}
(NOT|CLR|PUSH|POP|IN|OUT){spaces}+{R_REGISTER}{spaces}* {
    //printf("Reconocido 1 R 1 H: %s\n", yytext);

    char command[10];  // Para guardar el comando (LOAD, STORE, etc.)
    char reg1[10];  // Para guardar los registros

    if (sscanf(yytext, "%9s %[^,], %[^,]", command, reg1) == 2) {
        GenerarBinarioParams(command, reg1, "", "");
    } else {
        //printf("Error al analizar la instrucción: %s\n", yytext);
    }
}
(RET|NOP|HALT){spaces}* {
    //printf("Reconocido 1 R 1 H: %s\n", yytext);

    char command[10];  // Para guardar el comando (LOAD, STORE, etc.)

    if (sscanf(yytext, "%9s %[^,], %[^,]", command) == 1) {
        GenerarBinarioParams(command, "", "", "");
    } else {
        //printf("Error al analizar la instrucción: %s\n", yytext);
    }
}

{delim} { /* No action */ }
'-'{digits} {
    int value = atoi(yytext);
    printf("00000000011");
    print_binary(value);
    printf("\n");
}
.{digits} {
    printf("00000000100");
    binary_to_float_21_bits(yytext);
    printf("\n");
}
('+')*{digits} {
    int value = atoi(yytext);
    printf("00000000010");
    print_binary(value);
    printf("\n");
}
{boolean} {
    if (strcmp(yytext, "TRUE") == 0) {
        printf("00000000001000000000000000000001");  // 20 ceros antes del 1
        printf("\n");
    }
    // Si es FALSE, imprimir 20 ceros seguidos de 0
    else if (strcmp(yytext, "FALSE") == 0) {
        printf("00000000001000000000000000000000");  // 20 ceros antes del 0
        printf("\n");
    }
}
[A-Za-z] {
    int value = atoi(yytext);
    printf("00000000101");
    print_binary(value);
    printf("\n");
}
.+ {
    printf("%s\n", yytext);
}
%%

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "Uso: %s <archivo_python>\n", argv[0]);
        return 1;
    }

    FILE *file = fopen(argv[1], "r");
    if (!file) {
        perror("Error al abrir el archivo");
        return 1;
    }

    yyin = file;
    yylex();
    fclose(file);
    return 0;
}