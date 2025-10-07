import { useEffect, useMemo } from "react";
import { Outlet, useNavigate, useParams } from "react-router-dom";
import { Card, Flex, Grid, Space, Typography, theme, Tabs, Empty } from "antd";
import type { TabsProps } from "antd";
import { pageSectionStyle, panelCardBodyStyle, panelCardStyle } from "../theme";
import { slugify } from "../utils/slug";

const { Title, Paragraph, Text } = Typography;
 
type StartListDefinition = {
  label: string;
  categories: string[];
  assetSlug?: string;
  slugOverride?: string;
};

export type StartListEntry = {
  id: string;
  name: string;
  slug: string;
  assetHref: string;
  categoryNames: string[];
};

export type StartListsOutletContext = {
  entries: StartListEntry[];
};

const buildStartListAssetHref = (slug: string): string => `/start-lists/${slug}.pdf`;

const startListDefinitions: StartListDefinition[] = [
  {
    label: "Amator K65 i Junior K",
    categories: ["Amator K65", "Junior K"],
  },
  {
    label: "Amator K +65",
    categories: ["Amator K +65"],
  },
  {
    label: "Amator M85 + Junior M",
    categories: ["Amator M85", "Junior M"],
  },
  {
    label: "Amator M+85",
    categories: ["Amator +85"],
  },
  {
    label: "PRO K65 + PRO K+65",
    categories: ["PRO K65", "PRO K+65"],
  },
  {
    label: "PRO M85 + PRO M+85",
    categories: ["PRO M85", "PRO M+85"],
  },
];

const StartListsPage = () => {
  const navigate = useNavigate();
  const params = useParams();

  const { token } = theme.useToken();
  const screens = Grid.useBreakpoint();
  const isDesktop = screens.md ?? false;
  const sectionGap = isDesktop ? "spacious" : "regular";
  const cardGap = isDesktop ? "regular" : "compact";

  const startListEntries = useMemo<StartListEntry[]>(() => {
    return startListDefinitions.map((definition) => {
      const slug = definition.slugOverride ?? slugify(definition.label);
      const assetSlug = definition.assetSlug ?? slug;
      return {
        id: slug,
        name: definition.label,
        slug,
        assetHref: buildStartListAssetHref(assetSlug),
        categoryNames: definition.categories,
      } satisfies StartListEntry;
    });
  }, []);

  const hasEntries = startListEntries.length > 0;

  useEffect(() => {
    if (!hasEntries) {
      return;
    }

    const firstSlug = startListEntries[0].slug;
    if (!params.slug) {
      navigate(firstSlug, { replace: true });
      return;
    }

    const exists = startListEntries.some((entry) => entry.slug === params.slug);
    if (!exists) {
      navigate(firstSlug, { replace: true });
    }
  }, [params.slug, hasEntries, startListEntries, navigate]);

  if (!hasEntries) {
    return (
      <Space direction="vertical" style={pageSectionStyle(token, sectionGap)}>
        <Card style={panelCardStyle(token)} bodyStyle={panelCardBodyStyle(cardGap)}>
          <Title level={1}>Listy startowe</Title>
          <Paragraph type="secondary" italic style={{ marginBottom: 0 }}>
            Dodaj kategorie w panelu administracyjnym, aby przygotować listy startowe.
          </Paragraph>
        </Card>
        <Card style={panelCardStyle(token)} bodyStyle={panelCardBodyStyle(cardGap)}>
          <Flex align="center" justify="center" style={{ minHeight: 200 }}>
            <Space direction="vertical" align="center">
              <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="Brak przypisanych kategorii." />
              <Text type="secondary">Gdy pojawią się kategorie, lista zakładek wygeneruje się automatycznie.</Text>
            </Space>
          </Flex>
        </Card>
      </Space>
    );
  }

  const tabsItems: TabsProps["items"] = startListEntries.map((entry) => ({
    key: entry.slug,
    label: entry.name,
  }));

  const outletContext = useMemo<StartListsOutletContext>(() => ({ entries: startListEntries }), [startListEntries]);

  const activeTabKey = startListEntries.some((entry) => entry.slug === params.slug)
    ? params.slug
    : startListEntries[0]?.slug;

  return (
    <Space direction="vertical" style={pageSectionStyle(token, sectionGap)}>
      <Card style={panelCardStyle(token)} bodyStyle={panelCardBodyStyle(cardGap)}>
        <Title level={1}>Listy startowe</Title>
        <Paragraph type="secondary" italic style={{ marginBottom: 0 }}>
          Wybierz zakładkę z nazwą kategorii, aby zobaczyć dedykowaną listę startową.
        </Paragraph>
      </Card>

      <Card
        style={panelCardStyle(token)}
        bodyStyle={{
          ...panelCardBodyStyle(cardGap),
          gap: cardGap === "compact" ? 12 : 16,
        }}
      >
        <Tabs
          activeKey={activeTabKey}
          items={tabsItems}
          onChange={(key) => navigate(key)}
          destroyInactiveTabPane
        />
        <Outlet context={outletContext} />
      </Card>
    </Space>
  );
};

export default StartListsPage;
