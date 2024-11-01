from fastapi import FastAPI, HTTPException, Query, Path
from typing import List, Optional
from database import container
from models import Proyectos, Usuarios
from azure.cosmos import exceptions
from datetime import datetime

app = FastAPI(title='API de Gestion Proyectos')

#### Endpoint de Proyectos

@app.get("/")
def home():
    return "Hola Mundo proyecto"

# Crear proyecto

@app.post("/proyects/", response_model=Proyectos, status_code=201)
def create_proyect(proy: Proyectos):
    try:
        container.create_item(body=proy.dict())
        return proy
    except exceptions.CosmosResourceExistsError:
        raise HTTPException(status_code=400, detail="El evento con este ID ya existe.")
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# Obtener proyecto
@app.get("/proyects/{proyect_id}", response_model=Proyectos)
def get_proyect(proyect_id: str = Path(..., description="ID del proyecto a recuperar")):
    try:
        proy = container.read_item(item=proyect_id, partition_key=proyect_id)
        return proy
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

# Listar Proyectos

@app.get("/proyects/", response_model=List[Proyectos])
def list_proyect():
    
    query = "SELECT * FROM c WHERE 1=1"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    return items

# Actualizar Proyectos

@app.put("/proyects/{proyect_id}", response_model=Proyectos)
def update_proyect(proyect_id: str, update_proyect: Proyectos):

    try:
        existing_proy = container.read_item(item=proyect_id, partition_key=proyect_id)
        
        print(update_proyect.dict(exclude_unset=True))
        # Actualizar campos
        existing_proy.update(update_proyect.dict(exclude_unset=True))
        
        print(existing_proy)
        # Validar capacidad
       # if existing_proy['capacity'] < len(existing_proy['usuarios']):
       #     raise HTTPException(status_code=400, detail="La capacidad no puede ser menor que el número de participantes actuales.")
        
        container.replace_item(item=existing_proy, body=existing_proy)
        return existing_proy
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

# Eliminar proyecto

@app.delete("/proyects/{proyect_id}", status_code=204)
def delete_proyect(proyect_id: str):
    try:
        container.delete_item(item=proyect_id, partition_key=proyect_id)
        return
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail='Evento no encotrado')
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))


#### Endpoints de Usuarios

#Crear_usuario

@app.post("/proyects/{proyect_id}/users/", response_model=Usuarios, status_code=201)
def add_user(proyect_id: str, pr_usuario: Usuarios):

    # validar si el Usuario ya existe

    try:
        
        proy = container.read_item(item=proyect_id, partition_key=proyect_id)

        if any( p['id'] == pr_usuario.id for p in proy['id_usuario'] ):
             raise HTTPException(status_code=400, detail='El usario con este Id ya esta inscrito')

        proy['id_usuario'].append(pr_usuario.dict())

        container.replace_item(item=proyect_id, body=proy)

        return pr_usuario
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail='Proyecto no encontrado')
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))

#Obtener_usuario

@app.get("/proyects/{proyect_id}/users/{user_id}")
def get_user(proyect_id: str, user_id: str):

    try:
        proy = container.read_item(item=proyect_id, partition_key=proyect_id)
        
        user_id = next((p for p in  proy['id_usuario'] if p['id'] == user_id), None)

        if user_id:
            return user_id
        else:
            raise HTTPException(status_code=404, detail='Usuario no encontrado')
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail='Proyecto no encontrado')
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))

#Listar_usuario

@app.get("/proyects/{proyect_id}/users/", response_model=List[Usuarios])
def list_user(proyect_id: str):
    
    try:
        proy = container.read_item(item=proyect_id, partition_key= proyect_id)
        ## event['participants'] // event.get('parcitipants')
        user_id = proy.get('id_usuario', [])

        return user_id
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail='Proyecto no encontrado')
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))

#Actualizar_usuario

@app.put("/proyects/{proyect_id}/users/{user_id}", response_model=Usuarios)
def update_user(proyect_id: str, user_id: str, updated_user: Usuarios):

    try:
        proy = container.read_item(item=proyect_id, partition_key=proyect_id)
        user = next((p for p in proy['id_usuario'] if p['id'] == user_id), None)

        if not user:
            raise HTTPException(status_code=404, detail= "Usuario no encontrado")
        
        if user['id'] != updated_user.id :
            raise HTTPException(status_code=404, detail= "el id enviado en la peticion debe ser igual al id del body")

        user.update(updated_user.dict(exclude_unset=True))

      
        proy['id_usuario'] = [ p if p['id'] != user_id else user for p in proy['id_usuario']]

        container.replace_item(item=proyect_id, body=proy)

        return user

    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail='Proyecto no encotrado')
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))

 #Eliminar_usuario 

@app.delete("/proyects/{proyect_id}/users/{user_id}", status_code=204)
def delete_user(proyect_id: str, user_id: str):

    try:

        proy = container.read_item(item=proyect_id, partition_key=proyect_id)
        user = next((p for p in proy['id_usuario'] if p['id'] == user_id), None)

        if not user:
            raise HTTPException(status_code=404, detail='Usuario no encontrado')
        
        proy['id_usuario']  = [ p for p in proy['id_usuario'] if p['id'] != user_id]

        container.replace_item(item=proyect_id, body=proy)
        return
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail='Proyecto no encotrado')
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=str(e))
