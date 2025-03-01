
%%
/* bg_2_node: Representa una estructura con 2 operandos (elementoArreglo, elementoArreglo) */
bg_2_node:
       TOKEN_LPAREN elementoArreglo TOKEN_COMMA elementoArreglo TOKEN_RPAREN
       { $$ = create_node(NODE_BG_2_NODE, $2, $4); }
       ;

/* bg_vertice: Definiciones para añadir, intercambiar o borrar un nodo */
bg_vertice:
       TOKEN_ID TOKEN_BG_NOD_OPEN elementoArreglo TOKEN_RPAREN
       { $$ = create_node(NODE_BG_VERTICE_ADD, create_identifier_node($1), $3); }
     | TOKEN_ID TOKEN_BG_NOD bg_2_node
       { $$ = create_node(NODE_BG_VERTICE_SWAP, create_identifier_node($1), $3); }
     | TOKEN_ID TOKEN_BG_RNOD_OPEN elementoArreglo TOKEN_RPAREN
       { $$ = create_node(NODE_BG_VERTICE_DEL, create_identifier_node($1), $3); }
       ;

/* bg_enlace: Para la manipulación de aristas */
bg_enlace:
       TOKEN_ID TOKEN_BG_ENL bg_2_node
       { $$ = create_node(NODE_BG_ENLACE_ADD, create_identifier_node($1), $3); }
     | TOKEN_ID TOKEN_BG_ENL_OPEN TOKEN_ID TOKEN_COMMA TOKEN_ID TOKEN_RPAREN
       { 
         Node *id = create_identifier_node($1);
         $$ = create_node(NODE_BG_ENLACE_COMPOSE, id, 
                          create_node_list(create_identifier_node($3), create_identifier_node($5)));
       }
     | TOKEN_ID TOKEN_BG_RENL bg_2_node
       { $$ = create_node(NODE_BG_ENLACE_DEL, create_identifier_node($1), $3); }
       ;

/* bg_ctl: Para especificar control */
bg_ctl:
       TOKEN_ID TOKEN_BG_TIP_OPEN string TOKEN_COMMA elementoArreglo TOKEN_RPAREN
       { $$ = create_node(NODE_BG_CTL, create_identifier_node($1), create_string_node($3, $5)); }
       ;

/* bg_parent: Para añadir aristas de parentesco */
bg_parent:
       TOKEN_ID TOKEN_BG_HIJ bg_2_node
       { $$ = create_node(NODE_BG_PARENT, create_identifier_node($1), $2); }
       ;

/* bg_exit: Para las conexiones de salida */
bg_exit:
       TOKEN_ID TOKEN_BG_LNK_OPEN elementoArreglo TOKEN_COMMA nat TOKEN_RPAREN
       { $$ = create_node(NODE_BG_EXIT, create_identifier_node($1), create_node($3, create_nat_node($5), NULL)); }
       ;
%%