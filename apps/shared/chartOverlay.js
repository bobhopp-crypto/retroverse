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

function isSequentialChartWeek(prevDate, nextDate) {
  const prev = normalizeChartDate(prevDate);
  const next = normalizeChartDate(nextDate);
  if (!prev || !next) return false;
  const prevMs = Date.parse(prev + "T00:00:00Z");
  const nextMs = Date.parse(next + "T00:00:00Z");
  if (!Number.isFinite(prevMs) || !Number.isFinite(nextMs)) return false;
  return nextMs - prevMs === 7 * 24 * 60 * 60 * 1000;
}

function sortHistory(history) {
  return history
    .filter(function (entry) {
      return normalizeChartDate(entry && entry.chart_date) && toNumber(entry && entry.rank) != null;
    })
    .slice()
    .sort(function (a, b) {
      var dateDiff = normalizeChartDate(a.chart_date).localeCompare(normalizeChartDate(b.chart_date));
      if (dateDiff !== 0) return dateDiff;
      return (toNumber(a.rank) || 0) - (toNumber(b.rank) || 0);
    });
}

function getHistoryEntry(history, chartDate) {
  var normalizedDate = normalizeChartDate(chartDate);
  if (!normalizedDate) return null;
  for (var i = 0; i < history.length; i++) {
    if (normalizeChartDate(history[i].chart_date) === normalizedDate) {
      return { entry: history[i], index: i };
    }
  }
  return null;
}

function derivePeak(history, index, entry) {
  var peak = toNumber(entry.peak);
  if (peak != null) return peak;
  var best = null;
  for (var i = 0; i <= index; i++) {
    var rank = toNumber(history[i].rank);
    if (rank == null) continue;
    if (best == null || rank < best) best = rank;
  }
  return best;
}

function deriveWeeksOnChart(history, index, entry) {
  var weeks = toNumber(entry.weeks_on_chart);
  if (weeks != null) return weeks;
  return index + 1;
}

function deriveLastWeek(history, index, entry) {
  var lastWeek = toNumber(entry.last_week);
  if (lastWeek != null && lastWeek > 0) return lastWeek;
  if (index <= 0) return null;
  var previous = history[index - 1];
  if (!isSequentialChartWeek(previous.chart_date, entry.chart_date)) return null;
  return toNumber(previous.rank);
}

function deriveMovement(history, index, entry) {
  var currentRank = toNumber(entry.rank);
  var lastWeek = deriveLastWeek(history, index, entry);
  var weeksOnChart = deriveWeeksOnChart(history, index, entry);
  if (currentRank == null) return null;
  if (lastWeek == null || lastWeek <= 0) {
    return index === 0 || weeksOnChart <= 1 ? "NEW" : "RE-ENTRY";
  }
  if (currentRank < lastWeek) return "UP";
  if (currentRank > lastWeek) return "DOWN";
  return "SAME";
}

function getSongHistory(song) {
  if (Array.isArray(song && song.chart_history) && song.chart_history.length) {
    return sortHistory(song.chart_history);
  }
  var billboardHistory = song && song.billboard && Array.isArray(song.billboard.history)
    ? song.billboard.history
    : [];
  return sortHistory(billboardHistory);
}

function getAlbumHistory(album) {
  return sortHistory(Array.isArray(album && album.chart_history) ? album.chart_history : []);
}

function songHasVideo(song) {
  if (song && song.video && typeof song.video.url === "string" && song.video.url.trim()) {
    return true;
  }
  if (typeof (song && song.vdj_videos_count) === "number") {
    return song.vdj_videos_count > 0;
  }
  return Array.isArray(song && song.vdj_videos) && song.vdj_videos.length > 0;
}

export function buildSongChartRows(chartDate, songs) {
  if (!Array.isArray(songs)) return [];
  var normalizedDate = normalizeChartDate(chartDate);
  if (!normalizedDate) return [];

  var rows = [];
  for (var i = 0; i < songs.length; i++) {
    var song = songs[i];
    var history = getSongHistory(song);
    if (!history.length) continue;
    var match = getHistoryEntry(history, normalizedDate);
    if (!match) continue;

    var entry = match.entry;
    var rank = toNumber(entry.rank);
    if (rank == null) continue;

    rows.push({
      rank: rank,
      title: song.title || "",
      artist: song.artist_canonical || song.artist || "",
      last_week: deriveLastWeek(history, match.index, entry),
      peak: derivePeak(history, match.index, entry),
      weeks_on_chart: deriveWeeksOnChart(history, match.index, entry),
      movement: deriveMovement(history, match.index, entry),
      has_video: songHasVideo(song),
      play_count_total: toNumber(song.play_count_total) || 0,
      retroverse_id: song.retroverse_id || null,
    });
  }

  rows.sort(function (a, b) {
    return a.rank - b.rank;
  });
  return rows;
}

export function buildAlbumChartRows(chartDate, albums) {
  if (!Array.isArray(albums)) return [];
  var normalizedDate = normalizeChartDate(chartDate);
  if (!normalizedDate) return [];

  var rows = [];
  for (var i = 0; i < albums.length; i++) {
    var album = albums[i];
    var history = getAlbumHistory(album);
    if (!history.length) continue;
    var match = getHistoryEntry(history, normalizedDate);
    if (!match) continue;

    var entry = match.entry;
    var rank = toNumber(entry.rank);
    if (rank == null) continue;

    rows.push({
      rank: rank,
      title: album.album_title || "",
      artist: album.artist_canonical || album.artist || "",
      last_week: deriveLastWeek(history, match.index, entry),
      peak: derivePeak(history, match.index, entry),
      weeks_on_chart: deriveWeeksOnChart(history, match.index, entry),
      retroverse_album_id: album.retroverse_album_id || null,
    });
  }

  rows.sort(function (a, b) {
    return a.rank - b.rank;
  });
  return rows;
}
