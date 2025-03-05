Fun main() {
    Big bg1;
    
    // Add nodes
    bg1:nod("A");
    bg1:nod("B");
    bg1:nod("C");
    
    // Add edges between nodes
    bg1:enl(0, 1); // Edge from node 0 to node 1
    
    // Replace node
    bg1:nod("A", "D");
    
    // Remove node
    bg1:rnod("B");
    
    // Remove edge
    bg1:renl(0, 2);
    
    // Add type relation
    bg1:tip("person", 0);
    
    // Remove type relation
    bg1:rtip("person", 0);
    
    // Add parent-child relation
    bg1:hij(2, 0);
    
    // Set link count
    bg1:lnk(0, 2);
    
    // Remove link count
    bg1:rlnk(0);
    
    // Compose bigraphs
    Big bg2;
    bg1:enl(bg1, bg2);
    
    Ret 0;
} 