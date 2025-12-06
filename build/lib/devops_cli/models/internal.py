from pydantic import BaseModel, Field
from typing import Optional, List

class GenerationRequest(BaseModel):
    prompt: str
    environment: str = "dev"
    namespace: str = "default"
    replicas: int = 1
    expose: bool = False
    expose_type: str = "ClusterIP"

class ValidationResult(BaseModel):
    valid: bool
    errors: List[str] = Field(default_factory=list)
    resource_count: int = 0
    files_generated: List[str] = Field(default_factory=list)
