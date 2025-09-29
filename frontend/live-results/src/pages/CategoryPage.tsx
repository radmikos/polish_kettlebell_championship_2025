import { useMemo, useState, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Typography,
  Spin,
  Alert,
  Button,
  Input,
  Table,
  Tag,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import { ArrowLeftOutlined, ReloadOutlined } from "@ant-design/icons";
import useBreakpoint from "antd/es/grid/hooks/useBreakpoint";
import apiClient from "../services/api";
import {
  CategorySummary,
  CategoryOverallRow,
  CategoryResultsResponse,
  DisciplineLabel,
  AttemptsResult,
  SnatchResult,
} from "../types";
import styles from "./CategoryPage.module.css";

const { Title, Paragraph, Text } = Typography;
const { Search } = Input;

type CategoryQueryResponse = {
  info: CategorySummary;
  results: CategoryResultsResponse;
};

const formatNumber = (value: number | null | undefined, digits = 2): string => {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "-";
  }
  return new Intl.NumberFormat("pl-PL", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(value);
};

const formatInteger = (value: number | null | undefined): string => {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "-";
  }
  return String(value);
};

const buildLabelMap = (disciplines: DisciplineLabel[] | undefined) => {
  const map = new Map<string, string>();
  (disciplines ?? []).forEach((disc) => {
    map.set(disc.code, disc.label);
  });
  return map;
};

const getPlacementColor = (position: number | null | undefined): string | undefined => {
  if (position === 1) return "var(--color-warning)";
  if (position === 2) return "var(--color-link)";
  if (position === 3) return "var(--color-primary)";
  return undefined;
};

const fetchCategory = async (categoryId: string | undefined): Promise<CategoryQueryResponse> => {
  if (!categoryId) {
    throw new Error("Identyfikator kategorii jest wymagany");
  }

  const [infoResponse, resultsResponse] = await Promise.all([
    apiClient.get<CategorySummary>(`/categories/${categoryId}/`),
    apiClient.get<CategoryResultsResponse>(`/categories/${categoryId}/results/`),
  ]);

  const sortedResults = [...resultsResponse.data].sort((a, b) => {
    const left = a.final_position ?? Number.MAX_SAFE_INTEGER;
    const right = b.final_position ?? Number.MAX_SAFE_INTEGER;
    if (left !== right) return left - right;
    return (a.total_points ?? 0) < (b.total_points ?? 0) ? 1 : -1;
  });

  return {
    info: infoResponse.data,
    results: sortedResults,
  };
};

const useDisciplineColumns = (
  info: CategorySummary | undefined,
  labelMap: Map<string, string>,
): ColumnsType<CategoryOverallRow & { displayRank: number }> => {
  const baseColumns: ColumnsType<CategoryOverallRow & { displayRank: number }> = [
    {
      title: "M-ce",
      dataIndex: "displayRank",
      key: "rank",
      width: 70,
      align: "center",
      sorter: (a, b) => (a.displayRank ?? 999) - (b.displayRank ?? 999),
    },
    {
      title: "Zawodnik",
      dataIndex: ["player", "full_name"],
      key: "athlete",
      render: (_value, record) => record.player?.full_name ?? "-",
      sorter: (a, b) =>
        (a.player?.full_name ?? "").localeCompare(b.player?.full_name ?? ""),
      ellipsis: true,
    },
    {
      title: "Klub",
      dataIndex: ["player", "club", "name"],
      key: "club",
      render: (value, record) => value ?? record.player?.club?.name ?? "-",
      sorter: (a, b) =>
        (a.player?.club?.name ?? "").localeCompare(b.player?.club?.name ?? ""),
      ellipsis: true,
    },
    {
      title: "Waga",
      dataIndex: ["player", "weight"],
      key: "weight",
      align: "right",
      width: 90,
      render: (value: number | null | undefined) => formatNumber(value, 1),
      sorter: (a, b) => (a.player?.weight ?? 0) - (b.player?.weight ?? 0),
    },
    {
      title: "Suma pkt",
      dataIndex: "total_points",
      key: "total",
      align: "right",
      width: 110,
      render: (value: number | null | undefined) => formatNumber(value, 2),
      sorter: (a, b) => (a.total_points ?? 0) - (b.total_points ?? 0),
    },
    {
      title: "Liczone konkurencje",
      dataIndex: "counted_disciplines",
      key: "counted",
      width: 150,
      align: "center",
      render: (value: number | null | undefined) => formatInteger(value),
    },
    {
      title: "Dogrywka",
      dataIndex: "tiebreak_applied",
      key: "tiebreak",
      width: 110,
      align: "center",
      render: (value: boolean, record) =>
        value ? <Tag color="var(--color-warning)">+1 pkt</Tag> : record.tiebreak_points ? formatNumber(record.tiebreak_points, 2) : "-",
    },
  ];

  const disciplineColumns: ColumnsType<CategoryOverallRow & { displayRank: number }> =
    (info?.disciplines ?? []).map((code) => ({
      title: `Punkty · ${labelMap.get(code) ?? code}`,
      key: `points-${code}`,
      dataIndex: ["discipline_points", code],
      align: "right",
      render: (value: number | null | undefined) => formatNumber(value, 2),
      sorter: (a, b) =>
        (a.discipline_points?.[code] ?? 0) - (b.discipline_points?.[code] ?? 0),
      width: 130,
    }));

  const placementsColumn: ColumnsType<CategoryOverallRow & { displayRank: number }> = [
    {
      title: "Miejsca w konkurencjach",
      key: "placements",
      render: (_value, record) => (
        <div className={styles.placementsCell}>
          {record.placements?.map((placement) => (
            <Tag
              key={`${placement.discipline}-${record.id}`}
              color={getPlacementColor(placement.position)}
            >
              {labelMap.get(placement.discipline) ?? placement.discipline}
              {" · "}
              {placement.position ? `#${placement.position}` : "-"}
            </Tag>
          ))}
        </div>
      ),
    },
  ];

  return [...baseColumns, ...disciplineColumns, ...placementsColumn];
};

