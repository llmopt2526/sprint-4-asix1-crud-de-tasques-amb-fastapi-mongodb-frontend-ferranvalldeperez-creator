const API_URL = "http://127.0.0.1:8000";

const movieForm = document.getElementById("movie-form");
const movieIdInput = document.getElementById("movie-id");
const titleInput = document.getElementById("title");
const descriptionInput = document.getElementById("description");
const statusInput = document.getElementById("status");
const ratingInput = document.getElementById("rating");
const genreInput = document.getElementById("genre");
const userInput = document.getElementById("user");

const formTitle = document.getElementById("form-title");
const cancelEditBtn = document.getElementById("cancel-edit-btn");
const moviesList = document.getElementById("movies-list");

const filterGenre = document.getElementById("filter-genre");
const filterRating = document.getElementById("filter-rating");
const filterStatus = document.getElementById("filter-status");
const filterUser = document.getElementById("filter-user");
const applyFiltersBtn = document.getElementById("apply-filters-btn");
const clearFiltersBtn = document.getElementById("clear-filters-btn");

document.addEventListener("DOMContentLoaded", () => {
  loadMovies();

  movieForm.addEventListener("submit", handleFormSubmit);
  cancelEditBtn.addEventListener("click", resetForm);
  applyFiltersBtn.addEventListener("click", loadMovies);
  clearFiltersBtn.addEventListener("click", clearFilters);
});

async function loadMovies() {
  try {
    const queryParams = new URLSearchParams();

    if (filterGenre.value.trim()) {
      queryParams.append("genre", filterGenre.value.trim());
    }

    if (filterRating.value.trim()) {
      queryParams.append("rating", filterRating.value.trim());
    }

    if (filterStatus.value.trim()) {
      queryParams.append("status", filterStatus.value.trim());
    }

    if (filterUser.value.trim()) {
      queryParams.append("user", filterUser.value.trim());
    }

    const url = queryParams.toString()
      ? `${API_URL}/movies?${queryParams.toString()}`
      : `${API_URL}/movies`;

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error("No s'han pogut carregar les pel·lícules");
    }

    const movies = await response.json();
    renderMovies(movies);
  } catch (error) {
    moviesList.innerHTML = `<p>Error: ${error.message}</p>`;
  }
}

function renderMovies(movies) {
  if (movies.length === 0) {
    moviesList.innerHTML = "<p>No hi ha pel·lícules per mostrar.</p>";
    return;
  }

  moviesList.innerHTML = movies.map(movie => `
    <div class="movie-card">
      <h3>${escapeHtml(movie.title)}</h3>
      <p>${escapeHtml(movie.description)}</p>

      <div class="movie-meta"><strong>Estat:</strong> ${escapeHtml(movie.status)}</div>
      <div class="movie-meta"><strong>Puntuació:</strong> ${movie.rating}</div>
      <div class="movie-meta"><strong>Gènere:</strong> ${escapeHtml(movie.genre)}</div>
      <div class="movie-meta"><strong>Usuari:</strong> ${escapeHtml(movie.user)}</div>

      <div class="movie-actions">
        <button onclick="editMovie('${movie._id}')">Editar</button>
        <button onclick="toggleStatus('${movie._id}', '${movie.status}')" class="button button-outline">
          Canviar estat
        </button>
        <button onclick="deleteMovie('${movie._id}')" class="button button-outline">
          Eliminar
        </button>
      </div>
    </div>
  `).join("");
}

async function handleFormSubmit(event) {
  event.preventDefault();

  const movieData = {
    title: titleInput.value.trim(),
    description: descriptionInput.value.trim(),
    status: statusInput.value,
    rating: Number(ratingInput.value),
    genre: genreInput.value.trim(),
    user: userInput.value.trim()
  };

  if (
    !movieData.title ||
    !movieData.description ||
    !movieData.status ||
    !movieData.rating ||
    !movieData.genre ||
    !movieData.user
  ) {
    alert("Has d'omplir tots els camps.");
    return;
  }

  try {
    let response;
    const movieId = movieIdInput.value;

    if (movieId) {
      response = await fetch(`${API_URL}/movies/${movieId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(movieData)
      });
    } else {
      response = await fetch(`${API_URL}/movies`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(movieData)
      });
    }

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Error en guardar la pel·lícula");
    }

    resetForm();
    loadMovies();
  } catch (error) {
    alert(error.message);
  }
}

async function editMovie(id) {
  try {
    const response = await fetch(`${API_URL}/movies/${id}`);

    if (!response.ok) {
      throw new Error("No s'ha pogut carregar la pel·lícula");
    }

    const movie = await response.json();

    movieIdInput.value = movie._id;
    titleInput.value = movie.title;
    descriptionInput.value = movie.description;
    statusInput.value = movie.status;
    ratingInput.value = movie.rating;
    genreInput.value = movie.genre;
    userInput.value = movie.user;

    formTitle.textContent = "Editar pel·lícula";
    cancelEditBtn.classList.remove("hidden");
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (error) {
    alert(error.message);
  }
}

async function toggleStatus(id, currentStatus) {
  const newStatus = currentStatus === "vista" ? "pendent de veure" : "vista";

  try {
    const response = await fetch(`${API_URL}/movies/${id}/status`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ status: newStatus })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "No s'ha pogut canviar l'estat");
    }

    loadMovies();
  } catch (error) {
    alert(error.message);
  }
}

async function deleteMovie(id) {
  const confirmDelete = confirm("Segur que vols eliminar aquesta pel·lícula?");
  if (!confirmDelete) {
    return;
  }

  try {
    const response = await fetch(`${API_URL}/movies/${id}`, {
      method: "DELETE"
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "No s'ha pogut eliminar la pel·lícula");
    }

    loadMovies();
  } catch (error) {
    alert(error.message);
  }
}

function resetForm() {
  movieForm.reset();
  movieIdInput.value = "";
  formTitle.textContent = "Afegir pel·lícula";
  cancelEditBtn.classList.add("hidden");
}

function clearFilters() {
  filterGenre.value = "";
  filterRating.value = "";
  filterStatus.value = "";
  filterUser.value = "";
  loadMovies();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}