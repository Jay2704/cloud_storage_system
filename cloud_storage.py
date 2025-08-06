from abc import ABC, abstractmethod
from typing import Optional, List


class CloudStorage(ABC):
    """Abstract base class for cloud storage operations."""
    
    @abstractmethod
    def add_file(self, name: str, size: int) -> bool:
        """Add a file to storage.
        
        Args:
            name: Name of the file
            size: Size of the file in bytes
            
        Returns:
            True if file was added successfully, False if file already exists
        """
        pass
    
    @abstractmethod
    def get_file_size(self, name: str) -> Optional[int]:
        """Get the size of a file.
        
        Args:
            name: Name of the file
            
        Returns:
            Size of the file in bytes, or None if file doesn't exist
        """
        pass
    
    @abstractmethod
    def delete_file(self, name: str) -> Optional[int]:
        """Delete a file from storage.
        
        Args:
            name: Name of the file to delete
            
        Returns:
            Size of the deleted file in bytes, or None if file doesn't exist
        """
        pass
    
    @abstractmethod
    def get_n_largest(self, prefix: str, n: int) -> List[str]:
        """Get the n largest files that start with the given prefix.
        
        Args:
            prefix: Prefix to match file names
            n: Number of largest files to return
            
        Returns:
            List of strings in format "filename(size)" sorted by size descending, then by name
        """
        pass
    
    @abstractmethod
    def add_user(self, user_id: str, capacity: int) -> bool:
        """Add a new user with storage capacity.
        
        Args:
            user_id: Unique identifier for the user
            capacity: Storage capacity in bytes
            
        Returns:
            True if user was added successfully, False if user already exists or is admin
        """
        pass
    
    @abstractmethod
    def add_file_by(self, user_id: str, name: str, size: int) -> Optional[int]:
        """Add a file to storage on behalf of a user.
        
        Args:
            user_id: ID of the user adding the file
            name: Name of the file
            size: Size of the file in bytes
            
        Returns:
            Remaining capacity for the user, or None if operation failed
        """
        pass
    
    @abstractmethod
    def merge_user(self, user_id_1: str, user_id_2: str) -> Optional[int]:
        """Merge two users, transferring all files from user_id_2 to user_id_1.
        
        Args:
            user_id_1: ID of the target user (will receive files)
            user_id_2: ID of the source user (will be deleted)
            
        Returns:
            Remaining capacity for the merged user, or None if operation failed
        """
        pass
    
    @abstractmethod
    def backup_user(self, user_id: str) -> Optional[int]:
        """Create a backup snapshot of all files owned by a user.
        
        Args:
            user_id: ID of the user to backup
            
        Returns:
            Number of files in the backup, or None if operation failed
        """
        pass
    
    @abstractmethod
    def restore_user(self, user_id: str) -> Optional[int]:
        """Restore a user's files from their backup snapshot.
        
        Args:
            user_id: ID of the user to restore
            
        Returns:
            Number of files restored, or None if operation failed
        """
        pass 