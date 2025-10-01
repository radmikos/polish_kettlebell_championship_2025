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

// let SHOW_GENERAL_CLASSIFICATION = true;
// Odkomentuj poniższą linię, aby ukryć klasyfikację generalną na potrzeby testów lub prezentacji.
let SHOW_GENERAL_CLASSIFICATION = false;

type ProcessedCategoryRow = CategoryOverallRow & { displayRank: number };
type DisciplineRow = ProcessedCategoryRow & { disciplineRank: number };

const disciplineResultKeyMap = {
  snatch: "snatch_result",
  tgu: "tgu_result",
  squat: "squat_result",
  see_saw_press: "see_saw_press_result",
  pistol: "pistol_result",
  pull_up: "pull_up_result",
} as const;

type DisciplineResultKey = typeof disciplineResultKeyMap[keyof typeof disciplineResultKeyMap];

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

const isSnatchResult = (result: unknown): result is SnatchResult => {
  return Boolean(result) && typeof result === "object" && "repetitions" in (result as Record<string, unknown>);
};

const isAttemptsResult = (result: unknown): result is AttemptsResult => {
  return Boolean(result) && typeof result === "object" && "best_attempt" in (result as Record<string, unknown>);
};

const getDisciplinePlacement = (row: CategoryOverallRow, code: string) => {
  return row.placements?.find((placement) => placement.discipline === code);
};

const getDisciplineResult = (
  row: CategoryOverallRow,
  code: string,
): SnatchResult | AttemptsResult | null => {
  const key = (disciplineResultKeyMap as Record<string, DisciplineResultKey | undefined>)[code];
  if (!key) return null;
  return row[key] as SnatchResult | AttemptsResult | null;
};

const computePercentBw = (row: CategoryOverallRow, code: string): number | null => {
  const weight = row.player?.weight;
  if (!weight || weight <= 0) {
    return null;
  }

  const result = getDisciplineResult(row, code);
  if (!result) {
    return null;
  }

  if (isSnatchResult(result)) {
    const kettlebell = result.kettlebell_weight;
    if (kettlebell === null || kettlebell === undefined) {
      return null;
    }
    return (kettlebell / weight) * 100;
  }

  if (isAttemptsResult(result)) {
    const best = result.best_attempt;
    if (best === null || best === undefined) {
      return null;
    }
    return (best / weight) * 100;
  }

  return null;
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

    const leftPlacement = a.placement_points ?? Number.MAX_SAFE_INTEGER;
    const rightPlacement = b.placement_points ?? Number.MAX_SAFE_INTEGER;
    if (leftPlacement !== rightPlacement) return leftPlacement - rightPlacement;

    return (a.player?.full_name ?? '').localeCompare(b.player?.full_name ?? '');
  });

  return {
    info: infoResponse.data,
    results: sortedResults,
  };
};

const useOverallColumns = (
  info: CategorySummary | undefined,
  labelMap: Map<string, string>,
): ColumnsType<ProcessedCategoryRow> => {
  const baseColumns: ColumnsType<ProcessedCategoryRow> = [
    {
      title: "Miejsce",
      dataIndex: "displayRank",
      key: "rank",
      width: 90,
      align: "center",
      sorter: (a, b) => (a.displayRank ?? 999) - (b.displayRank ?? 999),
      render: (_value, record) => record.displayRank ?? "-",
    },
    {
      title: "Imię i nazwisko",
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
      width: 110,
      render: (value: number | null | undefined) => formatNumber(value, 1),
      sorter: (a, b) => (a.player?.weight ?? 0) - (b.player?.weight ?? 0),
    },
    {
      title: "Tie-break",
      dataIndex: "tiebreak_points",
      key: "tiebreak",
      align: "center",
      width: 120,
      render: (value: number | null | undefined) => formatInteger(value),
      sorter: (a, b) => (a.tiebreak_points ?? 0) - (b.tiebreak_points ?? 0),
    },
  ];

  const disciplineColumns: ColumnsType<ProcessedCategoryRow> = (info?.disciplines ?? []).map((code) => {
    const label = labelMap.get(code) ?? code;

    return {
      title: `Miejsce · ${label}`,
      key: `overall-place-${code}`,
      dataIndex: ["discipline_places", code],
      align: "center",
      width: 120,
      render: (_value: number | null | undefined, record) =>
        formatInteger(record.discipline_places?.[code]),
      sorter: (a, b) =>
        (a.discipline_places?.[code] ?? Number.MAX_SAFE_INTEGER) -
        (b.discipline_places?.[code] ?? Number.MAX_SAFE_INTEGER),
    };
  });

  const sumColumn: ColumnsType<ProcessedCategoryRow>[number] = {
    title: "Suma punktów",
    dataIndex: "total_points",
    key: "total-points",
    align: "right",
    width: 160,
    render: (value: number | null | undefined) => formatInteger(value),
    sorter: (a, b) =>
      (a.total_points ?? Number.MAX_SAFE_INTEGER) -
      (b.total_points ?? Number.MAX_SAFE_INTEGER),
  };

  return [...baseColumns, ...disciplineColumns, sumColumn];
};

