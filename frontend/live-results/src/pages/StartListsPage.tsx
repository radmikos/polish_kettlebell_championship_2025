import { useEffect, useMemo } from "react";
import { Outlet, useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Card, Flex, Grid, Space, Typography, theme, Spin, Alert, Empty, Tabs } from "antd";
import type { TabsProps } from "antd";
import apiClient from "../services/api";
import { CategorySummary } from "../types";
import { pageSectionStyle, panelCardBodyStyle, panelCardStyle } from "../theme";
import { slugify } from "../utils/slug";

const { Title, Paragraph, Text } = Typography;

type CategoryListResponse = CategorySummary[];

const fetchCategories = async (): Promise<CategoryListResponse> => {
  const response = await apiClient.get<CategorySummary[]>("/categories/");
  return response.data;
};

export type StartListEntry = {
  id: number;
  name: string;
  slug: string;
  assetHref: string;
};

export type StartListsOutletContext = {
  entries: StartListEntry[];
};

const buildStartListAssetHref = (slug: string): string => `/start-lists/${slug}.jpg`;

const StartListsPage = () => {
  const navigate = useNavigate();
  const params = useParams();
  const { data = [], isLoading, isError, error } = useQuery<CategoryListResponse>({
    queryKey: ["categories"],
    queryFn: fetchCategories,
    staleTime: 5 * 60 * 1000,
  });

  const { token } = theme.useToken();
  const screens = Grid.useBreakpoint();
  const isDesktop = screens.md ?? false;
  const sectionGap = isDesktop ? "spacious" : "regular";
  const cardGap = isDesktop ? "regular" : "compact";

  const startListEntries = useMemo<StartListEntry[]>(() => {
    return data
      .map((category) => {
        const slug = slugify(category.name);
        return {
          id: category.id,
          name: category.name,
          slug,
          assetHref: buildStartListAssetHref(slug),
        } satisfies StartListEntry;
      })
      .sort((left, right) => left.name.localeCompare(right.name, "pl", { sensitivity: "accent" }));
  }, [data]);

  const hasEntries = startListEntries.length > 0;

  useEffect(() => {
    if (!params.slug && hasEntries) {
      navigate(startListEntries[0].slug, { replace: true });
    }
  }, [params.slug, hasEntries, startListEntries, navigate]);

  if (isLoading) {
    return (
      <Flex align="center" justify="center" style={{ minHeight: 320 }}>
        <Spin size="large" tip="Ładujemy listy startowe..." />
      </Flex>
    );
  }

  if (isError) {
    return (
      <Flex align="center" justify="center" style={{ minHeight: 320 }}>
        <Alert
          type="error"
          message="Nie udało się pobrać kategorii"
          description={error instanceof Error ? error.message : "Spróbuj ponownie."}
          showIcon
        />
      </Flex>
    );
  }

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
          activeKey={params.slug ?? startListEntries[0]?.slug}
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
