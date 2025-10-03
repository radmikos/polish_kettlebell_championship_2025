export const slugify = (input: string, fallback = "lista-startowa"): string => {
  const base = (input ?? "").trim();
  if (!base) {
    return fallback;
  }

  const normalized = base
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .replace(/-{2,}/g, "-")
    .trim();

  return normalized || fallback;
};
