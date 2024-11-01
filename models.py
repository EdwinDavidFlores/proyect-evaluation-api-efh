from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class Usuarios(BaseModel):
    id: str = Field(..., example='u1')
    nombre: str= Field(..., example='Jesus')
    email: EmailStr = Field(..., example='jesus.velazques@example.com')
    edad: int = Field(..., example=25)


class Proyectos(BaseModel):
    id: str = Field(..., example='p1')
    nombre: str = Field(..., example='Big Data 2024')
    descripcion: Optional[str] = Field(None, example='Proyecto de Big Data enfocado al aprendizaje de nuevas tecnologias')
    id_usuario: List[Usuarios] = Field(default_factory=list)
    fecha_creacion: str = Field(..., example='2024-10-23T19:00:00Z')

