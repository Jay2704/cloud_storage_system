#!/usr/bin/env python3
"""
Test runner for the cloud storage implementation.

This module contains comprehensive test cases for the CloudStorage system,
covering file operations, user management, and backup/restore functionality.
All tests include timeout protection to prevent infinite loops.
"""

import unittest
import sys
import os

# Add the current directory to the path to ensure imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import required modules
from timeout_decorator import timeout  # Decorator to prevent test timeouts
from cloud_storage_impl import CloudStorageImpl  # The implementation to test


class TestCloudStorage(unittest.TestCase):
    """
    Test cases for the CloudStorage implementation.
    
    This class contains unit tests that verify all major functionality
    of the cloud storage system including file operations, user management,
    and backup/restore capabilities.
    """
    
    def setUp(self):
        """
        Set up a fresh storage instance for each test.
        
        This method is called before each test method to ensure
        tests start with a clean state and don't interfere with each other.
        """
        self.storage = CloudStorageImpl()
    
    @timeout(0.4)  # Prevent test from running longer than 0.4 seconds
    def test_basic_file_operations(self):
        """
        Test basic file operations: add, get size, and delete.
        
        Verifies that files can be added, their sizes retrieved,
        and files can be deleted properly. Also tests edge cases
        like non-existent files.
        """
        # Test adding files - should return True for successful additions
        self.assertTrue(self.storage.add_file('/file.txt', 10))
        self.assertTrue(self.storage.add_file('/file2.txt', 1))
        
        # Test getting file sizes - should return correct sizes or None
        self.assertEqual(self.storage.get_file_size('/file.txt'), 10)
        self.assertEqual(self.storage.get_file_size('/file2.txt'), 1)
        self.assertIsNone(self.storage.get_file_size('/non-existent.txt'))  # Non-existent file
        
        # Test deleting files - should return size of deleted file or None
        self.assertEqual(self.storage.delete_file('/file.txt'), 10)  # Returns size of deleted file
        self.assertIsNone(self.storage.delete_file('/non-existent.txt'))  # Can't delete non-existent file
    
    @timeout(0.4)  # Prevent test from running longer than 0.4 seconds
    def test_get_n_largest(self):
        """
        Test getting n largest files with prefix matching.
        
        Verifies that the system can correctly identify and return
        the largest files that match a given prefix, sorted by size
        in descending order.
        """
        # Add test files with different sizes and paths
        self.storage.add_file('/docs/file1.txt', 100)  # Smaller file in /docs/
        self.storage.add_file('/docs/file2.txt', 200)  # Largest file in /docs/
        self.storage.add_file('/docs/file3.txt', 150)  # Medium file in /docs/
        self.storage.add_file('/other/file.txt', 300)  # Large file but different prefix
        
        # Test getting the 2 largest files with '/docs/' prefix
        # Should return files sorted by size (descending), then by name
        result = self.storage.get_n_largest('/docs/', 2)
        expected = ['/docs/file2.txt(200)', '/docs/file3.txt(150)']  # Largest 2 from /docs/
        self.assertEqual(result, expected)
    
    @timeout(0.4)  # Prevent test from running longer than 0.4 seconds
    def test_user_operations(self):
        """
        Test user management operations: add users, file operations by users, and user merging.
        
        Verifies user creation with capacity limits, file operations on behalf of users,
        capacity tracking, and the ability to merge users while preserving data integrity.
        """
        # Test adding users with storage capacity
        self.assertTrue(self.storage.add_user('user1', 1000))  # Should succeed
        self.assertTrue(self.storage.add_user('user2', 500))   # Should succeed
        self.assertFalse(self.storage.add_user('admin', 1000))  # 'admin' is reserved, should fail
        self.assertFalse(self.storage.add_user('user1', 1000))  # Duplicate user, should fail
        
        # Test adding files by users with capacity tracking
        # add_file_by returns remaining capacity after adding file
        self.assertEqual(self.storage.add_file_by('user1', '/user1/file.txt', 100), 900)   # 1000 - 100 = 900 remaining
        self.assertEqual(self.storage.add_file_by('user1', '/user1/file2.txt', 200), 700)  # 900 - 200 = 700 remaining
        self.assertIsNone(self.storage.add_file_by('user1', '/user1/file3.txt', 1000))     # Exceeds capacity, should fail
        
        # Test merging users - combines capacities and transfers files
        # user1 has used 300 bytes, user2 has used 0 bytes
        # Combined capacity: 1000 + 500 = 1500, used: 300, remaining: 1200
        self.assertEqual(self.storage.merge_user('user1', 'user2'), 1200)
    
    @timeout(0.4)
    def test_backup_and_restore(self):
        """Test backup and restore operations."""
        # Add a user and some files
        self.storage.add_user('user1', 1000)
        self.storage.add_file_by('user1', '/user1/file1.txt', 100)
        self.storage.add_file_by('user1', '/user1/file2.txt', 200)
        
        # Create backup
        self.assertEqual(self.storage.backup_user('user1'), 2)
        
        # Delete files
        self.storage.delete_file('/user1/file1.txt')
        
        # Restore from backup
        self.assertEqual(self.storage.restore_user('user1'), 2)  # 2 files restored
        
        # Verify files are restored
        self.assertEqual(self.storage.get_file_size('/user1/file1.txt'), 100)
        self.assertEqual(self.storage.get_file_size('/user1/file2.txt'), 200)


def run_tests():
    """Run all tests."""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCloudStorage)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success/failure
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)


# Total test cases across all files: 45 