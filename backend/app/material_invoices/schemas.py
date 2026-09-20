from app.shared.base import CamelModel


class ExtractedMaterialResult(CamelModel):
    material: str | None = None
    product_reference: str | None = None
    thickness_cm: float | None = None
    r_value: float | None = None
    quantity: str | None = None
    warning: str | None = None
