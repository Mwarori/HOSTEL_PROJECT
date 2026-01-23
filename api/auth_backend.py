"""
Custom JWT Authentication backend for mongoengine
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework import exceptions
from api.models import User
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class MongoDBJWTAuthentication(JWTAuthentication):
    """Custom JWT Authentication for mongoengine-based User model"""

    def get_raw_token(self, request):
        """
        Override to properly extract token from Authorization header
        """
        auth = request.META.get('HTTP_AUTHORIZATION', '').split()
        
        if not auth or auth[0].lower() != 'bearer':
            return None
            
        if len(auth) == 1:
            raise InvalidToken('Invalid token header. No credentials provided.')
        elif len(auth) > 2:
            raise InvalidToken('Invalid token header. Token string should not contain spaces.')
        
        return auth[1]

    def authenticate(self, request):
        """
        Override authenticate to avoid Django ORM user lookup
        """
        try:
            auth = self.get_raw_token(request)
            if auth is None:
                return None
            
            validated_token = self.get_validated_token(auth)
            
            # Return a fake user object that contains the token data
            class FakeUser:
                def __init__(self, validated_token):
                    self.id = validated_token.get('user_id')
                    self.user_id = validated_token.get('user_id')
                    self.email = validated_token.get('email')
                    self.role = validated_token.get('role')
                    self.is_authenticated = True
                    
                @property
                def pk(self):
                    return self.id
            
            return (FakeUser(validated_token), validated_token)
        except InvalidToken as e:
            raise AuthenticationFailed(str(e))
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise AuthenticationFailed('Invalid authentication credentials.')
