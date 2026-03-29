import { buildAlbumChartRows, buildSongChartRows } from "../shared/chartOverlay.js";
import {
  CONFIG as VIDEO_CONFIG,
  enrichMasterWithTrackVideos,
  loadVideoCache,
  normalizeVideoTrackKey,
  resolveTrackVideoSource,
} from "./videoResolver.js";

const DATA_URL = "../../data/master/retroverse_master.json";
const BOOTSTRAP_DATA_URL = "./bootstrap.json";
/** Hot 100 / BB200 issue to open on first load. */
const DEFAULT_CHART_DATE = "1975-08-03";
const LOADING_DATA_MESSAGE = "Loading chart data...";
const PIPELINE_API_BASE = "http://127.0.0.1:8787";
const YOUTUBE_RESOLVE_ENDPOINT = PIPELINE_API_BASE + "/api/youtube/resolve";
const WORKLIST_STORAGE_KEY = "retroverse_charts_worklists_v1";
const LEGACY_COLLECTION_STORAGE_KEY = "retroverse_charts_collection_v1";
const WORKLIST_REQUEST_TIMEOUT_MS = 90000;
const LAYOUT_BREAKPOINTS = {
  mobile: 768,
  tablet: 1080,
};
const MONTH_OPTIONS = [
  { value: "01", label: "Jan" },
  { value: "02", label: "Feb" },
  { value: "03", label: "Mar" },
  { value: "04", label: "Apr" },
  { value: "05", label: "May" },
  { value: "06", label: "Jun" },
  { value: "07", label: "Jul" },
  { value: "08", label: "Aug" },
  { value: "09", label: "Sep" },
  { value: "10", label: "Oct" },
  { value: "11", label: "Nov" },
  { value: "12", label: "Dec" },
];
/** @type {'charts' | 'editions'} */
let viewMode = "editions";

const MONTH_SEARCH_OPTIONS = [
  { value: "01", short: "jan", full: "january" },
  { value: "02", short: "feb", full: "february" },
  { value: "03", short: "mar", full: "march" },
  { value: "04", short: "apr", full: "april" },
  { value: "05", short: "may", full: "may" },
  { value: "06", short: "jun", full: "june" },
  { value: "07", short: "jul", full: "july" },
  { value: "08", short: "aug", full: "august" },
  { value: "09", short: "sep", full: "september" },
  { value: "10", short: "oct", full: "october" },
  { value: "11", short: "nov", full: "november" },
  { value: "12", short: "dec", full: "december" },
];

const el = {
  appHeader: document.querySelector(".app-header"),
  chartNavBar: document.querySelector(".chart-nav-bar"),
  queueMenuSlot: document.getElementById("queueMenuSlot"),
  chartTypeButtons: document.getElementById("chartTypeButtons"),
  trackModeToggle: document.getElementById("trackModeToggle"),
  selectorPanel: document.getElementById("selectorPanel"),
  chartSearchInput: document.getElementById("chartSearchInput"),
  chartSearchResults: document.getElementById("chartSearchResults"),
  chartNavPrev: document.getElementById("chartNavPrev"),
  chartNavNext: document.getElementById("chartNavNext"),
  chartNavLabel: document.getElementById("chartNavLabel"),
  contextKicker: document.getElementById("contextKicker"),
  contextTitle: document.getElementById("contextTitle"),
  contextMeta: document.getElementById("contextMeta"),
  trackStatus: document.getElementById("trackStatus"),
  panelState: document.getElementById("panelState"),
  featureStrip: document.getElementById("chartFeatureStrip"),
  chartTableWrap: document.getElementById("chartTableWrap"),
  chartEditionWrap: document.getElementById("chartEditionWrap"),
  viewCharts: document.getElementById("viewCharts"),
  viewEditions: document.getElementById("viewEditions"),
  chartMobileList: document.getElementById("chartMobileList"),
  chartHead: document.getElementById("chartHead"),
  chartBody: document.getElementById("chartBody"),
  detailPanelToolbar: document.getElementById("detailPanelToolbar"),
  detailSheet: document.getElementById("detailSheet"),
  detailSheetBackdrop: document.getElementById("detailSheetBackdrop"),
  detailSheetClose: document.getElementById("detailSheetClose"),
  detailSheetContent: document.getElementById("detailSheetContent"),
  videoModal: document.getElementById("videoModal"),
  videoModalBackdrop: document.getElementById("videoModalBackdrop"),
  videoModalClose: document.getElementById("videoModalClose"),
  videoModalTitle: document.getElementById("videoModalTitle"),
  videoModalMeta: document.getElementById("videoModalMeta"),
  videoModalPlayer: document.getElementById("videoModalPlayer"),
  videoModalFrame: document.getElementById("videoModalFrame"),
  videoModalFallback: document.getElementById("videoModalFallback"),
  videoModalPrev: document.getElementById("videoModalPrev"),
  videoModalNext: document.getElementById("videoModalNext"),
};

const state = {
  master: null,
  usingBootstrapData: false,
  bootstrapYear: "",
  fullMasterLoaded: false,
  fullMasterLoadPromise: null,
  songById: new Map(),
  songByTrackKey: new Map(),
  albumById: new Map(),
  videosBySongId: new Map(),
  songsByAlbumId: new Map(),
  videoCacheByTrackKey: new Map(),
  chartIndex: {
    songs: {},
    albums: {},
  },
  allDates: {
    songs: [],
    albums: [],
  },
  rowCache: {
    songs: new Map(),
    albums: new Map(),
  },
  chartSearchIndex: {
    songs: null,
    albums: null,
  },
  currentChartType: "songs",
  currentYear: "",
  currentMonth: "",
  currentDate: "",
  chartSearchQuery: "",
  selected: null,
  trackedSelectionKey: "",
  trackedSelectionLabel: "",
  trackedSelectionMissing: false,
  pendingSelectionScroll: false,
  trackMode: false,
  videoPlayerOpen: false,
  layoutMode: "desktop",
  detailSheetOpen: false,
  historyTimeline: "upto",
  queue: [],
  queueIndex: new Set(),
  acquire: [],
  acquireIndex: new Set(),
  worklistOpen: false,
  acquireBusy: false,
  acquireNotice: "",
  acquireNoticeTone: "",
  destinationMenu: {
    open: false,
    x: 0,
    y: 0,
    item: null,
  },
};

function toNumber(value) {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value === "string" && value.trim() !== "") {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) return parsed;
  }
  return null;
}

function normalizeChartDate(value) {
  return typeof value === "string" ? value.slice(0, 10) : "";
}

function esc(value) {
  return String(value == null ? "" : value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function safePublicUrl(value) {
  if (typeof value !== "string") return "";
  const url = value.trim();
  if (!url) return "";
  if (url.includes("/Users/")) return "";
  if (!/^https?:\/\//i.test(url)) return "";
  return url;
}

function normalizeChartSearchText(value) {
  return String(value == null ? "" : value)
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/&/g, " and ")
    .replace(/[^a-zA-Z0-9]+/g, " ")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, " ");
}

function normalizeYoutubeId(value) {
  const youtubeId = typeof value === "string" ? value.trim() : "";
  return /^[A-Za-z0-9_-]{6,}$/.test(youtubeId) ? youtubeId : "";
}

function storageHandle() {
  try {
    if (typeof window === "undefined" || !window.localStorage) return null;
    return window.localStorage;
  } catch (_error) {
    return null;
  }
}

function formatIssueDate(chartDate) {
  const normalized = normalizeChartDate(chartDate);
  if (!normalized) return "Unknown Issue";
  const parsed = new Date(normalized + "T00:00:00Z");
  if (Number.isNaN(parsed.getTime())) return normalized;
  return new Intl.DateTimeFormat("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  }).format(parsed);
}

function formatShortIssueDate(chartDate) {
  const normalized = normalizeChartDate(chartDate);
  if (!normalized) return "";
  const parsed = new Date(normalized + "T00:00:00Z");
  if (Number.isNaN(parsed.getTime())) return normalized;
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  }).format(parsed);
}

function formatIssueSlotDate(chartDate) {
  const normalized = normalizeChartDate(chartDate);
  if (!normalized) return "";
  const parsed = new Date(normalized + "T00:00:00Z");
  if (Number.isNaN(parsed.getTime())) return normalized;
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  }).format(parsed);
}

function chartDateValue(chartDate) {
  const normalized = normalizeChartDate(chartDate);
  if (!normalized) return null;
  const parsed = new Date(normalized + "T00:00:00Z");
  const value = parsed.getTime();
  return Number.isFinite(value) ? value : null;
}

function dateParts(chartDate) {
  const normalized = normalizeChartDate(chartDate);
  if (!normalized) {
    return {
      date: "",
      year: "",
      month: "",
    };
  }

  const year = normalized.slice(0, 4);
  const month = normalized.slice(5, 7);

  return {
    date: normalized,
    year,
    month,
  };
}

function chartTypeLabel(chartType) {
  return chartType === "albums" ? "Billboard 200" : "Hot 100";
}

function currentChartType() {
  return state.currentChartType || "songs";
}

function currentYear() {
  return state.currentYear || "";
}

function currentDate() {
  return state.currentDate || "";
}

function currentLayoutMode() {
  return state.layoutMode || "desktop";
}

// Shared chart state is constant across breakpoints.
// Breakpoints now only tune spacing and typography; browsing + detail behavior stays unified.
function detectLayoutMode() {
  if (window.matchMedia("(max-width: " + LAYOUT_BREAKPOINTS.mobile + "px)").matches) {
    return "mobile";
  }
  if (window.matchMedia("(max-width: " + LAYOUT_BREAKPOINTS.tablet + "px)").matches) {
    return "tablet";
  }
  return "desktop";
}

function syncLayoutMode() {
  const nextMode = detectLayoutMode();
  const changed = state.layoutMode !== nextMode;
  state.layoutMode = nextMode;
  document.body.dataset.layout = nextMode;
  return changed;
}

function renderSelectorButtons(container, values, activeValue, labelForValue, onSelect) {
  if (!container) return;
  container.innerHTML = "";
  if (!values.length) {
    const empty = document.createElement("span");
    empty.className = "empty-inline";
    empty.textContent = "No options";
    container.appendChild(empty);
    return;
  }

  const fragment = document.createDocumentFragment();
  for (let i = 0; i < values.length; i += 1) {
    const value = String(values[i]);
    const button = document.createElement("button");
    button.type = "button";
    button.className = "selector-button";
    if (value === String(activeValue || "")) button.classList.add("active");
    button.setAttribute("aria-pressed", value === String(activeValue || "") ? "true" : "false");
    button.textContent = labelForValue ? labelForValue(value) : value;
    button.addEventListener("click", function () {
      onSelect(value);
    });
    fragment.appendChild(button);
  }
  container.appendChild(fragment);
}

function allDatesForChartType(chartType) {
  return state.allDates[chartType] ? state.allDates[chartType].slice() : [];
}

function currentIssueDateIndex(chartType) {
  return allDatesForChartType(chartType).indexOf(currentDate());
}

function currentIssueNavigationState(chartType) {
  const issueDate = currentDate();
  const issueDates = allDatesForChartType(chartType);
  const currentIndex = issueDates.indexOf(issueDate);
  const previousDate = currentIndex > 0 ? issueDates[currentIndex - 1] : "";
  const nextDate = currentIndex >= 0 && currentIndex < issueDates.length - 1 ? issueDates[currentIndex + 1] : "";

  return {
    label: issueDate ? formatIssueDate(issueDate) : "No chart date available",
    previousDate,
    nextDate,
    hasPrevious: Boolean(previousDate),
    hasNext: Boolean(nextDate),
  };
}

function closestAvailableDate(preferredDate, availableIssueDates) {
  if (!Array.isArray(availableIssueDates) || !availableIssueDates.length) return "";
  const preferred = normalizeChartDate(preferredDate);
  if (!preferred) return "";
  const preferredMs = chartDateValue(preferred);
  if (preferredMs == null) return "";

  let closestDate = "";
  let closestDistance = Number.POSITIVE_INFINITY;
  for (let index = 0; index < availableIssueDates.length; index += 1) {
    const issueDate = normalizeChartDate(availableIssueDates[index]);
    if (!issueDate) continue;
    const issueMs = chartDateValue(issueDate);
    if (issueMs == null) continue;
    const distance = Math.abs(issueMs - preferredMs);
    if (distance < closestDistance) {
      closestDistance = distance;
      closestDate = issueDate;
    }
  }

  return closestDate;
}

function syncWorklistPanelPosition() {
  if (!el.worklistPanel) return;

  if (el.worklistPanel.classList.contains("collection-panel--menu")) {
    el.worklistPanel.style.top = "";
    el.worklistPanel.style.bottom = "";
    return;
  }

  if (el.worklistPanel.classList.contains("collection-panel--in-detail")) {
    el.worklistPanel.style.top = "";
    el.worklistPanel.style.bottom = "";
    return;
  }

  if (currentLayoutMode() === "mobile") {
    el.worklistPanel.style.top = "";
    el.worklistPanel.style.bottom = "";
    return;
  }

  let top = 16;
  if (el.appHeader) {
    top = Math.max(top, Math.ceil(el.appHeader.getBoundingClientRect().bottom) + 16);
  }
  if (el.chartNavBar) {
    top = Math.max(top, Math.ceil(el.chartNavBar.getBoundingClientRect().bottom) + 16);
  }

  el.worklistPanel.style.top = top + "px";
  el.worklistPanel.style.bottom = "auto";
}

function movementValue(row) {
  if (row && row.movement) return row.movement;
  const rank = toNumber(row && row.rank);
  const lastWeek = toNumber(row && row.last_week);
  const weeks = toNumber(row && row.weeks_on_chart) || 0;
  if (rank == null) return "";
  if (lastWeek == null || lastWeek <= 0) {
    return weeks <= 1 ? "NEW" : "RE";
  }
  if (rank < lastWeek) return "UP";
  if (rank > lastWeek) return "DOWN";
  return "SAME";
}

function movementLabel(row) {
  const movement = movementValue(row);
  if (movement === "UP") return "▲";
  if (movement === "DOWN") return "▼";
  if (movement === "SAME") return "→";
  if (movement === "NEW") return "NEW";
  if (movement === "RE") return "RE";
  return "—";
}

function movementClass(row) {
  const movement = movementValue(row);
  if (movement === "UP") return "up";
  if (movement === "DOWN") return "down";
  if (movement === "SAME") return "same";
  if (movement === "NEW" || movement === "RE") return "new";
  return "same";
}

function trackedRowKey(row) {
  return normalizeVideoTrackKey(row && row.artist, row && row.title);
}

function rowDataKey(row) {
  const artist = String(row && row.artist ? row.artist : "").trim();
  const title = String(row && row.title ? row.title : "").trim();
  if (!artist || !title) return "";
  return artist + "__" + title;
}

function trackedSelectionMessage() {
  const trackedState = describeTrackedSongState(currentDate());
  if (trackedState && trackedState.stateLabel) {
    if (state.trackedSelectionLabel) {
      return state.trackedSelectionLabel + " · " + trackedState.stateLabel;
    }
    return trackedState.stateLabel;
  }
  if (state.trackedSelectionLabel) {
    return state.trackedSelectionLabel + " is not on this chart.";
  }
  return "Song not on chart.";
}

function trackModeEnabled() {
  return Boolean(state.trackMode && currentChartType() === "songs");
}

function rowSelectionKey(chartType, row) {
  if (chartType === "albums") {
    return row && row.retroverse_album_id ? "album:" + row.retroverse_album_id : null;
  }
  return row && row.retroverse_id ? "song:" + row.retroverse_id : null;
}

function songHistory(song) {
  if (Array.isArray(song && song.chart_history)) return song.chart_history.slice();
  if (song && song.billboard && Array.isArray(song.billboard.history)) return song.billboard.history.slice();
  return [];
}

function albumHistory(album) {
  return Array.isArray(album && album.chart_history) ? album.chart_history.slice() : [];
}

function buildMaps(master) {
  state.songById = new Map();
  state.songByTrackKey = new Map();
  state.albumById = new Map();
  state.videosBySongId = new Map();
  state.songsByAlbumId = new Map();

  const songs = Array.isArray(master.songs) ? master.songs : [];
  for (let i = 0; i < songs.length; i += 1) {
    const song = songs[i];
    if (song && song.retroverse_id) state.songById.set(song.retroverse_id, song);
    const trackKey = trackedRowKey(song);
    if (trackKey && !state.songByTrackKey.has(trackKey)) state.songByTrackKey.set(trackKey, song);
    const albumId = song && song.album && song.album.retroverse_album_id;
    if (albumId) {
      if (!state.songsByAlbumId.has(albumId)) state.songsByAlbumId.set(albumId, []);
      state.songsByAlbumId.get(albumId).push(song);
    }
  }

  const albums = Array.isArray(master.albums) ? master.albums : [];
  for (let i = 0; i < albums.length; i += 1) {
    const album = albums[i];
    if (album && album.retroverse_album_id) state.albumById.set(album.retroverse_album_id, album);
  }

  const videos = Array.isArray(master.videos) ? master.videos : [];
  for (let i = 0; i < videos.length; i += 1) {
    const video = videos[i];
    const songId = video && (video.matched_song_id || (video.matched_song && video.matched_song.retroverse_id));
    if (!songId) continue;
    if (!state.videosBySongId.has(songId)) state.videosBySongId.set(songId, []);
    state.videosBySongId.get(songId).push(video);
  }
}

function buildChartIndex(master) {
  const chartIndex = {
    songs: {},
    albums: {},
  };
  const allDates = {
    songs: new Set(),
    albums: new Set(),
  };

  const songs = Array.isArray(master.songs) ? master.songs : [];
  for (let i = 0; i < songs.length; i += 1) {
    const history = songHistory(songs[i]);
    for (let j = 0; j < history.length; j += 1) {
      const chartDate = normalizeChartDate(history[j] && history[j].chart_date);
      const year = chartDate ? chartDate.slice(0, 4) : "";
      if (!year) continue;
      if (!chartIndex.songs[year]) chartIndex.songs[year] = [];
      chartIndex.songs[year].push(chartDate);
      allDates.songs.add(chartDate);
    }
  }

  const albums = Array.isArray(master.albums) ? master.albums : [];
  for (let i = 0; i < albums.length; i += 1) {
    const history = albumHistory(albums[i]);
    for (let j = 0; j < history.length; j += 1) {
      const chartDate = normalizeChartDate(history[j] && history[j].chart_date);
      const year = chartDate ? chartDate.slice(0, 4) : "";
      if (!year) continue;
      if (!chartIndex.albums[year]) chartIndex.albums[year] = [];
      chartIndex.albums[year].push(chartDate);
      allDates.albums.add(chartDate);
    }
  }

  for (const type of ["songs", "albums"]) {
    const years = Object.keys(chartIndex[type]);
    for (let i = 0; i < years.length; i += 1) {
      chartIndex[type][years[i]] = Array.from(new Set(chartIndex[type][years[i]])).sort();
    }
  }

  state.chartIndex = chartIndex;
  state.allDates = {
    songs: Array.from(allDates.songs).sort(),
    albums: Array.from(allDates.albums).sort(),
  };
  state.chartSearchIndex = {
    songs: null,
    albums: null,
  };
}

function resetDerivedDataCaches() {
  state.rowCache = {
    songs: new Map(),
    albums: new Map(),
  };
  state.chartSearchIndex = {
    songs: null,
    albums: null,
  };
}

function latestYearForChartType(chartType) {
  const years = availableYears(chartType);
  return years.length ? years[years.length - 1] : "";
}