const renderAttemptsDetails = (
  key: string,
  label: string,
  result: AttemptsResult | null | undefined,
) => {
  if (!result) {
    return (
      <div key={key} className={styles.expandDiscipline}>
        <div className={styles.expandHeader}>{label}</div>
        <Text>Brak wyników.</Text>
      </div>
    );
  }

  return (
    <div key={key} className={styles.expandDiscipline}>
      <div className={styles.expandHeader}>{label}</div>
      <div className={styles.expandMeta}>
        <span>Próba 1: {formatNumber(result.attempt_1, 1)}</span>
        <span>Próba 2: {formatNumber(result.attempt_2, 1)}</span>
        <span>Próba 3: {formatNumber(result.attempt_3, 1)}</span>
        <span>Najlepsza: {formatNumber(result.best_attempt, 1)}</span>
        <span>Punkty: {formatNumber(result.points, 2)}</span>
      </div>
    </div>
  );
};

const renderSnatchDetails = (
  key: string,
  label: string,
  result: SnatchResult | null | undefined,
) => {
  if (!result) {
    return (
      <div key={key} className={styles.expandDiscipline}>
        <div className={styles.expandHeader}>{label}</div>
        <Text>Brak wyników.</Text>
      </div>
    );
  }

  return (
    <div key={key} className={styles.expandDiscipline}>
      <div className={styles.expandHeader}>{label}</div>
      <div className={styles.expandMeta}>
        <span>Waga kettla: {formatNumber(result.kettlebell_weight, 1)} kg</span>
        <span>Powtórzenia: {formatInteger(result.repetitions)}</span>
        <span>Punkty: {formatNumber(result.points, 2)}</span>
      </div>
    </div>
  );
};

