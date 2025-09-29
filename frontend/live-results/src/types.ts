export interface DisciplineLabel {
  code: string;
  label: string;
}

export interface SportClub {
  id: number;
  name: string;
}

export interface CategorySummary {
  id: number;
  name: string;
  disciplines: string[];
  disciplines_verbose: DisciplineLabel[];
  max_counted_disciplines: number | null;
}

export interface PlayerCategoryResult {
  category: Pick<CategorySummary, "id" | "name">;
  final_position: number | null;
  total_points: number | null;
  discipline_places: DisciplinePlaces;
  placement_points: number | null;
  counted_disciplines: number | null;
  tiebreak_points: number | null;
  discipline_points: DisciplinePoints;
}

export interface PlayerSummary {
  id: number;
  name: string;
  surname: string;
  full_name: string;
  gender: string;
  gender_display: string;
  weight: number | null;
  club: SportClub | null;
  categories: Pick<CategorySummary, "id" | "name">[];
}

export interface PlayerDetail extends PlayerSummary {
  snatch_result: SnatchResult | null;
  tgu_result: AttemptsResult | null;
  squat_result: AttemptsResult | null;
  see_saw_press_result: AttemptsResult | null;
  pistol_result: AttemptsResult | null;
  pull_up_result: AttemptsResult | null;
  overall_results: PlayerCategoryResult[];
}

export interface SnatchResult {
  kettlebell_weight: number | null;
  repetitions: number | null;
  points: number | null;
  place: number | null;
}

export interface AttemptsResult {
  attempt_1: number | null;
  attempt_2: number | null;
  attempt_3: number | null;
  best_attempt: number | null;
  points: number | null;
  place: number | null;
}

export interface DisciplinePoints {
  snatch: number | null;
  tgu: number | null;
  squat: number | null;
  see_saw_press: number | null;
  pistol: number | null;
  pull_up: number | null;
  [key: string]: number | null;
}

export interface DisciplinePlaces {
  snatch: number | null;
  tgu: number | null;
  squat: number | null;
  see_saw_press: number | null;
  pistol: number | null;
  pull_up: number | null;
  [key: string]: number | null;
}

export interface PlacementEntry {
  discipline: string;
  label: string;
  position: number | null;
  points: number | null;
}

export interface CategoryOverallRow {
  id: number;
  player: PlayerSummary;
  final_position: number | null;
  total_points: number | null;
  discipline_places: DisciplinePlaces;
  placement_points: number | null;
  counted_disciplines: number | null;
  tiebreak_points: number | null;
  tiebreak_applied: boolean;
  discipline_points: DisciplinePoints;
  placements: PlacementEntry[];
  snatch_result: SnatchResult | null;
  tgu_result: AttemptsResult | null;
  squat_result: AttemptsResult | null;
  see_saw_press_result: AttemptsResult | null;
  pistol_result: AttemptsResult | null;
  pull_up_result: AttemptsResult | null;
}

export type CategoryResultsResponse = CategoryOverallRow[];
