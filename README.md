[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/ULL36zWV)
# Estructura del projecte top

Pel que fa al meu readme, explicaré els passos que he seguit per a dur a terme el projecte, des de l'inici amb el clone del repositori fins al pas final del frontend.

# Clonació del repositori

Fem un git clone del repositori i accedim a n'ell.
```
git clone https://github.com/llmopt2526/sprint-4-asix1-crud-de-tasques-amb-fastapi-mongodb-frontend-ferranvalldeperez-creator.git
```
```
cd sprint-4-asix1-crud-de-tasques-amb-fastapi-mongodb-frontend-ferranvalldeperez-creator
```

# Configuració del backend

## Accedir a la carpeta backend
```
cd backend
```

## Crear l'entorn visual

Fiquem aquesta comanda de pyton
```
python -m venv .venv
```
i l'activem
```
.venv\Scripts\activate
```

## Instal·lar dependències

Fiquem aquesta comanda per a instal·lar el fitxer requirements
```
pip install -r requirements.txt
```

## Configurar MongoDB Atlas

Aquí, creo un cluster a MongoDB Atlas amb la base de dades, en aquest cas el nom es movies_db i col·lecció movies.
Després afegim la IP actual o la 0.0.0.0/0 per a que el mongo Db es pugui conectar amb l'API

## Crear fitxer .env

Dins de la carpeta backend, creo un fitxer .env amb la url del mongo db
```
MONGODB_URL=mongodb+srv://ferran:1234@ferranv.szzdgaw.mongodb.net/movies_db?retryWrites=true&w=majority
```

## Executar el servidor
```
python -m uvicorn app:app --reload
```

## Comprovar funcionament

Obrim al navegador
http://127.0.0.1:8000/docs

## CRUD de l'API

Aquí creo els endpoints:

POST /movies → Crear pel·lícula
GET /movies → Llistar pel·lícules
GET /movies/{id} → Obtenir una pel·lícula
PUT /movies/{id} → Actualitzar
PATCH /movies/{id}/status → Canviar estat
DELETE /movies/{id} → Eliminar
<img width="910" height="757" alt="image" src="https://github.com/user-attachments/assets/ed429cc7-0414-413a-9fa7-72dbc7fc38ce" />

# Frontend

## Accedir a la carpeta frontend
```
cd ../frontend
```
## Executar servidor local
```
python -m http.server 5500
```
## Obrir al navegador
```
http://localhost:5500
```

## Connexió frontend-backend
El frontend es connecta a http://127.0.0.1:8000 i es necessari que el backend estigui en funcionament

# VIDEO FRONTEND


https://github.com/user-attachments/assets/4f26006c-1f79-45e5-8d4b-cd600822727a


