function applyMasterData(master) {
  state.master = master && typeof master === "object" ? master : { songs: [], albums: [], videos: [] };
  resetDerivedDataCaches();
  enrichMasterWithTrackVideos(state.master, state.videoCacheByTrackKey);
  buildMaps(state.master);
  buildChartIndex(state.master);
}

function availableYears(chartType) {
  return Object.keys(state.chartIndex[chartType] || {}).sort(function (a, b) {
    return (toNumber(a) || 0) - (toNumber(b) || 0);
  });
}

function availableDates(chartType, year) {
  return year && state.chartIndex[chartType] && state.chartIndex[chartType][year]
    ? state.chartIndex[chartType][year].slice()
    : [];
}

function availableDatesForMonth(chartType, year, month) {
  return availableDates(chartType, year).filter(function (chartDate) {
    return normalizeChartDate(chartDate).slice(5, 7) === String(month || "");
  });
}

function linkedVideosForSong(songId) {
  return state.videosBySongId.get(songId) || [];
}

function linkedSongsForAlbum(albumId) {
  return state.songsByAlbumId.get(albumId) || [];
}

function sourceKindLabel(kind) {
  if (kind === "local") return "Local Video";
  if (kind === "youtube") return "YouTube";
  if (kind === "search") return "Search Results";
  return "Video Source";
}

function sourceActionLabel(kind) {
  if (kind === "local") return "Play from library";
  if (kind === "youtube") return "Play on YouTube";
  if (kind === "search") return "Search YouTube";
  return "Open source";
}

function normalizeWorkflowSource(source) {
  if (source === "local" || source === "youtube" || source === "search") {
    return source;
  }
  return "search";
}

function normalizeWorkflowBucket(bucket) {
  return bucket === "acquire" ? "acquire" : "queue";
}

function worklistLabel(bucket) {
  return normalizeWorkflowBucket(bucket) === "acquire" ? "Acquire" : "Queue";
}

function workflowItemKey(artist, title, retroverseId) {
  if (retroverseId) return "song:" + retroverseId;
  const normalized = normalizeVideoTrackKey(artist, title);
  return normalized ? "track:" + normalized : "";
}

function normalizeWorkflowItem(item) {
  if (!item || typeof item !== "object") return null;
  const artist = String(item.artist == null ? "" : item.artist).trim();
  const title = String(item.title == null ? "" : item.title).trim();
  const key = String(item.key == null ? "" : item.key).trim()
    || workflowItemKey(artist, title, item.retroverse_id);
  if (!artist || !title || !key) return null;

  const youtubeId = typeof item.youtube_id === "string" && item.youtube_id.trim()
    ? item.youtube_id.trim()
    : null;
  const confidence = Number(item.confidence);

  return {
    key,
    artist,
    title,
    youtube_id: youtubeId,
    source: normalizeWorkflowSource(item.source),
    url: safePublicUrl(item.url || item.video_url || item.videoUrl),
    confidence: Number.isFinite(confidence) ? confidence : 0,
  };
}

function worklistItems(bucket) {
  return normalizeWorkflowBucket(bucket) === "acquire" ? state.acquire : state.queue;
}

function worklistIndex(bucket) {
  return normalizeWorkflowBucket(bucket) === "acquire" ? state.acquireIndex : state.queueIndex;
}

function setWorklistItems(bucket, items) {
  const normalizedBucket = normalizeWorkflowBucket(bucket);
  const normalizedItems = [];
  const index = new Set();
  const values = Array.isArray(items) ? items : [];

  for (let i = 0; i < values.length; i += 1) {
    const item = normalizeWorkflowItem(values[i]);
    if (!item || index.has(item.key)) continue;
    index.add(item.key);
    normalizedItems.push(item);
  }

  if (normalizedBucket === "acquire") {
    state.acquire = normalizedItems;
    state.acquireIndex = index;
    return;
  }

  state.queue = normalizedItems;
  state.queueIndex = index;
}

function saveWorklistState() {
  const storage = storageHandle();
  if (!storage) return;
  try {
    storage.setItem(WORKLIST_STORAGE_KEY, JSON.stringify({
      queue: state.queue,
      acquire: state.acquire,
    }));
  } catch (_error) {
    // Ignore storage write failures; worklists remain in-memory.
  }
}

function loadWorklistState() {
  setWorklistItems("queue", []);
  setWorklistItems("acquire", []);

  const storage = storageHandle();
  if (!storage) return;

  try {
    const nextRaw = storage.getItem(WORKLIST_STORAGE_KEY);
    if (nextRaw) {
      const parsed = JSON.parse(nextRaw);
      if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
        setWorklistItems("queue", parsed.queue);
        setWorklistItems("acquire", parsed.acquire);
        return;
      }
    }

    const legacyRaw = storage.getItem(LEGACY_COLLECTION_STORAGE_KEY);
    if (!legacyRaw) return;
    const legacyItems = JSON.parse(legacyRaw);
    if (!Array.isArray(legacyItems)) return;
    setWorklistItems("queue", legacyItems);
    saveWorklistState();
  } catch (_error) {
    setWorklistItems("queue", []);
    setWorklistItems("acquire", []);
  }
}

function worklistCount(bucket) {
  return worklistItems(bucket).length;
}

function worklistContains(bucket, key) {
  return Boolean(key && worklistIndex(bucket).has(key));
}

function worklistMembershipLabel(key) {
  const inQueue = worklistContains("queue", key);
  const inAcquire = worklistContains("acquire", key);
  if (inQueue && inAcquire) return "In Queue and Acquire";
  if (inQueue) return "In Queue";
  if (inAcquire) return "In Acquire";
  return "";
}

function worklistButtonLabel(key) {
  const membership = worklistMembershipLabel(key);
  if (membership === "In Queue") return "In Queue · Add to Acquire";
  if (membership === "In Acquire") return "In Acquire · Add to Queue";
  if (membership === "In Queue and Acquire") return membership;
  return "Add to Queue or Acquire";
}

function trackInAnyWorklist(key) {
  return Boolean(worklistMembershipLabel(key));
}

function buildYoutubePlaylistUrl(ids) {
  const validIds = [];
  for (let i = 0; i < ids.length; i += 1) {
    const youtubeId = normalizeYoutubeId(ids[i]);
    if (!youtubeId) continue;
    validIds.push(youtubeId);
  }
  if (!validIds.length) return "";
  return "https://www.youtube.com/watch_videos?video_ids=" + validIds.map(encodeURIComponent).join(",");
}

function buildYoutubeWatchUrl(youtubeId) {
  const validId = normalizeYoutubeId(youtubeId);
  if (!validId) return "";
  return "https://www.youtube.com/watch?v=" + encodeURIComponent(validId);
}

function buildYoutubeSearchUrl(artist, title) {
  const parts = [];
  if (artist) parts.push(String(artist).trim());
  if (title) parts.push(String(title).trim());
  const query = parts.join(" ").trim();
  if (!query) return "";
  return "https://www.youtube.com/results?search_query=" + encodeURIComponent(query);
}

function worklistItemUrl(entry) {
  const directUrl = safePublicUrl(entry && entry.url);
  if (directUrl) return directUrl;

  const youtubeUrl = buildYoutubeWatchUrl(entry && entry.youtube_id);
  if (youtubeUrl) return youtubeUrl;

  return buildYoutubeSearchUrl(entry && entry.artist, entry && entry.title);
}

function worklistItemYoutubeUrl(entry) {
  const youtubeUrl = buildYoutubeWatchUrl(entry && entry.youtube_id);
  if (youtubeUrl) return youtubeUrl;
  return buildYoutubeSearchUrl(entry && entry.artist, entry && entry.title);
}

function acquireExportUrl(options) {
  const items = acquireItemsForYoutube(options);
  const ids = items.map(function (item) {
    return item.youtube_id;
  });
  return buildYoutubePlaylistUrl(ids);
}

function copyTextToClipboard(value) {
  const text = typeof value === "string" ? value.trim() : "";
  if (!text || !navigator.clipboard || !navigator.clipboard.writeText) {
    return Promise.resolve(false);
  }

  return navigator.clipboard.writeText(text).then(function () {
    return true;
  }).catch(function () {
    return false;
  });
}

function openWorkflowExport(url) {
  if (!url) return;
  const popup = window.open(url, "_blank", "noopener");
  if (!popup && navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(url).catch(function () {});
  }
}

function openDeferredWorkflowWindow(message) {
  const popup = window.open("about:blank", "_blank");
  if (!popup) return null;

  try {
    popup.opener = null;
  } catch (_error) {
    // Ignore cross-browser opener assignment failures.
  }

  try {
    popup.document.title = "RetroVerse";
    popup.document.body.innerHTML =
      '<main style="font: 16px/1.4 Georgia, serif; padding: 2rem; color: #1a1a1a; background: #f7f1e4;">' +
        '<p style="margin: 0; letter-spacing: 0.08em; font-size: 0.7rem; text-transform: uppercase; color: #8a5f16;">RetroVerse</p>' +
        '<h1 style="margin: 0.4rem 0 0; font-size: 1.25rem;">' + esc(message || "Resolving YouTube matches…") + "</h1>" +
      "</main>";
  } catch (_error) {
    // Ignore document write failures and fall back to standard export if needed.
  }

  return popup;
}

function finalizeDeferredWorkflowWindow(popup, url) {
  if (popup && !popup.closed && url) {
    try {
      popup.location.replace(url);
      return true;
    } catch (_error) {
      // Fall through to a normal window open below.
    }
  }
  openWorkflowExport(url);
  return Boolean(url);
}

function closeDeferredWorkflowWindow(popup) {
  if (!popup || popup.closed) return;
  try {
    popup.close();
  } catch (_error) {
    // Ignore popup close failures.
  }
}

function directQueuePlaybackItems() {
  return worklistItems("queue").filter(function (item) {
    return Boolean(worklistItemUrl(item));
  });
}

function firstQueuePlaybackItem() {
  const items = directQueuePlaybackItems();
  for (let i = 0; i < items.length; i += 1) {
    return items[i];
  }
  return null;
}

function openWorklistItem(entry) {
  const url = worklistItemUrl(entry);
  if (!url) return false;
  window.open(url, "_blank", "noopener");
  return true;
}

function playQueue() {
  const first = firstQueuePlaybackItem();
  if (!first) return false;
  return openWorklistItem(first);
}

function shuffleQueueAndPlay() {
  const items = worklistItems("queue").slice();
  if (!items.length) return false;

  for (let i = items.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    const next = items[i];
    items[i] = items[j];
    items[j] = next;
  }

  setWorklistItems("queue", items);
  saveWorklistState();
  const first = firstQueuePlaybackItem();
  if (!first) return false;
  return openWorklistItem(first);
}

function acquireItemsForYoutube(options) {
  const settings = options && typeof options === "object" ? options : {};
  const missingOnly = Boolean(settings.missingOnly);
  return worklistItems("acquire").filter(function (item) {
    if (!item) return false;
    if (missingOnly && item.source === "local") return false;
    return true;
  });
}

function acquireMissingOnlyCount() {
  return acquireItemsForYoutube({ missingOnly: true }).length;
}

function firstAcquireItem(options) {
  const items = acquireItemsForYoutube(options);
  return items.length ? items[0] : null;
}

function acquirePrimaryUrl(options) {
  const playlistUrl = acquireExportUrl(options);
  if (playlistUrl) return playlistUrl;
  return worklistItemYoutubeUrl(firstAcquireItem(options));
}

function setAcquireStatus(message, tone) {
  state.acquireNotice = typeof message === "string" ? message : "";
  state.acquireNoticeTone = tone === "error" ? "error" : "info";
}

function setAcquireBusy(nextBusy, message, tone) {
  state.acquireBusy = Boolean(nextBusy);
  if (typeof message === "string") {
    setAcquireStatus(message, tone);
  }
}

function mergeAcquireResolvedItems(resolvedItems) {
  const updates = new Map();
  const entries = Array.isArray(resolvedItems) ? resolvedItems : [];
  for (let i = 0; i < entries.length; i += 1) {
    const entry = entries[i];
    const key = entry && typeof entry.key === "string" ? entry.key.trim() : "";
    const youtubeId = normalizeYoutubeId(entry && entry.youtube_id);
    if (!key || !youtubeId) continue;
    updates.set(key, {
      youtube_id: youtubeId,
      confidence: Number(entry && entry.confidence),
    });
  }

  if (!updates.size) return false;

  let changed = false;
  const nextItems = worklistItems("acquire").map(function (item) {
    const update = updates.get(item.key);
    if (!update) return item;

    const nextConfidence = Number.isFinite(update.confidence)
      ? Math.max(item.confidence || 0, update.confidence)
      : item.confidence;
    if (item.youtube_id === update.youtube_id && nextConfidence === item.confidence) {
      return item;
    }

    changed = true;
    return {
      key: item.key,
      artist: item.artist,
      title: item.title,
      youtube_id: update.youtube_id,
      source: item.source,
      url: item.url,
      confidence: nextConfidence,
    };
  });

  if (!changed) return false;
  setWorklistItems("acquire", nextItems);
  saveWorklistState();
  return true;
}

function postJsonWithTimeout(url, payload, timeoutMs) {
  const controller = typeof AbortController === "function" ? new AbortController() : null;
  const timer = controller
    ? window.setTimeout(function () {
        controller.abort();
      }, timeoutMs)
    : 0;

  return fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload || {}),
    signal: controller ? controller.signal : undefined,
  }).then(function (response) {
    return response.json().catch(function () {
      return {};
    }).then(function (data) {
      if (!response.ok) {
        const message = data && typeof data.error === "string" && data.error.trim()
          ? data.error.trim()
          : response.status + " " + response.statusText;
        throw new Error(message);
      }
      return data;
    });
  }).finally(function () {
    if (timer) window.clearTimeout(timer);
  });
}

function buildAcquireResolvePayload(items) {
  return {
    items: items.map(function (item) {
      return {
        key: item.key,
        artist: item.artist,
        title: item.title,
        youtube_id: item.youtube_id,
        source: item.source,
      };
    }),
  };
}

function resolvedPlaylistUrlFromResponse(payload) {
  const entries = Array.isArray(payload && payload.items) ? payload.items : [];
  const ids = entries.map(function (item) {
    return item && item.youtube_id;
  });
  return buildYoutubePlaylistUrl(ids);
}

async function openAcquirePlaylist(options) {
  const settings = options && typeof options === "object" ? options : {};
  const items = acquireItemsForYoutube(settings);
  if (!items.length) {
    setAcquireStatus("No Acquire tracks match this filter yet.", "error");
    renderWorklistUi();
    return false;
  }

  const playlistUrl = acquireExportUrl(settings);
  if (playlistUrl) {
    const matchedCount = items.filter(function (item) {
      return Boolean(normalizeYoutubeId(item.youtube_id));
    }).length;
    setAcquireStatus("Opened " + matchedCount + " Acquire tracks in YouTube.", "info");
    renderWorklistUi();
    openWorkflowExport(playlistUrl);
    return true;
  }

  const fallbackItem = firstAcquireItem(settings);
  const fallbackUrl = worklistItemYoutubeUrl(fallbackItem);
  if (fallbackUrl) {
    openWorkflowExport(fallbackUrl);
    setAcquireStatus("Opened the first Acquire track in YouTube search.", "info");
    renderWorklistUi();
    return true;
  }

  setAcquireStatus("No Acquire tracks can be opened yet.", "error");
  renderWorklistUi();
  return false;
}

function workflowItemForRow(chartType, row) {
  const entry = primaryResolvedVideoEntry(chartType, row);
  const song = entry && entry.song
    ? entry.song
    : (chartType === "songs" && row && row.retroverse_id ? state.songById.get(row.retroverse_id) || null : null);
  if (!song) return null;

  const artist = song.artist_canonical || song.artist || row.artist || "";
  const title = song.title || row.title || "";
  const resolved = entry && entry.resolved ? entry.resolved : resolveTrackVideoSource(song.video);
  if (!artist || !title || !resolved || !resolved.url) return null;

  return {
    key: workflowItemKey(artist, title, song.retroverse_id),
    artist,
    title,
    youtube_id: resolved.youtubeId || null,
    source: normalizeWorkflowSource(resolved.kind),
    url: resolved.url,
    confidence: typeof resolved.confidence === "number" ? resolved.confidence : 0,
  };
}

function workflowItemFromTrigger(trigger) {
  if (!trigger) return null;
  return normalizeWorkflowItem({
    key: trigger.getAttribute("data-workflow-key"),
    artist: trigger.getAttribute("data-workflow-artist"),
    title: trigger.getAttribute("data-workflow-title"),
    youtube_id: trigger.getAttribute("data-workflow-youtube-id"),
    source: trigger.getAttribute("data-workflow-source"),
    url: trigger.getAttribute("data-workflow-url"),
    confidence: Number(trigger.getAttribute("data-workflow-confidence")),
  });
}

function addWorklistItem(bucket, item) {
  const normalizedBucket = normalizeWorkflowBucket(bucket);
  const normalizedItem = normalizeWorkflowItem(item);
  if (!normalizedItem) return false;
  if (worklistContains(normalizedBucket, normalizedItem.key)) return false;
  setWorklistItems(normalizedBucket, worklistItems(normalizedBucket).concat([normalizedItem]));
  saveWorklistState();
  return true;
}

function removeWorklistItem(bucket, key) {
  const normalizedBucket = normalizeWorkflowBucket(bucket);
  if (!worklistContains(normalizedBucket, key)) return false;
  setWorklistItems(normalizedBucket, worklistItems(normalizedBucket).filter(function (item) {
    return item.key !== key;
  }));
  saveWorklistState();
  return true;
}

function clearWorklist(bucket) {
  const normalizedBucket = normalizeWorkflowBucket(bucket);
  if (!worklistCount(normalizedBucket)) return false;
  setWorklistItems(normalizedBucket, []);
  saveWorklistState();
  return true;
}

function syncWorkflowButtons() {
  const buttons = document.querySelectorAll(".rv-collect[data-workflow-key]");
  for (let i = 0; i < buttons.length; i += 1) {
    const button = buttons[i];
    const key = button.getAttribute("data-workflow-key");
    const membership = worklistMembershipLabel(key);
    const label = worklistButtonLabel(key);
    button.classList.toggle("is-added", Boolean(membership));
    button.setAttribute("title", label);
    button.setAttribute("aria-label", label);
  }
}

function closeDestinationMenu() {
  state.destinationMenu = {
    open: false,
    x: 0,
    y: 0,
    item: null,
  };
  renderDestinationMenu();
}

function openDestinationMenu(trigger) {
  const item = workflowItemFromTrigger(trigger);
  if (!item) {
    closeDestinationMenu();
    return;
  }

  const isSameItem = state.destinationMenu.open
    && state.destinationMenu.item
    && state.destinationMenu.item.key === item.key;
  if (isSameItem) {
    closeDestinationMenu();
    return;
  }

  const rect = trigger.getBoundingClientRect();
  const menuWidth = Math.min(196, Math.max(160, window.innerWidth - 24));
  const estimatedHeight = 116;
  const left = Math.max(12, Math.min(window.innerWidth - menuWidth - 12, rect.right - menuWidth));
  let top = rect.bottom + 8;
  if (top + estimatedHeight > window.innerHeight - 12) {
    top = Math.max(12, rect.top - estimatedHeight - 8);
  }

  state.destinationMenu = {
    open: true,
    x: left,
    y: top,
    item,
  };
  renderDestinationMenu();
}

function renderDestinationMenuButton(bucket, item) {
  const normalizedBucket = normalizeWorkflowBucket(bucket);
  const added = worklistContains(normalizedBucket, item && item.key);
  return '<button type="button" class="workflow-menu-item" data-worklist-add="' + esc(normalizedBucket) + '"' +
    (added ? ' disabled aria-disabled="true"' : "") + '>' +
    '<span class="workflow-menu-item-name">' + esc(worklistLabel(normalizedBucket)) + "</span>" +
    '<span class="workflow-menu-item-note">' + esc(added ? "Added" : "") + "</span>" +
  "</button>";
}

