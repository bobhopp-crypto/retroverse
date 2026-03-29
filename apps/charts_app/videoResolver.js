export const CONFIG = {
  videoCacheUrl: "../../data/media/video_cache.json",
};

function normalizeTrackValue(value) {
  return String(value == null ? "" : value)
    .trim()
    .toLowerCase()
    .replace(/\s+/g, " ");
}

function safeHttpUrl(value) {
  if (typeof value !== "string") return "";
  const url = value.trim();
  if (!url) return "";
  if (!/^https?:\/\//i.test(url)) return "";
  return url;
}

function safeYoutubeId(value) {
  const youtubeId = String(value == null ? "" : value).trim();
  return /^[A-Za-z0-9_-]{6,}$/.test(youtubeId) ? youtubeId : "";
}

export function normalizeVideoTrackKey(artist, title) {
  const normalizedArtist = normalizeTrackValue(artist);
  const normalizedTitle = normalizeTrackValue(title);
  if (!normalizedArtist || !normalizedTitle) return "";
  return normalizedArtist + "__" + normalizedTitle;
}

export function buildYoutubeSearchUrl(artist, title) {
  const query = [artist, title]
    .map(function (value) {
      return String(value == null ? "" : value).trim();
    })
    .filter(Boolean)
    .join(" ");

  if (!query) return "";
  return "https://www.youtube.com/results?search_query=" + encodeURIComponent(query);
}

export function buildYoutubeWatchUrl(youtubeId) {
  const safeId = safeYoutubeId(youtubeId);
  if (!safeId) return "";
  return "https://www.youtube.com/watch?v=" + encodeURIComponent(safeId);
}

function extractYoutubeId(url) {
  const safeUrl = safeHttpUrl(url);
  if (!safeUrl) return "";

  try {
    const parsed = new URL(safeUrl);
    const hostname = parsed.hostname.replace(/^www\./i, "").toLowerCase();

    if (hostname === "youtu.be") {
      return parsed.pathname.replace(/^\/+/, "").split("/")[0] || "";
    }

    if (hostname === "youtube.com" || hostname === "m.youtube.com" || hostname === "music.youtube.com") {
      if (parsed.pathname === "/watch") {
        return parsed.searchParams.get("v") || "";
      }
      if (parsed.pathname.startsWith("/embed/")) {
        return parsed.pathname.slice("/embed/".length).split("/")[0] || "";
      }
      if (parsed.pathname.startsWith("/shorts/")) {
        return parsed.pathname.slice("/shorts/".length).split("/")[0] || "";
      }
    }
  } catch (_error) {
    return "";
  }

  return "";
}

export function toYoutubeEmbedUrl(video) {
  const youtubeId = safeYoutubeId(video && video.youtube_id)
    || extractYoutubeId(video && video.url);
  if (!youtubeId) return "";
  return "https://www.youtube-nocookie.com/embed/" + encodeURIComponent(youtubeId) + "?rel=0";
}

function primaryLocalVideo(song) {
  const videos = Array.isArray(song && song.vdj_videos) ? song.vdj_videos.slice() : [];
  const localVideos = videos
    .map(function (video) {
      const url = safeHttpUrl(video && video.video_url);
      if (!url) return null;
      return {
        url,
        playCount: typeof (video && video.play_count) === "number" ? video.play_count : 0,
      };
    })
    .filter(Boolean)
    .sort(function (a, b) {
      return b.playCount - a.playCount;
    });

  return localVideos.length ? localVideos[0] : null;
}

function normalizeVideoCacheEntry(entry) {
  if (!entry || typeof entry !== "object") return null;

  const youtubeId = safeYoutubeId(entry.youtube_id);
  if (!youtubeId) return null;

  const confidenceValue = Number(entry.confidence);
  return {
    youtube_id: youtubeId,
    confidence: Number.isFinite(confidenceValue) ? confidenceValue : 0,
  };
}

export async function loadVideoCache(source) {
  const lookup = new Map();
  if (!source) return lookup;

  try {
    const response = await fetch(source);
    if (!response.ok) {
      if (response.status === 404) return lookup;
      throw new Error(response.status + " " + response.statusText);
    }

    const payload = await response.json();
    if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
      return lookup;
    }

    const entries = Object.entries(payload);
    for (let i = 0; i < entries.length; i += 1) {
      const pair = entries[i];
      const key = normalizeTrackValue(pair[0]);
      const entry = normalizeVideoCacheEntry(pair[1]);
      if (!key || !entry) continue;
      lookup.set(key, entry);
    }
  } catch (error) {
    console.warn("RetroVerse video cache skipped:", source, error);
  }

  return lookup;
}

export function deriveTrackVideo(song, videoCache) {
  const artist = song && (song.artist_canonical || song.artist) ? (song.artist_canonical || song.artist) : "";
  const title = song && song.title ? song.title : "";

  if (!artist || !title) {
    return {
      source: "search",
      url: "",
      youtube_id: null,
      confidence: 0,
    };
  }

  const localVideo = primaryLocalVideo(song);
  if (localVideo && localVideo.url) {
    return {
      source: "local",
      url: localVideo.url,
      youtube_id: null,
      confidence: 1,
    };
  }

  const cacheKey = normalizeVideoTrackKey(artist, title);
  const cached = videoCache instanceof Map ? videoCache.get(cacheKey) : null;
  if (cached && cached.youtube_id) {
    return {
      source: "youtube",
      url: buildYoutubeWatchUrl(cached.youtube_id),
      youtube_id: cached.youtube_id,
      confidence: typeof cached.confidence === "number" ? cached.confidence : 0,
    };
  }

  return {
    source: "search",
    url: buildYoutubeSearchUrl(artist, title),
    youtube_id: null,
    confidence: 0,
  };
}

export function enrichMasterWithTrackVideos(master, videoCache) {
  const songs = Array.isArray(master && master.songs) ? master.songs : [];
  for (let i = 0; i < songs.length; i += 1) {
    const song = songs[i];
    if (!song || typeof song !== "object") continue;
    song.video = deriveTrackVideo(song, videoCache);
  }
  return master;
}

function labelForSource(source) {
  if (source === "local") return "Local Video";
  if (source === "youtube") return "YouTube";
  if (source === "search") return "Search Results";
  return "Video Source";
}

export function resolveTrackVideoSource(video) {
  if (!video || typeof video !== "object") return null;

  const source = typeof video.source === "string" ? video.source : "";
  const url = typeof video.url === "string" ? video.url.trim() : "";
  if (!source || !url) return null;

  return {
    kind: source,
    url,
    embedUrl: source === "youtube" ? toYoutubeEmbedUrl(video) : "",
    label: labelForSource(source),
    confidence: typeof video.confidence === "number" ? video.confidence : 0,
    youtubeId: typeof video.youtube_id === "string" ? video.youtube_id : null,
  };
}