const createDisciplineColumns = (code: string): ColumnsType<DisciplineRow> => {
  const baseColumns: ColumnsType<DisciplineRow> = [
    {
      title: "Miejsce",
      dataIndex: "disciplineRank",
      key: `${code}-rank`,
      width: 90,
      align: "center",
      sorter: (a, b) => (a.disciplineRank ?? 999) - (b.disciplineRank ?? 999),
      render: (_value, record) => {
        const placement = getDisciplinePlacement(record, code);
        return placement?.position ?? record.disciplineRank ?? "-";
      },
    },
    {
      title: "Imię i nazwisko",
      dataIndex: ["player", "full_name"],
      key: `${code}-athlete`,
      render: (_value, record) => record.player?.full_name ?? "-",
      sorter: (a, b) =>
        (a.player?.full_name ?? "").localeCompare(b.player?.full_name ?? ""),
      ellipsis: true,
    },
    {
      title: "Klub",
      dataIndex: ["player", "club", "name"],
      key: `${code}-club`,
      render: (value, record) => value ?? record.player?.club?.name ?? "-",
      sorter: (a, b) =>
        (a.player?.club?.name ?? "").localeCompare(b.player?.club?.name ?? ""),
      ellipsis: true,
    },
    {
      title: "Waga",
      dataIndex: ["player", "weight"],
      key: `${code}-weight`,
      align: "right",
      width: 110,
      render: (value: number | null | undefined) => formatNumber(value, 1),
      sorter: (a, b) => (a.player?.weight ?? 0) - (b.player?.weight ?? 0),
    },
    {
      title: "% BW",
      key: `${code}-percent-bw`,
      align: "right",
      width: 110,
      render: (_value, record) => {
        const percent = computePercentBw(record, code);
        return percent === null ? "-" : `${formatNumber(percent, 1)}%`;
      },
      sorter: (a, b) => {
        const left = computePercentBw(a, code) ?? Number.POSITIVE_INFINITY;
        const right = computePercentBw(b, code) ?? Number.POSITIVE_INFINITY;
        return left - right;
      },
    },
  ];

  const resultColumn = {
    title: "Wynik",
    key: `${code}-result`,
    render: (_value: unknown, record: DisciplineRow) => {
      const result = getDisciplineResult(record, code);
      if (!result) {
        return "-";
      }

      if (isSnatchResult(result)) {
        return (
          <div className={styles.disciplineResultCell}>
            <span>Powtórzenia: {formatInteger(result.repetitions)}</span>
            <span>Kettlebell: {formatNumber(result.kettlebell_weight, 1)} kg</span>
          </div>
        );
      }

      if (isAttemptsResult(result)) {
        const attempts = [result.attempt_1, result.attempt_2, result.attempt_3]
          .filter((attempt): attempt is number => attempt !== null && attempt !== undefined)
          .map((attempt) => formatNumber(attempt, 1))
          .join(" · ");

        return (
          <div className={styles.disciplineResultCell}>
            <span>Najlepsza próba: {formatNumber(result.best_attempt, 1)}</span>
            {attempts && <span>Próby: {attempts}</span>}
          </div>
        );
      }

      return "-";
    },
  } satisfies ColumnsType<DisciplineRow>[number];

  const pointsColumn: ColumnsType<DisciplineRow>[number] = {
    title: "Punkty",
    key: `${code}-points`,
    dataIndex: ["discipline_points", code],
    align: "right",
    width: 130,
    render: (value: number | null | undefined) => formatNumber(value, 2),
    sorter: (a, b) =>
      (a.discipline_points?.[code] ?? 0) - (b.discipline_points?.[code] ?? 0),
  };

  return [...baseColumns, resultColumn, pointsColumn];
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
        <span>Miejsce: {formatInteger(result.place)}</span>
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
        <span>Miejsce: {formatInteger(result.place)}</span>
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

  const overallColumns = useOverallColumns(data?.info, labelMap);

  const disciplineTables = useMemo(() => {
    const entries = (data?.info?.disciplines ?? []).map((code) => {
      const label = labelMap.get(code) ?? code;

      const sortedRows = [...filteredResults]
        .sort((left, right) => {
          const leftPlacement = getDisciplinePlacement(left, code)?.position;
          const rightPlacement = getDisciplinePlacement(right, code)?.position;

          if (leftPlacement && rightPlacement && leftPlacement !== rightPlacement) {
            return leftPlacement - rightPlacement;
          }

          if (leftPlacement && !rightPlacement) {
            return -1;
          }

          if (!leftPlacement && rightPlacement) {
            return 1;
          }

          const leftPoints = left.discipline_points?.[code] ?? Number.NEGATIVE_INFINITY;
          const rightPoints = right.discipline_points?.[code] ?? Number.NEGATIVE_INFINITY;

          if (leftPoints !== rightPoints) {
            return rightPoints - leftPoints;
          }

          return (left.player?.full_name ?? "").localeCompare(right.player?.full_name ?? "");
        })
        .map((row, index) => ({
          ...row,
          disciplineRank: getDisciplinePlacement(row, code)?.position ?? index + 1,
        }));

      return {
        code,
        label,
        columns: createDisciplineColumns(code),
        rows: sortedRows,
      };
    });

    return entries;
  }, [data?.info?.disciplines, filteredResults, labelMap]);

  const expandedRowRender = useCallback(
    (record: ProcessedCategoryRow) => {
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
          {info.drop_worst_result
            ? "W klasyfikacji pomijamy najgorszy wynik zawodnika (Snatch zawsze liczony)."
            : ""}
        </Paragraph>
        <div className={styles.disciplines}>
          {(info.disciplines_verbose ?? []).map((disc) => (
            <span key={disc.code} className={styles.disciplineChip}>
              {disc.label}
            </span>
          ))}
        </div>
      </div>

      <div className={styles.tablesStack}>
        {SHOW_GENERAL_CLASSIFICATION && (
          <div className={styles.tableCard}>
            <div className={styles.tableTitle}>
              <Title level={3}>Klasyfikacja generalna</Title>
            </div>
            <Table<ProcessedCategoryRow>
              columns={overallColumns}
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
              scroll={isMobile ? { x: "max-content" } : { x: "max-content" }}
              sticky={{ offsetHeader: isMobile ? 72 : 88 }}
            />
          </div>
        )}

        {disciplineTables.map((table) => (
          <div key={table.code} className={styles.tableCard}>
            <div className={styles.tableTitle}>
              <Title level={3}>Wyniki · {table.label}</Title>
            </div>
            <Table<DisciplineRow>
              columns={table.columns}
              dataSource={table.rows}
              rowKey={(record) => `${table.code}-${record.id}`}
              pagination={
                isMobile
                  ? { pageSize: 15, showSizeChanger: false }
                  : { pageSize: 25, showSizeChanger: true }
              }
              size={isMobile ? "small" : "middle"}
              scroll={isMobile ? { x: "max-content" } : { x: "max-content" }}
              sticky={{ offsetHeader: isMobile ? 72 : 88 }}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default CategoryPage;