function renderDestinationMenu() {
  if (!el.worklistMenu) return;

  const menuState = state.destinationMenu;
  if (!menuState || !menuState.open || !menuState.item) {
    el.worklistMenu.hidden = true;
    el.worklistMenu.innerHTML = "";
    return;
  }

  el.worklistMenu.hidden = false;
  el.worklistMenu.style.left = menuState.x + "px";
  el.worklistMenu.style.top = menuState.y + "px";
  el.worklistMenu.innerHTML =
    '<p class="workflow-menu-label">Add to</p>' +
    renderDestinationMenuButton("queue", menuState.item) +
    renderDestinationMenuButton("acquire", menuState.item);
}

function renderWorklistItemsHtml(bucket) {
  const items = worklistItems(bucket);
  if (!items.length) {
    const emptyMessage = normalizeWorkflowBucket(bucket) === "acquire"
      ? "Send tracks here when you want a YouTube review or export list."
      : "Send tracks here when you want a playback queue.";
    return '<p class="collection-empty">' + esc(emptyMessage) + "</p>";
  }

  return items.map(function (item) {
    const meta = [item.artist, sourceKindLabel(item.source)];
    if (!item.youtube_id && normalizeWorkflowBucket(bucket) === "acquire") {
      meta.push("No direct YouTube ID");
    }
    const itemUrl = worklistItemUrl(item);
    const itemLabel = itemUrl
      ? (item.source === "local"
        ? "Play from library"
        : (item.source === "youtube" || normalizeYoutubeId(item.youtube_id)
          ? "Play on YouTube"
          : "Search YouTube"))
      : "Open track";

    return '<div class="collection-item">' +
      '<button type="button" class="collection-item-main collection-item-link" data-worklist-open-item="true" data-workflow-key="' + esc(item.key) + '" data-workflow-artist="' + esc(item.artist) + '" data-workflow-title="' + esc(item.title) + '" data-workflow-youtube-id="' + esc(item.youtube_id || "") + '" data-workflow-source="' + esc(item.source) + '" data-workflow-url="' + esc(item.url || "") + '" title="' + esc(itemLabel) + '" aria-label="' + esc(itemLabel + ": " + item.artist + " — " + item.title) + '">' +
        '<p class="collection-item-title">' + esc(item.title) + "</p>" +
        '<p class="collection-item-meta">' + esc(meta.join(" · ")) + "</p>" +
      "</button>" +
      '<button type="button" class="collection-remove" data-worklist-remove="' + esc(normalizeWorkflowBucket(bucket)) + '" data-worklist-key="' + esc(item.key) + '" aria-label="Remove ' + esc(item.title) + ' from ' + esc(worklistLabel(bucket)) + '">Remove</button>' +
    "</div>";
  }).join("");
}

function renderWorklistSection(bucket) {
  const normalizedBucket = normalizeWorkflowBucket(bucket);
  const count = worklistCount(normalizedBucket);
  const heading = worklistLabel(normalizedBucket) + " (" + count + ")";
  const kicker = normalizedBucket === "acquire" ? "Acquire" : "Playback";
  const queuePlayable = Boolean(firstQueuePlaybackItem());
  const acquireHasItems = Boolean(worklistCount("acquire"));
  const acquireUrl = acquireExportUrl();
  const acquireOpenReady = acquireHasItems;
  const acquireMissingReady = Boolean(acquireMissingOnlyCount());
  const acquireBusy = Boolean(state.acquireBusy);
  const acquireNote = normalizedBucket === "acquire" && state.acquireNotice
    ? '<p class="worklist-section-note' + (state.acquireNoticeTone === "error" ? " is-error" : "") + '">' + esc(state.acquireNotice) + "</p>"
    : "";
  let actions = "";

  if (normalizedBucket === "queue") {
    actions =
      '<button type="button" class="collection-action worklist-action" data-worklist-play="queue"' + (queuePlayable ? "" : " disabled") + '>Play Queue</button>' +
      '<button type="button" class="collection-action worklist-action" data-worklist-shuffle="queue"' + (queuePlayable ? "" : " disabled") + '>Shuffle</button>';
  } else {
    actions =
      '<button type="button" class="collection-action worklist-action" data-worklist-export="acquire"' + (acquireHasItems && !acquireBusy ? "" : " disabled") + '>Export IDs</button>' +
      '<button type="button" class="collection-action worklist-action" data-worklist-copy="acquire"' + (acquireHasItems && !acquireBusy ? "" : " disabled") + '>Copy URL</button>' +
      '<button type="button" class="collection-action worklist-action" data-worklist-open="acquire"' + (acquireOpenReady && !acquireBusy ? "" : " disabled") + '>Open in YouTube</button>' +
      '<button type="button" class="collection-action worklist-action" data-worklist-open-missing="acquire"' + (acquireMissingReady && !acquireBusy ? "" : " disabled") + '>Open Missing Only</button>';
  }

  return '<section class="worklist-section">' +
    '<div class="worklist-section-head">' +
      '<div class="worklist-section-copy">' +
        '<p class="worklist-section-kicker">' + esc(kicker) + "</p>" +
        '<h3 class="worklist-section-title">' + esc(heading) + "</h3>" +
        acquireNote +
      "</div>" +
      '<div class="worklist-section-tools">' +
        '<div class="worklist-section-actions">' + actions + "</div>" +
        '<button type="button" class="collection-action collection-action-subtle worklist-clear" data-worklist-clear="' + esc(normalizedBucket) + '"' + (count ? "" : " disabled") + '>Clear</button>' +
      "</div>" +
    "</div>" +
    '<div class="collection-list">' + renderWorklistItemsHtml(normalizedBucket) + "</div>" +
  "</section>";
}

function renderWorklistUi() {
  if (!el.worklistPanel) return;

  const queueCount = worklistCount("queue");

  el.worklistPanel.classList.toggle("is-open", Boolean(state.worklistOpen));
  if (el.worklistToggle) {
    el.worklistToggle.setAttribute("aria-expanded", state.worklistOpen ? "true" : "false");
    el.worklistToggle.setAttribute("aria-label", (state.worklistOpen ? "Close" : "Open") + " Queue and Acquire panel");
  }
  if (el.worklistSummary) {
    el.worklistSummary.textContent = "Queue (" + queueCount + ")";
  }
  if (el.worklistBody) {
    el.worklistBody.hidden = !state.worklistOpen;
    el.worklistBody.innerHTML = renderWorklistSection("queue") + renderWorklistSection("acquire");
  }

  syncWorkflowButtons();
  renderDestinationMenu();
  syncWorklistPanelPosition();
}

function initWorklistUi() {
  if (el.worklistPanel) return;

  const panel = document.createElement("aside");
  panel.className = "collection-panel";
  panel.innerHTML =
    '<button type="button" class="collection-toggle" data-worklist-toggle="true" aria-expanded="false">' +
      '<span class="collection-toggle-summary" data-worklist-summary>Queue (0)</span>' +
    "</button>" +
    '<div class="collection-body worklist-body" data-worklist-body hidden></div>';

  const menu = document.createElement("div");
  menu.className = "workflow-menu";
  menu.hidden = true;

  const mount = el.queueMenuSlot || el.detailPanelToolbar || document.body;
  mount.appendChild(panel);
  if (el.queueMenuSlot) {
    panel.classList.add("collection-panel--menu");
  }
  if (el.detailPanelToolbar) {
    panel.classList.add("collection-panel--in-detail");
  }
  document.body.appendChild(menu);

  el.worklistPanel = panel;
  el.worklistToggle = panel.querySelector("[data-worklist-toggle]");
  el.worklistSummary = panel.querySelector("[data-worklist-summary]");
  el.worklistBody = panel.querySelector("[data-worklist-body]");
  el.worklistMenu = menu;
  syncWorklistPanelPosition();
}

function primaryLocalVideoForSong(songId) {
  if (!songId) return null;
  const videos = linkedVideosForSong(songId)
    .map(function (video) {
      return {
        video,
        localUrl: safePublicUrl(video && video.video_url),
        thumbnailUrl: safePublicUrl(video && video.thumbnail_url),
      };
    })
    .filter(function (entry) {
      return Boolean(entry.localUrl);
    })
    .sort(function (a, b) {
      return (toNumber(b.video && b.video.play_count) || 0) - (toNumber(a.video && a.video.play_count) || 0);
    });

  return videos.length ? videos[0] : null;
}

function resolvedVideoEntryForSong(song) {
  if (!song) return null;
  const primaryLocal = primaryLocalVideoForSong(song.retroverse_id);
  const sources = song.video && typeof song.video === "object" ? song.video : null;
  const resolved = resolveTrackVideoSource(sources);
  if (!resolved || !resolved.url) return null;

  return {
    song,
    video: primaryLocal ? primaryLocal.video : null,
    sources,
    resolved,
    videoUrl: resolved.url,
    thumbnailUrl: primaryLocal ? primaryLocal.thumbnailUrl : "",
    playCount: primaryLocal ? (toNumber(primaryLocal.video && primaryLocal.video.play_count) || 0) : 0,
  };
}

function videoEntryPriority(entry) {
  const kind = entry && entry.resolved && entry.resolved.kind;
  if (kind === "local") return 3;
  if (kind === "youtube") return 2;
  if (kind === "search") return 1;
  return 0;
}

function resolvedVideoEntriesForRow(chartType, row) {
  if (!row) return [];

  if (chartType === "albums") {
    const songs = row.retroverse_album_id ? linkedSongsForAlbum(row.retroverse_album_id) : [];
    return songs
      .map(function (song) {
        return resolvedVideoEntryForSong(song);
      })
      .filter(Boolean)
      .sort(function (a, b) {
        const priorityDelta = videoEntryPriority(b) - videoEntryPriority(a);
        if (priorityDelta !== 0) return priorityDelta;
        return (toNumber(b && b.playCount) || 0) - (toNumber(a && a.playCount) || 0);
      });
  }

  const song = row.retroverse_id ? state.songById.get(row.retroverse_id) || null : null;
  const entry = resolvedVideoEntryForSong(song);
  return entry ? [entry] : [];
}

function primaryResolvedVideoEntry(chartType, row) {
  const entries = resolvedVideoEntriesForRow(chartType, row);
  return entries.length ? entries[0] : null;
}

function rowHasUsableVideoSource(chartType, row) {
  return Boolean(primaryResolvedVideoEntry(chartType, row));
}

function isDirectPlayableEntry(entry) {
  const kind = entry && entry.resolved && entry.resolved.kind;
  return kind === "local" || kind === "youtube";
}

function playableVideoEntriesForRow(chartType, row) {
  return resolvedVideoEntriesForRow(chartType, row).filter(function (entry) {
    return isDirectPlayableEntry(entry);
  });
}

function primaryPlayableVideoEntry(chartType, row) {
  const entries = playableVideoEntriesForRow(chartType, row);
  return entries.length ? entries[0] : null;
}

function rowHasPlayableVideo(chartType, row) {
  return Boolean(primaryPlayableVideoEntry(chartType, row));
}

function currentChartRows() {
  const issueDate = currentDate();
  if (!issueDate) return [];
  return getChartRows(currentChartType(), issueDate);
}

function findAdjacentPlayableRow(chartType, rows, row, direction) {
  if (!row || !rows.length) return null;
  const currentKey = rowSelectionKey(chartType, row);
  const startIndex = rows.findIndex(function (candidate) {
    return rowSelectionKey(chartType, candidate) === currentKey;
  });
  if (startIndex === -1) return null;

  for (let i = startIndex + direction; i >= 0 && i < rows.length; i += direction) {
    if (rowHasPlayableVideo(chartType, rows[i])) {
      return rows[i];
    }
  }
  return null;
}

function pauseVideoModalPlayer() {
  if (el.videoModalPlayer) {
    el.videoModalPlayer.pause();
    el.videoModalPlayer.removeAttribute("src");
    el.videoModalPlayer.removeAttribute("poster");
    el.videoModalPlayer.hidden = true;
    el.videoModalPlayer.load();
    delete el.videoModalPlayer.dataset.src;
  }
  if (el.videoModalFrame) {
    el.videoModalFrame.hidden = true;
    el.videoModalFrame.removeAttribute("src");
    delete el.videoModalFrame.dataset.src;
  }
  if (el.videoModalFallback) {
    el.videoModalFallback.hidden = true;
    el.videoModalFallback.innerHTML = "";
  }
}

function closeVideoModal() {
  state.videoPlayerOpen = false;
  if (!el.videoModal) return;
  pauseVideoModalPlayer();
  el.videoModal.hidden = true;
  document.body.classList.remove("video-open");
  if (el.videoModalTitle) el.videoModalTitle.textContent = "Loading video…";
  if (el.videoModalMeta) el.videoModalMeta.textContent = "";
}

function renderVideoIconButton(chartType, row) {
  const entry = primaryResolvedVideoEntry(chartType, row);
  const url = safePublicUrl(entry && entry.videoUrl);
  if (!entry || !url) return "";
  const kind = entry && entry.resolved && entry.resolved.kind ? entry.resolved.kind : "search";
  const tooltip = sourceActionLabel(kind);
  return '<div class="rv-play ' + esc(kind) + '" data-video-trigger="true" data-video-url="' + esc(url) + '" title="' + esc(tooltip) + '" aria-label="' + esc(tooltip) + '"></div>';
}

function renderWorklistButton(chartType, row) {
  const item = workflowItemForRow(chartType, row);
  if (!item) return "";
  const tooltip = worklistButtonLabel(item.key);
  return '<div class="rv-collect' + (trackInAnyWorklist(item.key) ? " is-added" : "") + '"' +
    ' data-workflow-trigger="true"' +
    ' data-workflow-key="' + esc(item.key) + '"' +
    ' data-workflow-artist="' + esc(item.artist) + '"' +
    ' data-workflow-title="' + esc(item.title) + '"' +
    ' data-workflow-youtube-id="' + esc(item.youtube_id || "") + '"' +
    ' data-workflow-url="' + esc(item.url) + '"' +
    ' data-workflow-source="' + esc(item.source) + '"' +
    ' data-workflow-confidence="' + esc(item.confidence) + '"' +
    ' title="' + esc(tooltip) + '"' +
    ' aria-label="' + esc(tooltip) + '"></div>';
}

function renderRowActionButtons(chartType, row) {
  const playButton = renderVideoIconButton(chartType, row);
  const worklistButton = renderWorklistButton(chartType, row);
  if (!playButton && !worklistButton) return "";
  return '<span class="chart-row-actions">' + playButton + worklistButton + "</span>";
}

function videoTitleForRow(chartType, row, entry) {
  if (chartType === "albums" && entry && entry.song) {
    return (entry.song.title || row.title || "Video") + " — " + (entry.song.artist_canonical || entry.song.artist || row.artist || "");
  }
  return (row.title || "Video") + " — " + (row.artist || "");
}

function videoMetaForRow(chartType, row, entry) {
  const parts = [];
  if (entry && entry.resolved && entry.resolved.label) parts.push(entry.resolved.label);
  const displayTitle = entry && entry.video && (entry.video.title || entry.video.filename);
  if (displayTitle) parts.push(displayTitle);
  if (chartType === "albums" && row && row.title) parts.push(row.title);
  const issueDate = currentDate();
  if (issueDate) parts.push(formatIssueDate(issueDate));
  return parts.join(" · ");
}

function renderVideoFallbackHtml(entry) {
  const kind = entry && entry.resolved ? entry.resolved.kind : "";
  const label = sourceKindLabel(kind);
  const actionLabel = sourceActionLabel(kind);
  const url = safePublicUrl(entry && entry.videoUrl);
  const title = entry && entry.song && entry.song.title ? entry.song.title : "Selected track";
  const artist = entry && entry.song && (entry.song.artist_canonical || entry.song.artist)
    ? (entry.song.artist_canonical || entry.song.artist)
    : "";
  const description = kind === "search"
    ? "No direct video link is saved yet. Use the generated YouTube search for this track."
    : "Open the current source in a new tab.";

  return '<div class="video-fallback-card">' +
    '<p class="video-fallback-kicker">' + esc(label) + "</p>" +
    '<h4 class="video-fallback-title">' + esc(title) + "</h4>" +
    (artist ? '<p class="video-fallback-subtitle">' + esc(artist) + "</p>" : "") +
    '<p class="video-fallback-copy">' + esc(description) + "</p>" +
    (url ? '<p class="video-fallback-actions"><a href="' + esc(url) + '" target="_blank" rel="noopener">' + esc(actionLabel) + "</a></p>" : "") +
  "</div>";
}

function renderVideoModal(chartType, row) {
  if (!state.videoPlayerOpen || !el.videoModal) {
    closeVideoModal();
    return;
  }

  const entry = primaryPlayableVideoEntry(chartType, row);
  if (!row || !entry) {
    closeVideoModal();
    return;
  }

  const rows = currentChartRows();
  const previousRow = findAdjacentPlayableRow(chartType, rows, row, -1);
  const nextRow = findAdjacentPlayableRow(chartType, rows, row, 1);
  const posterUrl = safePublicUrl(entry.video && entry.video.thumbnail_url);

  el.videoModal.hidden = false;
  document.body.classList.add("video-open");
  if (el.videoModalTitle) el.videoModalTitle.textContent = videoTitleForRow(chartType, row, entry);
  if (el.videoModalMeta) el.videoModalMeta.textContent = videoMetaForRow(chartType, row, entry);
  if (el.videoModalPrev) el.videoModalPrev.disabled = !previousRow;
  if (el.videoModalNext) el.videoModalNext.disabled = !nextRow;

  pauseVideoModalPlayer();

  if (entry.resolved && entry.resolved.kind === "local" && el.videoModalPlayer) {
    if (posterUrl) {
      el.videoModalPlayer.poster = posterUrl;
    } else {
      el.videoModalPlayer.removeAttribute("poster");
    }
    el.videoModalPlayer.hidden = false;
    if (el.videoModalPlayer.dataset.src !== entry.videoUrl) {
      el.videoModalPlayer.pause();
      el.videoModalPlayer.src = entry.videoUrl;
      el.videoModalPlayer.load();
      el.videoModalPlayer.dataset.src = entry.videoUrl;
    }
    return;
  }

  if (entry.resolved && entry.resolved.kind === "youtube" && entry.resolved.embedUrl && el.videoModalFrame) {
    el.videoModalFrame.hidden = false;
    if (el.videoModalFrame.dataset.src !== entry.resolved.embedUrl) {
      el.videoModalFrame.src = entry.resolved.embedUrl;
      el.videoModalFrame.dataset.src = entry.resolved.embedUrl;
    }
    return;
  }

  if (el.videoModalFallback) {
    el.videoModalFallback.hidden = false;
    el.videoModalFallback.innerHTML = renderVideoFallbackHtml(entry);
  }
}

function stepVideoPlayer(direction) {
  const chartType = currentChartType();
  const rows = currentChartRows();
  const selectedRow = currentSelectedRow();
  const targetRow = findAdjacentPlayableRow(chartType, rows, selectedRow, direction);
  if (!targetRow) return;
  selectRow(chartType, targetRow, { openVideo: true });
}

function songHasVideo(songId) {
  const song = songId ? state.songById.get(songId) || null : null;
  return Boolean(resolvedVideoEntryForSong(song));
}

function albumHasVideo(albumId) {
  const songs = linkedSongsForAlbum(albumId);
  for (let i = 0; i < songs.length; i += 1) {
    if (songHasVideo(songs[i].retroverse_id)) return true;
  }
  return false;
}

