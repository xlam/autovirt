from pydantic import BaseModel


class GatewayOptions(BaseModel):
    company_id: int
    pagesize: int = 1000
