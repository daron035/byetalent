from pydantic import BaseModel, Field


class CreateDepartmentRequest(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=200,
    )

    parent_id: int | None = None


class DepartmentUpdatePatch(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    parent_id: int | None = Field(None)
