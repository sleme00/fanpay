const films = [
  {
    id: "film-1",
    title: "Северный меридиан",
    year: 2024,
    genre: "Sci-Fi",
    rating: "8.7",
    duration: "2ч 18м",
    description:
      "Команда исследователей отправляется к далёкому меридиану, чтобы спасти колонию.",
    cast: ["Эмилия Орлова", "Максим Пак", "Леон Картер"],
    tags: ["Космос", "Триллер", "IMAX"],
  },
  {
    id: "film-2",
    title: "Мягкий рассвет",
    year: 2023,
    genre: "Драма",
    rating: "8.2",
    duration: "1ч 52м",
    description:
      "История дирижёра, который ищет потерянный концерт и себя самого.",
    cast: ["Екатерина Юн", "Роман Леви"],
    tags: ["Музыка", "Город"],
  },
  {
    id: "film-3",
    title: "Пульс мегаполиса",
    year: 2022,
    genre: "Боевик",
    rating: "7.9",
    duration: "2ч 02м",
    description:
      "Команда журналистов оказывается в эпицентре расследования о городской корпорации.",
    cast: ["Давид Ким", "Ариана Ли"],
    tags: ["Экшен", "Технологии"],
  },
  {
    id: "film-4",
    title: "Городские линии",
    year: 2021,
    genre: "Романтика",
    rating: "7.6",
    duration: "1ч 40м",
    description:
      "Два архитектора спорят о будущем города и находят любовь.",
    cast: ["Нора Кавалли", "Илья Орсо"],
    tags: ["Любовь", "Дизайн"],
  },
];

const actors = [
  {
    id: "actor-1",
    name: "Эмилия Орлова",
    speciality: "Научная фантастика",
    years: "12 лет в кино",
    knownFor: "Северный меридиан",
    description:
      "Известна глубокими образами героинь в футуристических сюжетах.",
    tags: ["Премии", "Режиссура"],
    filmography: ["Северный меридиан", "Эхо орбиты", "Парадокс"],
  },
  {
    id: "actor-2",
    name: "Максим Пак",
    speciality: "Триллеры",
    years: "9 лет в кино",
    knownFor: "Пульс мегаполиса",
    description:
      "Обожает сложные характеры и социальные драмы.",
    tags: ["Боевик", "Психология"],
    filmography: ["Пульс мегаполиса", "Багровый рейс"],
  },
  {
    id: "actor-3",
    name: "Екатерина Юн",
    speciality: "Музыкальные драмы",
    years: "15 лет в кино",
    knownFor: "Мягкий рассвет",
    description:
      "Сочетает вокал и актёрскую игру, часто участвует в музыкальных проектах.",
    tags: ["Музыка", "Сериалы"],
    filmography: ["Мягкий рассвет", "Звёздный квартет"],
  },
  {
    id: "actor-4",
    name: "Нора Кавалли",
    speciality: "Романтические истории",
    years: "7 лет в кино",
    knownFor: "Городские линии",
    description:
      "Играет героинь, которые вдохновляют и меняют окружающих.",
    tags: ["Fashion", "Indie"],
    filmography: ["Городские линии", "Небесный трамвай"],
  },
];

const state = {
  view: "films",
  activeId: null,
  search: "",
  genre: "",
};

const cards = document.getElementById("cards");
const details = document.getElementById("details");
const detailsMeta = document.getElementById("detailsMeta");
const searchInput = document.getElementById("search");
const genreSelect = document.getElementById("genre");

const viewButtons = document.querySelectorAll(".chip");

const uniqueGenres = Array.from(
  new Set(films.map((film) => film.genre).concat(actors.map((actor) => actor.speciality)))
);

uniqueGenres.forEach((item) => {
  const option = document.createElement("option");
  option.value = item;
  option.textContent = item;
  genreSelect.append(option);
});

function setActiveCard(id) {
  state.activeId = id;
  render();
}

function buildCard(item) {
  const card = document.createElement("article");
  card.className = "card";
  card.dataset.id = item.id;

  const title = document.createElement("h3");
  title.textContent = state.view === "films" ? item.title : item.name;

  const description = document.createElement("p");
  description.textContent = item.description;

  const meta = document.createElement("div");
  meta.className = "meta";

  const tags = state.view === "films" ? item.tags : item.tags;
  tags.forEach((tag) => {
    const badge = document.createElement("span");
    badge.className = "tag";
    badge.textContent = tag;
    meta.append(badge);
  });

  card.append(title, description, meta);

  if (state.activeId === item.id) {
    card.classList.add("active");
  }

  card.addEventListener("click", () => setActiveCard(item.id));

  return card;
}

function buildDetails(item) {
  if (!item) {
    details.querySelector("h3").textContent = "Выберите карточку";
    details.querySelector(".details-text").textContent =
      "Мы подготовили краткие досье, чтобы было проще выбрать фильм на вечер или узнать, где ещё снимался любимый актёр.";
    detailsMeta.innerHTML = "";
    return;
  }

  details.querySelector("h3").textContent =
    state.view === "films" ? item.title : item.name;
  details.querySelector(".details-text").textContent = item.description;
  detailsMeta.innerHTML = "";

  const info =
    state.view === "films"
      ? [
          ["Год", item.year],
          ["Жанр", item.genre],
          ["Длительность", item.duration],
          ["Рейтинг", item.rating],
          ["Актёры", item.cast.join(", ")],
        ]
      : [
          ["Специализация", item.speciality],
          ["Опыт", item.years],
          ["Известна по", item.knownFor],
          ["Фильмография", item.filmography.join(", ")],
        ];

  info.forEach(([label, value]) => {
    const row = document.createElement("p");
    row.innerHTML = `<span>${label}:</span> ${value}`;
    detailsMeta.append(row);
  });
}

function render() {
  cards.innerHTML = "";

  const data = state.view === "films" ? films : actors;
  const filtered = data.filter((item) => {
    const title = state.view === "films" ? item.title : item.name;
    const matchesSearch = title.toLowerCase().includes(state.search.toLowerCase());
    const category = state.view === "films" ? item.genre : item.speciality;
    const matchesGenre = !state.genre || category === state.genre;
    return matchesSearch && matchesGenre;
  });

  filtered.forEach((item) => {
    cards.append(buildCard(item));
  });

  buildDetails(filtered.find((item) => item.id === state.activeId));
}

viewButtons.forEach((button) => {
  button.addEventListener("click", () => {
    viewButtons.forEach((btn) => btn.classList.remove("active"));
    button.classList.add("active");
    state.view = button.dataset.view;
    state.activeId = null;
    state.genre = "";
    genreSelect.value = "";
    render();
  });
});

searchInput.addEventListener("input", (event) => {
  state.search = event.target.value;
  render();
});

genreSelect.addEventListener("change", (event) => {
  state.genre = event.target.value;
  render();
});

render();
