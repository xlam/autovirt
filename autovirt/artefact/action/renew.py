from autovirt import utils
from autovirt.artefact.action.gateway import ArtefactGateway
from autovirt.artefact.domain import filter_artefacts_to_renew

logger = utils.get_logger()


class RenewAction:
    def __init__(self, artefact_gateway: ArtefactGateway, dry_run: bool = False):
        self.artfact_gateway = artefact_gateway
        self.dry_run = dry_run

    def run(self):
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
            if not self.dry_run:
                self.artfact_gateway.remove(artefact)
                self.artfact_gateway.attach(artefact)
