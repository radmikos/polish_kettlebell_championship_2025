import { useMemo } from "react";
import type { CSSProperties } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Typography,
  Spin,
  Alert,
  Card,
  Space,
  Tag,
  Flex,
  Grid,
  theme,
} from "antd";
import apiClient from "../services/api";
import { CategorySummary } from "../types";

const { Title, Paragraph, Text } = Typography;

type GroupKey = "junior" | "amateur" | "pro" | "masters" | "open" | "other";

interface GroupConfig {
  key: GroupKey;
  title: string;
  keywords: string[];
}

const groupConfig: GroupConfig[] = [
  { key: "junior", title: "Junior", keywords: ["junior", "u16", "u18", "u19", "młodzież", "youth"] },
  { key: "amateur", title: "Amator", keywords: ["amator", "amateur", "open"] },
  { key: "pro", title: "Pro", keywords: ["pro", "elita", "elite", "professional"] },
  { key: "masters", title: "Masters", keywords: ["master", "masters", "veteran"] },
  { key: "open", title: "Open", keywords: ["open", "najleps", "best", "mix"] },
  { key: "other", title: "Kategorie dodatkowe", keywords: [] },
];

const fetchCategories = async (): Promise<CategorySummary[]> => {
  const response = await apiClient.get<CategorySummary[]>("/categories/");
  return response.data.sort((a, b) => a.name.localeCompare(b.name));
};

const formatPrimaryName = (name: string): string => {
  if (!name) return "Kategoria";
  return name.includes(" / ") ? name.split(" / ")[0].trim() : name.trim();
};

const formatSecondaryName = (name: string): string | null => {
  if (!name || !name.includes(" / ")) return null;
  const [, secondary] = name.split(" / ");
  return secondary?.trim() || null;
};

const buildMetaDescription = (category: CategorySummary): string => {
  if (category.drop_worst_result) {
    return "";
  }
  return "";
};

const assignGroup = (name: string): GroupKey => {
  const lower = name.toLowerCase();
  for (const config of groupConfig) {
    if (config.key === "other") continue;
    if (config.keywords.some((keyword) => lower.includes(keyword))) {
      return config.key;
    }
  }
  return "other";
};

const HomePage = () => {
  const {
    data: categories = [],
    isLoading,
    isError,
    error,
    isFetching,
  } = useQuery<CategorySummary[], Error>({
    queryKey: ["categories"],
    queryFn: fetchCategories,
    staleTime: 5 * 60 * 1000,
  });

  const screens = Grid.useBreakpoint();
  const { token } = theme.useToken();
  const isMobile = !screens.md;

  const groupedCategories = useMemo(() => {
    const initial: Record<GroupKey, CategorySummary[]> = {
      junior: [],
      amateur: [],
      pro: [],
      masters: [],
      open: [],
      other: [],
    };

    for (const category of categories) {
      const key = assignGroup(category.name);
      initial[key].push(category);
    }

    return initial;
  }, [categories]);

  if (isLoading) {
    return (
      <Flex align="center" justify="center" style={{ minHeight: 320 }}>
        <Spin size="large" tip="Ładujemy kategorie..." />
      </Flex>
    );
  }

  if (isError) {
    return (
      <Flex align="center" justify="center" style={{ minHeight: 320 }}>
        <Alert
          type="error"
          message="Nie udało się pobrać kategorii"
          description={error?.message ?? "Spróbuj ponownie za chwilę."}
          showIcon
          style={{ maxWidth: 420 }}
        />
      </Flex>
    );
  }

  const hasAnyCategory = categories.length > 0;
  const sectionCardStyle: CSSProperties = {
    background: token.colorBgContainer,
    border: `1px solid ${token.colorBorder}`,
  };
  const pageGap = isMobile ? 16 : 24;
  const categoryGap = isMobile ? 12 : 20;

  return (
    <Space direction="vertical" size={pageGap} style={{ width: "100%" }}>
      <Card
        style={sectionCardStyle}
        bodyStyle={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: isMobile ? 8 : 12,
          textAlign: "center",
        }}
      >
        <Title
          level={1}
          style={{
            margin: 0,
            letterSpacing: "0.14em",
            textTransform: "uppercase",
            color: token.colorTextHeading,
          }}
        >
          Wyniki na żywo
        </Title>
        {isFetching && <Text type="secondary">Odświeżamy dane…</Text>}
      </Card>

      {hasAnyCategory ? (
        groupConfig.map((config) => {
          const group = groupedCategories[config.key];
          if (!group || group.length === 0) return null;

          return (
            <Card
              key={config.key}
              title={
                <Title level={2} style={{ margin: 0 }}>
                  {config.title}
                </Title>
              }
              style={sectionCardStyle}
              headStyle={{
                borderBottom: "none",
                paddingBottom: 0,
              }}
              bodyStyle={{
                paddingTop: isMobile ? 12 : 16,
              }}
            >
              <Flex
                wrap
                gap={categoryGap}
                justify={isMobile ? "center" : "flex-start"}
              >
                {group.map((category) => {
                  const secondary = formatSecondaryName(category.name);
                  const meta = buildMetaDescription(category);
                  return (
                    <Link
                      key={category.id}
                      to={`/category/${category.id}`}
                      style={{
                        textDecoration: "none",
                        flex: "1 1 260px",
                        maxWidth: 360,
                      }}
                    >
                      <Card
                        hoverable
                        style={{
                          height: "100%",
                          background: token.colorBgElevated,
                          border: `1px solid ${token.colorBorder}`,
                        }}
                        bodyStyle={{
                          display: "flex",
                          flexDirection: "column",
                          gap: 12,
                          alignItems: "center",
                          textAlign: "center",
                          padding: isMobile ? 16 : 20,
                        }}
                      >
                        <Space direction="vertical" size={6} style={{ width: "100%" }}>
                          <Text
                            strong
                            style={{
                              fontFamily: "Oswald, sans-serif",
                              fontSize: isMobile ? 18 : 20,
                              letterSpacing: "0.06em",
                              textTransform: "uppercase",
                              color: token.colorText,
                            }}
                          >
                            {formatPrimaryName(category.name)}
                          </Text>
                          {secondary && (
                            <Text
                              style={{
                                fontFamily: "Oswald, sans-serif",
                                fontSize: isMobile ? 15 : 16,
                                textTransform: "uppercase",
                                letterSpacing: "0.05em",
                                color: token.colorTextSecondary,
                              }}
                            >
                              {secondary}
                            </Text>
                          )}
                          {meta && (
                            <Text type="secondary" style={{ fontSize: 12 }}>
                              {meta}
                            </Text>
                          )}
                        </Space>
                        <Flex wrap gap={8} justify="center">
                          {category.disciplines_verbose?.map((disc) => (
                            <Tag
                              key={disc.code}
                              bordered={false}
                              style={{
                                background: token.colorBgContainer,
                                color: token.colorLink,
                                letterSpacing: "0.05em",
                              }}
                            >
                              {disc.label}
                            </Tag>
                          ))}
                        </Flex>
                      </Card>
                    </Link>
                  );
                })}
              </Flex>
            </Card>
          );
        })
      ) : (
        <Card style={sectionCardStyle}>
          <Paragraph style={{ textAlign: "center", margin: 0 }}>
            Kategorie nie są jeszcze dostępne.
          </Paragraph>
        </Card>
      )}
    </Space>
  );
};

export default HomePage;
