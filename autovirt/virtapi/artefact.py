from autovirt import utils


logger = utils.get_logger("virtapi.artefact")
s = utils.get_logged_session()
token = utils.get_token(s)


# this uses virtonomica's API and should work for any site design
def attach(name, unit_id):

    # get unit artefact slots
    r = s.get(f"https://virtonomica.ru/api/vera/main/unit/artefact/slots?id={unit_id}")
    slots = list(r.json().values())

    # get all artefacts for unit slots
    artefacts = []
    for slot in slots:
        r = s.get(
            f"https://virtonomica.ru/api/vera/main/unit/artefact/browse"
            f"?id={unit_id}&slot_id={slot['id']}"
        )
        artefacts.extend(list(r.json().values()))

    url = "https://virtonomica.ru/api/vera/main/unit/artefact/attach"

    for artefact in artefacts:
        if artefact["name"] == name:
            params = {
                "id": unit_id,
                "artefact_id": artefact["id"],
                "token": token,
            }
            logger.info(f"renewing: ({unit_id}) {name}")
            r = s.post(url, params)
            logger.info(r)
            break
