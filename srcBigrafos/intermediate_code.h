#ifndef INTERMEDIATE_CODE_H
#define INTERMEDIATE_CODE_H

#include "ast.h"

void generate_intermediate_code(Node *ast, const char *output_file);

#endif /* INTERMEDIATE_CODE_H */