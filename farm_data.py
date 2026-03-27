"""Farm data manager — in-memory store for testing, Supabase for production."""
import os
from datetime import datetime

# In-memory store for testing
_farm_store = {}

DEFAULT_FARM = {
    'name': 'Ravi Farm',
    'location': 'Kolar, Karnataka',
    'size_sqm': 500,
    'rows': 10,
    'tomato_variety': 'Hybrid (Arka Rakshak)',
    'days': 65,
    'last_kg': 45,
    'price': 18,
    'weather': 'Sunny, 28C',
    'created_at': datetime.now().isoformat(),
}

def get_or_create_farm(phone: str) -> dict:
    """Get existing farm or create new one for this phone number."""
    if not phone:
        raise ValueError("Phone number is required")

    # Normalise phone format
    phone = phone.strip()

    if phone not in _farm_store:
        farm = DEFAULT_FARM.copy()
        farm['phone'] = phone
        farm['farmer_id'] = f"farmer_{len(_farm_store) + 1}"
        _farm_store[phone] = farm

    return _farm_store[phone]


def update_farm(phone: str, updates: dict) -> dict:
    """Update farm data for a given phone number."""
    if phone not in _farm_store:
        raise KeyError(f"Farm not found for phone: {phone}")

    _farm_store[phone].update(updates)
    return _farm_store[phone]


def list_all_farms() -> list:
    """List all registered farms."""
    return list(_farm_store.values())


def reset_store():
    """Reset the in-memory store (for testing)."""
    global _farm_store
    _farm_store = {}
