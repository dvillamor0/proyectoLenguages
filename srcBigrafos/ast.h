#ifndef AST_H
#define AST_H

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
    NODE_NUMBER,
    NODE_ADD,
    NODE_SUB,
    NODE_MUL,
    NODE_DIV,
} NodeType;


typedef struct Node {
    NodeType type;
    int symbol_index;  
    struct Node *left;
    struct Node *right;
    struct Node *next;  
} Node;

Node* create_node(NodeType type, Node* left, Node* right);

#endif /* AST_H */