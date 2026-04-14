import os
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field, ConfigDict
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated
from dotenv import load_dotenv

from bson import ObjectId
from pymongo import AsyncMongoClient, ReturnDocument

# ------------------------------------------------------------------------ #
#                         Inicialització de l'aplicació                    #
# ------------------------------------------------------------------------ #

load_dotenv()

app = FastAPI(
    title="Movies Manager API",
    summary="API REST amb FastAPI i MongoDB per gestionar pel·lícules",
)

# ------------------------------------------------------------------------ #
#                   Configuració de la connexió amb MongoDB                #
# ------------------------------------------------------------------------ #

mongodb_url = os.environ.get("MONGODB_URL")
if not mongodb_url:
    raise ValueError("No s'ha trobat la variable d'entorn MONGODB_URL")

client = AsyncMongoClient(mongodb_url)
db = client.movies_db
movies_collection = db.get_collection("movies")

# MongoDB usa ObjectId a _id; aquí el tractem com string per l'API
PyObjectId = Annotated[str, BeforeValidator(str)]

# ------------------------------------------------------------------------ #
#                            Funcions auxiliars                            #
# ------------------------------------------------------------------------ #

def movie_helper(movie: dict) -> dict:
    return {
        "_id": str(movie["_id"]),
        "title": movie["title"],
        "description": movie["description"],
        "status": movie["status"],
        "rating": movie["rating"],
        "genre": movie["genre"],
        "user": movie["user"],
    }


def validate_status(status_value: str) -> str:
    valid_statuses = ["pendent de veure", "vista"]
    if status_value not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Status no vàlid. Valors permesos: {valid_statuses}"
        )
    return status_value


# ------------------------------------------------------------------------ #
#                            Definició dels models                         #
# ------------------------------------------------------------------------ #

class MovieModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    status: str = Field(..., min_length=1)
    rating: int = Field(..., ge=1, le=5)
    genre: str = Field(..., min_length=1)
    user: str = Field(..., min_length=1)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "title": "Inception",
                "description": "Pel·lícula de ciència-ficció sobre somnis",
                "status": "pendent de veure",
                "rating": 5,
                "genre": "ciència-ficció",
                "user": "Ferran"
            }
        },
    )


class UpdateMovieModel(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = Field(default=None, min_length=1)
    status: Optional[str] = Field(default=None, min_length=1)
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    genre: Optional[str] = Field(default=None, min_length=1)
    user: Optional[str] = Field(default=None, min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Interstellar",
                "description": "Pel·lícula sobre viatges espacials",
                "status": "vista",
                "rating": 4,
                "genre": "ciència-ficció",
                "user": "Ferran"
            }
        }
    )


class UpdateStatusModel(BaseModel):
    status: str = Field(..., min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "vista"
            }
        }
    )

# ------------------------------------------------------------------------ #
#                          Endpoint de comprovació                         #
# ------------------------------------------------------------------------ #

@app.get("/")
async def root():
    return {"message": "API del gestor de pel·lícules funcionant correctament"}

# ------------------------------------------------------------------------ #
#                              CREATE - POST                               #
# ------------------------------------------------------------------------ #

@app.post("/movies", response_model=MovieModel, status_code=status.HTTP_201_CREATED)
async def create_movie(movie: MovieModel):
    validate_status(movie.status)

    movie_dict = movie.model_dump(by_alias=True, exclude=["id"])
    result = await movies_collection.insert_one(movie_dict)
    created_movie = await movies_collection.find_one({"_id": result.inserted_id})

    if created_movie is None:
        raise HTTPException(
            status_code=500,
            detail="No s'ha pogut crear la pel·lícula"
        )

    return movie_helper(created_movie)

# ------------------------------------------------------------------------ #
#                         READ - GET ALL + FILTRES                         #
# ------------------------------------------------------------------------ #

@app.get("/movies", response_model=List[MovieModel])
async def get_movies(
    genre: Optional[str] = Query(default=None),
    rating: Optional[int] = Query(default=None, ge=1, le=5),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    user: Optional[str] = Query(default=None)
):
    query = {}

    if genre:
        query["genre"] = genre
    if rating is not None:
        query["rating"] = rating
    if status_filter:
        validate_status(status_filter)
        query["status"] = status_filter
    if user:
        query["user"] = user

    movies = []
    async for movie in movies_collection.find(query):
        movies.append(movie_helper(movie))

    return movies

# ------------------------------------------------------------------------ #
#                             READ - GET BY ID                             #
# ------------------------------------------------------------------------ #

@app.get("/movies/{id}", response_model=MovieModel)
async def get_movie(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID no vàlid")

    movie = await movies_collection.find_one({"_id": ObjectId(id)})

    if movie is None:
        raise HTTPException(status_code=404, detail="Pel·lícula no trobada")

    return movie_helper(movie)

# ------------------------------------------------------------------------ #
#                              UPDATE - PUT                                #
# ------------------------------------------------------------------------ #

@app.put("/movies/{id}", response_model=MovieModel)
async def update_movie(id: str, movie: UpdateMovieModel):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID no vàlid")

    movie_data = {k: v for k, v in movie.model_dump().items() if v is not None}

    if len(movie_data) == 0:
        raise HTTPException(
            status_code=400,
            detail="No hi ha dades per actualitzar"
        )

    if "status" in movie_data:
        validate_status(movie_data["status"])

    updated_movie = await movies_collection.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": movie_data},
        return_document=ReturnDocument.AFTER
    )

    if updated_movie is None:
        raise HTTPException(status_code=404, detail="Pel·lícula no trobada")

    return movie_helper(updated_movie)

# ------------------------------------------------------------------------ #
#                        UPDATE - PATCH NOMÉS STATUS                       #
# ------------------------------------------------------------------------ #

@app.patch("/movies/{id}/status", response_model=MovieModel)
async def update_movie_status(id: str, status_data: UpdateStatusModel):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID no vàlid")

    validate_status(status_data.status)

    updated_movie = await movies_collection.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": {"status": status_data.status}},
        return_document=ReturnDocument.AFTER
    )

    if updated_movie is None:
        raise HTTPException(status_code=404, detail="Pel·lícula no trobada")

    return movie_helper(updated_movie)

# ------------------------------------------------------------------------ #
#                             DELETE - DELETE                              #
# ------------------------------------------------------------------------ #

@app.delete("/movies/{id}")
async def delete_movie(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID no vàlid")

    deleted_movie = await movies_collection.delete_one({"_id": ObjectId(id)})

    if deleted_movie.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Pel·lícula no trobada")

    return {"message": "Pel·lícula eliminada correctament"}