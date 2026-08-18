import bcrypt


def hash_password(password: str) -> str:
    """Create a secure bcrypt hash from a password."""

    password_bytes = password.encode("utf-8")

    password_hash = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    )

    return password_hash.decode("utf-8")


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    """Check whether a password matches a bcrypt hash."""

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )

    except ValueError:
        return False