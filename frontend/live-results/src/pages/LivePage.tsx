import { Typography, Alert } from "antd";
import styles from "./LivePage.module.css";

const { Title, Link } = Typography;

// Read the live YouTube value from Vite environment. It may be a full URL
// (watch/embed/short) or just the video id — handle both so the iframe is shown
// when the user provides a link.
const rawYoutube = import.meta.env.VITE_LIVE_YOUTUBE_ID;

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

// Accept multiple links in the same env var separated by commas or newlines.
const rawList = rawYoutube
  ? String(rawYoutube)
      .split(/[,\n]+/)
      .map((s) => s.trim())
      .filter(Boolean)
  : [];

const parsed = rawList.map((s) => buildYoutubeUrls(s));
const youtubeEmbedUrls = parsed.map((p) => p.embedUrl).filter(Boolean) as string[];
const youtubeWatchUrls = parsed.map((p) => p.watchUrl).filter(Boolean) as string[];

const LivePage = () => {
  return (
    <div className={styles.livePage}>
      <Title level={1}>Transmisja na żywo</Title>


      {youtubeEmbedUrls.length > 0 ? (
        <>
          {youtubeEmbedUrls.map((src, idx) => (
            <div key={`${src}-${idx}`} className={styles.videoWrapper}>
              <iframe
                src={src}
                title={`Transmisja Mistrzostw Polski Kettlebell 2025 ${idx + 1}`}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
          ))}
        </>
      ) : (
        <Alert
          type="info"
          showIcon
          message="Transmisja w przygotowaniu"
          description="Link do relacji live pojawi się tutaj tuż przed rozpoczęciem zawodów."
        />
      )}

      <div className={styles.infoCard}>
        <Title level={3}>Przydatne odnośniki</Title>
        <div className={styles.links}>
          {youtubeWatchUrls.length > 0 ? (
            <>
              {youtubeWatchUrls.map((href, i) => (
                <Link key={`${href}-${i}`} href={href} target="_blank" rel="noopener noreferrer">
                  {youtubeWatchUrls.length > 1 ? `Otwórz transmisję ${i + 1} na YouTube` : "Otwórz transmisję na YouTube"}
                </Link>
              ))}
            </>
          ) : (
            <span>Link do transmisji pojawi się tutaj, gdy będzie dostępny.</span>
          )}
          <Link href="/">
            Powrót do listy kategorii
          </Link>
        </div>
      </div>
    </div>
  );
};

export default LivePage;
