#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ast.h"
#include "analizador_sintactico.tab.h"

extern struct {
    char *name;
    int type;
    union {
        double number_value;
        char *string_value;
    } value;
} symbol_table[];

typedef struct {
    int next_temp;
    char **temp_names;
    int capacity;
    int next_label;
} TempManager;

static TempManager *temp_mgr;
static char *generate_code(Node *node, FILE *output);

static TempManager *init_temp_manager() {
    TempManager *mgr = malloc(sizeof(TempManager));
    mgr->next_temp = 1;
    mgr->next_label = 1;
    mgr->capacity = 100;
    mgr->temp_names = malloc(sizeof(char*) * mgr->capacity);
    return mgr;
}

static char *new_temp() {
    if (temp_mgr->next_temp >= temp_mgr->capacity) {
        temp_mgr->capacity *= 2;
        temp_mgr->temp_names = realloc(temp_mgr->temp_names, sizeof(char*) * temp_mgr->capacity);
    }
    
    char *temp = malloc(20);
    sprintf(temp, "t%d", temp_mgr->next_temp++);
    return temp;
}

static char *new_label() {
    char *label = malloc(20);
    sprintf(label, "L%d", temp_mgr->next_label++);
    return label;
}

static char *get_symbol_name(int symbol_index) {
    return symbol_table[symbol_index].name;
}

static char *process_binary_op(Node *node, FILE *output) {
    char *left = generate_code(node->left, output);
    char *right = generate_code(node->right, output);
    char *temp = new_temp();
    
    switch (node->type) {
        case NODE_ADD:
            fprintf(output, "%s = %s + %s\n", temp, left, right);
            break;
        case NODE_SUB:
            fprintf(output, "%s = %s - %s\n", temp, left, right);
            break;
        case NODE_MUL:
            fprintf(output, "%s = %s * %s\n", temp, left, right);
            break;
        case NODE_DIV:
            fprintf(output, "%s = %s / %s\n", temp, left, right);
            break;
        case NODE_BINARY_OP:
            switch (node->symbol_index) {
                case TOKEN_RELOP_EQ:
                    fprintf(output, "%s = %s == %s\n", temp, left, right);
                    break;
                case TOKEN_RELOP_NE:
                    fprintf(output, "%s = %s != %s\n", temp, left, right);
                    break;
                case TOKEN_RELOP_LT:
                    fprintf(output, "%s = %s < %s\n", temp, left, right);
                    break;
                case TOKEN_RELOP_LE:
                    fprintf(output, "%s = %s <= %s\n", temp, left, right);
                    break;
                case TOKEN_RELOP_GT:
                    fprintf(output, "%s = %s > %s\n", temp, left, right);
                    break;
                case TOKEN_RELOP_GE:
                    fprintf(output, "%s = %s >= %s\n", temp, left, right);
                    break;
                case TOKEN_PLUS:
                    fprintf(output, "%s = %s + %s\n", temp, left, right);
                    break;
                case TOKEN_MINUS:
                    fprintf(output, "%s = %s - %s\n", temp, left, right);
                    break;
                case TOKEN_MULT:
                    fprintf(output, "%s = %s * %s\n", temp, left, right);
                    break;
                case TOKEN_DIV:
                    fprintf(output, "%s = %s / %s\n", temp, left, right);
                    break;
                default:
                    fprintf(output, "%s = %s + %s\n", temp, left, right);
            }
            break;
        default:
            fprintf(output, "%s = %s + %s\n", temp, left, right);
    }
    
    return temp;
}

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

void generate_intermediate_code(Node *ast, const char *output_file) {
    if (!ast) return;
    
    FILE *output = fopen(output_file, "w");
    if (!output) {
        fprintf(stderr, "Could not open output file %s\n", output_file);
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