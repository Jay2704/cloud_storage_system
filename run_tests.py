#!/usr/bin/env python3
"""
Test runner for the cloud storage implementation.
"""

import unittest
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from timeout_decorator import timeout
from cloud_storage_impl import CloudStorageImpl


class TestCloudStorage(unittest.TestCase):
    """Test cases for the CloudStorage implementation."""
    
    def setUp(self):
        """Set up a fresh storage instance for each test."""
        self.storage = CloudStorageImpl()
    
    @timeout(0.4)
    def test_basic_file_operations(self):
        """Test basic file operations."""
        # Test adding files
        self.assertTrue(self.storage.add_file('/file.txt', 10))
        self.assertTrue(self.storage.add_file('/file2.txt', 1))
        
        # Test getting file sizes
        self.assertEqual(self.storage.get_file_size('/file.txt'), 10)
        self.assertEqual(self.storage.get_file_size('/file2.txt'), 1)
        self.assertIsNone(self.storage.get_file_size('/non-existent.txt'))
        
        # Test deleting files
        self.assertEqual(self.storage.delete_file('/file.txt'), 10)
        self.assertIsNone(self.storage.delete_file('/non-existent.txt'))
    
    @timeout(0.4)
    def test_get_n_largest(self):
        """Test getting n largest files with prefix."""
        # Add some files
        self.storage.add_file('/docs/file1.txt', 100)
        self.storage.add_file('/docs/file2.txt', 200)
        self.storage.add_file('/docs/file3.txt', 150)
        self.storage.add_file('/other/file.txt', 300)
        
        # Test getting largest files with prefix
        result = self.storage.get_n_largest('/docs/', 2)
        expected = ['/docs/file2.txt(200)', '/docs/file3.txt(150)']
        self.assertEqual(result, expected)
    
    @timeout(0.4)
    def test_user_operations(self):
        """Test user management operations."""
        # Test adding users
        self.assertTrue(self.storage.add_user('user1', 1000))
        self.assertTrue(self.storage.add_user('user2', 500))
        self.assertFalse(self.storage.add_user('admin', 1000))  # admin is reserved
        self.assertFalse(self.storage.add_user('user1', 1000))  # user already exists
        
        # Test adding files by users
        self.assertEqual(self.storage.add_file_by('user1', '/user1/file.txt', 100), 900)
        self.assertEqual(self.storage.add_file_by('user1', '/user1/file2.txt', 200), 700)
        self.assertIsNone(self.storage.add_file_by('user1', '/user1/file3.txt', 1000))  # exceeds capacity
        
        # Test merging users
        self.assertEqual(self.storage.merge_user('user1', 'user2'), 1200)  # 1000 + 500 - 300 used
    
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