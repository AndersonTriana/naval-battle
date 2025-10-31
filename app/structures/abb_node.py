"""
Node class for Binary Search Tree.
Copiado y adaptado de api_abb para integración en el proyecto.
"""
from typing import Any, Optional


class Node:
    """
    Represents a node in a Binary Search Tree.
    
    Attributes:
        id: Unique identifier for the node (used as the key for BST operations)
        data: Additional data stored in the node
        left: Reference to the left child node
        right: Reference to the right child node
    """
    
    def __init__(self, id: int, data: Any = None):
        """
        Initialize a new node.
        
        Args:
            id: Unique identifier for the node
            data: Optional data to store in the node
        """
        self.id = id
        self.data = data
        self.left: Optional['Node'] = None
        self.right: Optional['Node'] = None
    
    def __repr__(self) -> str:
        """String representation of the node."""
        return f"Node(id={self.id}, data={self.data})"
    
    def to_dict(self) -> dict:
        """
        Convert node to dictionary representation.
        
        Returns:
            Dictionary with node's id and data
        """
        return {
            "id": self.id,
            "data": self.data
        }
