// Test file for BigGraph operations
fun main() {
    // Declare a new BigGraph
    BigGraph bg1;
    
    // Add nodes
    bg1.addNode("A");
    bg1.addNode("B");
    bg1.addNode("C");
    
    // Add edges
    bg1.addEdge("A", "B");
    bg1.addEdge("B", "C");
    
    // Replace a node
    bg1.replaceNode("A", "D");
    
    // Remove an edge
    bg1.removeEdge("B", "C");
    
    // Add a type
    bg1.addType("person");
    
    // Remove a type
    bg1.removeType("person");
    
    // Add a parent
    bg1.addParent("child", "parent");
    
    // Set link
    bg1.setLink("node1", "node2", "relationshipType");
    
    // Remove link
    bg1.removeLink("node1", "node2");
    
    // Compose graphs
    BigGraph bg2;
    BigGraph bg3 = bg1.compose(bg2);
    
    return 0;
} 