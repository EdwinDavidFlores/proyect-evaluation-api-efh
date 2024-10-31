from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class Usuarios(BaseModel):
    id: str = Field(..., example='p1')
    nombre: str= Field(..., example='Juan')
    email: EmailStr = Field(..., example='juan.perez@example.com')
    edad: int = Field(..., example=25)


class Proyectos(BaseModel):
    id: str = Field(..., example='e1')
    nombre: str = Field(..., example='Machine Learning EFH 2024')
    descripcion: Optional[str] = Field(None, example='Poyecto de Machine Learning enfocado al aprendizaje de nuevas tecnologias')
    id_usuario: List[Usuarios] = Field(default_factory=list)
    fecha_creacion: str = Field(..., example='2024-10-23T19:00:00Z')

