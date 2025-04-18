# Matrix Chat Client

A modern GUI client for Matrix, built with PyQt5. This client allows you to chat with others on the Matrix network, send and receive images, and manage multiple chat rooms.

## Features

- Modern dark theme with blue accents
- Real-time message updates
- Image sharing support
- Message history with "Load More" functionality
- Timestamps for all messages
- Multiple room support
- User-friendly interface

## Requirements

- Python 3.7 or higher
- PyQt5
- requests
- Pillow (PIL)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd matrix-chat-client
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Client

Run the client using:
```bash
python matrix_gui.py
```

### Logging In

1. When the client starts, you'll see a login dialog
2. Enter your Matrix homeserver URL (e.g., https://matrix.org)
3. Enter your username and password
4. Click "Login" to connect to your account

### Registering an Account 🔴IMPORTANT🔴

 - The server 'https://www.whyps3.net' is currently unavailable, and thus to register an account,
   with this program - you must find a homeserver that doesn't require email/phone number verification.

### Using the Chat Client

#### Rooms
- The left panel shows your joined rooms
- Click on a room to view its messages
- Use the "Join Room" button to join a new room

#### Sending Messages
- Type your message in the input field at the bottom
- Press Enter or click "Send" to send the message
- Use the "Send Image" button to share images

#### Viewing Messages
- Messages are displayed in chronological order
- Images are displayed inline with the chat
- Timestamps show when each message was sent
- Use the "Load More Messages" button to view older messages

#### Image Support
- Supported image formats: PNG, JPG, JPEG, GIF, BMP
- Images are automatically scaled to fit the chat window
- Failed image loads will show a fallback message

## DevTools

### Running Unit Tests

To run the unit tests:
```bash
python -m unittest test_matrix_gui.py -v
```

#### Code Structure

- `matrix_gui.py`: Main GUI application
- `matrix_login.py`: Matrix client implementation
- `test_matrix_gui.py`: Unit tests

## Troubleshooting

### Common Issues

1. **Login Failed**
   - Verify your homeserver URL is correct
   - Check your username and password
   - Ensure your homeserver is accessible

2. **Images Not Displaying**
   - Check your internet connection
   - Verify the image format is supported
   - Check if the Matrix server supports media uploads

3. **Messages Not Updating**
   - Check your internet connection
   - Verify you're connected to the correct room
   - Try rejoining the room