import { Typography, Alert } from "antd";
import styles from "./LivePage.module.css";

const { Title, Paragraph, Link } = Typography;

const videoId = import.meta.env.VITE_LIVE_YOUTUBE_ID;
const youtubeEmbedUrl = videoId ? `https://www.youtube.com/watch?v=dQw4w9WgXcQ` : null;
const youtubeWatchUrl = videoId ? `https://www.youtube.com/watch?v=dQw4w9WgXcQ` : null;

const LivePage = () => {
  return (
    <div className={styles.livePage}>
      <Title level={1}>Transmisja na żywo</Title>


      {youtubeEmbedUrl ? (
        <div className={styles.videoWrapper}>
          <iframe
            src={youtubeEmbedUrl}
            title="Transmisja Mistrzostw Polski Kettlebell 2025"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          />
        </div>
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
          {youtubeWatchUrl && (
            <Link href={youtubeWatchUrl} target="_blank" rel="noopener noreferrer">
              Otwórz transmisję na YouTube
            </Link>
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
