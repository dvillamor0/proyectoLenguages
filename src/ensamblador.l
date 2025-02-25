%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h> 
#include <stdint.h>
#include <stdarg.h>

#define TRUE 1
#define FALSE 0

FILE *debug_file = NULL;

void debug_print(const char *format, ...) {
    if (debug_file == NULL) {
        debug_file = fopen("assembler_debug.log", "w");
    }
    
    if (debug_file != NULL) {
        va_list args;
        va_start(args, format);
        vfprintf(debug_file, format, args);
        va_end(args);
        fprintf(debug_file, "\n");
        fflush(debug_file);
    }
}

void print_binary(int num) {
    unsigned int mask = 1 << 20; // Máscara para el bit más significativo (bit 20)
    
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

void binary_to_float_21_bits(const char *str) {
    float num = strtof(str, NULL);
    uint32_t ieee_754_bin = *(uint32_t*)&num;
    uint8_t sign = (ieee_754_bin >> 31) & 0x1;
    int exponent_full = (ieee_754_bin >> 23) & 0xFF;  // Exponente de 8 bits
    int exponent_adjusted = exponent_full - 127 + 63; // Nuevo sesgo de 7 bits

    if (exponent_adjusted < 0) exponent_adjusted = 0;
    if (exponent_adjusted > 127) exponent_adjusted = 127;
    uint16_t mantissa_reduced = (ieee_754_bin & 0x7FFFFF) >> 10;  // 13 bits más significativos
    printf("%d", sign);
    for (int i = 6; i >= 0; i--) 
        printf("%d", (exponent_adjusted >> i) & 1);
    for (int i = 12; i >= 0; i--) 
        printf("%d", (mantissa_reduced >> i) & 1);
}

void print_binary_from_entero(int num) {
    // Asegurar que el número cabe en 21 bits con signo (-1048576 a 1048575)
    if (num < -1048576 || num > 1048575) {
        printf("Error: Número fuera del rango de 21 bits (-1048576 a 1048575)\n");
    }

    // Convertir a un entero sin signo de 21 bits (manejo del complemento a 2)
    uint32_t binary_rep = (num < 0) ? (num & 0x1FFFFF) : num;

    // Imprimir la representación binaria de 21 bits
    for (int i = 20; i >= 0; i--) {
        printf("%d", (binary_rep >> i) & 1);
    }
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

char* GetBinarioRegistro(const char *reg) {
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

// Extract hex value from [0xNNN] or [NNN] format and return in (N) format
char* ExtractHexAddress(const char *addr) {
    static char result[20];
    memset(result, 0, sizeof(result));

    // Remove whitespace
    char clean_addr[50] = {0};
    int j = 0;
    for (int i = 0; addr[i]; i++) {
        if (!isspace(addr[i])) {
            clean_addr[j++] = addr[i];
        }
    }
    clean_addr[j] = '\0';
    
    // Extract the number between brackets
    char *start = strchr(clean_addr, '[');
    char *end = strchr(clean_addr, ']');
    
    if (start && end && start < end) {
        char hex_part[20] = {0};
        int len = end - start - 1;
        strncpy(hex_part, start + 1, len);
        hex_part[len] = '\0';
        
        // Convert to decimal value
        int value;
        if (strncmp(hex_part, "0x", 2) == 0) {
            // Handle 0x prefix
            sscanf(hex_part + 2, "%x", &value);
        } else {
            // No prefix, assume hex
            sscanf(hex_part, "%x", &value);
        }
        
        sprintf(result, "(%d)", value);
        return result;
    }
    
    // Default if parsing fails
    strcpy(result, "(0)");
    return result;
}

char* CompletarCeros(const char *numero) {
    static char resultado[33];
    memset(resultado, 0, sizeof(resultado));
    int numero_len = strlen(numero);
    int size_to_fill = 32 - numero_len;
    
    for (int i = 0; i < size_to_fill; i++) {
        strcat(resultado, "0");
    }
    
    return resultado;
}

// Process floating point numbers
void process_float(const char *str) {
    printf("00000000100");
    binary_to_float_21_bits(str);
    printf("\n");
}

// Process a full assembly instruction
void process_instruction(const char *line) {
    debug_print("Processing: %s", line);
    
    // Extract the command
    char command[10] = {0};
    char operands[100] = {0};
    
    sscanf(line, "%9s %99[^\n]", command, operands);
    debug_print("Command: %s, Operands: %s", command, operands);
    
    // Arithmetic operations with 3 registers
    if (strcmp(command, "ADD") == 0 || strcmp(command, "SUB") == 0 || 
        strcmp(command, "MUL") == 0 || strcmp(command, "DIV") == 0 || 
        strcmp(command, "AND") == 0 || strcmp(command, "OR") == 0 || 
        strcmp(command, "NOR") == 0) {
        
        // Check if this is a 3-register operation
        char reg1[5] = {0}, reg2[5] = {0}, reg3[5] = {0};
        int count = sscanf(operands, "%4[^,], %4[^,], %4s", reg1, reg2, reg3);
        
        if (count == 3 && reg1[0] == 'R' && reg2[0] == 'R' && reg3[0] == 'R') {
            // This is a 3-register arithmetic operation
            debug_print("3-reg op: %s %s, %s, %s", command, reg1, reg2, reg3);
            
            // Generate 5-bit opcode
            char *opcode = GetBinarioCommand(command, 0);
            
            // Generate register encodings
            char *r1_code = GetBinarioRegistro(reg1);
            char *r2_code = GetBinarioRegistro(reg2);
            char *r3_code = GetBinarioRegistro(reg3);
            
            // Combine and pad
            char binary[33] = {0};
            sprintf(binary, "%s%s%s%s", opcode, r1_code, r2_code, r3_code);
            strcat(binary, CompletarCeros(binary));
            
            printf("%s\n", binary);
            return;
        }
    }
    
    // Branch operations
    if (strcmp(command, "BEQ") == 0 || strcmp(command, "BNE") == 0 || 
        strcmp(command, "BLT") == 0 || strcmp(command, "JLE") == 0) {
        
        char reg1[5] = {0}, reg2[5] = {0}, addr[20] = {0};
        int count = sscanf(operands, "%4[^,], %4[^,], %19s", reg1, reg2, addr);
        
        if (count == 3 && reg1[0] == 'R' && reg2[0] == 'R' && addr[0] == '[') {
            debug_print("Branch: %s %s, %s, %s", command, reg1, reg2, addr);
            
            char *opcode = GetBinarioCommand(command, 0);
            char *r1_code = GetBinarioRegistro(reg1);
            char *r2_code = GetBinarioRegistro(reg2);
            char *addr_str = ExtractHexAddress(addr);
            
            char binary[33] = {0};
            sprintf(binary, "%s%s%s%s", opcode, r1_code, r2_code, addr_str);
            
            printf("%s\n", binary);
            return;
        }
    }
    
    // LOAD/STORE with register and memory
    if (strcmp(command, "LOAD") == 0 || strcmp(command, "STORE") == 0) {
        char op1[20] = {0}, op2[20] = {0};
        int count = sscanf(operands, "%19[^,], %19s", op1, op2);
        
        if (count == 2) {
            if (op1[0] == 'R' && op2[0] == '[') {
                // Register to memory: LOAD/STORE Rx, [addr]
                debug_print("%s reg,mem: %s, %s", command, op1, op2);
                
                char *opcode = GetBinarioCommand(command, 1); // Use special opcode for reg->mem
                char *reg_code = GetBinarioRegistro(op1);
                char *addr_str = ExtractHexAddress(op2);
                
                char binary[33] = {0};
                sprintf(binary, "%s%s%s", opcode, reg_code, addr_str);
                
                printf("%s\n", binary);
                return;
            } else if (op1[0] == '[' && op2[0] == 'R') {
                // Memory to register: LOAD/STORE [addr], Rx
                debug_print("%s mem,reg: %s, %s", command, op1, op2);
                
                char *opcode = GetBinarioCommand(command, 0);
                char *addr_str = ExtractHexAddress(op1);
                char *reg_code = GetBinarioRegistro(op2);
                
                char binary[33] = {0};
                sprintf(binary, "%s00%s%s", opcode, addr_str, reg_code);
                
                printf("%s\n", binary);
                return;
            }
        }
    }
    
    // JUMP and CALL
    if (strcmp(command, "JUMP") == 0 || strcmp(command, "CALL") == 0) {
        if (operands[0] == '[') {
            debug_print("%s to address: %s", command, operands);
            
            char *opcode = GetBinarioCommand(command, 0);
            char *addr_str = ExtractHexAddress(operands);
            
            char binary[33] = {0};
            sprintf(binary, "%s00%s", opcode, addr_str);
            
            printf("%s\n", binary);
            return;
        }
    }
    
    // Single register instructions
    if (strcmp(command, "NOT") == 0 || strcmp(command, "CLR") == 0 || 
        strcmp(command, "PUSH") == 0 || strcmp(command, "POP") == 0 || 
        strcmp(command, "IN") == 0 || strcmp(command, "OUT") == 0) {
        
        if (operands[0] == 'R') {
            debug_print("Single reg op: %s %s", command, operands);
            
            char *opcode = GetBinarioCommand(command, 0);
            char *reg_code = GetBinarioRegistro(operands);
            
            char binary[33] = {0};
            sprintf(binary, "%s%s", opcode, reg_code);
            strcat(binary, CompletarCeros(binary));
            
            printf("%s\n", binary);
            return;
        }
    }
    
    // CMP instruction
    if (strcmp(command, "CMP") == 0) {
        char reg1[5] = {0}, reg2[5] = {0};
        int count = sscanf(operands, "%4[^,], %4s", reg1, reg2);
        
        if (count == 2 && reg1[0] == 'R' && reg2[0] == 'R') {
            debug_print("CMP: %s, %s", reg1, reg2);
            
            char *opcode = GetBinarioCommand(command, 0);
            char *r1_code = GetBinarioRegistro(reg1);
            char *r2_code = GetBinarioRegistro(reg2);
            
            char binary[33] = {0};
            sprintf(binary, "%s%s%s", opcode, r1_code, r2_code);
            strcat(binary, CompletarCeros(binary));
            
            printf("%s\n", binary);
            return;
        }
    }
    
    // No-operand instructions
    if (strcmp(command, "RET") == 0 || strcmp(command, "NOP") == 0 || 
        strcmp(command, "HALT") == 0) {
        
        debug_print("No-op instruction: %s", command);
        
        char *opcode = GetBinarioCommand(command, 0);
        
        char binary[33] = {0};
        strcpy(binary, opcode);
        strcat(binary, CompletarCeros(binary));
        
        printf("%s\n", binary);
        return;
    }
    
    // If we couldn't parse it, just print the original line
    printf("%s\n", line);
}

%}

%option noyywrap

WHITESPACE  [ \t\n\r]+
FLOAT       [+-]?[0-9]+\.[0-9]+
SINT        [+-][0-9]+
UINT        [0-9]+
BOOLEAN     TRUE|FALSE|true|false
CHAR        [A-Za-z]
INSTR       [A-Z][A-Z][A-Z][A-Z]?.*

%%

{FLOAT}     {
    debug_print("Float: %s", yytext);
    printf("00000000100");
    binary_to_float_21_bits(yytext);
    printf("\n");
}

{SINT}      {
    debug_print("Signed int: %s", yytext);
    int value = atoi(yytext);
    printf("00000000011");
    print_binary_from_entero(value);
    printf("\n");
}

{UINT}      {
    debug_print("Unsigned int: %s", yytext);
    int value = atoi(yytext);
    printf("00000000010");
    print_binary(value);
    printf("\n");
}

{BOOLEAN}   {
    debug_print("Boolean: %s", yytext);
    if (strcasecmp(yytext, "TRUE") == 0) {
        printf("00000000001000000000000000000001\n");
    } else {
        printf("00000000001000000000000000000000\n");
    }
}

{CHAR}      {
    debug_print("Char: %s", yytext);
    int value = (int)yytext[0];
    printf("00000000101");
    print_binary(value);
    printf("\n");
}

^LOAD.*     |
^STORE.*    |
^ADD.*      |
^SUB.*      |
^MUL.*      |
^DIV.*      |
^AND.*      |
^OR.*       |
^NOR.*      |
^NOT.*      |
^BEQ.*      |
^BNE.*      |
^BLT.*      |
^JLE.*      |
^JUMP.*     |
^CALL.*     |
^RET.*      |
^PUSH.*     |
^POP.*      |
^IN.*       |
^OUT.*      |
^CMP.*      |
^CLR.*      |
^NOP.*      |
^HALT.*     {
    process_instruction(yytext);
}

{WHITESPACE}    { /* ignore */ }

.+      {
    debug_print("Unknown: %s", yytext);
    printf("%s\n", yytext);
}

%%

int main() {
    FILE *infile = fopen("output.asm", "r");
    if (!infile) {
        perror("Error al abrir output.asm");
        return 1;
    }

    // Create debug file
    debug_file = fopen("assembler_debug.log", "w");
    if (!debug_file) {
        perror("Error al crear archivo de depuración");
    }

    // Redirect stdout to output.bin
    if (freopen("output.bin", "w", stdout) == NULL) {
        perror("Error al crear output.bin");
        fclose(infile);
        return 1;
    }

    yyin = infile;
    yylex();
    
    fclose(infile);
    fclose(stdout);
    if (debug_file) fclose(debug_file);
    return 0;
}