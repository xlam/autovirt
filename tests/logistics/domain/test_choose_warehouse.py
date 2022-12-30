from autovirt.logistics.domain.storage.warehouse import Warehouse
from autovirt.logistics.domain.storage import choose_warehouse


def test_choose_warehouse():
    warehouses = [Warehouse(1, 1000, 10), Warehouse(2, 2000, 20), Warehouse(3, 0, 1)]
    warehouse = choose_warehouse(warehouses)
    assert warehouse == warehouses[1]