const CategoryPage = () => {
  const { categoryId } = useParams();
  const navigate = useNavigate();
  const [searchValue, setSearchValue] = useState("");
  const screens = useBreakpoint();
  const isMobile = !screens.md;

  const {
    data,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<CategoryQueryResponse, Error>({
    queryKey: ["category", categoryId],
    queryFn: () => fetchCategory(categoryId),
    enabled: Boolean(categoryId),
    staleTime: 60 * 1000,
  });

  const labelMap = useMemo(() => buildLabelMap(data?.info?.disciplines_verbose), [data?.info?.disciplines_verbose]);

  const processedResults = useMemo(() => {
    return (data?.results ?? []).map((row, index) => ({
      ...row,
      key: row.id,
      displayRank: row.final_position ?? index + 1,
    }));
  }, [data?.results]);

  const filteredResults = useMemo(() => {
    const term = searchValue.trim().toLowerCase();
    if (!term) return processedResults;
    return processedResults.filter((row) => {
      const fullName = row.player?.full_name?.toLowerCase() ?? "";
      const clubName = row.player?.club?.name?.toLowerCase() ?? "";
      return fullName.includes(term) || clubName.includes(term);
    });
  }, [processedResults, searchValue]);

  const columns = useDisciplineColumns(data?.info, labelMap);

  const expandedRowRender = useCallback(
    (record: CategoryOverallRow & { displayRank: number }) => {
      const disciplineBlocks = (data?.info?.disciplines ?? []).map((code) => {
        const label = labelMap.get(code) ?? code;
        switch (code) {
          case "snatch":
            return renderSnatchDetails(code, label, record.snatch_result);
          case "tgu":
            return renderAttemptsDetails(code, label, record.tgu_result);
          case "squat":
            return renderAttemptsDetails(code, label, record.squat_result);
          case "see_saw_press":
            return renderAttemptsDetails(code, label, record.see_saw_press_result);
          case "pistol":
            return renderAttemptsDetails(code, label, record.pistol_result);
          case "pull_up":
            return renderAttemptsDetails(code, label, record.pull_up_result);
          default:
            return (
              <div className={styles.expandDiscipline} key={code}>
                <div className={styles.expandHeader}>{label}</div>
                <Text>Brak danych dla tej konkurencji.</Text>
              </div>
            );
        }
      });

      return <div className={styles.expandWrapper}>{disciplineBlocks}</div>;
    },
    [data?.info?.disciplines, labelMap],
  );

  if (isLoading) {
    return (
      <div className={styles.page}>
        <Spin size="large" tip="Ładujemy wyniki kategorii..." />
      </div>
    );
  }

  if (isError) {
    return (
      <div className={styles.page}>
        <Alert
          type="error"
          showIcon
          message="Nie udało się wczytać danych kategorii"
          description={error?.message ?? "Spróbuj ponownie."}
          action={
            <Button onClick={() => refetch()} icon={<ReloadOutlined />}>Spróbuj ponownie</Button>
          }
        />
      </div>
    );
  }

  if (!data?.info) {
    return (
      <div className={styles.page}>
        <Alert type="warning" message="Brak danych kategorii" />
      </div>
    );
  }

  const { info } = data;

  return (
    <div className={styles.page}>
      <div className={styles.toolbar}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate(-1)}>
          Wróć
        </Button>
        <div className={styles.toolbarActions}>
          <Search
            allowClear
            placeholder="Filtruj zawodników lub klub"
            value={searchValue}
            onChange={(event) => setSearchValue(event.target.value)}
            style={{ maxWidth: isMobile ? "100%" : 320 }}
          />
          <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
            Odśwież
          </Button>
        </div>
      </div>

      <div className={styles.metaCard}>
        <Title level={2} className={styles.metaTitle}>
          {info.name}
        </Title>
        <Paragraph>
          Liczymy {info.max_counted_disciplines ? `${info.max_counted_disciplines} najlepsze wyniki` : "wszystkie konkurencje"}.
        </Paragraph>
        <div className={styles.disciplines}>
          {(info.disciplines_verbose ?? []).map((disc) => (
            <span key={disc.code} className={styles.disciplineChip}>
              {disc.label}
            </span>
          ))}
        </div>
      </div>

      <div className={styles.tableCard}>
        <div className={styles.tableTitle}>
          <Title level={3}>Klasyfikacja</Title>
          <Text type="secondary">Rekordy: {filteredResults.length}</Text>
        </div>
        <Table<CategoryOverallRow & { displayRank: number }>
          columns={columns}
          dataSource={filteredResults}
          rowKey={(record) => record.id}
          pagination={
            isMobile
              ? { pageSize: 15, showSizeChanger: false }
              : { pageSize: 25, showSizeChanger: true }
          }
          expandable={{
            expandRowByClick: true,
            expandedRowRender,
          }}
          size={isMobile ? "small" : "middle"}
          scroll={isMobile ? { x: "max-content" } : { x: 900 }}
          sticky={{ offsetHeader: isMobile ? 72 : 88 }}
        />
      </div>
    </div>
  );
};

export default CategoryPage;
