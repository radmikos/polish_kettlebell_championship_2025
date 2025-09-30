import { useMemo } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Typography, Spin, Alert } from "antd";
import apiClient from "../services/api";
import { CategorySummary } from "../types";
import styles from "./HomePage.module.css";

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
  { key: "pro", title: "Zawodowcy", keywords: ["pro", "elita", "elite", "professional"] },
  { key: "masters", title: "Masters", keywords: ["master", "masters", "veteran"] },
  { key: "open", title: "Open / Ogólne", keywords: ["open", "najleps", "best", "mix"] },
  { key: "other", title: "Pozostałe kategorie", keywords: [] },
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
    return "Odrzucamy najgorszy wynik (Snatch liczony obowiązkowo)";
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
      <div className={styles.loadingWrapper}>
        <Spin size="large" tip="Ładujemy kategorie..." />
      </div>
    );
  }

  if (isError) {
    return (
      <div className={styles.errorWrapper}>
        <Alert
          type="error"
          message="Nie udało się pobrać kategorii"
          description={error?.message ?? "Spróbuj ponownie za chwilę."}
          showIcon
          className={styles.errorText}
        />
      </div>
    );
  }

  const hasAnyCategory = categories.length > 0;

  return (
    <div className={styles.homePage}>
      <header className={styles.header}>
        <Title level={1}>Wyniki na żywo</Title>
        {isFetching && <Text>Odświeżamy dane…</Text>}
      </header>

      {hasAnyCategory ? (
        groupConfig.map((config) => {
          const group = groupedCategories[config.key];
          if (!group || group.length === 0) return null;

          return (
            <section key={config.key} className={styles.categorySection}>
              <Title level={2} className={styles.sectionTitle}>
                {config.title}
              </Title>
              <div className={styles.cards}>
                {group.map((category) => {
                  const secondary = formatSecondaryName(category.name);
                  return (
                    <Link
                      key={category.id}
                      to={`/category/${category.id}`}
                      className={styles.categoryLink}
                    >
                      <article className={styles.categoryCard}>
                        <div className={styles.categoryName}>
                          {formatPrimaryName(category.name)}
                        </div>
                        {secondary && (
                          <div className={styles.secondaryName}>{secondary}</div>
                        )}
                        <div className={styles.meta}>
                          {buildMetaDescription(category)}
                        </div>
                        <div className={styles.disciplines}>
                          {category.disciplines_verbose?.map((disc) => (
                            <span key={disc.code} className={styles.disciplineTag}>
                              {disc.label}
                            </span>
                          ))}
                        </div>
                      </article>
                    </Link>
                  );
                })}
              </div>
            </section>
          );
        })
      ) : (
        <Paragraph className={styles.emptyState}>
          Kategorie nie są jeszcze dostępne.
        </Paragraph>
      )}
    </div>
  );
};

export default HomePage;
