"""Basic smoke-test checklist. Run with: python -m unittest discover -s tests"""
import unittest
from db import init_db, query_df

class TestERPDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_seeded_products_exist(self):
        products = query_df("SELECT * FROM products")
        self.assertGreaterEqual(len(products), 1)

    def test_bom_components_exist(self):
        bom = query_df("SELECT * FROM bom")
        self.assertGreaterEqual(len(bom), 1)

    def test_supplier_master_exists(self):
        suppliers = query_df("SELECT * FROM suppliers")
        self.assertGreaterEqual(len(suppliers), 1)

if __name__ == "__main__":
    unittest.main()
