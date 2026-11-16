(() => {
  "use strict";

  // Seleção editorial: cada missão usa uma coleção existente no Supabase.
  const missions = [
  {
    "id": "landsat",
    "name": "Landsat",
    "description": "Décadas de imagens para acompanhar florestas, cidades e mudanças na paisagem.",
    "conceptId": "C3604193990-ORNL_CLOUD",
    "area": "Manguezais no sudeste da Ásia",
    "color": "#286f8c"
  },
  {
    "id": "terra",
    "name": "Terra",
    "description": "Observa a relação entre atmosfera, solo, oceanos e energia do planeta.",
    "conceptId": "C2170972734-ORNL_CLOUD",
    "area": "Vegetação no Alasca",
    "color": "#4c8c95"
  },
  {
    "id": "aqua",
    "name": "Aqua",
    "description": "Investiga água, nuvens, gelo e outras peças do ciclo hídrico global.",
    "conceptId": "C2227456123-CEOS_EXTRA",
    "area": "Imagens MODIS sobre o Brasil",
    "color": "#2a789b"
  },
  {
    "id": "gpm",
    "name": "GPM",
    "description": "Reúne observações de satélites para estudar a precipitação na Terra.",
    "conceptId": "C2647820404-GHRC_DAAC",
    "area": "Precipitação no Atlântico e Caribe",
    "color": "#327f78"
  },
  {
    "id": "icesat",
    "name": "ICESat-2",
    "description": "Mede a altura de gelo, oceanos e superfícies com pulsos de laser.",
    "conceptId": "C3206495206-NSIDC_CPRD",
    "area": "Lagoas de degelo no Ártico",
    "color": "#5a8799"
  },
  {
    "id": "grace",
    "name": "GRACE-FO",
    "description": "Acompanha variações da gravidade ligadas ao movimento da água.",
    "conceptId": "C1993409520-GES_DISC",
    "area": "Água subterrânea nos Estados Unidos",
    "color": "#4c7890"
  }
];
  const byId = new Map(missions.map((mission) => [mission.id, mission]));
  const cards = [...document.querySelectorAll("[data-mission-card]")];
  const buttons = [...document.querySelectorAll("[data-focus-mission]")];
  const globeElement = document.getElementById("mission-globe");
  const globeSection = document.querySelector(".globe-section");
  const statusElement = document.getElementById("globe-status");
  const missionName = document.getElementById("globe-mission-name");
  const missionDescription = document.getElementById("globe-mission-description");
  const collectionTitle = document.getElementById("globe-collection-title");
  const areaElement = document.getElementById("globe-area");
  const cmrLink = document.getElementById("globe-cmr-link");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let selected = "landsat";
  let featured = [];
  let globe = null;
  let globeLoading = null;
  let globeUnavailable = false;

  function parseBox(rawData) {
    const boxes = rawData && Array.isArray(rawData.boxes) ? rawData.boxes : [];
    for (const value of boxes) {
      if (typeof value !== "string") continue;
      // CMR Atom JSON usa sul, oeste, norte, leste em cada caixa.
      const parts = value.trim().split(/\s+/).map(Number);
      if (parts.length !== 4 || parts.some((number) => !Number.isFinite(number))) continue;
      const [south, west, north, east] = parts;
      if (south < -90 || north > 90 || west < -180 || east > 180) continue;
      if (north <= south || east <= west || east - west >= 180) continue;
      return { south, west, north, east };
    }
    return null;
  }

  function polygonFor(box) {
    return {
      type: "Polygon",
      coordinates: [[
        [box.west, box.south], [box.east, box.south],
        [box.east, box.north], [box.west, box.north],
        [box.west, box.south]
      ]]
    };
  }

  function updateDetails() {
    const mission = byId.get(selected);
    const item = featured.find((entry) => entry.id === selected);
    missionName.textContent = mission.name;
    missionDescription.textContent = mission.description;
    collectionTitle.textContent = item ? item.title : "Coleção indisponível no momento";
    areaElement.textContent = mission.area;
    cmrLink.href = "https://cmr.earthdata.nasa.gov/search/concepts/" + encodeURIComponent(mission.conceptId);
    cards.forEach((card) => card.classList.toggle("is-active", card.dataset.missionCard === selected));
    buttons.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.focusMission === selected)));
  }

  function updateLayers() {
    if (!globe) return;
    const areas = featured.map((entry) => ({
      id: entry.id,
      name: entry.name,
      color: entry.color,
      box: entry.box,
      geometry: polygonFor(entry.box),
      lat: (entry.box.south + entry.box.north) / 2,
      lng: (entry.box.west + entry.box.east) / 2
    }));
    globe
      .polygonsData(areas)
      .polygonGeoJsonGeometry("geometry")
      .polygonCapColor((area) => area.id === selected ? "rgba(27, 106, 139, 0.42)" : "rgba(55, 129, 135, 0.18)")
      .polygonSideColor(() => "rgba(24, 88, 106, 0.12)")
      .polygonStrokeColor((area) => area.id === selected ? "#124e68" : "#5d9ba6")
      .polygonAltitude((area) => area.id === selected ? 0.014 : 0.007)
      .polygonLabel((area) => area.name + " · cobertura da coleção")
      .onPolygonClick((area) => selectMission(area.id, false));
    globe
      .pointsData(areas)
      .pointLat("lat")
      .pointLng("lng")
      .pointColor((area) => area.id === selected ? "#123f59" : area.color)
      .pointRadius((area) => area.id === selected ? 0.85 : 0.55)
      .pointAltitude(0.025)
      .pointLabel((area) => area.name + " · " + byId.get(area.id).area)
      .onPointClick((area) => selectMission(area.id, false));
  }

  function selectMission(id, scrollToMap) {
    if (!byId.has(id)) return;
    selected = id;
    updateDetails();
    updateLayers();
    const item = featured.find((entry) => entry.id === id);
    if (globe && item) {
      globe.pointOfView({
        lat: (item.box.south + item.box.north) / 2,
        lng: (item.box.west + item.box.east) / 2,
        altitude: 1.7
      }, reducedMotion ? 0 : 900);
    }
    if (scrollToMap) {
      globeSection.scrollIntoView({ behavior: reducedMotion ? "instant" : "smooth", block: "start" });
      ensureGlobe();
    }
  }

  async function loadFeatured() {
    try {
      const params = new URLSearchParams();
      params.set("select", "cmr_id,title,raw_data");
      params.set("cmr_id", "in.(" + missions.map((mission) => mission.conceptId).join(",") + ")");
      const response = await fetch(SUPABASE_URL + "/rest/v1/colecoes?" + params.toString(), {
        headers: { apikey: SUPABASE_KEY }
      });
      if (!response.ok) throw new Error("Supabase respondeu " + response.status);
      const rows = await response.json();
      if (!Array.isArray(rows)) throw new Error("Resposta inesperada do Supabase");
      const records = new Map(rows.map((row) => [row.cmr_id, row]));
      featured = missions.map((mission) => {
        const record = records.get(mission.conceptId);
        const box = record && parseBox(record.raw_data);
        return record && box ? { ...mission, title: record.title || mission.name, box } : null;
      }).filter(Boolean);
      updateDetails();
      updateLayers();
      if (!globeUnavailable) {
        statusElement.textContent = featured.length
          ? featured.length + " áreas do CMR · arraste para girar"
          : "Nenhuma área geográfica disponível agora.";
      }
    } catch (error) {
      statusElement.textContent = "Não foi possível carregar as áreas do Supabase.";
      collectionTitle.textContent = "Consulte a coleção pelo link abaixo.";
      console.warn("Falha ao consultar coleções em destaque:", error);
    }
  }

  function loadGlobeLibrary() {
    if (window.Globe) return Promise.resolve();
    if (globeLoading) return globeLoading;
    globeLoading = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "https://cdn.jsdelivr.net/npm/globe.gl@2.46.2/dist/globe.gl.min.js";
      script.async = true;
      script.onload = () => window.Globe ? resolve() : reject(new Error("Globe não inicializou"));
      script.onerror = () => reject(new Error("Não foi possível carregar o globo"));
      document.head.append(script);
    });
    return globeLoading;
  }

  async function ensureGlobe() {
    if (globe) return;
    try {
      const probe = document.createElement("canvas");
      if (!probe.getContext("webgl2") && !probe.getContext("webgl")) {
        throw new Error("WebGL indisponível");
      }
      await loadGlobeLibrary();
      if (globe) return;
      globe = new Globe(globeElement, { animateIn: !reducedMotion })
        .width(globeElement.clientWidth)
        .height(globeElement.clientHeight)
        .globeImageUrl("https://unpkg.com/three-globe@2.27.4/example/img/earth-blue-marble.jpg")
        .backgroundColor("#deebed")
        .showAtmosphere(true)
        .atmosphereColor("#9bcdd6")
        .atmosphereAltitude(0.16);
      globe.controls().autoRotate = false;
      globeElement.parentElement.classList.add("has-webgl");
      updateLayers();
      selectMission(selected, false);
      if ("ResizeObserver" in window) {
        new ResizeObserver(() => {
          if (globe && globeElement.clientWidth && globeElement.clientHeight) {
            globe.width(globeElement.clientWidth).height(globeElement.clientHeight);
          }
        }).observe(globeElement);
      }
      if (featured.length) statusElement.textContent = featured.length + " áreas do CMR · arraste para girar";
    } catch (error) {
      globeUnavailable = true;
      statusElement.textContent = "Globo 3D indisponível neste navegador. Os links das coleções continuam acessíveis.";
      console.warn("Falha ao iniciar o globo:", error);
    }
  }

  buttons.forEach((button) => button.addEventListener("click", () => {
    selectMission(button.dataset.focusMission, true);
  }));
  updateDetails();
  loadFeatured();
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      if (entries.some((entry) => entry.isIntersecting)) {
        observer.disconnect();
        ensureGlobe();
      }
    }, { rootMargin: "250px" });
    observer.observe(globeSection);
  } else {
    ensureGlobe();
  }
})();