function getChartRows(chartType, chartDate) {
  const normalizedDate = normalizeChartDate(chartDate);
  if (!normalizedDate) return [];
  const cache = state.rowCache[chartType];
  if (cache.has(normalizedDate)) return cache.get(normalizedDate);

  let rows = [];
  if (chartType === "albums") {
    rows = buildAlbumChartRows(
      normalizedDate,
      Array.isArray(state.master.albums) ? state.master.albums : []
    ).map(function (row) {
      return {
        ...row,
        movement: movementValue(row),
        has_video: row.retroverse_album_id ? albumHasVideo(row.retroverse_album_id) : false,
      };
    });
  } else {
    rows = buildSongChartRows(
      normalizedDate,
      Array.isArray(state.master.songs) ? state.master.songs : []
    );
  }

  cache.set(normalizedDate, rows);
  return rows;
}

function chartPreviewLines(chartType, rows) {
  return rows.slice(0, 3).map(function (row) {
    const title = String(row && row.title ? row.title : "").trim();
    const artist = String(row && row.artist ? row.artist : "").trim();
    if (!title) return "";
    if (!artist) return title;
    return chartType === "albums" ? (title + " · " + artist) : (artist + " — " + title);
  }).filter(Boolean);
}

function buildChartSearchIndex(chartType) {
  const cached = state.chartSearchIndex[chartType];
  if (Array.isArray(cached)) return cached;

  const chartMap = new Map();
  const sourceItems = chartType === "albums"
    ? (Array.isArray(state.master && state.master.albums) ? state.master.albums : [])
    : (Array.isArray(state.master && state.master.songs) ? state.master.songs : []);

  for (let i = 0; i < sourceItems.length; i += 1) {
    const item = sourceItems[i];
    if (!item || typeof item !== "object") continue;

    const title = String(
      chartType === "albums"
        ? (item.album_title || item.title || "")
        : (item.title || "")
    ).trim();
    const artist = String(item.artist_canonical || item.artist || "").trim();
    const history = chartType === "albums" ? albumHistory(item) : songHistory(item);
    if (!title || !history.length) continue;

    for (let j = 0; j < history.length; j += 1) {
      const entry = history[j];
      const chartDate = normalizeChartDate(entry && entry.chart_date);
      if (!chartDate) continue;

      if (!chartMap.has(chartDate)) {
        chartMap.set(chartDate, {
          chartType,
          chartDate,
          formattedDate: formatIssueDate(chartDate),
          year: chartDate.slice(0, 4),
          tokens: [],
          previewRows: [],
        });
      }

      const bucket = chartMap.get(chartDate);
      if (artist) bucket.tokens.push(artist);
      bucket.tokens.push(title);

      const rank = toNumber(entry && entry.rank);
      if (rank != null && rank > 0 && rank <= 3) {
        bucket.previewRows.push({
          rank,
          artist,
          title,
        });
      }
    }
  }

  const entries = allDatesForChartType(chartType).map(function (chartDate) {
    const bucket = chartMap.get(chartDate) || {
      chartType,
      chartDate,
      formattedDate: formatIssueDate(chartDate),
      year: chartDate.slice(0, 4),
      tokens: [],
      previewRows: [],
    };

    const previewRows = bucket.previewRows
      .slice()
      .sort(function (a, b) {
        return a.rank - b.rank;
      })
      .slice(0, 3);
    const preview = previewRows.map(function (row) {
      if (!row.artist) return row.title;
      return chartType === "albums"
        ? (row.title + " · " + row.artist)
        : (row.artist + " — " + row.title);
    });

    return {
      chartType,
      chartDate,
      formattedDate: bucket.formattedDate,
      year: bucket.year,
      month: chartDate.slice(5, 7),
      preview,
      matchText: normalizeChartSearchText(
        [chartDate, bucket.formattedDate, bucket.year, bucket.tokens.join(" ")].join(" ")
      ),
      dateText: normalizeChartSearchText(bucket.formattedDate + " " + chartDate),
    };
  });

  state.chartSearchIndex[chartType] = entries;
  return entries;
}

function scoreChartSearchEntry(entry, normalizedQuery, queryTokens) {
  if (!entry || !normalizedQuery) return 0;

  let score = 0;
  if (normalizeChartSearchText(entry.chartDate) === normalizedQuery) score += 16;
  if (entry.year === normalizedQuery) score += 14;
  if (entry.dateText.includes(normalizedQuery)) score += 10;
  if (entry.matchText.includes(normalizedQuery)) score += 7;

  let tokenMatches = 0;
  for (let i = 0; i < queryTokens.length; i += 1) {
    const token = queryTokens[i];
    if (!token) continue;
    if (entry.dateText.includes(token)) {
      score += 2;
      tokenMatches += 1;
    } else if (entry.matchText.includes(token)) {
      score += 1;
      tokenMatches += 1;
    }
  }

  if (queryTokens.length && tokenMatches === queryTokens.length) {
    score += 3;
  }

  return score;
}

function parseChartSearchQuery(query) {
  const normalizedQuery = normalizeChartSearchText(query);
  const tokens = normalizedQuery.split(" ").filter(Boolean);
  if (!tokens.length) {
    return {
      normalizedQuery: "",
      queryTokens: [],
      year: "",
      month: "",
      filteredQuery: "",
      filteredTokens: [],
    };
  }

  let year = "";
  const tokensWithoutYear = [];
  for (let i = 0; i < tokens.length; i += 1) {
    const token = tokens[i];
    if (!year && /^\d{4}$/.test(token)) {
      year = token;
      continue;
    }
    tokensWithoutYear.push(token);
  }

  let month = "";
  const filteredTokens = [];
  for (let i = 0; i < tokensWithoutYear.length; i += 1) {
    const token = tokensWithoutYear[i];
    if (
      year
      && !month
      && token.length >= 3
    ) {
      const matchedMonth = MONTH_SEARCH_OPTIONS.find(function (option) {
        return option.full.startsWith(token) || option.short.startsWith(token);
      });
      if (matchedMonth) {
        month = matchedMonth.value;
        continue;
      }
    }
    filteredTokens.push(token);
  }

  return {
    normalizedQuery,
    queryTokens: tokens,
    year,
    month,
    filteredQuery: filteredTokens.join(" "),
    filteredTokens,
  };
}

function currentChartSearchResults() {
  const parsedQuery = parseChartSearchQuery(state.chartSearchQuery);
  if (!parsedQuery.normalizedQuery) return [];

  const searchEntries = buildChartSearchIndex(currentChartType()).filter(function (entry) {
    if (parsedQuery.year && entry.year !== parsedQuery.year) return false;
    if (parsedQuery.year && parsedQuery.month && entry.month !== parsedQuery.month) return false;
    return true;
  });

  if (!parsedQuery.year) {
    return searchEntries
      .map(function (entry) {
        return {
          entry,
          score: scoreChartSearchEntry(entry, parsedQuery.normalizedQuery, parsedQuery.queryTokens),
          time: chartDateValue(entry.chartDate) || 0,
        };
      })
      .filter(function (candidate) {
        return candidate.score > 0;
      })
      .sort(function (a, b) {
        if (b.score !== a.score) return b.score - a.score;
        return b.time - a.time;
      })
      .map(function (candidate) {
        return candidate.entry;
      });
  }

  if (!parsedQuery.filteredQuery) {
    return searchEntries
      .slice()
      .sort(function (a, b) {
        return (chartDateValue(b.chartDate) || 0) - (chartDateValue(a.chartDate) || 0);
      });
  }

  return searchEntries
    .map(function (entry) {
      return {
        entry,
        score: scoreChartSearchEntry(entry, parsedQuery.filteredQuery, parsedQuery.filteredTokens),
        time: chartDateValue(entry.chartDate) || 0,
      };
    })
    .filter(function (candidate) {
      return candidate.score > 0;
    })
    .sort(function (a, b) {
      if (b.score !== a.score) return b.score - a.score;
      return b.time - a.time;
    })
    .map(function (candidate) {
      return candidate.entry;
    });
}

function renderChartSearchResults() {
  if (!el.chartSearchResults) return;
  if (el.chartSearchInput && el.chartSearchInput.value !== String(state.chartSearchQuery || "")) {
    el.chartSearchInput.value = String(state.chartSearchQuery || "");
  }

  const query = String(state.chartSearchQuery || "").trim();
  if (!query) {
    el.chartSearchResults.hidden = true;
    el.chartSearchResults.innerHTML = "";
    syncWorklistPanelPosition();
    return;
  }

  const results = currentChartSearchResults();
  if (!results.length) {
    el.chartSearchResults.hidden = false;
    el.chartSearchResults.innerHTML = '<p class="chart-search-empty">No charts match this search yet.</p>';
    syncWorklistPanelPosition();
    return;
  }

  el.chartSearchResults.hidden = false;
  el.chartSearchResults.innerHTML = results.map(function (entry) {
    const preview = entry.preview.map(function (line) {
      return '<li>' + esc(line) + "</li>";
    }).join("");
    return '<button type="button" class="chart-search-card" data-chart-search-date="' + esc(entry.chartDate) + '">' +
      '<span class="chart-search-card-kicker">' + esc(chartTypeLabel(entry.chartType)) + "</span>" +
      '<span class="chart-search-card-date">' + esc(entry.formattedDate) + "</span>" +
      '<ul class="chart-search-card-preview">' + preview + "</ul>" +
    "</button>";
  }).join("");
  syncWorklistPanelPosition();
}

function syncSelectorState(options) {
  const opts = options || {};
  const chartType = currentChartType();
  const years = availableYears(chartType);
  let year = opts.preferredYear != null ? String(opts.preferredYear) : currentYear();
  if (!years.includes(year)) {
    year = years[years.length - 1] || "";
  }
  state.currentYear = year;

  let issueDate = opts.preferredDate != null ? String(opts.preferredDate) : currentDate();
  const dates = availableDates(chartType, state.currentYear);
  if (!dates.includes(issueDate)) {
    issueDate = closestAvailableDate(issueDate, dates) || dates[dates.length - 1] || "";
  }
  state.currentMonth = issueDate ? dateParts(issueDate).month : "";
  state.currentDate = issueDate;

  renderSelectorButtons(
    el.chartTypeButtons,
    ["songs", "albums"],
    chartType,
    function (value) {
      return value === "albums" ? "Albums" : "Songs";
    },
    async function (value) {
      if (value === currentChartType()) return;
      state.currentChartType = value;
      state.selected = null;
      state.trackMode = false;
      state.videoPlayerOpen = false;
      state.trackedSelectionKey = "";
      state.trackedSelectionLabel = "";
      state.trackedSelectionMissing = false;
      state.pendingSelectionScroll = false;
      state.currentMonth = "";
      state.detailSheetOpen = false;
      state.historyTimeline = "upto";
      if (state.usingBootstrapData && !state.fullMasterLoaded) {
        const loaded = await ensureFullMasterLoaded();
        if (!loaded) return;
      }
      syncSelectorState();
      renderChart();
    }
  );

  renderTrackModeToggle();
}

function goToChartDate(chartType, chartDate, options) {
  const normalizedDate = normalizeChartDate(chartDate);
  if (!normalizedDate) return false;

  const parts = dateParts(normalizedDate);
  if (!parts.date) return false;

  const opts = options || {};
  state.selected = null;
  state.pendingSelectionScroll = Boolean(chartType === "songs" && trackModeEnabled() && state.trackedSelectionKey);
  state.detailSheetOpen = false;
  state.historyTimeline = "upto";
  state.currentChartType = chartType;
  state.currentYear = parts.year;
  state.currentMonth = parts.month;
  state.currentDate = parts.date;

  if (opts.clearSearch) {
    state.chartSearchQuery = "";
    if (el.chartSearchInput) el.chartSearchInput.value = "";
  }

  syncSelectorState({
    preferredYear: parts.year,
    preferredMonth: parts.month,
    preferredDate: parts.date,
  });
  renderChart();
  renderChartSearchResults();
  return true;
}

async function navigateIssue(direction) {
  const chartType = currentChartType();
  let navigation = currentIssueNavigationState(chartType);
  let targetDate = direction < 0 ? navigation.previousDate : navigation.nextDate;
  if (!targetDate && state.usingBootstrapData && !state.fullMasterLoaded) {
    const loaded = await ensureFullMasterLoaded();
    if (!loaded) return;
    navigation = currentIssueNavigationState(chartType);
    targetDate = direction < 0 ? navigation.previousDate : navigation.nextDate;
  }
  if (!targetDate) return;
  goToChartDate(chartType, targetDate);
}

function rowClassNames(row) {
  const classes = [];
  const rank = toNumber(row && row.rank);
  if (rank != null && rank > 0) {
    const band = Math.floor((rank - 1) / 10);
    classes.push(band % 2 === 0 ? "band-even" : "band-odd");
    if (rank > 10 && (rank - 1) % 10 === 0) {
      classes.push("band-start");
      if (rank === 11) {
        classes.push("band-start-top");
      } else if (rank <= 61) {
        classes.push("band-start-mid");
      } else {
        classes.push("band-start-low");
      }
    }
  }
  if (row && row.rank === 1) classes.push("number-one");
  if (row && row.rank <= 10) classes.push("top-10");
  return classes.join(" ");
}

function renderChartHeader(chartType) {
  const issueDate = currentDate();
  const rows = getChartRows(chartType, issueDate);
  el.contextKicker.textContent = chartTypeLabel(chartType);
  el.contextTitle.textContent = issueDate ? formatIssueDate(issueDate) : "No chart date available";
  let meta = rows.length
    ? rows.length + " rows" + (chartType === "songs" ? " · historical issue data" : " · Billboard 200 subset")
    : "No rows for the selected date";
  if (chartType === "songs" && trackModeEnabled() && state.trackedSelectionMissing) {
    meta += " · " + trackedSelectionMessage();
  }
  el.contextMeta.textContent = meta;
}

function renderChartNavigation(chartType) {
  const navigation = currentIssueNavigationState(chartType);
  if (el.chartNavLabel) {
    el.chartNavLabel.textContent = navigation.label;
  }
  if (el.chartNavPrev) {
    el.chartNavPrev.disabled = !navigation.hasPrevious;
  }
  if (el.chartNavNext) {
    el.chartNavNext.disabled = !navigation.hasNext;
  }
}

function historyTimelineLabel() {
  return state.historyTimeline === "full" ? "Full run" : "Up to this week";
}

function renderHistoryTimelineToggle() {
  const uptoActive = state.historyTimeline !== "full";
  const fullActive = state.historyTimeline === "full";
  return '<div class="history-toggle">' +
    '<span class="history-toggle-label">Timeline</span>' +
    '<div class="history-toggle-buttons" role="radiogroup" aria-label="Timeline">' +
      '<button type="button" class="history-toggle-button' + (uptoActive ? " active" : "") + '" data-history-timeline="upto" aria-pressed="' + (uptoActive ? "true" : "false") + '">' +
        "Up to this week" +
      "</button>" +
      '<button type="button" class="history-toggle-button' + (fullActive ? " active" : "") + '" data-history-timeline="full" aria-pressed="' + (fullActive ? "true" : "false") + '">' +
        "Full run" +
      "</button>" +
    "</div>" +
  "</div>";
}

function historyEntryDate(entry) {
  return normalizeChartDate(entry && (entry.chart_date || entry.date));
}

function buildHistorySeries(history, selectedDate) {
  const selectedTime = chartDateValue(selectedDate);
  const selectedKey = normalizeChartDate(selectedDate);
  const chronological = history
    .slice()
    .map(function (entry) {
      return {
        ...entry,
        chart_date: historyEntryDate(entry),
        rank: toNumber(entry && entry.rank),
        last_week: toNumber(entry && entry.last_week),
        peak: toNumber(entry && entry.peak),
        time: chartDateValue(historyEntryDate(entry)),
      };
    })
    .filter(function (entry) {
      return Boolean(entry.chart_date) && entry.time != null;
    })
    .sort(function (a, b) {
      return a.time - b.time;
    });

  if (!chronological.length) {
    return {
      selectedDate: selectedKey,
      selectedTime,
      selectedEntry: null,
      allAsc: [],
      visibleAsc: [],
      visibleDesc: [],
    };
  }

  const derived = [];
  let runningPeak = null;

  for (let i = 0; i < chronological.length; i += 1) {
    const entry = chronological[i];
    if (entry.rank != null) {
      runningPeak = runningPeak == null ? entry.rank : Math.min(runningPeak, entry.rank);
    }
    const prior = derived[i - 1] || null;
    derived.push({
      ...entry,
      peak: entry.peak != null ? entry.peak : (runningPeak != null ? runningPeak : null),
      last_week: entry.last_week != null ? entry.last_week : (prior && prior.rank != null ? prior.rank : null),
      weeks_on_chart: i + 1,
    });
  }

  const visibleAsc = derived
    .filter(function (entry) {
      if (state.historyTimeline === "full") return true;
      if (selectedTime == null) return true;
      return entry.time <= selectedTime;
    })
    .slice();

  const visibleDesc = visibleAsc
    .slice()
    .sort(function (a, b) {
      return b.time - a.time;
    });

  const selectedEntry = derived.find(function (entry) {
    return entry.chart_date === selectedKey;
  }) || null;

  return {
    selectedDate: selectedKey,
    selectedTime,
    selectedEntry,
    allAsc: derived,
    visibleAsc,
    visibleDesc,
  };
}

function currentTrackedSong() {
  return state.trackedSelectionKey ? state.songByTrackKey.get(state.trackedSelectionKey) || null : null;
}

function movementMetaFromCode(code) {
  if (code === "UP") return { label: "▲", className: "up" };
  if (code === "DOWN") return { label: "▼", className: "down" };
  if (code === "SAME") return { label: "→", className: "same" };
  if (code === "NEW") return { label: "NEW", className: "new" };
  if (code === "RE") return { label: "RE", className: "new" };
  if (code === "OUT") return { label: "OUT", className: "out" };
  return { label: "—", className: "same" };
}

function formatRankLabel(value, fallback) {
  const numeric = toNumber(value);
  if (numeric != null && numeric > 0) return "#" + numeric;
  return fallback || "—";
}

function describeTrackedSongState(chartDate) {
  const song = currentTrackedSong();
  if (!song) return null;

  const series = buildHistorySeries(songHistory(song), chartDate);
  const allAsc = series.allAsc || [];
  const selectedTime = series.selectedTime;
  const entriesToDate = allAsc.filter(function (entry) {
    return selectedTime == null || entry.time <= selectedTime;
  });
  const currentEntry = series.selectedEntry;
  const latestEntryToDate = entriesToDate.length ? entriesToDate[entriesToDate.length - 1] : null;
  const firstEntry = allAsc[0] || null;
  const lastEntry = allAsc.length ? allAsc[allAsc.length - 1] : null;

  let peakToDate = null;
  for (let i = 0; i < entriesToDate.length; i += 1) {
    const rank = toNumber(entriesToDate[i] && entriesToDate[i].rank);
    if (rank == null) continue;
    peakToDate = peakToDate == null ? rank : Math.min(peakToDate, rank);
  }

  if (currentEntry) {
    const movementCode = movementValue(currentEntry);
    return {
      song,
      onChart: true,
      stateLabel: "On chart",
      currentRank: formatRankLabel(currentEntry.rank),
      previousRank: formatRankLabel(currentEntry.last_week, "NEW"),
      movementCode,
      peak: formatRankLabel(currentEntry.peak != null ? currentEntry.peak : peakToDate),
      weeks: currentEntry.weeks_on_chart != null ? String(currentEntry.weeks_on_chart) : "—",
      movement: movementMetaFromCode(movementCode),
    };
  }

  let stateLabel = "Off chart";
  if (!entriesToDate.length) {
    stateLabel = firstEntry && selectedTime != null && selectedTime < firstEntry.time ? "Not on chart yet" : "Song not on chart";
  } else if (lastEntry && selectedTime != null && selectedTime > lastEntry.time) {
    stateLabel = "Dropped off chart";
  }

  return {
    song,
    onChart: false,
    stateLabel,
    currentRank: "OUT",
    previousRank: formatRankLabel(latestEntryToDate && latestEntryToDate.rank),
    movementCode: "OUT",
    peak: formatRankLabel(peakToDate),
    weeks: latestEntryToDate && latestEntryToDate.weeks_on_chart != null ? String(latestEntryToDate.weeks_on_chart) : "0",
    movement: movementMetaFromCode("OUT"),
  };
}

