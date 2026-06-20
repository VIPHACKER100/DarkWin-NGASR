"""Integration tests for database operations."""

import unittest

from core.database import SessionLocal
from core.models import Target


class TestDatabaseIntegration(unittest.TestCase):
    """Test database CRUD operations."""

    def test_create_target(self) -> None:
        """Create, verify, and clean up a Target record."""
        with SessionLocal() as db:
            new_target = Target(domain="integration-test.com", scope_confirmed=True)
            db.add(new_target)
            db.commit()

            target = db.query(Target).filter(Target.domain == "integration-test.com").first()
            self.assertIsNotNone(target)
            self.assertTrue(target.scope_confirmed)

            db.delete(target)
            db.commit()


if __name__ == "__main__":
    unittest.main()
