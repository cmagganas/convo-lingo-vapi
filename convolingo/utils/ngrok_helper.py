import subprocess
import time
import os
import signal
import logging
import requests
import re
import sys
from typing import Optional, Dict, Any, Tuple

# Set up logging
logger = logging.getLogger(__name__)


class NgrokTunnel:
    """Helper class to manage ngrok tunnel"""
    
    def __init__(self):
        """Initialize the ngrok tunnel"""
        self.process = None
        self.public_url = None
    
    def start(self, port: int = 5000, 
             check_interval: float = 0.5,
             timeout: float = 10.0) -> Optional[str]:
        """
        Start ngrok tunnel for the specified port
        
        Args:
            port: The port to tunnel
            check_interval: How often to check if tunnel is ready (seconds)
            timeout: Maximum time to wait for tunnel (seconds)
            
        Returns:
            The public URL if successful, None otherwise
        """
        # Check if ngrok is installed
        if not self._check_ngrok_installed():
            logger.error("ngrok is not installed. Please install it first.")
            return None
        
        # Kill any existing ngrok processes
        self._kill_existing_ngrok()
        
        # Start ngrok process
        logger.info(f"Starting ngrok tunnel for port {port}...")
        try:
            # Start ngrok as a subprocess
            self.process = subprocess.Popen(
                ["ngrok", "http", str(port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                # Prevent the child process from receiving signals sent to the parent
                preexec_fn=os.setpgrp if os.name != 'nt' else None
            )
            
            # Wait for tunnel to be established
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Check if ngrok is running
                if self.process.poll() is not None:
                    logger.error("ngrok process exited unexpectedly")
                    return None
                
                # Try to get the tunnel URL from the ngrok API
                self.public_url = self._get_public_url()
                if self.public_url:
                    logger.info(f"ngrok tunnel established at {self.public_url}")
                    return self.public_url
                
                time.sleep(check_interval)
            
            logger.error(f"Timed out waiting for ngrok tunnel after {timeout} seconds")
            self.stop()
            return None
            
        except Exception as e:
            logger.error(f"Error starting ngrok: {e}")
            self.stop()
            return None
    
    def stop(self) -> None:
        """Stop the ngrok tunnel"""
        if self.process:
            logger.info("Stopping ngrok tunnel...")
            if os.name == 'nt':
                # Windows
                self.process.terminate()
            else:
                # Unix/Mac - more reliable way to kill process group
                try:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                except (AttributeError, ProcessLookupError):
                    self.process.terminate()
            
            self.process = None
            self.public_url = None
    
    def _check_ngrok_installed(self) -> bool:
        """Check if ngrok is installed"""
        try:
            subprocess.run(
                ["ngrok", "--version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                check=True
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _kill_existing_ngrok(self) -> None:
        """Kill any existing ngrok processes"""
        try:
            if os.name == 'nt':
                # Windows
                subprocess.run(
                    ["taskkill", "/F", "/IM", "ngrok.exe"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                # Unix/Mac
                subprocess.run(
                    ["pkill", "-f", "ngrok"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
        except subprocess.SubprocessError:
            pass  # Ignore errors if no processes exist
    
    def _get_public_url(self) -> Optional[str]:
        """Get the public URL from the ngrok API"""
        try:
            response = requests.get("http://localhost:4040/api/tunnels")
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get("tunnels", [])
                for tunnel in tunnels:
                    if tunnel.get("proto") == "https":
                        return tunnel.get("public_url")
            return None
        except requests.RequestException:
            return None
    
    def get_api_url(self, path: str = "") -> Optional[str]:
        """
        Get the full API URL including the specified path
        
        Args:
            path: The API path to append (without leading slash)
            
        Returns:
            The full public API URL
        """
        if not self.public_url:
            return None
            
        # Remove trailing slash from URL if present
        url = self.public_url.rstrip('/')
        
        # Remove leading slash from path if present
        clean_path = path.lstrip('/')
        
        # Join URL and path
        if clean_path:
            return f"{url}/{clean_path}"
        else:
            return url 