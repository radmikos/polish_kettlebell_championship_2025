import styles from "./LivePage.module.css";

// Paste your YouTube links (full URL or just the video id) directly below.
// The component will render one player per entry in this array.
// Example:
// const rawList = [
//   'https://www.youtube.com/watch?v=abcDefGhIJk',
//   'https://youtu.be/xyz123AbC',
//   'dQw4w9WgXcQ' // bare id also works
// ];

const rawList: string[] = [
  // TODO: replace these example links with your actual YouTube links or ids
  'https://www.youtube.com/embed/dQw4w9WgXcQ?si=MtK3vPJ4V3EXJKuA',
  'https://www.youtube.com/embed/dQw4w9WgXcQ?si=MtK3vPJ4V3EXJKuA',
];

function buildYoutubeUrls(input: string | undefined | null) {
  if (!input) return { embedUrl: null as string | null, watchUrl: null as string | null };
  const s = String(input).trim();

  try {
    // If it's already an embed url, return as-is (ensure protocol)
    if (s.includes("youtube.com/embed")) {
      const url = s.startsWith("http") ? s : `https://${s}`;
      // try to extract id for watch url
      const id = new URL(url).pathname.split('/').pop();
      return { embedUrl: url, watchUrl: id ? `https://www.youtube.com/watch?v=${id}` : null };
    }

    // Short youtu.be link
    if (s.includes("youtu.be/")) {
      const maybe = s.split('/').pop();
      const id = maybe || null;
      return { embedUrl: id ? `https://www.youtube.com/embed/${id}` : null, watchUrl: id ? `https://www.youtube.com/watch?v=${id}` : null };
    }

    // Full watch URL
    if (s.includes("youtube.com/watch") || s.includes("youtube.com/")) {
      const url = s.startsWith("http") ? s : `https://${s}`;
      const parsed = new URL(url);
      const id = parsed.searchParams.get('v');
      if (id) return { embedUrl: `https://www.youtube.com/embed/${id}`, watchUrl: `https://www.youtube.com/watch?v=${id}` };
      // fallback: if no v param, maybe path contains the id
      const pathId = parsed.pathname.split('/').pop();
      if (pathId) return { embedUrl: `https://www.youtube.com/embed/${pathId}`, watchUrl: `https://www.youtube.com/watch?v=${pathId}` };
    }

    // If it looks like a bare id (letters/numbers/_-)
    if (/^[a-zA-Z0-9_-]{6,}$/.test(s)) {
      return { embedUrl: `https://www.youtube.com/embed/${s}`, watchUrl: `https://www.youtube.com/watch?v=${s}` };
    }

    // Last resort: treat input as a watch URL
    return { embedUrl: null as string | null, watchUrl: s.startsWith('http') ? s : `https://${s}` };
  } catch (e) {
    return { embedUrl: null as string | null, watchUrl: null as string | null };
  }
}

const parsed = rawList.map((s) => buildYoutubeUrls(s));
const youtubeEmbedUrls = parsed.map((p) => p.embedUrl).filter(Boolean) as string[];

const LivePage = () => {
  return (
    <div className={styles.livePage}>
      {youtubeEmbedUrls.map((src, idx) => (
        <div key={`${src}-${idx}`} className={styles.videoWrapper}>
          <iframe
            src={src}
            title={`transmission-${idx + 1}`}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
      ))}
    </div>
  );
};

export default LivePage;
