"""
JWT Token Generator for Instagram Business API Testing
Usage: poetry run python generate_token.py
"""

from src.shared.util.jwt_handler.index import JWTHandler
import sys

def generate_token(user_id="seller_nitin_001", name="Nitin", expire_minutes=1440):
    """Generate JWT token for API testing"""
    payload = {
        "sub": user_id,
        "name": name,
        "security": {
            "party": ["party_2"]  # client party
        }
    }
    
    token = JWTHandler.create_token(payload, expire_minutes=expire_minutes)
    return token

if __name__ == "__main__":
    user_id = sys.argv[1] if len(sys.argv) > 1 else "seller_nitin_001"
    name = sys.argv[2] if len(sys.argv) > 2 else "Nitin"
    
    token = generate_token(user_id, name)
    
    print("=" * 80)
    print("JWT TOKEN GENERATED FOR API TESTING")
    print("=" * 80)
    print(f"\nUser ID: {user_id}")
    print(f"Name: {name}")
    print(f"Valid for: 24 hours (1440 minutes)")
    print(f"\n{'-' * 80}\n")
    print(f"Authorization Header:")
    print(f"Bearer {token}")
    print(f"\n{'-' * 80}\n")
    print("Copy the above 'Bearer ...' line and use it in your API requests")
    print("=" * 80)
