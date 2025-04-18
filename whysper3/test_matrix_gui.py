import unittest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QByteArray, QBuffer, QIODevice
from PyQt5.QtGui import QPixmap, QImage
import sys
import os
import base64
from matrix_gui import MatrixGUI
from matrix_login import MatrixLogin

class TestMatrixGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create QApplication instance for GUI tests
        cls.app = QApplication(sys.argv)
        
    def setUp(self):
        # Create a mock Matrix client
        self.mock_client = MagicMock(spec=MatrixLogin)
        self.mock_client.login.return_value = True
        self.mock_client.get_joined_rooms.return_value = {'joined_rooms': ['!testroom:matrix.org']}
        self.mock_client.get_room_messages.return_value = [
            {
                'sender': '@testuser:matrix.org',
                'content': {
                    'msgtype': 'm.text',
                    'body': 'Test message'
                },
                'origin_server_ts': 1234567890
            }
        ]
        
        # Create GUI instance with mock client
        self.gui = MatrixGUI()
        self.gui.matrix_client = self.mock_client
        
    def test_handle_message_text(self):
        """Test handling of text messages"""
        message = {
            'sender': '@testuser:matrix.org',
            'content': {
                'msgtype': 'm.text',
                'body': 'Test message'
            },
            'origin_server_ts': 1234567890
        }
        
        self.gui.handle_message(message)
        
        # Check if message was added to chat display
        self.assertIn('Test message', self.gui.chat_display.toPlainText())
        
    def test_handle_message_image(self):
        """Test handling of image messages"""
        # Create a test image
        image = QImage(100, 100, QImage.Format_RGB32)
        image.fill(Qt.blue)
        
        # Convert image to bytes
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")
        image_data = byte_array.data()
        
        # Mock the download_media method to return the image data
        self.mock_client.download_media.return_value = image_data
        
        message = {
            'sender': '@testuser:matrix.org',
            'content': {
                'msgtype': 'm.image',
                'url': 'mxc://test.com/testimage',
                'body': 'Test image'
            },
            'origin_server_ts': 1234567890000
        }
        
        self.gui.handle_message(message)
        
        # Check if image HTML was added to chat display
        html_content = self.gui.chat_display.toHtml()
        self.assertIn('data:image/png;base64', html_content)
        
    def test_send_message(self):
        """Test sending a message"""
        self.gui.current_room = '!testroom:matrix.org'
        self.gui.message_input.setText('Test message')
        
        self.mock_client.send_message.return_value = True
        self.gui.send_message()
        
        # Check if message was sent
        self.mock_client.send_message.assert_called_once_with('!testroom:matrix.org', 'Test message')
        self.assertEqual(self.gui.message_input.text(), '')
        
    def test_send_image(self):
        """Test sending an image"""
        self.gui.current_room = '!testroom:matrix.org'
        
        # Create a test image file
        test_image_path = 'test_image.png'
        image = QImage(100, 100, QImage.Format_RGB32)
        image.fill(Qt.blue)
        image.save(test_image_path)
        
        # Mock the file dialog to return our test image
        with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName', 
                  return_value=(test_image_path, 'Image Files (*.png *.jpg *.jpeg *.gif *.bmp)')):
            self.mock_client.send_image.return_value = True
            self.gui.send_image()
            
            # Check if image was sent
            self.mock_client.send_image.assert_called_once()
            
        # Clean up test image
        os.remove(test_image_path)
        
    def test_load_more_messages(self):
        """Test loading more messages"""
        self.gui.current_room = '!testroom:matrix.org'
        self.gui.last_message_token = 'test_token'
        
        self.mock_client.get_room_messages.return_value = [
            {
                'sender': '@testuser:matrix.org',
                'content': {
                    'msgtype': 'm.text',
                    'body': 'Older message'
                },
                'origin_server_ts': 1234567890
            }
        ]
        
        self.gui.load_more_messages()
        
        # Check if older messages were loaded
        self.assertIn('Older message', self.gui.chat_display.toPlainText())
        
    def test_format_timestamp(self):
        """Test timestamp formatting"""
        # Use a timestamp that corresponds to 2009-02-13 23:31:30
        timestamp = 1234567890000  # Milliseconds since epoch
        formatted = self.gui.format_timestamp(timestamp)
        
        # Check if timestamp was formatted correctly
        self.assertIn('2009', formatted)  # Year should be 2009
        self.assertIn(':', formatted)     # Should contain time separator
        
    def test_pixmap_to_base64(self):
        """Test converting pixmap to base64"""
        # Create a test image
        image = QImage(100, 100, QImage.Format_RGB32)
        image.fill(Qt.blue)
        pixmap = QPixmap.fromImage(image)
        
        # Convert to base64
        base64_str = self.gui.pixmap_to_base64(pixmap)
        
        # Check if conversion was successful
        self.assertTrue(base64_str.startswith('iVBOR'))
        self.assertTrue(len(base64_str) > 0)

if __name__ == '__main__':
    unittest.main() 