import requests
import json
from typing import Dict, Optional, Callable
import time
import threading
import queue
import os
import mimetypes
import base64
from urllib.parse import urlparse

class MatrixLogin:
    def __init__(self, homeserver_url: str):
        """
        Initialize the Matrix login client.
        
        Args:
            homeserver_url (str): The URL of the Matrix homeserver (e.g., 'https://matrix.org')
        """
        self.homeserver_url = homeserver_url.rstrip('/')
        self.session = requests.Session()
        self.access_token = None
        self.user_id = None
        self.message_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.media_cache = {}  # Cache for downloaded media
    
    def register(self, username: str, password: str, display_name: Optional[str] = None) -> Optional[Dict]:
        """
        Register a new account on the Matrix homeserver.
        
        Args:
            username (str): The desired username (without the @ and homeserver part)
            password (str): The desired password
            display_name (Optional[str]): The display name for the account
            
        Returns:
            Optional[Dict]: The registration response if successful, None if failed
        """
        register_url = f"{self.homeserver_url}/_matrix/client/r0/register"
        
        # First, get the registration flow
        try:
            response = self.session.get(register_url)
            if response.status_code != 200:
                print(f"Failed to get registration flow with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
            # Get the session ID from the response
            session_id = response.json().get('session')
            
            # Prepare the registration payload
            payload = {
                "auth": {
                    "type": "m.login.dummy"
                },
                "username": username,
                "password": password,
                "inhibit_login": False
            }
            
            if display_name:
                payload["displayname"] = display_name
            
            # Send the registration request
            response = self.session.post(
                register_url,
                json=payload,
                params={"kind": "user"},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                self.access_token = response_data.get('access_token')
                self.user_id = response_data.get('user_id')
                return response_data
            else:
                print(f"Registration failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error during registration: {str(e)}")
            return None
    
    def login(self, username: str, password: str) -> Optional[Dict]:
        """
        Attempt to login to the Matrix homeserver.
        
        Args:
            username (str): The Matrix username (e.g., '@user:matrix.org')
            password (str): The account password
            
        Returns:
            Optional[Dict]: The login response containing access token and user ID if successful,
                          None if login failed
        """
        login_url = f"{self.homeserver_url}/_matrix/client/r0/login"
        
        # Prepare the login request payload
        payload = {
            "type": "m.login.password",
            "identifier": {
                "type": "m.id.user",
                "user": username
            },
            "password": password
        }
        
        try:
            response = self.session.post(
                login_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                response_data = response.json()
                self.access_token = response_data.get('access_token')
                self.user_id = response_data.get('user_id')
                return response_data
            else:
                print(f"Login failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error during login: {str(e)}")
            return None

    def join_room(self, room_id_or_alias: str) -> Optional[Dict]:
        """
        Join a Matrix room using its ID or alias.
        
        Args:
            room_id_or_alias (str): The room ID (e.g., '!room:matrix.org') or alias (e.g., '#room:matrix.org')
            
        Returns:
            Optional[Dict]: The join response if successful, None if failed
        """
        if not self.access_token:
            print("Not logged in. Please login first.")
            return None

        # URL encode the room ID or alias
        encoded_room = requests.utils.quote(room_id_or_alias)
        join_url = f"{self.homeserver_url}/_matrix/client/r0/join/{encoded_room}"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.post(
                join_url,
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to join room with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error joining room: {str(e)}")
            return None

    def get_joined_rooms(self) -> Optional[Dict]:
        """
        Get a list of rooms the user has joined.
        
        Returns:
            Optional[Dict]: The response containing joined rooms if successful, None if failed
        """
        if not self.access_token:
            print("Not logged in. Please login first.")
            return None

        rooms_url = f"{self.homeserver_url}/_matrix/client/r0/joined_rooms"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            response = self.session.get(
                rooms_url,
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get joined rooms with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error getting joined rooms: {str(e)}")
            return None

    def send_message(self, room_id: str, message: str) -> Optional[Dict]:
        """
        Send a text message to a Matrix room.
        
        Args:
            room_id (str): The room ID (e.g., '!room:matrix.org')
            message (str): The message to send
            
        Returns:
            Optional[Dict]: The send response if successful, None if failed
        """
        if not self.access_token:
            print("Not logged in. Please login first.")
            return None

        # URL encode the room ID
        encoded_room = requests.utils.quote(room_id)
        send_url = f"{self.homeserver_url}/_matrix/client/r0/rooms/{encoded_room}/send/m.room.message"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        # Generate a unique transaction ID using timestamp
        txn_id = str(int(time.time() * 1000))
        
        payload = {
            "msgtype": "m.text",
            "body": message
        }
        
        try:
            response = self.session.put(
                f"{send_url}/{txn_id}",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to send message with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error sending message: {str(e)}")
            return None

    def start_listening(self, room_id: str, message_callback: Optional[Callable[[Dict], None]] = None) -> None:
        """
        Start listening for messages in a room.
        
        Args:
            room_id (str): The room ID to listen to
            message_callback (Optional[Callable[[Dict], None]]): Optional callback function for received messages
        """
        if not self.access_token:
            print("Not logged in. Please login first.")
            return

        def listen_thread():
            next_batch = None
            
            while not self.stop_event.is_set():
                try:
                    sync_url = f"{self.homeserver_url}/_matrix/client/r0/sync"
                    params = {
                        "access_token": self.access_token,
                        "timeout": 30000,  # 30 seconds
                        "filter": json.dumps({
                            "room": {
                                "timeline": {
                                    "limit": 10
                                }
                            }
                        })
                    }
                    
                    if next_batch:
                        params["since"] = next_batch
                    
                    response = self.session.get(sync_url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        next_batch = data.get("next_batch")
                        
                        # Process room events
                        for room_id, room_data in data.get("rooms", {}).get("join", {}).items():
                            for event in room_data.get("timeline", {}).get("events", []):
                                if event.get("type") == "m.room.message":
                                    message = {
                                        "room_id": room_id,
                                        "sender": event.get("sender"),
                                        "content": event.get("content", {}),
                                        "event_id": event.get("event_id")
                                    }
                                    
                                    # Add message to queue
                                    self.message_queue.put(message)
                                    
                                    # Call callback if provided
                                    if message_callback:
                                        message_callback(message)
                    
                except requests.exceptions.RequestException as e:
                    print(f"Error during sync: {str(e)}")
                    time.sleep(5)  # Wait before retrying
                except Exception as e:
                    print(f"Unexpected error: {str(e)}")
                    time.sleep(5)  # Wait before retrying
        
        # Start the listening thread
        self.stop_event.clear()
        threading.Thread(target=listen_thread, daemon=True).start()
    
    def stop_listening(self) -> None:
        """
        Stop listening for messages.
        """
        self.stop_event.set()
    
    def get_next_message(self, timeout: Optional[float] = None) -> Optional[Dict]:
        """
        Get the next message from the queue.
        
        Args:
            timeout (Optional[float]): Timeout in seconds, None for no timeout
            
        Returns:
            Optional[Dict]: The next message if available, None if timeout or no messages
        """
        try:
            return self.message_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def upload_file(self, file_path: str) -> Optional[Dict]:
        """
        Upload a file to the Matrix homeserver.
        
        Args:
            file_path (str): Path to the file to upload
            
        Returns:
            Optional[Dict]: The upload response containing the MXC URI if successful, None if failed
        """
        if not self.access_token:
            print("Not logged in. Please login first.")
            return None

        try:
            # Get file info
            file_name = os.path.basename(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            # Prepare upload URL
            upload_url = f"{self.homeserver_url}/_matrix/media/r0/upload"
            params = {
                "access_token": self.access_token,
                "filename": file_name
            }
            
            # Read and upload file
            with open(file_path, 'rb') as file:
                response = self.session.post(
                    upload_url,
                    params=params,
                    data=file,
                    headers={
                        "Content-Type": mime_type
                    }
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Upload failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            return None

    def send_image(self, room_id: str, image_path: str) -> Optional[Dict]:
        """
        Send an image to a Matrix room.
        
        Args:
            room_id (str): The room ID to send the image to
            image_path (str): Path to the image file
            
        Returns:
            Optional[Dict]: The send response if successful, None if failed
        """
        if not self.access_token:
            print("Not logged in. Please login first.")
            return None

        # Upload the image first
        upload_response = self.upload_file(image_path)
        if not upload_response:
            return None

        # Get the MXC URI from the upload response
        mxc_uri = upload_response.get('content_uri')
        if not mxc_uri:
            return None

        # Get image info
        file_name = os.path.basename(image_path)
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = 'image/jpeg'  # Default to JPEG if type can't be determined

        # Prepare the send URL
        encoded_room = requests.utils.quote(room_id)
        send_url = f"{self.homeserver_url}/_matrix/client/r0/rooms/{encoded_room}/send/m.room.message"
        
        # Generate a unique transaction ID
        txn_id = str(int(time.time() * 1000))
        
        # Prepare the message payload
        payload = {
            "msgtype": "m.image",
            "body": file_name,
            "url": mxc_uri,
            "info": {
                "mimetype": mime_type,
                "size": os.path.getsize(image_path)
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.put(
                f"{send_url}/{txn_id}",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to send image with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error sending image: {str(e)}")
            return None

    def download_media(self, mxc_uri: str) -> bytes:
        """
        Download media from a Matrix MXC URI.
        
        Args:
            mxc_uri (str): The MXC URI of the media to download
            
        Returns:
            bytes: The media data, or None if download failed
        """
        if not self.access_token:
            print("Not logged in. Please login first.")
            return None

        try:
            # Extract server name and media ID from MXC URI
            if not mxc_uri.startswith("mxc://"):
                print(f"Invalid MXC URI: {mxc_uri}")
                return None
                
            parts = mxc_uri[6:].split("/")
            if len(parts) != 2:
                print(f"Invalid MXC URI format: {mxc_uri}")
                return None
                
            server_name = parts[0]
            media_id = parts[1]
            
            # Construct download URL
            download_url = f"{self.homeserver_url}/_matrix/media/r0/download/{server_name}/{media_id}"
            
            # Make the request
            response = self.session.get(
                download_url,
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if response.status_code == 200:
                return response.content
            else:
                print(f"Failed to download media. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error downloading media: {str(e)}")
            return None

    def get_media_url(self, mxc_uri: str) -> Optional[str]:
        """
        Get the direct URL for a Matrix MXC URI.
        
        Args:
            mxc_uri (str): The MXC URI of the media
            
        Returns:
            Optional[str]: The direct URL if successful, None if failed
        """
        try:
            # Parse MXC URI
            parsed = urlparse(mxc_uri)
            if parsed.scheme != 'mxc':
                print(f"Invalid MXC URI: {mxc_uri}")
                return None

            # Extract server and media ID
            server = parsed.netloc
            media_id = parsed.path.lstrip('/')

            # Construct download URL
            download_url = f"{self.homeserver_url}/_matrix/media/r0/download/{server}/{media_id}"
            
            # Add access token to URL
            download_url += f"?access_token={self.access_token}"

            return download_url
                
        except Exception as e:
            print(f"Error getting media URL: {str(e)}")
            return None

    def get_room_messages(self, room_id: str, limit: int = 50, since: str = None, filter_type: str = None) -> list:
        """
        Get messages from a room with improved functionality.
        
        Args:
            room_id (str): The ID of the room to get messages from
            limit (int): Maximum number of messages to retrieve per request
            since (str): Token to paginate from (for getting older messages)
            filter_type (str): Optional filter for message types (e.g., 'm.text', 'm.image')
            
        Returns:
            list: List of messages from the room
        """
        if not self.access_token:
            print("Not logged in. Please login first.")
            return []

        try:
            # Prepare the request parameters
            params = {
                "limit": limit,
                "dir": "b",  # 'b' for backwards (older messages)
                "access_token": self.access_token
            }
            
            # Add since token if provided
            if since:
                params["from"] = since
                
            # Add filter if provided
            if filter_type:
                params["filter"] = json.dumps({
                    "types": ["m.room.message"],
                    "msgtypes": [filter_type]
                })
            
            # Make the request
            response = self.session.get(
                f"{self.homeserver_url}/_matrix/client/r0/rooms/{room_id}/messages",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get('chunk', [])
                
                # Process messages to include additional metadata
                processed_messages = []
                for msg in messages:
                    # Add room_id to each message
                    msg['room_id'] = room_id
                    
                    # Add timestamp if not present
                    if 'origin_server_ts' not in msg:
                        msg['origin_server_ts'] = int(time.time() * 1000)
                    
                    processed_messages.append(msg)
                
                return processed_messages
            else:
                print(f"Failed to get room messages. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Error getting room messages: {str(e)}")
            return []
        except Exception as e:
            print(f"Unexpected error getting room messages: {str(e)}")
            return []

def main():
    # Example usage
    homeserver = "https://matrix.org"
    
    # Ask user if they want to register or login
    action = input("Do you want to (1) Register or (2) Login? Enter 1 or 2: ")
    
    matrix_client = MatrixLogin(homeserver)
    
    if action == "1":
        # Registration flow
        # WARNING: AN HOMESERVER IS NEEDED THAT DOES NOT REQUIRE EMAIL VERIFICATION OR PHONE NUMBER VERIFICATION
        # TODO a resgistration function that allows for email and phone number verification.
        username = input("Enter desired username (without @ and homeserver): ")
        password = input("Enter desired password: ")
        display_name = input("Enter display name (optional, press Enter to skip): ")
        
        response = matrix_client.register(username, password, display_name if display_name else None)
        
        if response:
            print("\nRegistration successful!")
            print(f"User ID: {response.get('user_id')}")
            print(f"Access Token: {response.get('access_token')[:20]}...")  # Only show first 20 chars of token
        else:
            print("\nRegistration failed. Please try again.")
            return
    else:
        # Login flow
        username = input("Enter your Matrix username (e.g., @user:matrix.org): ")
        password = input("Enter your password: ")
        
        response = matrix_client.login(username, password)
        
        if not response:
            print("\nLogin failed. Please check your credentials and try again.")
            return
    
    # After successful registration or login, continue with room operations
    print("\nLogin successful!")
    print(f"User ID: {response.get('user_id')}")
    print(f"Access Token: {response.get('access_token')[:20]}...")  # Only show first 20 chars of token
    
    # Example of joining a room
    room_id = input("\nEnter room ID or alias to join (e.g., !room:matrix.org or #room:matrix.org): ")
    join_response = matrix_client.join_room(room_id)
    
    if join_response:
        print("\nSuccessfully joined the room!")
        room_id = join_response.get('room_id')
        print(f"Room ID: {room_id}")
        
        # Define a callback for received messages
        def message_callback(message):
            sender = message.get("sender")
            content = message.get("content", {})
            body = content.get("body", "")
            print(f"\nNew message from {sender}: {body}")
        
        # Start listening for messages
        print("\nStarting to listen for messages...")
        matrix_client.start_listening(room_id, message_callback)
        
        # Send messages in the room
        while True:
            message = input("\nEnter message to send (or 'quit' to exit): ")
            if message.lower() == 'quit':
                break
                
            send_response = matrix_client.send_message(room_id, message)
            if send_response:
                print("Message sent successfully!")
            else:
                print("Failed to send message.")
        
        # Stop listening when done
        matrix_client.stop_listening()
    
    # Get list of joined rooms
    print("\nFetching list of joined rooms...")
    rooms_response = matrix_client.get_joined_rooms()
    if rooms_response:
        print("\nJoined rooms:")
        for room_id in rooms_response.get('joined_rooms', []):
            print(f"- {room_id}")

if __name__ == "__main__":
    main() 