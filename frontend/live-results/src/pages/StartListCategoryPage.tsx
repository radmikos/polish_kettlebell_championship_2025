import { useMemo, useState } from "react";
import { useOutletContext, useParams } from "react-router-dom";
import { Alert, Flex, Grid, Image, Space, Typography, theme, Button } from "antd";
import { DownloadOutlined } from "@ant-design/icons";
import type { StartListsOutletContext } from "./StartListsPage";

const { Title, Paragraph, Text, Link } = Typography;

const StartListCategoryPage = () => {
  const { entries } = useOutletContext<StartListsOutletContext>();
  const { slug } = useParams();
  const { token } = theme.useToken();
  const screens = Grid.useBreakpoint();
  const isDesktop = screens.md ?? false;
  const [loadError, setLoadError] = useState(false);

  const entry = useMemo(() => entries.find((item) => item.slug === slug), [entries, slug]);

  if (!entry) {
    return (
      <Alert
        type="warning"
        message="Nie znaleźliśmy listy startowej"
        description="Spróbuj wybrać kategorię ponownie lub przeładuj stronę."
        showIcon
      />
    );
  }

  return (
    <Space
      direction="vertical"
      size={isDesktop ? 16 : 12}
      style={{ width: "100%" }}
    >
      <Space direction="vertical" size={8} style={{ width: "100%" }}>
        <Title level={3} style={{ margin: 0 }}>
          {entry.name}
        </Title>
        <Paragraph type="secondary" style={{ marginBottom: 0 }}>
          Lista startowa otwiera się w nowej karcie. Jeżeli potrzebujesz pobrać plik,
          skorzystaj z poniższego przycisku lub odnośnika.
        </Paragraph>
        {entry.categoryNames.length > 1 ? (
          <Text type="secondary">
            Obejmuje kategorie: {entry.categoryNames.join(" · ")}
          </Text>
        ) : (
          <Text type="secondary">Kategoria: {entry.categoryNames[0]}</Text>
        )}
        <Flex gap={isDesktop ? 12 : 8} wrap>
          <Button
            icon={<DownloadOutlined />}
            href={entry.assetHref}
            target="_blank"
            rel="noreferrer"
            type="primary"
          >
            Pobierz listę
          </Button>
          <Text type="secondary">
            Alternatywnie: <Link href={entry.assetHref} target="_blank" rel="noreferrer">otwórz w nowej karcie</Link>
          </Text>
        </Flex>
      </Space>

      {!loadError ? (
        <Image
          src={entry.assetHref}
          alt={`Lista startowa dla kategorii ${entry.name}`}
          style={{
            width: "100%",
            maxWidth: 940,
            borderRadius: token.borderRadiusLG,
            border: `1px solid ${token.colorBorder}`,
          }}
          onError={() => setLoadError(true)}
          preview
        />
      ) : (
        <Alert
          type="info"
          message="Brak podpiętego pliku JPG"
          description="Umieść plik w katalogu public/start-lists i odśwież stronę, aby go wyświetlić."
          showIcon
        />
      )}
    </Space>
  );
};

export default StartListCategoryPage;
