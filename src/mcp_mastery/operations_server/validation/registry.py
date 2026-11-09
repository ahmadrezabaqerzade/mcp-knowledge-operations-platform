from pydantic import BaseModel

from mcp_mastery.operations_server.validation.models import UserProfile

SCHEMA_REGISTRY: dict[str, type[BaseModel]] = {
    "user_profile": UserProfile,
}
