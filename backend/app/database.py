"""
Compatibility alias for app.db.base_class.

Several model files (customer, product, order, pricing, etc.) import
``from app.database import Base`` instead of the canonical
``from app.db.base_class import Base``.  Rather than rewriting every
file, this module re-exports the canonical Base so the old import path
continues to work.

New code should always use:
    from app.db.base_class import Base
"""
from app.db.base_class import Base  # noqa: F401

__all__ = ["Base"]
