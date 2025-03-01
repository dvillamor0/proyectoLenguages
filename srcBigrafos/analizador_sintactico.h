#ifndef ANALIZADOR_SINTACTICO_H
#define ANALIZADOR_SINTACTICO_H

#include <stdio.h>
#include <stdlib.h>

typedef enum {
    NODE_PROGRAM,
    NODE_FUNCTION,
    NODE_BLOCK,
    NODE_DECLARATION,
    NODE_ASSIGNMENT,
    NODE_IF,
    NODE_WHILE,
    NODE_RETURN,
    NODE_BINARY_OP,
    NODE_FUNCTION_CALL,
    NODE_IDENTIFIER,
    NODE_NUMBER
} NodeType;

typedef struct Node {
    NodeType type;
    int symbol_index;
    struct Node *left;
    struct Node *right;
    struct Node *next;
} Node;

#define MAX_SYMBOLS 1000
#define SYMTAB_IDENTIFIER 1
#define SYMTAB_NUMBER 2

typedef struct {
    char *name;
    int type;
    union {
        double number_value;
        char *string_value;
    } value;
    int is_function;
    int data_type;
    int return_type;
    int *param_types;
    int param_count;
} SymbolEntry;

extern SymbolEntry symbol_table[MAX_SYMBOLS];
extern int symbol_count;

Node* create_node(NodeType type, Node* left, Node* right);
int install_id(char *lexeme);
int install_num(char *lexeme);

#endif