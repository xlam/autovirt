from unittest.mock import Mock

from autovirt.equipment.domain.equipment import (
    SelectOfferInstrumentation,
    FilteredOffer,
)
from autovirt.equipment.domain.repair_offer import RepairOffer


def test_filtered_offers_are_logged():
    filtered_offer = FilteredOffer(
        RepairOffer(
            id=1,
            company_id=1,
            company_name="company",
            cost=100,
            quality=20,
            quantity=1000,
        ),
        cost_norm=0,
        qual_exp=0,
        qual_diff=0,
        diff_norm=0,
        qp_dist=0,
    )
    offers = [filtered_offer, filtered_offer]

    instrumentation = SelectOfferInstrumentation()
    instrumentation.logger = Mock()
    instrumentation.offers_filtered(offers, quality=10)
    assert instrumentation.logger.info.call_count == 3