function renderTrackModeToggle() {
  if (!el.trackModeToggle) return;
  const showToggle = currentChartType() === "songs";
  el.trackModeToggle.hidden = !showToggle;
  if (!showToggle) return;
  el.trackModeToggle.textContent = "Track Mode: " + (state.trackMode ? "ON" : "OFF");
  el.trackModeToggle.classList.toggle("active", state.trackMode);
  el.trackModeToggle.setAttribute("aria-pressed", state.trackMode ? "true" : "false");
}

function renderTrackMetric(label, value, className) {
  return '<div class="track-metric">' +
    '<span class="track-metric-label">' + esc(label) + '</span>' +
    '<span class="track-metric-value' + (className ? " " + esc(className) : "") + '">' + esc(value) + "</span>" +
  "</div>";
}

function renderTrackStatus(chartType, selectedRow) {
  if (!el.trackStatus) return;
  if (chartType !== "songs" || !trackModeEnabled() || !currentDate()) {
    el.trackStatus.hidden = true;
    el.trackStatus.innerHTML = "";
    return;
  }

  const trackedState = describeTrackedSongState(currentDate());
  if (!trackedState) {
    el.trackStatus.hidden = false;
    el.trackStatus.className = "track-status";
    el.trackStatus.innerHTML =
      '<div class="track-status-card">' +
        '<div><p class="track-status-kicker">Track Mode</p><p class="track-status-title">Select a song to start tracking.</p></div>' +
      "</div>";
    return;
  }

  const title = trackedState.song && trackedState.song.title ? trackedState.song.title : (state.trackedSelectionLabel || "Tracked song");
  const artist = trackedState.song && (trackedState.song.artist_canonical || trackedState.song.artist)
    ? (trackedState.song.artist_canonical || trackedState.song.artist)
    : "";
  const isMissing = !trackedState.onChart;
  const movement = trackedState.movement || movementMetaFromCode(trackedState.movementCode);

  el.trackStatus.hidden = false;
  el.trackStatus.className = "track-status" + (isMissing ? " is-missing" : "");
  el.trackStatus.innerHTML =
    '<div class="track-status-card">' +
      '<div class="track-status-main">' +
        '<p class="track-status-kicker">Track Mode · ' + (state.trackMode ? "ON" : "OFF") + '</p>' +
        '<h3 class="track-status-title">' + esc(title) + "</h3>" +
        (artist ? '<p class="track-status-subtitle">' + esc(artist) + "</p>" : "") +
      "</div>" +
      '<div class="track-status-summary">' +
        '<span class="track-status-state">' + esc(trackedState.stateLabel) + "</span>" +
        '<span class="move ' + esc(movement.className) + '">' + esc(movement.label) + "</span>" +
      "</div>" +
      '<div class="track-metrics">' +
        renderTrackMetric("Current", trackedState.currentRank, isMissing ? "is-out" : "") +
        renderTrackMetric("Previous", trackedState.previousRank) +
        renderTrackMetric("Movement", movement.label, "move " + movement.className) +
        renderTrackMetric("Peak", trackedState.peak) +
        renderTrackMetric("Weeks", trackedState.weeks) +
      "</div>" +
    "</div>";
}

const HISTORY_GRAPH_DRAW_MS = 800;
const historyGraphAnimationState = new WeakMap();

function initHistoryGraphAnimation(rootEl) {
  if (!rootEl) return;

  const prevState = historyGraphAnimationState.get(rootEl);
  if (prevState) {
    if (prevState.rafId) window.cancelAnimationFrame(prevState.rafId);
    if (prevState.markerTimer) window.clearTimeout(prevState.markerTimer);
  }

  const animationState = { rafId: 0, markerTimer: 0 };
  historyGraphAnimationState.set(rootEl, animationState);

  function apply() {
    const paths = rootEl.querySelectorAll(".history-graph--editorial .history-graph-line");
    if (!paths.length) return;

    const markers = rootEl.querySelectorAll(".history-graph--editorial .chart-journey-current-week-marker");
    let needsRetry = false;

    for (let i = 0; i < markers.length; i += 1) {
      markers[i].style.transition = "none";
      markers[i].style.opacity = "0";
    }

    for (let i = 0; i < paths.length; i += 1) {
      const path = paths[i];
      if (!path || typeof path.getTotalLength !== "function") continue;
      const len = path.getTotalLength();
      if (len <= 0) {
        needsRetry = true;
        continue;
      }
      path.style.transition = "none";
      path.style.strokeDasharray = String(len);
      path.style.strokeDashoffset = String(len);
      path.getBoundingClientRect();
    }

    if (needsRetry) {
      animationState.rafId = window.requestAnimationFrame(apply);
      return;
    }

    animationState.rafId = window.requestAnimationFrame(function () {
      for (let i = 0; i < paths.length; i += 1) {
        paths[i].style.transition = "stroke-dashoffset 0.8s ease-out";
        paths[i].style.strokeDashoffset = "0";
      }

      animationState.markerTimer = window.setTimeout(function () {
        for (let i = 0; i < markers.length; i += 1) {
          markers[i].style.transition = "opacity 0.18s ease-out";
          markers[i].style.opacity = "1";
        }
      }, HISTORY_GRAPH_DRAW_MS);
    });
  }

  apply();
}

const EDITORIAL_HISTORY_MAX_POINTS = 20;

function buildEditorialPlottedSeries(series) {
  const withRank = series.visibleAsc.filter(function (entry) {
    return entry.rank != null;
  });
  if (!withRank.length) return null;

  let activeSeries;
  if (state.historyTimeline === "full") {
    activeSeries = withRank.slice();
  } else {
    let idx = withRank.findIndex(function (e) {
      return e.chart_date === series.selectedDate;
    });
    if (idx === -1) idx = withRank.length - 1;
    activeSeries = withRank.slice(0, idx + 1);
  }

  let plottedSeries;
  if (activeSeries.length <= EDITORIAL_HISTORY_MAX_POINTS) {
    plottedSeries = activeSeries.slice();
  } else {
    const bucketSize = Math.ceil(activeSeries.length / EDITORIAL_HISTORY_MAX_POINTS);
    plottedSeries = [];
    for (let i = 0; i < activeSeries.length; i += bucketSize) {
      const bucket = activeSeries.slice(i, i + bucketSize);
      const bestPoint = bucket.reduce(function (best, current) {
        return current.rank < best.rank ? current : best;
      });
      plottedSeries.push(bestPoint);
    }
  }

  return plottedSeries;
}

function editionSmoothPathFromPoints(points) {
  if (!points.length) return "";
  if (points.length === 1) {
    return "M " + points[0].x.toFixed(2) + " " + points[0].y.toFixed(2);
  }
  let d = "M " + points[0].x.toFixed(2) + " " + points[0].y.toFixed(2);
  for (let i = 0; i < points.length - 1; i += 1) {
    const p0 = i > 0 ? points[i - 1] : points[i];
    const p1 = points[i];
    const p2 = points[i + 1];
    const p3 = i < points.length - 2 ? points[i + 2] : points[i + 1];
    const cp1x = p1.x + (p2.x - p0.x) / 6;
    const cp1y = p1.y + (p2.y - p0.y) / 6;
    const cp2x = p2.x - (p3.x - p1.x) / 6;
    const cp2y = p2.y - (p3.y - p1.y) / 6;
    d +=
      " C " +
      cp1x.toFixed(2) +
      " " +
      cp1y.toFixed(2) +
      " " +
      cp2x.toFixed(2) +
      " " +
      cp2y.toFixed(2) +
      " " +
      p2.x.toFixed(2) +
      " " +
      p2.y.toFixed(2);
  }
  return d;
}

function renderEditorialHistoryGraphSvg(series, plottedRows) {
  const width = 420;
  const height = 240;
  const padding = { top: 18, right: 14, bottom: 24, left: 46 };
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;
  const baselineTop = padding.top;
  const baselineBottom = padding.top + plotHeight;
  const baselineLeft = padding.left;
  const baselineRight = padding.left + plotWidth;
  const realRows = plottedRows;
  const n = realRows.length;
  if (n === 0) return "";

  const ceiling = Math.max(
    currentChartType() === "albums" ? 200 : 100,
    realRows.reduce(function (max, entry) {
      return Math.max(max, entry.rank || 0);
    }, 0)
  );

  function pointY(rank) {
    if (ceiling <= 1) return padding.top + plotHeight / 2;
    return padding.top + ((rank - 1) / (ceiling - 1)) * plotHeight;
  }

  const maxPts = EDITORIAL_HISTORY_MAX_POINTS;
  function pointX(i, realCount) {
    if (realCount <= 1) {
      return padding.left + (plotWidth * (1 / maxPts)) / 2;
    }
    return padding.left + (i / (maxPts - 1)) * plotWidth;
  }

  const coords = [];
  for (let i = 0; i < n; i += 1) {
    coords.push({
      x: pointX(i, n),
      y: pointY(realRows[i].rank) + (Math.random() * 3 - 1.5),
    });
  }

  const path = editionSmoothPathFromPoints(coords);
  const rankedRows = series.visibleAsc.filter(function (entry) {
    return entry.rank != null;
  });
  const currentWeekEntry = rankedRows.length ? rankedRows[rankedRows.length - 1] : null;
  let currentWeekLabelHtml = "";

  if (currentWeekEntry && coords.length) {
    const endPoint = coords[coords.length - 1];
    const currentWeek = currentWeekEntry.weeks_on_chart != null
      ? currentWeekEntry.weeks_on_chart
      : rankedRows.length;
    const markerRadius = 22;
    const markerSize = 48;
    const markerGap = 28;
    const markerEdgePad = markerRadius + 4;
    let markerCx = endPoint.x + markerGap;
    let markerCy = endPoint.y <= baselineTop + 34 ? endPoint.y + 24 : endPoint.y - 24;

    if (markerCx > baselineRight - markerEdgePad) markerCx = endPoint.x - markerGap;
    if (markerCx < baselineLeft + markerEdgePad) markerCx = endPoint.x + markerGap;

    markerCx = Math.max(baselineLeft + markerEdgePad, Math.min(baselineRight - markerEdgePad, markerCx));
    markerCy = Math.max(baselineTop + markerEdgePad, Math.min(baselineBottom - markerEdgePad, markerCy));

    currentWeekLabelHtml =
      '<svg class="chart-journey-current-week-marker" x="' +
      (markerCx - markerSize / 2).toFixed(2) +
      '" y="' +
      (markerCy - markerSize / 2).toFixed(2) +
      '" width="' +
      markerSize.toFixed(2) +
      '" height="' +
      markerSize.toFixed(2) +
      '" viewBox="0 0 48 48" preserveAspectRatio="xMidYMid meet" aria-hidden="true">' +
      '<g transform="translate(24 24)">' +
      '<circle cx="0" cy="0" r="' +
      markerRadius.toFixed(2) +
      '" fill="rgba(247,239,223,1)" stroke="#7a1e1e" stroke-width="3.4"></circle>' +
      '<text x="0" y="0" fill="#7a1e1e" font-family="inherit" font-weight="700" letter-spacing="0.02em" text-anchor="middle" dominant-baseline="middle">' +
      '<tspan x="0" dy="-6" font-size="8.2">WK</tspan>' +
      '<tspan x="0" dy="14" font-size="11.2">' +
      esc(currentWeek) +
      "</tspan>" +
      "</text>" +
      "</g>" +
      "</svg>";
  }

  const backgroundHtml =
    '<rect class="chart-journey-plot-bg" x="' +
    baselineLeft.toFixed(2) +
    '" y="' +
    baselineTop.toFixed(2) +
    '" width="' +
    plotWidth.toFixed(2) +
    '" height="' +
    plotHeight.toFixed(2) +
    '"></rect>';

  const ranksToLabel = [1];
  const midRank = Math.round((ceiling + 1) / 2);
  if (midRank > 1 && midRank < ceiling) {
    ranksToLabel.push(midRank);
  }
  if (ceiling > 1 && ranksToLabel.indexOf(ceiling) === -1) {
    ranksToLabel.push(ceiling);
  }

  let rankLabelsHtml = "";
  let rankLinesHtml = "";
  for (let li = 0; li < ranksToLabel.length; li += 1) {
    const r = ranksToLabel[li];
    if (r > ceiling) continue;
    const yLine = pointY(r);
    const yy = yLine + 4;
    rankLinesHtml +=
      '<line class="chart-journey-rank-line" x1="' +
      baselineLeft.toFixed(2) +
      '" y1="' +
      yLine.toFixed(2) +
      '" x2="' +
      baselineRight.toFixed(2) +
      '" y2="' +
      yLine.toFixed(2) +
      '"></line>';
    rankLabelsHtml +=
      '<text class="chart-journey-rank-label" x="' +
      (baselineLeft - 6) +
      '" y="' +
      yy.toFixed(2) +
      '" text-anchor="end">#' +
      esc(r) +
      "</text>";
  }

  return (
    '<svg class="history-graph history-graph--editorial" viewBox="0 0 ' +
    width +
    " " +
    height +
    '" preserveAspectRatio="none" role="img" aria-label="Rank over time graph">' +
    backgroundHtml +
    '<g class="chart-journey-rank-lines" aria-hidden="true">' +
    rankLinesHtml +
    "</g>" +
    '<line class="history-graph-axis" x1="' +
    baselineLeft +
    '" y1="' +
    baselineTop +
    '" x2="' +
    baselineLeft +
    '" y2="' +
    baselineBottom +
    '"></line>' +
    '<line class="history-graph-axis" x1="' +
    baselineLeft +
    '" y1="' +
    baselineBottom +
    '" x2="' +
    baselineRight +
    '" y2="' +
    baselineBottom +
    '"></line>' +
    rankLabelsHtml +
    '<path class="history-graph-line" d="' +
    path +
    '"></path>' +
    currentWeekLabelHtml +
    "</svg>"
  );
}

function renderHistoryGraph(series) {
  const plottedRows = buildEditorialPlottedSeries(series);
  if (!plottedRows) return "";

  const svgBlock = renderEditorialHistoryGraphSvg(series, plottedRows);

  const card =
    '<div class="history-graph-card history-graph-card--editorial history-graph-card--edition">' +
    svgBlock +
    "</div>";

  return (
    '<div class="chart-journey">' +
    '<div class="chart-journey-label">CHART JOURNEY</div>' +
    card +
    "</div>"
  );
}

function renderHistoryTable(series) {
  const rows = series.visibleDesc;
  if (!rows.length) {
    return '<p class="empty-inline">No chart history is available for ' + esc(historyTimelineLabel().toLowerCase()) + ".</p>";
  }

  let html = '<div class="history-table-wrap"><table class="mini-table history-table"><thead><tr><th>Date</th><th class="num">#</th><th class="num">Last</th><th class="num">Peak</th><th class="num">Weeks</th></tr></thead><tbody>';
  for (let i = 0; i < rows.length; i += 1) {
    const row = rows[i];
    const rowDate = row.chart_date;
    const className = rowDate === series.selectedDate ? ' class="is-current"' : "";
    html += "<tr" + className + ">" +
      "<td>" + esc(rowDate) + "</td>" +
      '<td class="num">' + esc(row.rank != null ? row.rank : "—") + "</td>" +
      '<td class="num">' + esc(row.last_week != null && row.last_week !== 0 ? row.last_week : "—") + "</td>" +
      '<td class="num">' + esc(row.peak != null ? row.peak : "—") + "</td>" +
      '<td class="num">' + esc(row.weeks_on_chart != null ? row.weeks_on_chart : "—") + "</td>" +
      "</tr>";
  }
  html += "</tbody></table></div>";
  return html;
}

function getEditionBlurb(row) {
  const title = row && row.title != null ? String(row.title) : "This track";
  const rank = toNumber(row && row.rank);
  const improvement = rankImprovement(row);
  const isNew = movementValue(row) === "NEW";
  const rankLabel = rank != null ? String(rank) : "—";

  if (isNew && rank != null) {
    return title + " enters at #" + rankLabel + " this week, marking its chart debut.";
  }

  if (improvement > 0 && rank != null) {
    return title + " climbs to #" + rankLabel + ", rising " + improvement + " spots from last week.";
  }

  if (improvement < 0 && rank != null) {
    return title + " eases to #" + rankLabel + " this week, down " + Math.abs(improvement) + " spots.";
  }

  if (rank != null) {
    return title + " holds at #" + rankLabel + ", extending its run on the chart.";
  }

  return title + " on the chart this week.";
}

function getChartFallbackBlurb(chartType, row, currentEntry) {
  const subject = chartType === "albums" ? "This album" : "This track";
  const rank = toNumber(currentEntry && currentEntry.rank != null ? currentEntry.rank : row && row.rank);
  const lastWeek = toNumber(currentEntry && currentEntry.last_week != null ? currentEntry.last_week : row && row.last_week);
  const peak = toNumber(currentEntry && currentEntry.peak != null ? currentEntry.peak : row && row.peak);

  if (rank == null) {
    return subject + " is on the chart this week.";
  }

  let movementText = "";
  if (lastWeek == null || lastWeek === 0) {
    movementText = "making a new appearance";
  } else if (lastWeek > rank) {
    movementText = "up from #" + lastWeek + " last week";
  } else if (lastWeek < rank) {
    movementText = "down from #" + lastWeek + " last week";
  } else {
    movementText = "holding from #" + lastWeek + " last week";
  }

  let sentence = subject + " is at #" + rank + " this week";
  if (movementText) {
    sentence += ", " + movementText;
  }
  if (peak != null) {
    sentence += ", with a peak of #" + peak;
  }
  sentence += ".";
  return sentence;
}

function buildDetailPanelData(chartType, row, chartDate, mode) {
  if (!row) return null;

  let title = "";
  let artist = "";
  let historySeries;
  let mediaTracks = [];

  if (chartType === "albums") {
    const album = row.retroverse_album_id ? state.albumById.get(row.retroverse_album_id) : null;
    if (!album) return null;
    title = album.album_title || "Untitled album";
    artist = album.artist_canonical || album.artist || "Unknown artist";
    historySeries = buildHistorySeries(albumHistory(album), chartDate);
    mediaTracks = linkedSongsForAlbum(row.retroverse_album_id)
      .map(function (song) {
        return song && song.title ? String(song.title) : "";
      })
      .filter(Boolean);
  } else {
    const song = row.retroverse_id ? state.songById.get(row.retroverse_id) : null;
    if (!song) return null;
    title = song.title || "Untitled";
    artist = song.artist_canonical || song.artist || "Unknown artist";
    historySeries = buildHistorySeries(songHistory(song), chartDate);
  }

  const currentEntry = historySeries.selectedEntry;
  const narrative = mode === "editions"
    ? getEditionBlurb(row)
    : getChartFallbackBlurb(chartType, row, currentEntry);
  const currentRank = toNumber(currentEntry && currentEntry.rank != null ? currentEntry.rank : row.rank);
  const lastWeek = toNumber(currentEntry && currentEntry.last_week != null ? currentEntry.last_week : row.last_week);
  const peak = toNumber(currentEntry && currentEntry.peak != null ? currentEntry.peak : row.peak);
  const weeks = toNumber(currentEntry && currentEntry.weeks_on_chart != null ? currentEntry.weeks_on_chart : row.weeks_on_chart);
  const videoEntry = primaryResolvedVideoEntry(chartType, row);
  const thumbUrl = safePublicUrl(
    (videoEntry && videoEntry.thumbnailUrl) ||
    (videoEntry && videoEntry.video && videoEntry.video.thumbnail_url) ||
    ""
  );
  const inlineStats = [
    "Current " + (currentRank != null ? ("#" + currentRank) : "—"),
    "Last " + (lastWeek != null && lastWeek !== 0 ? ("#" + lastWeek) : "NEW"),
    "Peak " + (peak != null ? ("#" + peak) : "—"),
    (weeks != null ? weeks : "—") + " weeks",
  ].join(" · ");

  return {
    detailType: chartType === "albums" ? "album" : "song",
    title,
    artist,
    narrative,
    inlineStats,
    thumbUrl,
    mediaTracks,
    hasPlayableVideo: rowHasPlayableVideo(chartType, row),
    presentationMode: mode === "editions" ? "summary" : "charts",
    historySeries,
  };
}

