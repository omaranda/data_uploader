# Copyright 2025 Omar Miranda
# SPDX-License-Identifier: Apache-2.0

#!/usr/bin/env python3
"""
Generate bcrypt password hash for demo users.
This uses the same hashing method as the backend application.
"""

import sys
from passlib.context import CryptContext

# Same configuration as backend
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_hash(password: str) -> str:
    """Generate bcrypt hash for a password."""
    return pwd_context.hash(password)


def verify_hash(password: str, hash: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(password, hash)


if __name__ == "__main__":
    # Generate hash for default password
    default_password = "admin123"

    print("=" * 70)
    print("Password Hash Generator")
    print("=" * 70)
    print()
    print(f"Password: {default_password}")
    print()

    # Generate hash
    password_hash = generate_hash(default_password)
    print(f"Bcrypt Hash (12 rounds):")
    print(password_hash)
    print()

    # Verify it works
    is_valid = verify_hash(default_password, password_hash)
    print(f"Verification Test: {'✅ PASSED' if is_valid else '❌ FAILED'}")
    print()

    print("=" * 70)
    print("Use this hash in SQL files:")
    print("=" * 70)
    print(f"'{password_hash}'")
    print()
