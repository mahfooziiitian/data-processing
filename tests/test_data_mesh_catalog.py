"""Tests for the self-serve data product catalog."""
from data_proc.data_mesh import catalog
from data_proc.data_mesh.contract import DataContract

_CONTRACT = DataContract(
    domain="customers",
    name="customer_profile",
    version="v1",
    owner="customers-domain-team",
    description="A sufficiently long and descriptive product description.",
    schema={"customer_id": "int"},
)


def test_get_product_missing_entry_returns_none(tmp_path):
    catalog_path = tmp_path / "catalog.json"

    assert catalog.get_product(catalog_path, "customers.customer_profile") is None


def test_register_and_get_product_roundtrips(tmp_path):
    catalog_path = tmp_path / "catalog.json"

    catalog.register_product(catalog_path, _CONTRACT, "data_mesh_customers_product", 10)
    entry = catalog.get_product(catalog_path, "customers.customer_profile")

    assert entry["domain"] == "customers"
    assert entry["owner"] == "customers-domain-team"
    assert entry["table_name"] == "data_mesh_customers_product"
    assert entry["row_count"] == 10
    assert "published_at" in entry


def test_register_product_overwrites_previous_entry(tmp_path):
    catalog_path = tmp_path / "catalog.json"
    catalog.register_product(catalog_path, _CONTRACT, "data_mesh_customers_product", 10)

    catalog.register_product(catalog_path, _CONTRACT, "data_mesh_customers_product", 20)

    entry = catalog.get_product(catalog_path, "customers.customer_profile")
    assert entry["row_count"] == 20


def test_list_products_returns_all_registered_entries(tmp_path):
    catalog_path = tmp_path / "catalog.json"
    orders_contract = DataContract(
        domain="orders", name="order_summary", version="v1", owner="orders-domain-team",
        description="A sufficiently long and descriptive product description.",
        schema={"customer_id": "int"},
    )
    catalog.register_product(catalog_path, _CONTRACT, "data_mesh_customers_product", 10)
    catalog.register_product(catalog_path, orders_contract, "data_mesh_orders_product", 8)

    products = catalog.list_products(catalog_path)

    assert {p["name"] for p in products} == {"customer_profile", "order_summary"}
