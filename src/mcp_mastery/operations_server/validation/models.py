from pydantic import BaseModel, ConfigDict, Field


class UserProfile(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    username: str = Field(
        description="Unique username identifying the user.",
        min_length=3,
        max_length=30,
    )
    age: int = Field(
        description="User's age in years. Must be between 18 and 120.",
        ge=18,
        le=120,
    )
    is_active: bool = Field(
        description="Indicates whether the user account is currently active."
    )
