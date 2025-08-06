# Cloud Storage Implementation

This project implements a cloud storage system with file management, user management, and backup/restore capabilities.

## Files

- `cloud_storage.py` - Abstract base class defining the CloudStorage interface
- `cloud_storage_impl.py` - Concrete implementation of the CloudStorage interface
- `timeout_decorator.py` - Timeout decorator for test execution
- `sandbox_tests.py` - Playground test file for custom testing
- `run_tests.py` - Comprehensive test suite
- `test.py` - Original implementation file

## Features

### File Operations
- Add files to storage
- Get file sizes
- Delete files
- Get n largest files with a prefix

### User Management
- Add users with storage capacity
- Add files on behalf of users
- Merge users (transfer files between users)
- Track user storage usage

### Backup and Restore
- Create backup snapshots of user files
- Restore user files from backups
- Handle admin user backups

## Usage

### Running Tests
```bash
python run_tests.py
```

### Using the Storage System
```python
from cloud_storage_impl import CloudStorageImpl

# Create storage instance
storage = CloudStorageImpl()

# Add files
storage.add_file('/file.txt', 100)

# Add users
storage.add_user('user1', 1000)

# Add files by users
storage.add_file_by('user1', '/user1/file.txt', 200)

# Get largest files
largest = storage.get_n_largest('/user1/', 5)

# Backup and restore
storage.backup_user('user1')
storage.restore_user('user1')
```

## Implementation Details

The implementation uses in-memory data structures:
- `_files`: Maps file names to sizes
- `_owners`: Maps file names to user IDs
- `_users`: Maps user IDs to capacity and usage info
- `_backups`: Maps user IDs to backup snapshots

All operations are designed to be efficient and handle edge cases properly. 