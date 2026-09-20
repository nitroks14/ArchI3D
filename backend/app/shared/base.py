"""
Base Pydantic commune : serialise/parse le JSON en camelCase cote API tout en gardant du
snake_case idiomatique cote code Python. Evite d'avoir a ecrire des mappers manuels dans
chaque module et garde le contrat HTTP coherent avec les types TypeScript du frontend
(src/domain/model/*.ts).
"""
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
