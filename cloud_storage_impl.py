from typing import Optional, List
from cloud_storage import CloudStorage


class CloudStorageImpl(CloudStorage):
    """Implementation of the CloudStorage interface."""
    
    def __init__(self):
        """Initialize the cloud storage system."""
        self._files: dict[str, int] = {}
        self._owners: dict[str, str] = {}
        self._users: dict[str, dict[str, int]] = {}
        self._backups: dict[str, dict[str, int]] = {}

    def add_file(self, name: str, size: int) -> bool:
        """Add a file to storage.
        
        Args:
            name: Name of the file
            size: Size of the file in bytes
            
        Returns:
            True if file was added successfully, False if file already exists
        """
        if name in self._files:
            return False
        self._files[name] = size
        self._owners[name] = "admin"
        return True

    def get_file_size(self, name: str) -> Optional[int]:
        """Get the size of a file.
        
        Args:
            name: Name of the file
            
        Returns:
            Size of the file in bytes, or None if file doesn't exist
        """
        return self._files.get(name)

    def delete_file(self, name: str) -> Optional[int]:
        """Delete a file from storage.
        
        Args:
            name: Name of the file to delete
            
        Returns:
            Size of the deleted file in bytes, or None if file doesn't exist
        """
        size = self._files.pop(name, None)
        if size is None:
            return None
        owner = self._owners.pop(name)
        if owner in self._users:
            self._users[owner]["used"] -= size
        return size

    def get_n_largest(self, prefix: str, n: int) -> List[str]:
        """Get the n largest files that start with the given prefix.
        
        Args:
            prefix: Prefix to match file names
            n: Number of largest files to return
            
        Returns:
            List of strings in format "filename(size)" sorted by size descending, then by name
        """
        matches = [
            (path, sz)
            for path, sz in self._files.items()
            if path.startswith(prefix)
        ]
        matches.sort(key=lambda x: (-x[1], x[0]))
        return [f"{path}({sz})" for path, sz in matches[:n]]

    def add_user(self, user_id: str, capacity: int) -> bool:
        """Add a new user with storage capacity.
        
        Args:
            user_id: Unique identifier for the user
            capacity: Storage capacity in bytes
            
        Returns:
            True if user was added successfully, False if user already exists or is admin
        """
        if user_id == "admin" or user_id in self._users:
            return False
        self._users[user_id] = {"capacity": capacity, "used": 0}
        return True

    def add_file_by(self, user_id: str, name: str, size: int) -> Optional[int]:
        """Add a file to storage on behalf of a user.
        
        Args:
            user_id: ID of the user adding the file
            name: Name of the file
            size: Size of the file in bytes
            
        Returns:
            Remaining capacity for the user, or None if operation failed
        """
        if user_id not in self._users or name in self._files:
            return None
        user = self._users[user_id]
        if user["used"] + size > user["capacity"]:
            return None
        self._files[name] = size
        self._owners[name] = user_id
        user["used"] += size
        return user["capacity"] - user["used"]

    def merge_user(self, user_id_1: str, user_id_2: str) -> Optional[int]:
        """Merge two users, transferring all files from user_id_2 to user_id_1.
        
        Args:
            user_id_1: ID of the target user (will receive files)
            user_id_2: ID of the source user (will be deleted)
            
        Returns:
            Remaining capacity for the merged user, or None if operation failed
        """
        if (
            user_id_1 not in self._users
            or user_id_2 not in self._users
            or user_id_1 == user_id_2
        ):
            return None
        u1 = self._users[user_id_1]
        u2 = self._users[user_id_2]
        for path, owner in list(self._owners.items()):
            if owner == user_id_2:
                self._owners[path] = user_id_1
        u1["capacity"] += u2["capacity"]
        u1["used"] += u2["used"]
        del self._users[user_id_2]
        self._backups.pop(user_id_2, None)
        return u1["capacity"] - u1["used"]

    def backup_user(self, user_id: str) -> Optional[int]:
        """Create a backup snapshot of all files owned by a user.
        
        Args:
            user_id: ID of the user to backup
            
        Returns:
            Number of files in the backup, or None if operation failed
        """
        if user_id != "admin" and user_id not in self._users:
            return None
        snapshot = {
            path: self._files[path]
            for path, owner in self._owners.items()
            if owner == user_id
        }
        self._backups[user_id] = snapshot
        return len(snapshot)

    def restore_user(self, user_id: str) -> Optional[int]:
        """Restore a user's files from their backup snapshot.
        
        Args:
            user_id: ID of the user to restore
            
        Returns:
            Number of files restored, or None if operation failed
        """
        if user_id != "admin" and user_id not in self._users:
            return None
        backup = self._backups.get(user_id)
        current = [p for p, o in self._owners.items() if o == user_id]
        if backup is None:
            for path in current:
                self._files.pop(path, None)
                self._owners.pop(path, None)
            if user_id in self._users:
                self._users[user_id]["used"] = 0
            return 0
        for path in current:
            if path not in backup:
                self._files.pop(path, None)
                self._owners.pop(path, None)
        restored = 0
        for path, size in backup.items():
            if path in self._files:
                if self._owners[path] != user_id:
                    if user_id == "admin":
                        old_owner = self._owners[path]
                        old_size = self._files[path]
                        if old_owner in self._users:
                            self._users[old_owner]["used"] -= old_size
                        self._files[path] = size
                        self._owners[path] = "admin"
                        restored += 1
                    continue
                if user_id in self._users:
                    diff = size - self._files[path]
                    self._users[user_id]["used"] += diff
                self._files[path] = size
                restored += 1
            else:
                self._files[path] = size
                self._owners[path] = user_id
                if user_id in self._users:
                    self._users[user_id]["used"] += size
                restored += 1
        if user_id in self._users:
            total = sum(
                self._files[p]
                for p, o in self._owners.items()
                if o == user_id
            )
            self._users[user_id]["used"] = total
        return restored