function renderDetailPanel(detailData) {
  if (!detailData) return "";

  const isAlbum = detailData.detailType === "album";
  let mediaHtml = "";
  let videoButtonHtml = "";

  if (isAlbum) {
    const tracks = Array.isArray(detailData.mediaTracks) ? detailData.mediaTracks : [];
    let trackItemsHtml = "";
    for (let i = 0; i < tracks.length; i += 1) {
      trackItemsHtml += "<li>" + esc(tracks[i]) + "</li>";
    }
    mediaHtml = tracks.length
      ? '<section class="edition-detail-tracklist"><h3 class="edition-detail-tracklist-title">Tracklist</h3><ol class="edition-detail-tracklist-list">' + trackItemsHtml + "</ol></section>"
      : '<section class="edition-detail-tracklist edition-detail-tracklist--empty"><h3 class="edition-detail-tracklist-title">Tracklist</h3><p class="edition-detail-tracklist-empty">No tracklist available.</p></section>';
  } else {
    mediaHtml = detailData.thumbUrl
      ? '<figure class="edition-detail-visual"><img class="edition-detail-visual-img" src="' + esc(detailData.thumbUrl) + '" alt="" loading="lazy" /></figure>'
      : '<figure class="edition-detail-visual edition-detail-visual--empty"><div class="edition-detail-visual-fallback">♪</div></figure>';
    videoButtonHtml = detailData.hasPlayableVideo
      ? '<button type="button" class="edition-detail-video-open" data-detail-open-video="true">Play Video</button>'
      : "";
  }

  return (
    '<div class="edition-detail edition-detail--' + esc(detailData.presentationMode || "charts") + '">' +
    '<section class="edition-detail-media">' +
    mediaHtml +
    videoButtonHtml +
    "</section>" +
    '<header class="edition-detail-hero">' +
    '<h2 class="edition-detail-title">' +
    esc(detailData.title) +
    "</h2>" +
    '<p class="edition-detail-artist">' +
    esc(detailData.artist) +
    "</p>" +
    "</header>" +
    '<section class="edition-detail-history">' +
    renderHistoryTimelineToggle() +
    renderHistoryGraph(detailData.historySeries) +
    "</section>" +
    '<p class="edition-detail-inline-stats">' +
    esc(detailData.inlineStats) +
    "</p>" +
    '<p class="edition-detail-lede">' +
    esc(detailData.narrative) +
    "</p>" +
    '<details class="edition-detail-history-table edition-detail-history-table--collapsible">' +
    '<summary>Chart History</summary>' +
    renderHistoryTable(detailData.historySeries) +
    "</details>" +
    "</div>"
  );
}

function buildChartDetailHtml(chartType, row) {
  return renderDetailPanel(buildDetailPanelData(chartType, row, currentDate(), "charts"));
}

function buildEditionDetailHtml(chartType, row) {
  return renderDetailPanel(buildDetailPanelData(chartType, row, currentDate(), "editions"));
}

function currentSelectedRow() {
  const chartType = currentChartType();
  const issueDate = currentDate();
  if (!issueDate) return null;
  const rows = getChartRows(chartType, issueDate);
  return findSelectedRow(chartType, rows);
}

function bindHistoryToggle(container) {
  if (!container) return;
  const buttons = container.querySelectorAll("[data-history-timeline]");
  for (let i = 0; i < buttons.length; i += 1) {
    buttons[i].addEventListener("click", function () {
      const nextMode = this.getAttribute("data-history-timeline");
      if (!nextMode || nextMode === state.historyTimeline) return;
      state.historyTimeline = nextMode;
      const activeRow = currentSelectedRow();
      if (!activeRow) return;
      if (state.detailSheetOpen) {
        renderDetailSheet(currentChartType(), activeRow);
        return;
      }
    });
  }
}

function closeDetailSheet() {
  state.detailSheetOpen = false;
  document.body.classList.remove("sheet-open");
  el.detailSheet.hidden = true;
  el.detailSheetContent.innerHTML = "";
}

function renderDetailSheet(chartType, row) {
  const html = viewMode === "charts" ? buildChartDetailHtml(chartType, row) : buildEditionDetailHtml(chartType, row);
  if (!html) {
    closeDetailSheet();
    return;
  }

  state.detailSheetOpen = true;
  el.detailSheetContent.innerHTML = html;
  el.detailSheet.hidden = false;
  document.body.classList.add("sheet-open");
  initHistoryGraphAnimation(el.detailSheetContent);
  bindHistoryToggle(el.detailSheetContent);
}

function findSelectedRow(chartType, rows) {
  const selection = state.selected;
  if (!selection) return null;
  for (let i = 0; i < rows.length; i += 1) {
    if (rowSelectionKey(chartType, rows[i]) === selection) {
      return rows[i];
    }
  }
  return null;
}

function findTrackedRow(rows) {
  const trackedKey = state.trackedSelectionKey;
  if (!trackedKey) return null;
  for (let i = 0; i < rows.length; i += 1) {
    if (trackedRowKey(rows[i]) === trackedKey) {
      return rows[i];
    }
  }
  return null;
}

function resolveSelectedRow(chartType, rows) {
  const selectedRow = findSelectedRow(chartType, rows);
  if (selectedRow) {
    if (chartType === "songs") state.trackedSelectionMissing = false;
    return selectedRow;
  }

  if (chartType === "songs" && trackModeEnabled() && state.trackedSelectionKey) {
    const trackedRow = findTrackedRow(rows);
    if (trackedRow) {
      state.selected = rowSelectionKey(chartType, trackedRow);
      state.trackedSelectionMissing = false;
      return trackedRow;
    }
    state.selected = null;
    state.trackedSelectionMissing = true;
    return null;
  }

  state.trackedSelectionMissing = false;
  state.selected = null;
  return null;
}

// Row selection stays shared; each layout decides how detail is presented.
function selectRow(chartType, row, options) {
  const wantsVideo = Boolean(options && options.openVideo && row && rowHasPlayableVideo(chartType, row));
  state.selected = row ? rowSelectionKey(chartType, row) : null;
  if (chartType === "songs" && row) {
    state.trackedSelectionKey = trackedRowKey(row);
    state.trackedSelectionLabel = (row.title || "Untitled") + " — " + (row.artist || "Unknown artist");
    state.trackedSelectionMissing = false;
  } else if (chartType !== "songs") {
    state.trackedSelectionKey = "";
    state.trackedSelectionLabel = "";
    state.trackedSelectionMissing = false;
  }
  state.pendingSelectionScroll = false;
  state.historyTimeline = "upto";
  state.videoPlayerOpen = wantsVideo;
  state.detailSheetOpen = Boolean(!wantsVideo && options && options.openSheet && row);
  renderChart();
}

function isRowActionTarget(event) {
  return Boolean(event && event.target && event.target.closest && event.target.closest(".rv-play, .rv-collect"));
}

function renderDesktopTable(chartType, rows) {
  if (!el.chartHead || !el.chartBody) return;
  const showVideo = true;
  const selectedKey = state.selected;

  el.chartHead.innerHTML =
    "<tr>" +
      '<th class="num">#</th>' +
      "<th>Title</th>" +
      "<th>Artist</th>" +
      '<th class="num">Last</th>' +
      '<th class="num">Peak</th>' +
      '<th class="num">Weeks</th>' +
      "<th>Move</th>" +
      (showVideo ? '<th class="num">Actions</th>' : "") +
    "</tr>";

  el.chartBody.innerHTML = "";
  const fragment = document.createDocumentFragment();

  for (let i = 0; i < rows.length; i += 1) {
    const row = rows[i];
    const tr = document.createElement("tr");
    const classNames = rowClassNames(row);
    const selectionKey = rowSelectionKey(chartType, row);
    const domKey = rowDataKey(row);
    const rank = toNumber(row && row.rank);
    if (classNames) tr.className = classNames;
    if (selectionKey && selectionKey === selectedKey) {
      tr.classList.add("selected");
    }
    if (domKey) tr.dataset.key = domKey;
    if (rank != null) tr.dataset.rank = String(rank);

    tr.innerHTML =
      '<td class="num chart-rank">' + esc(row.rank != null ? row.rank : "—") + "</td>" +
      '<td class="title-cell"><span class="chart-title">' + esc(row.title || "") + "</span></td>" +
      '<td class="artist-cell">' + esc(row.artist || "") + "</td>" +
      '<td class="num">' + esc(row.last_week != null && row.last_week !== 0 ? row.last_week : "—") + "</td>" +
      '<td class="num">' + esc(row.peak != null ? row.peak : "—") + "</td>" +
      '<td class="num">' + esc(row.weeks_on_chart != null ? row.weeks_on_chart : "—") + "</td>" +
      '<td><span class="move ' + esc(movementClass(row)) + '">' + esc(movementLabel(row)) + "</span></td>" +
      (showVideo ? '<td class="num">' + renderRowActionButtons(chartType, row) + "</td>" : "");

    tr.addEventListener("click", function (event) {
      if (isRowActionTarget(event)) return;
      selectRow(chartType, row);
    });

    fragment.appendChild(tr);
  }

  el.chartBody.appendChild(fragment);
}

function mobileSupportingMeta(row) {
  const peak = toNumber(row && row.peak);
  const weeks = toNumber(row && row.weeks_on_chart);
  const parts = [];
  if (peak != null) parts.push("Peak #" + peak);
  if (weeks != null) parts.push(weeks + " weeks");
  return parts.join(" · ");
}

function renderMobileList(chartType, rows) {
  el.chartMobileList.innerHTML = "";
  const selectedKey = state.selected;
  const fragment = document.createDocumentFragment();

  for (let i = 0; i < rows.length; i += 1) {
    const row = rows[i];
    const button = document.createElement("button");
    const selectionKey = rowSelectionKey(chartType, row);
    const classNames = rowClassNames(row);
    const domKey = rowDataKey(row);
    const rank = toNumber(row && row.rank);
    button.type = "button";
    button.className = "mobile-chart-row";
    if (classNames) button.classList.add(...classNames.split(" "));
    if (selectionKey && selectionKey === selectedKey) {
      button.classList.add("selected");
    }
    if (domKey) button.dataset.key = domKey;
    if (rank != null) button.dataset.rank = String(rank);

    button.innerHTML =
      '<span class="mobile-chart-rank">' + esc(row.rank != null ? row.rank : "—") + "</span>" +
      '<span class="mobile-chart-main">' +
        '<span class="mobile-chart-titleline">' +
          '<span class="mobile-chart-title">' + esc(row.title || "") + "</span>" +
          renderRowActionButtons(chartType, row) +
        "</span>" +
        '<span class="mobile-chart-artist">' + esc(row.artist || "") + "</span>" +
        '<span class="mobile-chart-meta">' + esc(mobileSupportingMeta(row)) + "</span>" +
      "</span>" +
      '<span class="mobile-chart-side">' +
        '<span class="move ' + esc(movementClass(row)) + '">' + esc(movementLabel(row)) + "</span>" +
      "</span>";

    button.addEventListener("click", function (event) {
      if (isRowActionTarget(event)) return;
      selectRow(chartType, row, { openSheet: true });
    });

    fragment.appendChild(button);
  }

  el.chartMobileList.appendChild(fragment);
}

function buildSummaryMediaCard(media) {
  const rank = toNumber(media && media.rank);
  const peak = toNumber(media && media.peak);
  const weeks = toNumber(media && media.weeks);
  const moveRaw = Number(media && media.move);
  const move = Number.isFinite(moveRaw) ? moveRaw : 0;
  const moveClass = move > 0 ? "rv-album-meta--move-up" : (move < 0 ? "rv-album-meta--move-down" : "rv-album-meta--move-flat");
  const moveLabel = move > 0 ? ("▲ +" + move) : (move < 0 ? ("▼ -" + Math.abs(move)) : "→");
  const title = media && media.title ? String(media.title) : "Untitled";
  const artist = media && media.artist ? String(media.artist) : "Unknown artist";
  const tracks = Array.isArray(media && media.tracks) ? media.tracks.slice(0, 3) : [];
  const type = media && media.type === "album" ? "album" : "song";
  const rowChartType = media && media.chartType
    ? media.chartType
    : (type === "album" ? "albums" : "songs");
  const actionRow = media && media.row ? media.row : media;

  const button = document.createElement("button");
  button.type = "button";
  button.className = "summary-module-row-button rv-album-card";
  button.classList.add(type === "album" ? "rv-album-card--album" : "rv-album-card--song");
  button.setAttribute("aria-label", "Open " + type + " detail for " + title + " by " + artist);
  if (media && media.isHero) {
    button.classList.add("rv-album-card--hero");
  }

  const top = document.createElement("span");
  top.className = "rv-card-top";

  const visualSlot = document.createElement("span");
  visualSlot.className = "rv-card-visual";

  const visualPlaceholder = document.createElement("span");
  visualPlaceholder.className = "rv-card-visual-placeholder";
  visualPlaceholder.textContent = type === "album" ? "ALB" : "SNG";

  const topRank = document.createElement("span");
  topRank.className = "rv-album-rank";
  topRank.textContent = "#" + (rank != null ? rank : "—");

  visualSlot.appendChild(visualPlaceholder);
  visualSlot.appendChild(topRank);

  const visual = document.createElement("span");
  visual.className = "rv-album-visual";
  const badge = document.createElement("span");
  badge.className = "rv-album-badge";
  badge.textContent = rank != null ? String(rank) : "—";
  visual.appendChild(badge);

  top.appendChild(visualSlot);
  top.appendChild(visual);

  const middle = document.createElement("span");
  middle.className = "rv-card-middle rv-album-main";

  const titleEl = document.createElement("span");
  titleEl.className = "rv-album-title";
  titleEl.textContent = title;

  const artistEl = document.createElement("span");
  artistEl.className = "rv-album-artist";
  artistEl.textContent = artist;

  const stats = document.createElement("span");
  stats.className = "rv-album-stats";

  const peakEl = document.createElement("span");
  peakEl.className = "rv-album-meta";
  peakEl.textContent = "Peak " + (peak != null ? ("#" + peak) : "—");

  const weeksEl = document.createElement("span");
  weeksEl.className = "rv-album-meta";
  weeksEl.textContent = (weeks != null ? weeks : "—") + " wks";

  const moveEl = document.createElement("span");
  moveEl.className = "rv-album-meta " + moveClass;
  moveEl.textContent = moveLabel;

  stats.appendChild(peakEl);
  stats.appendChild(weeksEl);
  stats.appendChild(moveEl);

  middle.appendChild(titleEl);
  middle.appendChild(artistEl);

  const bottom = document.createElement("span");
  bottom.className = "rv-card-bottom";

  const bottomMeta = document.createElement("span");
  bottomMeta.className = "rv-card-bottom-meta";
  bottomMeta.appendChild(stats);

  if (tracks.length) {
    const trackLabels = [];
    for (let i = 0; i < tracks.length; i += 1) {
      const track = tracks[i];
      const label = typeof track === "string"
        ? track
        : (track && track.title ? String(track.title) : "");
      if (!label) continue;
      trackLabels.push(label);
    }
    if (trackLabels.length) {
      const trackLine = document.createElement("span");
      trackLine.className = "rv-card-tracks";
      trackLine.textContent = "Tracks: " + trackLabels.slice(0, 3).join(" • ");
      bottomMeta.appendChild(trackLine);
    }
  }

  bottom.appendChild(bottomMeta);
  const bottomActions = document.createElement("span");
  bottomActions.className = "rv-card-bottom-actions";
  const actions = document.createElement("span");
  actions.className = "rv-album-actions";
  const actionsHtml = media && typeof media.actionsHtml === "string" && media.actionsHtml.trim()
    ? media.actionsHtml
    : renderRowActionButtons(rowChartType, actionRow);
  if (actionsHtml) {
    actions.innerHTML = actionsHtml;
  } else {
    actions.classList.add("rv-album-actions--empty");
  }
  bottomActions.appendChild(actions);
  bottom.appendChild(bottomActions);

  button.appendChild(top);
  button.appendChild(middle);
  button.appendChild(bottom);

  return button;
}

function buildAlbumSummaryCard(album) {
  return buildSummaryMediaCard(
    Object.assign({}, album, {
      type: "album",
      chartType: "albums",
      row: album && album.row ? album.row : album,
    })
  );
}

function buildSongSummaryCard(song) {
  return buildSummaryMediaCard(
    Object.assign({}, song, {
      type: "song",
      chartType: "songs",
      row: song && song.row ? song.row : song,
    })
  );
}

