from pydantic import BaseModel


#############
#
#  Excecute Script Model
#


class ValueResult(BaseModel):
    type: str
    value: str | None


class MiddleResult(BaseModel):
    result: ValueResult


class ExecuteScriptResult(BaseModel):
    id: int
    result: MiddleResult


#################
#
# JWT payload
#


class JWTPayload(BaseModel):
    sub: str
    exp: int
