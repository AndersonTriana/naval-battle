"""
Binary Search Tree implementation.
Copiado y adaptado de api_abb para integración en el proyecto.
"""
from typing import List, Optional, Any
from app.structures.abb_node import Node


class BinarySearchTree:
    """
    Binary Search Tree (ABB) implementation.
    
    Provides efficient insertion, search, deletion, and traversal operations.
    """
    
    def __init__(self):
        """Initialize an empty binary search tree."""
        self.root: Optional[Node] = None
        self._size: int = 0
    
    def insert(self, node: Node) -> None:
        """
        Insert a new node into the tree.
        
        Args:
            node: Node to insert (must have an id attribute)
        
        Raises:
            ValueError: If a node with the same id already exists
        """
        if self.root is None:
            self.root = node
            self._size += 1
        else:
            self._insert_recursive(self.root, node)
    
    def _insert_recursive(self, current: Node, new_node: Node) -> None:
        """
        Recursively insert a node into the tree.
        
        Args:
            current: Current node being examined
            new_node: Node to insert
        
        Raises:
            ValueError: If a node with the same id already exists
        """
        if new_node.id == current.id:
            raise ValueError(f"Node with id {new_node.id} already exists")
        
        if new_node.id < current.id:
            if current.left is None:
                current.left = new_node
                self._size += 1
            else:
                self._insert_recursive(current.left, new_node)
        else:
            if current.right is None:
                current.right = new_node
                self._size += 1
            else:
                self._insert_recursive(current.right, new_node)
    
    def search(self, id: int) -> Optional[Node]:
        """
        Search for a node by its id.
        
        Args:
            id: The id of the node to search for
        
        Returns:
            The node object if found, None otherwise
        """
        return self._search_recursive(self.root, id)
    
    def _search_recursive(self, current: Optional[Node], id: int) -> Optional[Node]:
        """
        Recursively search for a node.
        
        Args:
            current: Current node being examined
            id: The id to search for
        
        Returns:
            The node if found, None otherwise
        """
        if current is None:
            return None
        
        if id == current.id:
            return current
        elif id < current.id:
            return self._search_recursive(current.left, id)
        else:
            return self._search_recursive(current.right, id)
    
    def delete(self, id: int) -> bool:
        """
        Delete a node by its id.
        
        Handles three cases:
        1. Node is a leaf (no children)
        2. Node has one child
        3. Node has two children
        
        Args:
            id: The id of the node to delete
        
        Returns:
            True if the node was deleted, False if not found
        """
        initial_size = self._size
        self.root = self._delete_recursive(self.root, id)
        return self._size < initial_size
    
    def _delete_recursive(self, current: Optional[Node], id: int) -> Optional[Node]:
        """
        Recursively delete a node.
        
        Args:
            current: Current node being examined
            id: The id of the node to delete
        
        Returns:
            The updated node (or None if deleted)
        """
        if current is None:
            return None
        
        if id < current.id:
            current.left = self._delete_recursive(current.left, id)
        elif id > current.id:
            current.right = self._delete_recursive(current.right, id)
        else:
            # Node found - handle three cases
            self._size -= 1
            
            # Case 1: Leaf node (no children)
            if current.left is None and current.right is None:
                return None
            
            # Case 2: One child
            if current.left is None:
                return current.right
            if current.right is None:
                return current.left
            
            # Case 3: Two children
            # Find the inorder successor (minimum in right subtree)
            successor = self._find_min(current.right)
            # Copy successor's data to current node
            current.id = successor.id
            current.data = successor.data
            # Delete the successor
            # Increment size first since we're not actually deleting the current node
            self._size += 1
            current.right = self._delete_recursive(current.right, successor.id)
        
        return current
    
    def _find_min(self, node: Node) -> Node:
        """
        Find the node with minimum id in a subtree.
        
        Args:
            node: Root of the subtree
        
        Returns:
            Node with minimum id
        """
        current = node
        while current.left is not None:
            current = current.left
        return current
    
    def inOrder(self) -> List[dict]:
        """
        Perform in-order traversal (left, root, right).
        
        Returns nodes in ascending order by id.
        
        Returns:
            List of node dictionaries in in-order sequence
        """
        result = []
        self._inorder_recursive(self.root, result)
        return result
    
    def _inorder_recursive(self, node: Optional[Node], result: List[dict]) -> None:
        """
        Recursively perform in-order traversal.
        
        Args:
            node: Current node
            result: List to accumulate results
        """
        if node is not None:
            self._inorder_recursive(node.left, result)
            result.append(node.to_dict())
            self._inorder_recursive(node.right, result)
    
    def preOrder(self) -> List[dict]:
        """
        Perform pre-order traversal (root, left, right).
        
        Returns:
            List of node dictionaries in pre-order sequence
        """
        result = []
        self._preorder_recursive(self.root, result)
        return result
    
    def _preorder_recursive(self, node: Optional[Node], result: List[dict]) -> None:
        """
        Recursively perform pre-order traversal.
        
        Args:
            node: Current node
            result: List to accumulate results
        """
        if node is not None:
            result.append(node.to_dict())
            self._preorder_recursive(node.left, result)
            self._preorder_recursive(node.right, result)
    
    def postOrder(self) -> List[dict]:
        """
        Perform post-order traversal (left, right, root).
        
        Returns:
            List of node dictionaries in post-order sequence
        """
        result = []
        self._postorder_recursive(self.root, result)
        return result
    
    def _postorder_recursive(self, node: Optional[Node], result: List[dict]) -> None:
        """
        Recursively perform post-order traversal.
        
        Args:
            node: Current node
            result: List to accumulate results
        """
        if node is not None:
            self._postorder_recursive(node.left, result)
            self._postorder_recursive(node.right, result)
            result.append(node.to_dict())
    
    def size(self) -> int:
        """
        Get the total number of nodes in the tree.
        
        Returns:
            Number of nodes in the tree
        """
        return self._size
    
    def is_empty(self) -> bool:
        """
        Check if the tree is empty.
        
        Returns:
            True if tree is empty, False otherwise
        """
        return self.root is None
    
    def clear(self) -> None:
        """Clear all nodes from the tree."""
        self.root = None
        self._size = 0
    
    def get_root(self) -> Optional[Node]:
        """
        Get the root node of the tree.
        
        Returns:
            Root node or None if tree is empty
        """
        return self.root
    
    def get_min(self) -> Optional[Node]:
        """
        Get the node with minimum id in the tree.
        
        Returns:
            Node with minimum id or None if tree is empty
        """
        if self.root is None:
            return None
        return self._find_min(self.root)
    
    def get_max(self) -> Optional[Node]:
        """
        Get the node with maximum id in the tree.
        
        Returns:
            Node with maximum id or None if tree is empty
        """
        if self.root is None:
            return None
        
        current = self.root
        while current.right is not None:
            current = current.right
        return current