function renderSummaryCards(chartType, rows) {
  el.chartMobileList.innerHTML = "";
  const selectedKey = state.selected;
  const issueDate = currentDate();
  const songRows = issueDate ? getChartRows("songs", issueDate) : [];
  const albumRows = issueDate ? getChartRows("albums", issueDate) : [];
  const heroRow = songRows.length ? songRows[0] : (rows.length ? rows[0] : null);
  const heroChartType = songRows.length ? "songs" : chartType;

  function normalizeRowsForSummaryModules(sourceRows, type) {
    const rowChartType = type === "album" ? "albums" : "songs";
    if (!sourceRows || !sourceRows.length) return [];
    const out = [];
    for (let i = 0; i < sourceRows.length; i += 1) {
      const row = sourceRows[i];
      const rank = toNumber(row && row.rank);
      const lastValue = toNumber(row && row.last_week);
      const last = lastValue != null && lastValue > 0 ? lastValue : null;
      const move = rank != null && last != null ? last - rank : 0;
      out.push({
        type: type === "album" ? "album" : "song",
        chartType: rowChartType,
        row: row,
        title: row && row.title ? String(row.title) : "—",
        artist: row && row.artist ? String(row.artist) : "",
        rank: rank != null ? rank : null,
        last: last,
        move: move,
        isNew: movementValue(row) === "NEW",
      });
    }
    return out;
  }

  function movementDescriptor(row, moveOverride) {
    const override = Number(moveOverride);
    if (Number.isFinite(override)) {
      if (override > 0) return { label: "▲ +" + override, tone: "up" };
      if (override < 0) return { label: "▼ -" + Math.abs(override), tone: "down" };
      return { label: "→", tone: "flat" };
    }

    const movement = movementValue(row);
    const rank = toNumber(row && row.rank);
    const last = toNumber(row && row.last_week);
    if (movement === "NEW" || movement === "RE") return { label: "NEW", tone: "new" };
    if (movement === "UP" && rank != null && last != null && last > rank) {
      return { label: "▲ +" + (last - rank), tone: "up" };
    }
    if (movement === "DOWN" && rank != null && last != null && rank > last) {
      return { label: "▼ -" + (rank - last), tone: "down" };
    }
    return { label: "→", tone: "flat" };
  }

  function wireSelectable(button, rowChartType, row) {
    if (!button || !row) return button;
    const selectionKey = rowSelectionKey(rowChartType, row);
    const domKey = rowDataKey(row);
    const rank = toNumber(row && row.rank);
    if (selectionKey && selectionKey === selectedKey) {
      button.classList.add("selected");
    }
    if (domKey) button.dataset.key = domKey;
    if (rank != null) button.dataset.rank = String(rank);
    button.addEventListener("click", function (event) {
      if (isRowActionTarget(event)) return;
      if (state.currentChartType !== rowChartType) {
        state.currentChartType = rowChartType;
      }
      selectRow(rowChartType, row, { openSheet: true });
    });
    return button;
  }

  function buildSection(title, className) {
    const section = document.createElement("section");
    section.className = "summary-mag-section " + className;
    section.innerHTML = '<h3 class="summary-mag-section-title">' + esc(title) + "</h3>";
    const body = document.createElement("div");
    body.className = "summary-mag-section-body";
    section.appendChild(body);
    return { section, body };
  }

  function buildEditorialRow(row, rowChartType, variantClass, moveOverride, includeActions) {
    if (!row) return null;
    const rank = toNumber(row && row.rank);
    const peak = toNumber(row && row.peak);
    const weeks = toNumber(row && row.weeks_on_chart);
    const movement = movementDescriptor(row, moveOverride);
    const button = document.createElement("button");
    button.type = "button";
    button.className = "summary-mag-row " + variantClass;
    button.setAttribute(
      "aria-label",
      "Open detail for " + String(row && row.title ? row.title : "chart entry")
    );
    button.innerHTML =
      '<span class="summary-mag-row-rank">#' + esc(rank != null ? rank : "—") + "</span>" +
      '<span class="summary-mag-row-copy">' +
        '<span class="summary-mag-row-headline">' +
          '<span class="summary-mag-row-title">' + esc(row && row.title ? row.title : "—") + "</span>" +
          (includeActions ? renderRowActionButtons(rowChartType, row) : "") +
        "</span>" +
        '<span class="summary-mag-row-artist">' + esc(row && row.artist ? row.artist : "") + "</span>" +
        '<span class="summary-mag-row-meta">' +
          "<span>Peak " + esc(peak != null ? ("#" + peak) : "—") + "</span>" +
          "<span>·</span>" +
          "<span>" + esc(weeks != null ? (weeks + " wks") : "—") + "</span>" +
          "<span>·</span>" +
          '<span class="summary-mag-move summary-mag-move--' + esc(movement.tone) + '">' + esc(movement.label) + "</span>" +
        "</span>" +
      "</span>";
    return wireSelectable(button, rowChartType, row);
  }

  function appendRowsFromRows(body, sourceRows, rowChartType, variantClass, includeActions, emptyLabel) {
    if (!sourceRows || !sourceRows.length) {
      body.innerHTML = '<p class="summary-mag-empty">' + esc(emptyLabel) + "</p>";
      return;
    }
    for (let i = 0; i < sourceRows.length; i += 1) {
      const rowButton = buildEditorialRow(sourceRows[i], rowChartType, variantClass, null, includeActions);
      if (rowButton) body.appendChild(rowButton);
    }
  }

  function appendRowsFromEntries(body, entries, rowChartType, variantClass, includeActions, emptyLabel) {
    if (!entries || !entries.length) {
      body.innerHTML = '<p class="summary-mag-empty">' + esc(emptyLabel) + "</p>";
      return;
    }
    for (let i = 0; i < entries.length; i += 1) {
      const entry = entries[i];
      const row = entry && entry.row ? entry.row : null;
      const move = Number(entry && entry.move);
      if (!row) continue;
      const rowButton = buildEditorialRow(
        row,
        rowChartType,
        variantClass,
        Number.isFinite(move) ? move : null,
        includeActions
      );
      if (rowButton) body.appendChild(rowButton);
    }
  }

  const topSongs = songRows.slice(0, 5);
  const topAlbums = albumRows.slice(0, 5);
  const songRowsNormalized = normalizeRowsForSummaryModules(songRows, "song");
  const albumRowsNormalized = normalizeRowsForSummaryModules(albumRows, "album");

  const songMovers = songRowsNormalized
    .filter(function (entry) {
      return entry.move > 0;
    })
    .sort(function (a, b) {
      return b.move - a.move;
    })
    .slice(0, 5);

  const albumMovers = albumRowsNormalized
    .filter(function (entry) {
      return entry.move > 0;
    })
    .sort(function (a, b) {
      return b.move - a.move;
    })
    .slice(0, 5);

  const songNewEntries = songRowsNormalized.filter(function (entry) {
    return entry.isNew === true;
  }).slice(0, 5);

  const albumNewEntries = albumRowsNormalized.filter(function (entry) {
    return entry.isNew === true;
  }).slice(0, 5);
  const layout = document.createElement("div");
  layout.className = "summary-mag-layout";

  if (heroRow) {
    const heroMovement = movementDescriptor(heroRow, null);
    const heroRank = toNumber(heroRow && heroRow.rank);
    const heroPeak = toNumber(heroRow && heroRow.peak);
    const heroWeeks = toNumber(heroRow && heroRow.weeks_on_chart);
    const hero = document.createElement("button");
    hero.type = "button";
    hero.className = "summary-mag-hero";
    hero.innerHTML =
      '<span class="summary-mag-hero-kicker">No. 1 Song</span>' +
      '<span class="summary-mag-hero-title">' + esc(heroRow && heroRow.title ? heroRow.title : "—") + "</span>" +
      '<span class="summary-mag-hero-artist">' + esc(heroRow && heroRow.artist ? heroRow.artist : "") + "</span>" +
      '<span class="summary-mag-hero-meta">' +
        '<span>#' + esc(heroRank != null ? heroRank : "—") + "</span>" +
        "<span>•</span>" +
        "<span>Peak " + esc(heroPeak != null ? ("#" + heroPeak) : "—") + "</span>" +
        "<span>•</span>" +
        "<span>" + esc(heroWeeks != null ? (heroWeeks + " weeks") : "—") + "</span>" +
        "<span>•</span>" +
        '<span class="summary-mag-move summary-mag-move--' + esc(heroMovement.tone) + '">' + esc(heroMovement.label) + "</span>" +
      "</span>";
    layout.appendChild(wireSelectable(hero, heroChartType, heroRow));
  }

  const columns = document.createElement("div");
  columns.className = "summary-mag-columns";

  const songsColumn = document.createElement("div");
  songsColumn.className = "summary-mag-column summary-mag-column--songs";
  const albumsColumn = document.createElement("div");
  albumsColumn.className = "summary-mag-column summary-mag-column--albums";

  const songsTop = buildSection("Top Songs", "summary-mag-section--songs-top");
  appendRowsFromRows(songsTop.body, topSongs, "songs", "summary-mag-row--songs-top", true, "No songs available.");
  songsColumn.appendChild(songsTop.section);

  const songsMoversSection = buildSection("Big Movers", "summary-mag-section--songs-movers");
  appendRowsFromEntries(
    songsMoversSection.body,
    songMovers,
    "songs",
    "summary-mag-row--songs-movers",
    true,
    "No upward movers this week."
  );
  songsColumn.appendChild(songsMoversSection.section);

  const songsNewSection = buildSection("New Entries", "summary-mag-section--songs-new");
  appendRowsFromEntries(
    songsNewSection.body,
    songNewEntries,
    "songs",
    "summary-mag-row--songs-new summary-mag-row--compact",
    true,
    "No new song entries."
  );
  songsColumn.appendChild(songsNewSection.section);

  const albumsTopSection = buildSection("Top Albums", "summary-mag-section--albums-top");
  appendRowsFromRows(
    albumsTopSection.body,
    topAlbums,
    "albums",
    "summary-mag-row--albums-top",
    true,
    "No albums available."
  );
  albumsColumn.appendChild(albumsTopSection.section);

  const albumsMoversSection = buildSection("Album Movers", "summary-mag-section--albums-movers");
  appendRowsFromEntries(
    albumsMoversSection.body,
    albumMovers,
    "albums",
    "summary-mag-row--albums-movers",
    true,
    "No album movers this week."
  );
  albumsColumn.appendChild(albumsMoversSection.section);

  const albumsNewSection = buildSection("Album New Entries", "summary-mag-section--albums-new");
  appendRowsFromEntries(
    albumsNewSection.body,
    albumNewEntries,
    "albums",
    "summary-mag-row--albums-new summary-mag-row--compact",
    true,
    "No new album entries."
  );
  albumsColumn.appendChild(albumsNewSection.section);

  if (songsColumn.childElementCount) columns.appendChild(songsColumn);
  if (albumsColumn.childElementCount) columns.appendChild(albumsColumn);
  if (columns.childElementCount) layout.appendChild(columns);
  el.chartMobileList.appendChild(layout);
}

function scrollSelectedChartRowIntoView() {
  if (!el.chartMobileList) return;
  const selectedElement = el.chartMobileList.querySelector(
    ".mobile-chart-row.selected, .summary-mag-row.selected, .summary-mag-hero.selected, .rv-album-card.selected, .summary-feature-card.selected"
  );
  if (!selectedElement) return;
  selectedElement.scrollIntoView({
    block: "center",
    behavior: "smooth",
  });
}

function rankImprovement(row) {
  const rank = toNumber(row && row.rank);
  const last = toNumber(row && row.last_week);
  if (rank == null || last == null || last <= 0) return 0;
  return last - rank;
}

function isUpMovementRow(row) {
  return movementValue(row) === "UP";
}

function isNewEntryRow(row) {
  const m = row && row.movement;
  return m === "NEW" || m === "RE-ENTRY";
}

function featureThumbnailUrl(chartType, row) {
  if (chartType !== "songs" || !row) return "";
  const entry = primaryResolvedVideoEntry(chartType, row);
  if (!entry) return "";
  if (entry.thumbnailUrl) return entry.thumbnailUrl;
  const thumb = entry.video && entry.video.thumbnail_url;
  return safePublicUrl(thumb) || "";
}

function renderFeatureStrip(chartType, rows) {
  if (!el.featureStrip) return;
  if (!rows || !rows.length) {
    el.featureStrip.hidden = true;
    el.featureStrip.innerHTML = "";
    return;
  }

  const rankOne = rows.find(function (r) {
    return toNumber(r && r.rank) === 1;
  }) || null;

  const top10 = rows.filter(function (r) {
    const rank = toNumber(r && r.rank);
    return rank != null && rank >= 1 && rank <= 10;
  });

  const moverCandidates = rows
    .filter(function (r) {
      return isUpMovementRow(r) && rankImprovement(r) > 0;
    })
    .map(function (r) {
      return { row: r, delta: rankImprovement(r) };
    })
    .sort(function (a, b) {
      return b.delta - a.delta;
    })
    .slice(0, 3);

  const newEntries = rows.filter(isNewEntryRow).slice(0, 4);

  const heroKey = rankOne ? rowDataKey(rankOne) : "";
  const thumbUrl = rankOne ? featureThumbnailUrl(chartType, rankOne) : "";
  const heroTitle = rankOne
    ? String(rankOne.title || "").trim() || "—"
    : "—";
  const heroArtist = rankOne
    ? String(rankOne.artist || "").trim() || "—"
    : "—";

  const thumbBlock = thumbUrl
    ? '<div class="feature-hero-thumb"><img src="' + esc(thumbUrl) + '" alt="" loading="lazy" /></div>'
    : '<div class="feature-hero-thumb feature-hero-thumb--empty" aria-hidden="true"></div>';

  const heroCard =
    '<article class="feature-card feature-card--hero feature-card--paper-red" ' +
      (heroKey
        ? 'role="button" tabindex="0" data-feature-row-key="' + esc(heroKey) + '"'
        : "") +
    ">" +
      '<p class="feature-hero-badge">#1 THIS WEEK</p>' +
      '<div class="feature-hero-main">' +
        '<div class="feature-hero-copy">' +
          '<h3 class="feature-hero-title">' + esc(heroTitle) + "</h3>" +
          '<p class="feature-hero-artist">' + esc(heroArtist) + "</p>" +
        "</div>" +
        thumbBlock +
      "</div>" +
    "</article>";

  let top10Items = "";
  for (let i = 0; i < top10.length; i += 1) {
    const r = top10[i];
    const rk = rowDataKey(r);
    const line = chartType === "albums"
      ? esc(String(r.title || "").trim()) + " · " + esc(String(r.artist || "").trim())
      : esc(String(r.title || "").trim()) + " — " + esc(String(r.artist || "").trim());
    top10Items +=
      '<li class="feature-top10-item">' +
        (rk
          ? '<button type="button" class="feature-top10-hit" data-feature-row-key="' + esc(rk) + '">'
          : "<span>") +
        '<span class="feature-top10-rank">' + esc(toNumber(r.rank) != null ? r.rank : "—") + "</span>" +
        '<span class="feature-top10-line">' + line + "</span>" +
        (rk ? "</button>" : "</span>") +
      "</li>";
  }

  const top10Card =
    '<article class="feature-card feature-card--top10 feature-card--paper-blue">' +
      '<h4 class="feature-card-kicker">Top 10</h4>' +
      (top10Items
        ? '<ol class="feature-top10-list">' + top10Items + "</ol>"
        : '<p class="feature-card-empty">No entries.</p>') +
    "</article>";

  let moversHtml = "";
  for (let i = 0; i < moverCandidates.length; i += 1) {
    const r = moverCandidates[i].row;
    const delta = moverCandidates[i].delta;
    const rk = rowDataKey(r);
    const title = esc(String(r.title || "").trim() || "—");
    moversHtml +=
      '<li class="feature-mover-row">' +
        (rk
          ? '<button type="button" class="feature-mover-hit" data-feature-row-key="' + esc(rk) + '">'
          : "<span>") +
        '<span class="feature-mover-arrow" aria-hidden="true">▲</span>' +
        '<span class="feature-mover-delta">+' + esc(delta) + "</span>" +
        '<span class="feature-mover-title">' + title + "</span>" +
        (rk ? "</button>" : "</span>") +
      "</li>";
  }

  const moversCard =
    '<article class="feature-card feature-card--movers feature-card--paper-gold">' +
      '<h4 class="feature-card-kicker">Big movers</h4>' +
      (moversHtml
        ? '<ul class="feature-mover-list">' + moversHtml + "</ul>"
        : '<p class="feature-card-empty">No upward moves this week.</p>') +
    "</article>";

  let newHtml = "";
  for (let i = 0; i < newEntries.length; i += 1) {
    const r = newEntries[i];
    const rk = rowDataKey(r);
    const title = esc(String(r.title || "").trim() || "—");
    newHtml +=
      '<li class="feature-new-row">' +
        (rk
          ? '<button type="button" class="feature-new-hit" data-feature-row-key="' + esc(rk) + '">'
          : "<span>") +
        '<span class="feature-new-label">' +
          esc(r.movement === "RE-ENTRY" ? "RE" : r.movement === "NEW" ? "NEW" : movementLabel(r)) +
        "</span>" +
        '<span class="feature-new-title">' + title + "</span>" +
        (rk ? "</button>" : "</span>") +
      "</li>";
  }

  const newCard =
    '<article class="feature-card feature-card--new feature-card--paper-olive">' +
      '<h4 class="feature-card-kicker">New entries</h4>' +
      (newHtml
        ? '<ul class="feature-new-list">' + newHtml + "</ul>"
        : '<p class="feature-card-empty">None this week.</p>') +
    "</article>";

  el.featureStrip.innerHTML =
    '<div class="chart-feature-grid">' +
      heroCard +
      '<div class="chart-feature-row2">' +
        top10Card +
        moversCard +
        newCard +
      "</div>" +
    "</div>";
  el.featureStrip.hidden = false;
}

function syncViewToggleUi() {
  if (el.viewCharts && el.viewEditions) {
    el.viewCharts.classList.toggle("active", viewMode === "charts");
    el.viewEditions.classList.toggle("active", viewMode === "editions");
  }
}

function renderEditionView(chartType, rows) {
  if (!el.chartEditionWrap) return;
  if (!rows || !rows.length) {
    el.chartEditionWrap.innerHTML = "";
    return;
  }

  const rankOne = rows.find(function (r) {
    return toNumber(r && r.rank) === 1;
  }) || rows[0];
  const top10 = rows.filter(function (r) {
    const rank = toNumber(r && r.rank);
    return rank != null && rank >= 1 && rank <= 10;
  });
  const moverCandidates = rows
    .filter(function (r) {
      return isUpMovementRow(r) && rankImprovement(r) > 0;
    })
    .map(function (r) {
      return { row: r, delta: rankImprovement(r) };
    })
    .sort(function (a, b) {
      return b.delta - a.delta;
    })
    .slice(0, 5);
  const newEntries = rows.filter(isNewEntryRow).slice(0, 5);

  const heroKey = rowDataKey(rankOne);
  const thumbUrl = featureThumbnailUrl(chartType, rankOne);
  const thumbBlock = thumbUrl
    ? '<div class="edition-hero-thumb"><img src="' + esc(thumbUrl) + '" alt="" loading="lazy" /></div>'
    : "";

  let top10Rows = "";
  for (let i = 0; i < top10.length; i += 1) {
    const r = top10[i];
    const rk = rowDataKey(r);
    const rank = toNumber(r.rank);
    const lineTitle = esc(String(r.title || "").trim() || "—");
    const lineArtist = esc(String(r.artist || "").trim() || "—");
    top10Rows +=
      '<div class="edition-row">' +
        (rk
          ? '<button type="button" class="edition-row-hit" data-feature-row-key="' + esc(rk) + '">'
          : "<span class=\"edition-row-static\">") +
        "<span>#" + esc(rank != null ? rank : "—") + "</span>" +
        "<span>" + lineTitle + "</span>" +
        "<span>" + lineArtist + "</span>" +
        (rk ? "</button>" : "</span>") +
      "</div>";
  }

  let moversRows = "";
  for (let i = 0; i < moverCandidates.length; i += 1) {
    const r = moverCandidates[i].row;
    const delta = moverCandidates[i].delta;
    const rk = rowDataKey(r);
    moversRows +=
      '<div class="edition-row edition-row--mover">' +
        (rk
          ? '<button type="button" class="edition-row-hit" data-feature-row-key="' + esc(rk) + '">'
          : "<span class=\"edition-row-static\">") +
        '<span class="edition-mover-arrow" aria-hidden="true">▲</span>' +
        "<span>+" + esc(delta) + "</span>" +
        "<span>" + esc(String(r.title || "").trim() || "—") + "</span>" +
        (rk ? "</button>" : "</span>") +
      "</div>";
  }

  let newRows = "";
  for (let i = 0; i < newEntries.length; i += 1) {
    const r = newEntries[i];
    const rk = rowDataKey(r);
    const lab = r.movement === "RE-ENTRY" ? "RE" : r.movement === "NEW" ? "NEW" : movementLabel(r);
    newRows +=
      '<div class="edition-row">' +
        (rk
          ? '<button type="button" class="edition-row-hit" data-feature-row-key="' + esc(rk) + '">'
          : "<span class=\"edition-row-static\">") +
        "<span>" + esc(lab) + "</span>" +
        "<span>" + esc(String(r.title || "").trim() || "—") + "</span>" +
        (rk ? "</button>" : "</span>") +
      "</div>";
  }

  el.chartEditionWrap.innerHTML =
    '<div class="edition-layout">' +
      '<div class="edition-feature">' +
        (heroKey
          ? '<button type="button" class="edition-feature-hit" data-feature-row-key="' + esc(heroKey) + '">'
          : "<div>") +
        '<div class="feature-rank">#1 This Week</div>' +
        '<div class="feature-title">' + esc(String(rankOne.title || "").trim() || "—") + "</div>" +
        '<div class="feature-artist">' + esc(String(rankOne.artist || "").trim() || "—") + "</div>" +
        thumbBlock +
        (heroKey ? "</button>" : "</div>") +
      "</div>" +
      '<div class="edition-grid">' +
        '<div class="edition-block">' +
          "<h3>Top 10</h3>" +
          (top10Rows || '<p class="edition-empty">No entries.</p>') +
        "</div>" +
        '<div class="edition-block edition-block--movers">' +
          "<h3>Big Movers</h3>" +
          (moversRows || '<p class="edition-empty">No upward moves this week.</p>') +
        "</div>" +
        '<div class="edition-block edition-block--new">' +
          "<h3>New This Week</h3>" +
          (newRows || '<p class="edition-empty">None this week.</p>') +
        "</div>" +
      "</div>" +
    "</div>";
}

