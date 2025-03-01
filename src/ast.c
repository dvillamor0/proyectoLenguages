#include <stdio.h>
#include <stdlib.h>
#include "ast.h"

Node* create_node(NodeType type, Node* left, Node* right) {
    Node* node = (Node*)malloc(sizeof(Node));
    node->type = type;
    node->left = left;
    node->right = right;
    node->next = NULL;
    node->symbol_index = -1;
    return node;
}