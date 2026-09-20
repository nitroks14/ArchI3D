"""
Schemas Pydantic partages entre modules backend, reflets du modele hierarchique du batiment :

Building > Floor(s) > Room(s) > Wall(s) > Opening(s)
                              > Equipment(s)

Ce fichier est la source de verite cote backend. Le frontend maintient des types TypeScript
equivalents dans src/domain/model/ (pas de generation automatique en V1, cf README > compromis).
"""
from typing import Literal
from uuid import uuid4

from pydantic import Field

from app.shared.base import CamelModel

ConstructionTypeId = Literal[
    "wood_frame",
    "ite",
    "monomur",
    "parpaing_iti",
    "brick",
    "stone",
    "unknown",
]

MaterialSource = Literal["vision_estimate", "invoice", "user_input", "default"]

CardinalDirection = Literal["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

ThermalInertiaClass = Literal["light", "medium", "heavy"]

# Mesure QUALITATIVE et INDEPENDANTE de ThermalInertiaClass - jamais fusionnee avec elle ni
# utilisee pour l'ajuster. Cf app/thermal_engine/inertia.py > estimate_additional_thermal_mass.
AdditionalThermalMassLevel = Literal["low", "notable", "significant"]


class Opening(CamelModel):
    """Ouverture percee dans une paroi : fenetre ou porte."""

    id: str = Field(default_factory=lambda: f"opening_{uuid4().hex[:8]}")
    type: Literal["window", "door"] = "window"
    width_m: float = 1.2
    height_m: float = 1.2
    glazing_type: str | None = None  # cle vers reference_data/glazing.json
    uw_value: float | None = None  # W/m2.K, si connu (facture / saisie utilisateur)


class MaterialLayer(CamelModel):
    """Couche de materiau constituant une paroi, issue d'une estimation vision ou d'une facture."""

    id: str = Field(default_factory=lambda: f"layer_{uuid4().hex[:8]}")
    source: MaterialSource = "default"
    material_ref: str | None = None  # cle vers reference_data/materials.json
    thickness_cm: float | None = None
    r_value: float | None = None  # resistance thermique m2.K/W, si connue
    product_reference: str | None = None
    invoice_id: str | None = None


class Wall(CamelModel):
    """Paroi d'une piece : exterieure, interieure, plancher ou toiture."""

    id: str = Field(default_factory=lambda: f"wall_{uuid4().hex[:8]}")
    kind: Literal["exterior", "interior", "floor", "roof"] = "exterior"
    construction_type: ConstructionTypeId = "unknown"
    length_m: float | None = None
    height_m: float | None = None
    layers: list[MaterialLayer] = Field(default_factory=list)
    openings: list[Opening] = Field(default_factory=list)
    # Orientation de la facade, utile pour les apports solaires et les ponts thermiques par
    # facade. Reste null en V1 : l'heuristique plan -> volume agrege tout le perimetre d'une
    # piece en une seule paroi "exterior" (pas de segmentation par facade). Pret pour le calcul
    # automatique (cf app/shared/geo.py) des que la vectorisation par facade sera disponible (V2).
    azimuth_deg: float | None = None  # angle 0-360 depuis le Nord, sens horaire
    cardinal_orientation: CardinalDirection | None = None


class SolarInstallation(CamelModel):
    """
    Installation photovoltaique/solaire thermique existante, detectee sur l'image aerienne
    et/ou les photos exterieures (cf app/vision_analysis) ou saisie manuellement. Alimente le
    bilan energetique (production existante) et se relie au point d'integration PVGIS prevu en
    V2 pour le potentiel solaire (cf app/climate).
    """

    id: str = Field(default_factory=lambda: f"solar_{uuid4().hex[:8]}")
    source: Literal["vision_estimate", "user_input"] = "user_input"
    area_m2: float | None = None  # surface approximative des panneaux
    tilt_deg: float | None = None  # inclinaison estimee par rapport a l'horizontale
    cardinal_orientation: CardinalDirection | None = None  # reutilise l'orientation de facade/versant
    estimated_capacity_kwp: float | None = None
    roof_wall_id: str | None = None  # paroi (kind="roof") sur laquelle l'installation est situee, si connue


class Equipment(CamelModel):
    """Equipement visible/declare (chauffage, ventilation, ECS...)."""

    id: str = Field(default_factory=lambda: f"equipment_{uuid4().hex[:8]}")
    type: Literal["heating", "ventilation", "hot_water", "other"] = "other"
    label: str
    source: Literal["vision_estimate", "user_input"] = "user_input"


class RoomBoundingBox(CamelModel):
    """Position/emprise 2D + hauteur sous plafond, issues de l'heuristique plan -> volume."""

    x: float
    y: float
    width_m: float
    depth_m: float
    height_m: float = 2.5


class Room(CamelModel):
    id: str = Field(default_factory=lambda: f"room_{uuid4().hex[:8]}")
    floor_id: str
    name: str  # nom retenu, editable par l'utilisateur
    suggested_name: str | None = None  # suggestion IA (OCR plan + analyse photos), non ecrasee
    name_confirmed: bool = False
    room_type: str | None = None  # kitchen, bedroom, living_room, bathroom, other...
    bounding_box: RoomBoundingBox
    walls: list[Wall] = Field(default_factory=list)
    equipment: list[Equipment] = Field(default_factory=list)
    photo_ids: list[str] = Field(default_factory=list)


class Floor(CamelModel):
    id: str = Field(default_factory=lambda: f"floor_{uuid4().hex[:8]}")
    name: str  # "RDC", "Etage 1", "Combles", "Sous-sol"...
    level: int = 0  # 0 = RDC, 1 = etage 1, -1 = sous-sol...
    plan_id: str | None = None  # plan 2D source de la generation
    rooms: list[Room] = Field(default_factory=list)


class BuildingModel(CamelModel):
    project_id: str
    name: str = "Batiment"
    address: str | None = None
    aerial_image_id: str | None = None
    floors: list[Floor] = Field(default_factory=list)
    generated_at: str | None = None
    glb_url: str | None = None  # export 3D (boites simplifiees) genere pour le viewer Three.js
    solar_installations: list[SolarInstallation] = Field(default_factory=list)

    # Classe d'inertie thermique simplifiee (leger/moyen/lourd), calculee automatiquement a partir
    # des materiaux/typologies des parois exposees (cf app/thermal_engine/inertia.py) a chaque
    # calcul du rapport thermique. Null tant qu'aucun rapport n'a ete calcule. Seul facteur norme
    # (parois) - INTACT, jamais modifie par le mobilier.
    thermal_inertia_class: ThermalInertiaClass | None = None

    # Masse thermique complementaire (mobilier/elements massifs : cheminee en pierre, poele de
    # masse, chape beton apparente...), issue du questionnaire et/ou de l'analyse vision des
    # photos. Indicateur QUALITATIF de confort d'ete / risque de surchauffe en approche
    # bioclimatique (la masse interieure amortit reellement les variations de temperature) - PAS
    # un facteur de conformite reglementaire (RE2020/RT ne comptabilisent que les parois dans
    # thermal_inertia_class). Affiche a cote, jamais fusionne ni utilise pour ajuster ce dernier.
    additional_thermal_mass_estimate: AdditionalThermalMassLevel | None = None

    # --- Geolocalisation (cf app/geolocation) ---
    latitude: float | None = None
    longitude: float | None = None
    altitude_m: float | None = None  # elevation du terrain, via Open-Meteo Elevation API

    # Rotation du Nord reel par rapport au "haut" du plan/modele (degres, sens horaire).
    # Par defaut alignee sur le Nord de l'image aerienne quand elle est fournie en Nord-up
    # standard (cas general imagerie satellite/IGN) ; ajustable via le widget compas frontend.
    north_offset_deg: float = 0.0
