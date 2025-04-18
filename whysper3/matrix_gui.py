import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QListWidget, QMessageBox, QFrame,
                            QFileDialog, QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QByteArray, QBuffer, QIODevice
from PyQt5.QtGui import QPixmap, QImage, QTextDocument, QTextCursor
from matrix_login import MatrixLogin
import io
from PIL import Image
import base64
import time
from datetime import datetime

class MessageListener(QThread):
    message_received = pyqtSignal(dict)
    
    def __init__(self, matrix_client, room_id):
        super().__init__()
        self.matrix_client = matrix_client
        self.room_id = room_id
        self.running = True
        
    def run(self):
        def message_callback(message):
            self.message_received.emit(message)
        
        self.matrix_client.start_listening(self.room_id, message_callback)
        
    def stop(self):
        self.running = False
        self.matrix_client.stop_listening()

class MatrixGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Initialize Matrix client
        self.matrix_client = None
        self.current_room = None
        self.message_listener = None
        self.last_message_token = None
        
        # Show login dialog
        self.show_login_dialog()
    
    def init_ui(self):
        self.setWindowTitle("whysper")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set the main window background
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
            }
            QListWidget {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                color: #ffffff;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #3a3a3a;
            }
            QListWidget::item:selected {
                background-color: #0066cc;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                color: #ffffff;
            }
            QLineEdit {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
                color: #ffffff;
                padding: 5px;
            }
            QPushButton {
                background-color: #0066cc;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #0077dd;
            }
            QPushButton:pressed {
                background-color: #0055aa;
            }
            QPushButton:disabled {
                background-color: #3a3a3a;
                color: #666666;
            }
            QLabel {
                color: #ffffff;
            }
            QScrollBar:vertical {
                border: none;
                background: #2a2a2a;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #0066cc;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left panel for rooms
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.StyledPanel)
        left_panel.setMinimumWidth(200)
        left_layout = QVBoxLayout(left_panel)
        
        # Room list
        self.room_list = QListWidget()
        self.room_list.itemClicked.connect(self.room_selected)
        left_layout.addWidget(QLabel("Rooms"))
        left_layout.addWidget(self.room_list)
        
        # Join room button
        join_room_btn = QPushButton("Join Room")
        join_room_btn.clicked.connect(self.show_join_room_dialog)
        left_layout.addWidget(join_room_btn)
        
        # Right panel for chat
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.StyledPanel)
        right_layout = QVBoxLayout(right_panel)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setAcceptRichText(True)
        right_layout.addWidget(self.chat_display)
        
        # Message input area
        message_layout = QHBoxLayout()
        
        # Message input and buttons
        input_layout = QVBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)
        
        # Button layout
        button_layout = QHBoxLayout()
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)
        image_btn = QPushButton("Send Image")
        image_btn.clicked.connect(self.send_image)
        button_layout.addWidget(send_btn)
        button_layout.addWidget(image_btn)
        input_layout.addLayout(button_layout)
        
        message_layout.addLayout(input_layout)
        right_layout.addLayout(message_layout)
        
        # Add Load More button
        self.load_more_button = QPushButton("Load More Messages")
        self.load_more_button.clicked.connect(self.load_more_messages)
        self.load_more_button.setEnabled(False)
        right_layout.addWidget(self.load_more_button)
        
        # Add panels to main layout
        layout.addWidget(left_panel)
        layout.addWidget(right_panel)
    
    def show_login_dialog(self):
        dialog = QWidget()
        dialog.setWindowTitle("Login")
        dialog.setFixedSize(300, 200)
        layout = QVBoxLayout(dialog)
        
        # Homeserver input
        homeserver_label = QLabel("Homeserver URL:")
        self.homeserver_input = QLineEdit()
        self.homeserver_input.setText("https://matrix.org")
        layout.addWidget(homeserver_label)
        layout.addWidget(self.homeserver_input)
        
        # Username input
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        
        # Password input
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        
        # Action buttons
        button_layout = QHBoxLayout()
        login_btn = QPushButton("Login")
        register_btn = QPushButton("Register")
        login_btn.clicked.connect(lambda: self.handle_login(dialog))
        register_btn.clicked.connect(lambda: self.handle_register(dialog))
        button_layout.addWidget(login_btn)
        button_layout.addWidget(register_btn)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.show()
    
    def handle_login(self, dialog):
        homeserver = self.homeserver_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        
        self.matrix_client = MatrixLogin(homeserver)
        response = self.matrix_client.login(username, password)
        
        if response:
            dialog.close()
            self.update_room_list()
            self.show()
        else:
            QMessageBox.critical(dialog, "Login Failed", "Failed to login. Please check your credentials.")
    
    def handle_register(self, dialog):
        homeserver = self.homeserver_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        
        self.matrix_client = MatrixLogin(homeserver)
        response = self.matrix_client.register(username, password)
        
        if response:
            dialog.close()
            self.update_room_list()
            self.show()
        else:
            QMessageBox.critical(dialog, "Registration Failed", "Failed to register. Please try again.")
    
    def show_join_room_dialog(self):
        dialog = QWidget()
        dialog.setWindowTitle("Join Room")
        dialog.setFixedSize(300, 100)
        layout = QVBoxLayout(dialog)
        
        room_label = QLabel("Room ID or Alias:")
        self.room_input = QLineEdit()
        join_btn = QPushButton("Join")
        join_btn.clicked.connect(lambda: self.join_room(dialog))
        
        layout.addWidget(room_label)
        layout.addWidget(self.room_input)
        layout.addWidget(join_btn)
        
        dialog.setLayout(layout)
        dialog.show()
    
    def join_room(self, dialog):
        room_id = self.room_input.text()
        response = self.matrix_client.join_room(room_id)
        
        if response:
            dialog.close()
            self.update_room_list()
        else:
            QMessageBox.critical(dialog, "Join Failed", "Failed to join room. Please check the room ID.")
    
    def update_room_list(self):
        self.room_list.clear()
        response = self.matrix_client.get_joined_rooms()
        if response:
            for room_id in response.get('joined_rooms', []):
                self.room_list.addItem(room_id)
    
    def room_selected(self, item):
        room_id = item.text()
        self.current_room = room_id
        
        # Stop previous listener if exists
        if self.message_listener:
            self.message_listener.stop()
        
        # Start new listener
        self.message_listener = MessageListener(self.matrix_client, room_id)
        self.message_listener.message_received.connect(self.handle_message)
        self.message_listener.start()
        
        # Clear chat display and reset pagination
        self.chat_display.clear()
        self.last_message_token = None
        
        # Load initial messages
        messages = self.matrix_client.get_room_messages(room_id)
        if messages:
            # Process messages in chronological order
            for message in reversed(messages):
                self.handle_message(message)
        
        # Scroll to bottom
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
        
        # Enable Load More button if we have messages
        self.load_more_button.setEnabled(bool(messages))
    
    def handle_message(self, message):
        sender = message.get("sender")
        content = message.get("content", {})
        msgtype = content.get("msgtype")
        body = content.get("body", "")
        timestamp = message.get("origin_server_ts", int(time.time() * 1000))
        formatted_time = self.format_timestamp(timestamp)
        
        # Format message based on type
        if msgtype == "m.image":
            mxc_uri = content.get("url", "")
            if mxc_uri:
                try:
                    # Download the image
                    image_data = self.matrix_client.download_media(mxc_uri)
                    if image_data:
                        # Convert image data to QPixmap
                        image = QImage()
                        if image.loadFromData(image_data):
                            pixmap = QPixmap.fromImage(image)
                            if not pixmap.isNull():
                                # Scale the image to a reasonable size
                                scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                                
                                # Create HTML for the image with timestamp
                                image_html = f'<div style="margin: 10px 0;"><b>{sender}</b> <span style="color: gray; font-size: 0.8em;">[{formatted_time}]</span><br><img src="data:image/png;base64,{self.pixmap_to_base64(scaled_pixmap)}" style="max-width: 300px; max-height: 300px;"></div>'
                                
                                # Insert HTML at the current cursor position
                                cursor = self.chat_display.textCursor()
                                cursor.movePosition(QTextCursor.End)
                                cursor.insertHtml(image_html)
                                cursor.insertHtml("<br>")
                            else:
                                self.chat_display.append(f"<b>{sender}</b> <span style='color: gray; font-size: 0.8em;'>[{formatted_time}]</span> sent an image: {body}<br>")
                        else:
                            self.chat_display.append(f"<b>{sender}</b> <span style='color: gray; font-size: 0.8em;'>[{formatted_time}]</span> sent an image: {body}<br>")
                    else:
                        self.chat_display.append(f"<b>{sender}</b> <span style='color: gray; font-size: 0.8em;'>[{formatted_time}]</span> sent an image: {body}<br>")
                except Exception as e:
                    print(f"Error handling image message: {str(e)}")
                    self.chat_display.append(f"<b>{sender}</b> <span style='color: gray; font-size: 0.8em;'>[{formatted_time}]</span> sent an image: {body}<br>")
            else:
                self.chat_display.append(f"<b>{sender}</b> <span style='color: gray; font-size: 0.8em;'>[{formatted_time}]</span> sent an image: {body}<br>")
        else:
            self.chat_display.append(f"<b>{sender}</b> <span style='color: gray; font-size: 0.8em;'>[{formatted_time}]</span>: {body}<br>")
        
        # Store the last message token for pagination
        self.last_message_token = message.get("event_id")
        
        # Enable Load More button if we have a token
        self.load_more_button.setEnabled(bool(self.last_message_token))
        
        # Scroll to bottom
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def format_timestamp(self, timestamp_ms):
        """
        Format a timestamp in milliseconds to a readable string.
        
        Args:
            timestamp_ms (int): Timestamp in milliseconds
            
        Returns:
            str: Formatted timestamp string
        """
        if not timestamp_ms:
            return ""
        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    def pixmap_to_base64(self, pixmap: QPixmap) -> str:
        """
        Convert a QPixmap to a base64-encoded string.
        
        Args:
            pixmap (QPixmap): The pixmap to convert
            
        Returns:
            str: The base64-encoded string
        """
        # Convert to QImage
        image = pixmap.toImage()
        
        # Convert to bytes
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")
        
        # Convert to base64
        return base64.b64encode(byte_array).decode('utf-8')
    
    def send_message(self):
        if not hasattr(self, 'current_room'):
            return
            
        message = self.message_input.text()
        if message:
            response = self.matrix_client.send_message(self.current_room, message)
            if response:
                self.message_input.clear()
            else:
                QMessageBox.critical(self, "Send Failed", "Failed to send message.")
    
    def send_image(self):
        if not hasattr(self, 'current_room'):
            QMessageBox.warning(self, "No Room Selected", "Please select a room first.")
            return
        
        # Open file dialog to select image
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        
        if file_path:
            response = self.matrix_client.send_image(self.current_room, file_path)
            if not response:
                QMessageBox.critical(self, "Send Failed", "Failed to send image.")
            else:
                # Display the sent image in the chat
                image = QImage(file_path)
                if not image.isNull():
                    pixmap = QPixmap.fromImage(image)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        
                        # Create HTML for the image
                        image_html = f'<div style="margin: 10px 0;"><b>You</b> sent an image:<br><img src="data:image/png;base64,{self.pixmap_to_base64(scaled_pixmap)}" style="max-width: 300px; max-height: 300px;"></div>'
                        self.chat_display.append(image_html)
                        
                        # Scroll to bottom
                        self.chat_display.verticalScrollBar().setValue(
                            self.chat_display.verticalScrollBar().maximum()
                        )
                    else:
                        QMessageBox.warning(self, "Invalid Image", "Failed to load the selected image.")
                else:
                    QMessageBox.warning(self, "Invalid Image", "Failed to load the selected image.")

    def load_more_messages(self):
        """
        Load older messages from the current room.
        """
        if not self.current_room or not self.last_message_token:
            return
            
        # Get older messages
        messages = self.matrix_client.get_room_messages(
            self.current_room,
            since=self.last_message_token
        )
        
        if messages:
            # Store current scroll position
            scrollbar = self.chat_display.verticalScrollBar()
            old_position = scrollbar.value()
            old_max = scrollbar.maximum()
            
            # Insert messages at the top
            for message in reversed(messages):
                self.handle_message(message)
            
            # Restore scroll position
            new_max = scrollbar.maximum()
            scrollbar.setValue(old_position + (new_max - old_max))
        else:
            QMessageBox.information(self, "No More Messages", "No older messages available.")

def main():
    app = QApplication(sys.argv)
    window = MatrixGUI()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 