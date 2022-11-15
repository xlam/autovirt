from typing import Optional

from autovirt import utils
from autovirt.artefact.action.gateway import ArtefactGateway
from autovirt.artefact.domain import filter_artefacts_to_renew

logger = utils.get_logger()


class RenewAction:
    def __init__(self, artefact_gateway: ArtefactGateway):
        self.artfact_gateway = artefact_gateway

    def run(self, config_name: Optional[str] = None):
        if not config_name:
            pass

        artefacts = self.artfact_gateway.get_artefacts()
        artefacts_to_renew = filter_artefacts_to_renew(artefacts)
        if not artefacts_to_renew:
            logger.info("no artefacts to renew")
            return
        logger.info(f"{len(artefacts_to_renew)} artefacts to renew")
        for artefact in artefacts_to_renew:
            logger.info(
                f"renewing {artefact.name} at unit {artefact.unit_id} ({artefact.unit_name}, {artefact.city_name})"
            )
            self.artfact_gateway.remove(artefact)
            self.artfact_gateway.attach(artefact)
