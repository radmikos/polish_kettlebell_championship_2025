import type { CSSProperties } from "react";
import { Card, Space, Flex, Button, Typography, theme, Grid, Empty } from "antd";

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
  "https://www.youtube.com/embed/dQw4w9WgXcQ?si=MtK3vPJ4V3EXJKuA",
  "https://www.youtube.com/embed/dQw4w9WgXcQ?si=MtK3vPJ4V3EXJKuA",
];

type ParsedVideo = {
  embedUrl: string | null;
  watchUrl: string | null;
};

function buildYoutubeUrls(input: string | undefined | null): ParsedVideo {
  if (!input) return { embedUrl: null, watchUrl: null };
  const s = String(input).trim();

  try {
    if (s.includes("youtube.com/embed")) {
      const url = s.startsWith("http") ? s : `https://${s}`;
      const id = new URL(url).pathname.split("/").pop();
      return { embedUrl: url, watchUrl: id ? `https://www.youtube.com/watch?v=${id}` : null };
    }

    if (s.includes("youtu.be/")) {
      const maybe = s.split("/").pop();
      const id = maybe || null;
      return {
        embedUrl: id ? `https://www.youtube.com/embed/${id}` : null,
        watchUrl: id ? `https://www.youtube.com/watch?v=${id}` : null,
      };
    }

    if (s.includes("youtube.com/watch") || s.includes("youtube.com/")) {
      const url = s.startsWith("http") ? s : `https://${s}`;
      const parsed = new URL(url);
      const id = parsed.searchParams.get("v");
      if (id) {
        return {
          embedUrl: `https://www.youtube.com/embed/${id}`,
          watchUrl: `https://www.youtube.com/watch?v=${id}`,
        };
      }
      const pathId = parsed.pathname.split("/").pop();
      if (pathId) {
        return {
          embedUrl: `https://www.youtube.com/embed/${pathId}`,
          watchUrl: `https://www.youtube.com/watch?v=${pathId}`,
        };
      }
    }

    if (/^[a-zA-Z0-9_-]{6,}$/.test(s)) {
      return {
        embedUrl: `https://www.youtube.com/embed/${s}`,
        watchUrl: `https://www.youtube.com/watch?v=${s}`,
      };
    }

    return {
      embedUrl: null,
      watchUrl: s.startsWith("http") ? s : `https://${s}`,
    };
  } catch (error) {
    return { embedUrl: null, watchUrl: null };
  }
}

const parsedVideos = rawList
  .map((entry) => buildYoutubeUrls(entry))
  .filter((video) => video.embedUrl || video.watchUrl);

const { Text } = Typography;

/**
 * LivePage layout guide
 * - Video cards: rendered inside the `parsedVideos.map` block, each wrapped in an Ant Design `Card`
 *   using shared helpers from `theme/sharedStyles.ts` for consistent surfaces.
 * - Empty state: see the conditional branch returning `<Empty />` when there are no videos.
 * - Action buttons / links: located near the iframe markup inside each card body.
 * Adjust spacing via `videoCardStyle`, `videoContainerStyle`, and breakpoint-aware `pageGap`.
 */

const LivePage = () => {
  const { token } = theme.useToken();
  const screens = Grid.useBreakpoint();
  const isMobile = !screens.md;

  const videoCardStyle: CSSProperties = {
    background: token.colorBgContainer,
    border: `1px solid ${token.colorBorder}`,
  };

  const videoContainerStyle: CSSProperties = {
    position: "relative",
    width: "100%",
    paddingBottom: "56.25%",
    borderRadius: token.borderRadiusLG,
    overflow: "hidden",
    background: token.colorBgElevated,
  };

  const iframeStyle: CSSProperties = {
    position: "absolute",
    inset: 0,
    width: "100%",
    height: "100%",
    border: 0,
  };

  const pageGap = isMobile ? 16 : 24;

  return (
    <Space direction="vertical" size={pageGap} style={{ width: "100%" }}>
      {parsedVideos.length === 0 ? (
        <Card style={videoCardStyle}>
          <Empty
            description="Dodaj linki do transmisji, aby zobaczyć podgląd."
            imageStyle={{ filter: "grayscale(0.4)" }}
          />
        </Card>
      ) : (
        parsedVideos.map(({ embedUrl, watchUrl }, index) => (
          <Card
            key={`${embedUrl ?? watchUrl ?? "video"}-${index}`}
            style={videoCardStyle}
            bodyStyle={{
              display: "flex",
              flexDirection: "column",
              gap: 16,
              padding: isMobile ? 16 : 20,
            }}
          >
            {embedUrl ? (
              <div style={videoContainerStyle}>
                <iframe
                  src={embedUrl}
                  style={iframeStyle}
                  title={`transmission-${index + 1}`}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              </div>
            ) : (
              <Flex align="center" justify="center" style={{ minHeight: 180 }}>
                <Text>Nie udało się wczytać podglądu.</Text>
              </Flex>
            )}
            {watchUrl && (
              <Button
                type="primary"
                href={watchUrl}
                target="_blank"
                rel="noreferrer"
                block={isMobile}
              >
                Otwórz transmisję na YouTube
              </Button>
            )}
          </Card>
        ))
      )}
    </Space>
  );
};

export default LivePage;