function renderCurrentView(chartType, rows, selectedRow) {
  syncViewToggleUi();
  renderBrowsePresentation(chartType, rows, selectedRow);
}

function buildSummaryRows(rows) {
  if (!rows || !rows.length) return [];
  const dedup = new Map();
  function add(list) {
    for (let i = 0; i < list.length; i += 1) {
      const row = list[i];
      const key = rowDataKey(row);
      if (!key || dedup.has(key)) continue;
      dedup.set(key, row);
    }
  }

  const rankOne = rows.find(function (r) {
    return toNumber(r && r.rank) === 1;
  });
  if (rankOne) add([rankOne]);

  const topTen = rows.filter(function (r) {
    const rank = toNumber(r && r.rank);
    return rank != null && rank >= 1 && rank <= 10;
  });
  add(topTen);

  const movers = rows
    .filter(function (r) {
      return isUpMovementRow(r) && rankImprovement(r) > 0;
    })
    .map(function (r) {
      return { row: r, delta: rankImprovement(r) };
    })
    .sort(function (a, b) {
      return b.delta - a.delta;
    })
    .slice(0, 8)
    .map(function (item) {
      return item.row;
    });
  add(movers);

  const newEntries = rows.filter(isNewEntryRow).slice(0, 8);
  add(newEntries);

  if (dedup.size < 12) add(rows.slice(0, 24));
  return Array.from(dedup.values()).slice(0, 12);
}

function rowsForBrowseMode(rows) {
  if (viewMode === "charts") return rows;
  return buildSummaryRows(rows);
}

function renderBrowsePresentation(chartType, rows, selectedRow) {
  if (el.chartTableWrap) {
    el.chartTableWrap.hidden = true;
  }
  if (el.chartEditionWrap) {
    el.chartEditionWrap.hidden = true;
    el.chartEditionWrap.innerHTML = "";
  }
  if (el.featureStrip) {
    el.featureStrip.hidden = true;
    el.featureStrip.innerHTML = "";
  }
  if (el.chartMobileList) {
    el.chartMobileList.hidden = false;
    const summaryMode = viewMode === "editions";
    el.chartMobileList.classList.toggle("chart-mobile-list--summary", summaryMode);
    el.chartMobileList.classList.toggle("chart-mobile-list--charts", !summaryMode);
    if (summaryMode) {
      renderSummaryCards(chartType, rowsForBrowseMode(rows));
    } else {
      renderMobileList(chartType, rowsForBrowseMode(rows));
    }
  }

  if (state.detailSheetOpen && selectedRow) {
    renderDetailSheet(chartType, selectedRow);
  } else {
    closeDetailSheet();
  }
}

function setPanelState(message) {
  el.panelState.hidden = false;
  el.panelState.textContent = message;
  if (el.chartTableWrap) el.chartTableWrap.hidden = true;
  if (el.chartMobileList) el.chartMobileList.hidden = true;
  if (el.featureStrip) {
    el.featureStrip.hidden = true;
    el.featureStrip.innerHTML = "";
  }
  if (el.chartEditionWrap) {
    el.chartEditionWrap.hidden = true;
    el.chartEditionWrap.innerHTML = "";
  }
}

function renderChart() {
  syncLayoutMode();

  const chartType = currentChartType();
  const issueDate = currentDate();

  renderChartNavigation(chartType);
  renderChartSearchResults();
  renderChartHeader(chartType);

  if (!issueDate) {
    setPanelState("No valid issue dates are available for this chart.");
    state.selected = null;
    closeDetailSheet();
    closeVideoModal();
    renderTrackStatus(chartType, null);
    return;
  }

  const rows = getChartRows(chartType, issueDate);
  if (!rows.length) {
    setPanelState("No chart rows are available for this issue date.");
    state.selected = null;
    closeDetailSheet();
    closeVideoModal();
    renderTrackStatus(chartType, null);
    return;
  }

  el.panelState.hidden = true;
  const selectedRow = resolveSelectedRow(chartType, rows);
  renderChartHeader(chartType);
  renderTrackStatus(chartType, selectedRow);
  if (viewMode === "editions") {
    if (el.featureStrip) {
      el.featureStrip.hidden = true;
      el.featureStrip.innerHTML = "";
    }
  } else if (el.featureStrip) {
    el.featureStrip.hidden = true;
    el.featureStrip.innerHTML = "";
  }
  renderCurrentView(chartType, rows, selectedRow);
  renderVideoModal(chartType, selectedRow);
  if (state.pendingSelectionScroll && selectedRow) {
    window.requestAnimationFrame(function () {
      scrollSelectedChartRowIntoView();
    });
  }
  state.pendingSelectionScroll = false;
}

async function fetchJsonOrThrow(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(response.status + " " + response.statusText);
  }
  return response.json();
}

async function ensureFullMasterLoaded() {
  if (state.fullMasterLoaded) return true;
  if (state.fullMasterLoadPromise) return state.fullMasterLoadPromise;

  const selectedChartType = currentChartType();
  const selectedYear = currentYear();
  const selectedDate = currentDate();
  const selectedSearch = String(state.chartSearchQuery || "");
  const selectedTrackedKey = state.trackedSelectionKey;
  const selectedTrackedLabel = state.trackedSelectionLabel;
  const selectedHistoryTimeline = state.historyTimeline;

  state.fullMasterLoadPromise = (async function () {
    setPanelState(LOADING_DATA_MESSAGE);
    const master = await fetchJsonOrThrow(DATA_URL);
    applyMasterData(master);
    state.usingBootstrapData = false;
    state.fullMasterLoaded = true;
    state.currentChartType = selectedChartType === "albums" ? "albums" : "songs";
    syncSelectorState({
      preferredYear: selectedYear || state.bootstrapYear || "1975",
      preferredDate: selectedDate || DEFAULT_CHART_DATE,
    });
    state.chartSearchQuery = selectedSearch;
    state.trackedSelectionKey = selectedTrackedKey;
    state.trackedSelectionLabel = selectedTrackedLabel;
    state.historyTimeline = selectedHistoryTimeline === "full" ? "full" : "upto";
    renderChart();
    renderChartSearchResults();
    return true;
  })()
    .catch(function (error) {
      setPanelState("Could not load chart data: " + error.message);
      closeDetailSheet();
      el.contextKicker.textContent = "Load Error";
      el.contextTitle.textContent = "Chart data unavailable";
      el.contextMeta.textContent = "Check the master dataset path and reload.";
      return false;
    })
    .finally(function () {
      state.fullMasterLoadPromise = null;
    });

  return state.fullMasterLoadPromise;
}

async function loadMaster() {
  setPanelState(LOADING_DATA_MESSAGE);

  try {
    const [videoCacheByTrackKey, bootstrapMaster] = await Promise.all([
      loadVideoCache(VIDEO_CONFIG.videoCacheUrl),
      fetchJsonOrThrow(BOOTSTRAP_DATA_URL).catch(function () {
        return null;
      }),
    ]);

    state.videoCacheByTrackKey = videoCacheByTrackKey;

    if (bootstrapMaster) {
      applyMasterData(bootstrapMaster);
      state.usingBootstrapData = true;
      state.fullMasterLoaded = false;
      state.bootstrapYear = String(
        (bootstrapMaster.meta && (bootstrapMaster.meta.bootstrap_year || bootstrapMaster.meta.bootstrapYear)) ||
        latestYearForChartType("songs") ||
        latestYearForChartType("albums") ||
        ""
      );
      syncSelectorState({
        preferredYear: state.bootstrapYear || "1975",
        preferredDate: DEFAULT_CHART_DATE,
      });
      renderChart();
      return;
    }

    const fullMaster = await fetchJsonOrThrow(DATA_URL);
    applyMasterData(fullMaster);
    state.usingBootstrapData = false;
    state.fullMasterLoaded = true;
    state.bootstrapYear = "";
    syncSelectorState({
      preferredYear: "1975",
      preferredDate: DEFAULT_CHART_DATE,
    });
    renderChart();
  } catch (error) {
    setPanelState("Could not load chart data: " + error.message);
    closeDetailSheet();
    el.contextKicker.textContent = "Load Error";
    el.contextTitle.textContent = "Chart data unavailable";
    el.contextMeta.textContent = "Check the master dataset path and reload.";
  }
}

function bindUi() {
  if (el.viewCharts && el.viewEditions) {
    el.viewCharts.addEventListener("click", function () {
      if (viewMode === "charts") return;
      viewMode = "charts";
      if (state.master) {
        renderChart();
      }
    });
    el.viewEditions.addEventListener("click", function () {
      if (viewMode === "editions") return;
      viewMode = "editions";
      if (state.master) {
        renderChart();
      }
    });
  }

  if (el.trackModeToggle) {
    el.trackModeToggle.addEventListener("click", function () {
      if (currentChartType() !== "songs") return;
      state.trackMode = !state.trackMode;
      state.trackedSelectionMissing = false;
      state.pendingSelectionScroll = false;
      if (state.trackMode) {
        const selectedRow = currentSelectedRow();
        if (selectedRow) {
          state.trackedSelectionKey = trackedRowKey(selectedRow);
          state.trackedSelectionLabel = (selectedRow.title || "Untitled") + " — " + (selectedRow.artist || "Unknown artist");
        }
      }
      renderTrackModeToggle();
      if (state.master) {
        renderChart();
      }
    });
  }

  if (el.chartNavPrev) {
    el.chartNavPrev.addEventListener("click", function (event) {
      event.preventDefault();
      void navigateIssue(-1);
    });
  }

  if (el.chartNavNext) {
    el.chartNavNext.addEventListener("click", function (event) {
      event.preventDefault();
      void navigateIssue(1);
    });
  }

  if (el.chartSearchInput) {
    el.chartSearchInput.addEventListener("input", function () {
      state.chartSearchQuery = this.value || "";
      if (state.usingBootstrapData && !state.fullMasterLoaded) {
        const parsedQuery = parseChartSearchQuery(state.chartSearchQuery);
        if (parsedQuery.year && !availableYears(currentChartType()).includes(parsedQuery.year)) {
          void ensureFullMasterLoaded();
          return;
        }
      }
      renderChartSearchResults();
    });

    el.chartSearchInput.addEventListener("keydown", async function (event) {
      if (event.key !== "Enter") return;
      if (state.usingBootstrapData && !state.fullMasterLoaded) {
        const parsedQuery = parseChartSearchQuery(state.chartSearchQuery);
        if (parsedQuery.year && !availableYears(currentChartType()).includes(parsedQuery.year)) {
          event.preventDefault();
          const loaded = await ensureFullMasterLoaded();
          if (!loaded) return;
        }
      }
      const results = currentChartSearchResults();
      if (!results.length) return;
      event.preventDefault();
      goToChartDate(currentChartType(), results[0].chartDate, { clearSearch: true });
    });
  }

  if (el.detailSheetBackdrop) {
    el.detailSheetBackdrop.addEventListener("click", closeDetailSheet);
  }

  if (el.detailSheetClose) {
    el.detailSheetClose.addEventListener("click", closeDetailSheet);
  }

  if (el.videoModalBackdrop) {
    el.videoModalBackdrop.addEventListener("click", closeVideoModal);
  }

  if (el.videoModalClose) {
    el.videoModalClose.addEventListener("click", closeVideoModal);
  }

  if (el.videoModalPrev) {
    el.videoModalPrev.addEventListener("click", function () {
      stepVideoPlayer(-1);
    });
  }

  if (el.videoModalNext) {
    el.videoModalNext.addEventListener("click", function () {
      stepVideoPlayer(1);
    });
  }

  document.addEventListener("click", function (event) {
    const detailVideoButton = event.target && event.target.closest ? event.target.closest("[data-detail-open-video]") : null;
    if (detailVideoButton) {
      event.preventDefault();
      event.stopPropagation();
      const row = currentSelectedRow();
      if (row) {
        selectRow(currentChartType(), row, { openVideo: true });
      }
      return;
    }

    const playTrigger = event.target && event.target.closest ? event.target.closest(".rv-play") : null;
    if (playTrigger) {
      event.preventDefault();
      event.stopPropagation();
      const videoUrl = safePublicUrl(playTrigger.getAttribute("data-video-url"));
      if (videoUrl) {
        window.open(videoUrl, "_blank", "noopener");
      }
      return;
    }

    const workflowTrigger = event.target && event.target.closest ? event.target.closest(".rv-collect") : null;
    if (workflowTrigger) {
      event.preventDefault();
      event.stopPropagation();
      openDestinationMenu(workflowTrigger);
      return;
    }

    const workflowAdd = event.target && event.target.closest ? event.target.closest("[data-worklist-add]") : null;
    if (workflowAdd) {
      event.preventDefault();
      event.stopPropagation();
      const bucket = workflowAdd.getAttribute("data-worklist-add");
      if (state.destinationMenu && state.destinationMenu.item) {
        addWorklistItem(bucket, state.destinationMenu.item);
      }
      closeDestinationMenu();
      renderWorklistUi();
      return;
    }

    const worklistItemTrigger = event.target && event.target.closest ? event.target.closest("[data-worklist-open-item]") : null;
    if (worklistItemTrigger) {
      event.preventDefault();
      closeDestinationMenu();
      openWorklistItem(workflowItemFromTrigger(worklistItemTrigger));
      return;
    }

    const toggle = event.target && event.target.closest ? event.target.closest("[data-worklist-toggle]") : null;
    if (toggle) {
      event.preventDefault();
      closeDestinationMenu();
      state.worklistOpen = !state.worklistOpen;
      renderWorklistUi();
      return;
    }

    const removeButton = event.target && event.target.closest ? event.target.closest("[data-worklist-remove]") : null;
    if (removeButton) {
      event.preventDefault();
      const bucket = removeButton.getAttribute("data-worklist-remove");
      const key = removeButton.getAttribute("data-worklist-key");
      closeDestinationMenu();
      if (removeWorklistItem(bucket, key)) {
        renderWorklistUi();
      }
      return;
    }

    const clearButton = event.target && event.target.closest ? event.target.closest("[data-worklist-clear]") : null;
    if (clearButton) {
      event.preventDefault();
      const bucket = clearButton.getAttribute("data-worklist-clear");
      closeDestinationMenu();
      if (clearWorklist(bucket)) {
        renderWorklistUi();
      }
      return;
    }

    const playQueueButton = event.target && event.target.closest ? event.target.closest("[data-worklist-play]") : null;
    if (playQueueButton) {
      event.preventDefault();
      closeDestinationMenu();
      playQueue();
      return;
    }

    const shuffleQueueButton = event.target && event.target.closest ? event.target.closest("[data-worklist-shuffle]") : null;
    if (shuffleQueueButton) {
      event.preventDefault();
      closeDestinationMenu();
      shuffleQueueAndPlay();
      renderWorklistUi();
      return;
    }

    const exportButton = event.target && event.target.closest ? event.target.closest("[data-worklist-export]") : null;
    if (exportButton) {
      event.preventDefault();
      const bucket = exportButton.getAttribute("data-worklist-export");
      closeDestinationMenu();
      if (normalizeWorkflowBucket(bucket) === "acquire") {
        const url = acquirePrimaryUrl();
        if (url) {
          openWorkflowExport(url);
        } else {
          setAcquireStatus("No Acquire tracks can be exported yet.", "error");
          renderWorklistUi();
        }
      }
      return;
    }

    const openButton = event.target && event.target.closest ? event.target.closest("[data-worklist-open]") : null;
    if (openButton) {
      event.preventDefault();
      const bucket = openButton.getAttribute("data-worklist-open");
      closeDestinationMenu();
      if (normalizeWorkflowBucket(bucket) === "acquire") {
        void openAcquirePlaylist();
      }
      return;
    }

    const openMissingButton = event.target && event.target.closest ? event.target.closest("[data-worklist-open-missing]") : null;
    if (openMissingButton) {
      event.preventDefault();
      const bucket = openMissingButton.getAttribute("data-worklist-open-missing");
      closeDestinationMenu();
      if (normalizeWorkflowBucket(bucket) === "acquire") {
        void openAcquirePlaylist({ missingOnly: true });
      }
      return;
    }

    const copyButton = event.target && event.target.closest ? event.target.closest("[data-worklist-copy]") : null;
    if (copyButton) {
      event.preventDefault();
      const bucket = copyButton.getAttribute("data-worklist-copy");
      closeDestinationMenu();
      if (normalizeWorkflowBucket(bucket) === "acquire") {
        const url = acquirePrimaryUrl();
        if (url) {
          copyTextToClipboard(url);
        } else {
          setAcquireStatus("No Acquire URL is available yet.", "error");
          renderWorklistUi();
        }
      }
      return;
    }

    const searchCard = event.target && event.target.closest ? event.target.closest("[data-chart-search-date]") : null;
    if (searchCard) {
      event.preventDefault();
      const chartDate = searchCard.getAttribute("data-chart-search-date");
      if (chartDate) {
        goToChartDate(currentChartType(), chartDate, { clearSearch: true });
      }
      return;
    }

    const featureHit = event.target && event.target.closest ? event.target.closest("[data-feature-row-key]") : null;
    if (featureHit) {
      event.preventDefault();
      const key = featureHit.getAttribute("data-feature-row-key");
      if (!key) return;
      const ct = currentChartType();
      const issueDate = currentDate();
      const chartRows = getChartRows(ct, issueDate);
      const hitRow = chartRows.find(function (r) {
        return rowDataKey(r) === key;
      });
      if (hitRow) {
        selectRow(ct, hitRow, { openSheet: true });
      }
      return;
    }

    if (state.destinationMenu && state.destinationMenu.open) {
      const menu = event.target && event.target.closest ? event.target.closest(".workflow-menu") : null;
      if (!menu) {
        closeDestinationMenu();
      }
    }
  });

  window.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && state.chartSearchQuery) {
      state.chartSearchQuery = "";
      if (el.chartSearchInput) el.chartSearchInput.value = "";
      renderChartSearchResults();
      return;
    }
    if (event.key === "Escape" && state.destinationMenu && state.destinationMenu.open) {
      closeDestinationMenu();
      return;
    }
    if (event.key === "Escape" && state.detailSheetOpen) {
      closeDetailSheet();
      return;
    }
    if (event.key === "Escape" && state.videoPlayerOpen) {
      closeVideoModal();
    }
  });

  let resizeFrame = 0;
  window.addEventListener("resize", function () {
    if (resizeFrame) return;
    resizeFrame = window.requestAnimationFrame(function () {
      resizeFrame = 0;
      if (syncLayoutMode() && state.master) {
        renderChart();
      }
      closeDestinationMenu();
      renderWorklistUi();
    });
  });
}

syncLayoutMode();
loadWorklistState();
initWorklistUi();
renderWorklistUi();
bindUi();
loadMaster();
