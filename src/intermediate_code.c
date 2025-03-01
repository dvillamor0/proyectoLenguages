#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ast.h"
#include "analizador_sintactico.tab.h"
#define DEBUG 1  // Cambiar a 0 para desactivar la depuración

#define LOG(fmt, ...) \
    if (DEBUG) { \
        FILE *debug_file = fopen("debug_intermediate.log", "a"); \
        fprintf(debug_file, fmt, ##__VA_ARGS__); \
        fclose(debug_file); \
    }

// Declaracion externa de la tabla de simbolos
extern struct {
    char *name;
    int type;
    union {
        double number_value;
        char *string_value;
    } value;
} symbol_table[];

// Estructura para manejar los temporales y etiquetas en la generacion de codigo
typedef struct {
    int next_temp;
    char **temp_names;
    int capacity;
    int next_label;
} TempManager;

static TempManager *temp_mgr;
static char *generate_code(Node *node, FILE *output);

// Funcion: init_temp_manager
// ---------------------------
// Crea e inicializa el manejador de temporales con una capacidad inicial de 100.
static TempManager *init_temp_manager() {
    TempManager *mgr = malloc(sizeof(TempManager));
    mgr->next_temp = 1;
    mgr->next_label = 1;
    mgr->capacity = 100;
    mgr->temp_names = malloc(sizeof(char*) * mgr->capacity);
    return mgr;
}

// Funcion: new_temp
// -----------------
// Genera un nuevo nombre de temporal. Si se alcanza la capacidad, la duplica.
static char *new_temp() {
    if (temp_mgr->next_temp >= temp_mgr->capacity) {
        temp_mgr->capacity *= 2;
        temp_mgr->temp_names = realloc(temp_mgr->temp_names, sizeof(char*) * temp_mgr->capacity);
    }
    
    char *temp = malloc(20);
    sprintf(temp, "t%d", temp_mgr->next_temp++);
    return temp;
}

// Funcion: new_label
// ------------------
// Genera una nueva etiqueta.
static char *new_label() {
    char *label = malloc(20);
    sprintf(label, "L%d", temp_mgr->next_label++);
    return label;
}

// Funcion: get_symbol_name
// -------------------------
// Retorna el nombre del simbolo a partir de su indice en la tabla.
static char *get_symbol_name(int symbol_index) {
    return symbol_table[symbol_index].name;
}

// Funcion: process_binary_op
// ---------------------------
// Procesa una operacion binaria, genera el codigo intermedio y retorna el temporal
// donde se almacena el resultado.
static char *process_binary_op(Node *node, FILE *output) {
    char *left = generate_code(node->left, output);
    char *right = generate_code(node->right, output);
    char *temp = new_temp();
    
    switch (node->type) {
        case NODE_ADD:
            fprintf(output, "%s = %s + %s\n", temp, left, right);
            LOG("%s = %s + %s\n", temp, left, right);
            break;
        case NODE_SUB:
            fprintf(output, "%s = %s - %s\n", temp, left, right);
            LOG("%s = %s - %s\n", temp, left, right);
            break;
        case NODE_MUL:
            fprintf(output, "%s = %s * %s\n", temp, left, right);
            LOG("%s = %s * %s\n", temp, left, right);
            break;
        case NODE_DIV:
            fprintf(output, "%s = %s / %s\n", temp, left, right);
            LOG("%s = %s / %s\n", temp, left, right);
            break;
        case NODE_BINARY_OP:
            switch (node->symbol_index) {
                case TOKEN_RELOP_EQ:
                    fprintf(output, "%s = %s == %s\n", temp, left, right);
                    LOG("%s = %s == %s\n", temp, left, right);
                    break;
                case TOKEN_RELOP_NE:
                    fprintf(output, "%s = %s != %s\n", temp, left, right);
                    LOG("%s = %s != %s\n", temp, left, right);
                    break;
                case TOKEN_RELOP_LT:
                    fprintf(output, "%s = %s < %s\n", temp, left, right);
                    LOG("%s = %s < %s\n", temp, left, right);
                    break;
                case TOKEN_RELOP_LE:
                    fprintf(output, "%s = %s <= %s\n", temp, left, right);
                    LOG("%s = %s <= %s\n", temp, left, right);
                    break;
                case TOKEN_RELOP_GT:
                    fprintf(output, "%s = %s > %s\n", temp, left, right);
                    LOG("%s = %s > %s\n", temp, left, right);
                    break;
                case TOKEN_RELOP_GE:
                    fprintf(output, "%s = %s >= %s\n", temp, left, right);
                    LOG("%s = %s >= %s\n", temp, left, right);
                    break;
                case TOKEN_PLUS:
                    fprintf(output, "%s = %s + %s\n", temp, left, right);
                    LOG("%s = %s + %s\n", temp, left, right);
                    break;
                case TOKEN_MINUS:
                    fprintf(output, "%s = %s - %s\n", temp, left, right);
                    LOG("%s = %s - %s\n", temp, left, right);
                    break;
                case TOKEN_MULT:
                    fprintf(output, "%s = %s * %s\n", temp, left, right);
                    LOG("%s = %s * %s\n", temp, left, right);
                    break;
                case TOKEN_DIV:
                    fprintf(output, "%s = %s / %s\n", temp, left, right);
                    LOG("%s = %s / %s\n", temp, left, right);
                    break;
                default:
                    fprintf(output, "%s = %s + %s\n", temp, left, right);
                    LOG("%s = %s + %s\n", temp, left, right);
            }
            break;
        default:
            fprintf(output, "%s = %s + %s\n", temp, left, right);
            LOG("%s = %s + %s\n", temp, left, right);
    }
    
    return temp;
}

// Funcion: process_function_def
// -------------------------------
// Procesa la definicion de una funcion, genera el codigo para sus parametros
// y su cuerpo, e imprime las etiquetas de inicio y fin.
static void process_function_def(Node *node, FILE *output) {
    fprintf(output, "begin_func %s\n", get_symbol_name(node->symbol_index));
    
    if (node->left) {
        Node *param = node->left;
        while (param) {
            fprintf(output, "param %s\n", get_symbol_name(param->symbol_index));
            param = param->next;
        }
    }
    
    if (node->right) {
        generate_code(node->right, output);
    }
    
    fprintf(output, "end_func\n\n");
}

// Funcion: process_if_statement
// ------------------------------
// Procesa una sentencia if. Genera el codigo para evaluar la condicion,
// y para el bloque verdadero y falso usando etiquetas.
static void process_if_statement(Node *node, FILE *output) {
    char *condition = generate_code(node->left, output);
    char *label_else = new_label();
    char *label_end = new_label();
    
    fprintf(output, "ifz %s goto %s\n", condition, label_else);
    
    if (node->right) {
        generate_code(node->right, output);
    }
    
    fprintf(output, "goto %s\n", label_end);
    fprintf(output, "%s:\n", label_else);
    fprintf(output, "%s:\n", label_end);
}

// Funcion: process_while_statement
// -------------------------------
// Procesa una sentencia while. Genera etiquetas para el inicio y fin
// del bucle, y el codigo de la condicion y del cuerpo.
static void process_while_statement(Node *node, FILE *output) {
    char *label_start = new_label();
    char *label_end = new_label();
    
    fprintf(output, "%s:\n", label_start);
    char *condition = generate_code(node->left, output);
    fprintf(output, "ifz %s goto %s\n", condition, label_end);
    
    if (node->right) {
        generate_code(node->right, output);
    }
    
    fprintf(output, "goto %s\n", label_start);
    fprintf(output, "%s:\n", label_end);
}

// Funcion: process_function_call
// -------------------------------
// Procesa una llamada a funcion. Genera el codigo para cada argumento,
// invoca la funcion y retorna el temporal con el resultado.
static char *process_function_call(Node *node, FILE *output) {
    Node *arg = node->right;
    int arg_count = 0;
    
    while (arg) {
        char *arg_result = generate_code(arg, output);
        fprintf(output, "param %s\n", arg_result);
        arg = arg->next;
        arg_count++;
    }
    
    char *temp = new_temp();
    char *func_name = get_symbol_name(node->left->symbol_index);
    fprintf(output, "%s = call %s, %d\n", temp, func_name, arg_count);
    
    return temp;
}

// Funcion: generate_code
// -----------------------
// Genera el codigo intermedio de forma recursiva para el AST.
// Dependiendo del tipo de nodo, se invocan diferentes funciones
// para procesar la operacion correspondiente.
static char *generate_code(Node *node, FILE *output) {
    if (!node) return NULL;
    
    char *result = NULL;
    
    switch (node->type) {
        case NODE_PROGRAM:
            if (node->left) result = generate_code(node->left, output);
            break;
            
        case NODE_FUNCTION:
            process_function_def(node, output);
            break;
            
        case NODE_BLOCK:
            if (node->left) {
                result = generate_code(node->left, output);
            }
            break;
            
        case NODE_DECLARATION:
        case NODE_ASSIGNMENT: {
            char *expr_result = generate_code(node->right, output);
            char *var_name = get_symbol_name(node->left->symbol_index);
            fprintf(output, "%s = %s\n", var_name, expr_result ? expr_result : "0");
            result = var_name;
            break;
        }
            
        case NODE_RETURN: {
            char *expr_result = generate_code(node->left, output);
            fprintf(output, "return %s\n", expr_result);
            break;
        }
            
        case NODE_BINARY_OP:
        case NODE_ADD:
        case NODE_SUB:
        case NODE_MUL:
        case NODE_DIV:
            result = process_binary_op(node, output);
            break;
            
        case NODE_NUMBER:
        case NODE_IDENTIFIER:
            result = get_symbol_name(node->symbol_index);
            break;
            
        case NODE_FUNCTION_CALL:
            result = process_function_call(node, output);
            break;
            
        case NODE_IF:
            process_if_statement(node, output);
            break;
            
        case NODE_WHILE:
            process_while_statement(node, output);
            break;
    }
    
    if (node->next && node->type != NODE_BLOCK) {
        generate_code(node->next, output);
    }
    
    return result;
}

// Funcion: generate_intermediate_code
// -------------------------------------
// Genera el codigo intermedio a partir del AST y lo escribe en el archivo de salida.
// Inicializa el manejador de temporales, procesa el AST y libera los recursos.
void generate_intermediate_code(Node *ast, const char *output_file) {
    if (!ast) return;
    
    FILE *output = fopen(output_file, "w");
    if (!output) {
        fprintf(stderr, "Could not open output file %s\n", output_file);
        LOG("Could not open output file %s\n", output_file);
        return;
    }
    
    temp_mgr = init_temp_manager();
    generate_code(ast, output);
    
    fclose(output);
    
    for (int i = 0; i < temp_mgr->next_temp; i++) {
        free(temp_mgr->temp_names[i]);
    }
    free(temp_mgr->temp_names);
    free(temp_mgr);
}
