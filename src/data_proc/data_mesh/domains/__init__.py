"""The two independent domains of this Data Mesh demo.

`customers_domain.py` and `orders_domain.py` each own their own source
data and build/publish logic end-to-end. Neither module imports the
other — the decentralized-ownership principle this demo illustrates means
one domain must never reach into another's internals; any cross-domain
need goes through the shared `data_proc.data_mesh.catalog` platform
instead (see `examples/run_data_mesh.py`'s consumer step).
"""
