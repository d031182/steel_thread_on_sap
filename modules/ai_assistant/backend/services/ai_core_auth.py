"""
SAP AI Core OAuth2 Authentication Helper

Handles OAuth2 token acquisition for SAP AI Core API access.
"""

import os
import requests
from typing import Optional
from datetime import datetime, timedelta


class AICoreOAuth2:
    """
    OAuth2 token manager for SAP AI Core
    
    Automatically fetches and caches access tokens using client credentials flow.
    """
    
    def __init__(self):
        """Initialize with credentials from environment"""
        self.client_id = os.getenv("AI_CORE_CLIENT_ID")
        self.client_secret = os.getenv("AI_CORE_CLIENT_SECRET")
        self.auth_url = os.getenv("AI_CORE_AUTH_URL")
        self.resource_group = os.getenv("AI_CORE_RESOURCE_GROUP", "default")
        
        if not all([self.client_id, self.client_secret, self.auth_url]):
            raise ValueError(
                "Missing AI Core credentials. Set AI_CORE_CLIENT_ID, "
                "AI_CORE_CLIENT_SECRET, and AI_CORE_AUTH_URL in .env"
            )
        
        self._token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
    
    def get_access_token(self) -> str:
        """
        Get valid access token (cached or fetch new)
        
        Returns:
            str: Valid OAuth2 access token
        """
        # Return cached token if still valid (with 5 min buffer)
        if self._token and self._token_expiry:
            if datetime.now() < self._token_expiry - timedelta(minutes=5):
                return self._token
        
        # Fetch new token
        return self._fetch_new_token()
    
    def _fetch_new_token(self) -> str:
        """
        Fetch new access token from SAP AI Core OAuth2 endpoint
        
        Returns:
            str: Fresh access token
            
        Raises:
            RuntimeError: If token acquisition fails
        """
        token_url = f"{self.auth_url}/oauth/token"
        
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = requests.post(
                token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            response.raise_for_status()
            
            token_data = response.json()
            self._token = token_data["access_token"]
            
            # Calculate expiry (default 12 hours if not specified)
            expires_in = token_data.get("expires_in", 43200)
            self._token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            print(f"[AI Core OAuth2] Token acquired, expires in {expires_in}s")
            return self._token
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to get AI Core access token: {e}")
    
    def get_headers(self) -> dict:
        """
        Get HTTP headers with valid access token
        
        Returns:
            dict: Headers for AI Core API requests
        """
        token = self.get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "AI-Resource-Group": self.resource_group,
            "Content-Type": "application/json"
        }


# Singleton instance
_auth_instance: Optional[AICoreOAuth2] = None


def get_ai_core_auth() -> AICoreOAuth2:
    """Get singleton AI Core OAuth2 instance"""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = AICoreOAuth2()
    return _auth_instance
