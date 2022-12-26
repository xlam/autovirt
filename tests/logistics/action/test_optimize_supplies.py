from autovirt.logistics.action import (
    OptimizeUnitSuppliesAction,
    OptimizeShopsSuppliesAction,
)
from autovirt.logistics.action.gateway import SuppliesGateway, UnitsGateway
from autovirt.logistics.domain.unitsupplies import Supply, UnitSupplies, SupplyContract

COPIES = 3


def make_unit_supplies(unit_id) -> UnitSupplies:
    return UnitSupplies(
        unit_id,
        [
            Supply(
                unit_id=unit_id,
                product_id=1,
                product_name="Product1",
                quantity=100,
                required=5,
                contracts=[
                    SupplyContract(
                        consumer_id=unit_id,
                        offer_id=1,
                        supplier_id=11,
                        free_for_buy=100,
                        party_quantity=10,
                    )
                ],
            ),
            Supply(
                unit_id,
                2,
                "Product2",
                5,
                10,
                [SupplyContract(unit_id, 2, 12, 100, 10)],
            ),
            Supply(
                unit_id,
                3,
                "Product3",
                200,
                100,
                [SupplyContract(unit_id, 3, 13, 100, 200)],
            ),
            Supply(
                unit_id,
                4,
                "Product4",
                200,
                10,
                [SupplyContract(unit_id, 4, 14, 100, 0)],
            ),
        ],
    )


def more_supplies() -> list[UnitSupplies]:
    return [make_unit_supplies(unit_id) for unit_id in range(COPIES)]


class FakeSuppliesGateway(SuppliesGateway):
    def __init__(self):
        self.supplies = more_supplies()
        self.sets = []

    def get(self, unit_id: int) -> UnitSupplies:
        return self.supplies[unit_id]

    def set_supplies(self, supplies: UnitSupplies):
        self.sets.append(supplies)


class FakeUnitsGateway(UnitsGateway):
    def get_shops_ids(self) -> list[int]:
        return list(range(COPIES))


def test_optimize_supplies_action():
    unit_id = 0
    factor = 2
    action = OptimizeUnitSuppliesAction(FakeSuppliesGateway())
    res = action.execute(unit_id, factor)
    assert len(res) == 2
    assert res[0].ordered == 0
    assert res[1].ordered == 20


def test_optimize_shops_supplies():
    factor = 2
    action = OptimizeShopsSuppliesAction(FakeUnitsGateway(), FakeSuppliesGateway())
    res = action.execute(factor)
    assert len(res) == 3
    print(res)
    assert res[1][0].ordered == 0
    assert res[1][1].ordered == 20
