import type { CSSProperties } from "react";
import type { GlobalToken } from "antd";

/**
 * Centralized helpers for layout/styling primitives shared across feature pages.
 *
 * Page style overview:
 * - `pages/HomePage.tsx`: hero banner + category grids (inline Ant Design styles).
 * - `pages/CategoryPage.tsx`: tables and discipline detail cards (inline + table tokens).
 * - `pages/LivePage.tsx`: video cards (reuses panel helpers for card backgrounds).
 * - `pages/ContactPage.tsx`: fully driven by the utilities below for section spacing.
 */

type GapSize = "compact" | "regular" | "spacious";

const gapMap: Record<GapSize, number> = {
  compact: 12,
  regular: 20,
  spacious: 28,
};

export const pageSectionStyle = (
  token: GlobalToken,
  gap: GapSize = "regular",
): CSSProperties => ({
  display: "flex",
  flexDirection: "column",
  gap: gapMap[gap],
  width: "100%",
  color: token.colorText,
});

/**
 * Shared card shell used by LivePage video items and ContactPage panels.
 * Keeps background/border consistent with the theme tokens.
 */

export const panelCardStyle = (token: GlobalToken): CSSProperties => ({
  background: token.colorBgContainer,
  border: `1px solid ${token.colorBorder}`,
  borderRadius: token.borderRadiusLG,
  width: "100%",
});

/**
 * Default paddings/stacks for panel content. Compact = mobile sections, spacious = desktop hero cards.
 */
export const panelCardBodyStyle = (gap: GapSize = "regular"): CSSProperties => ({
  display: "flex",
  flexDirection: "column",
  gap: gapMap[gap],
  padding: gapMap[gap],
});

/**
 * Typography helpers used for metadata labels within ContactPage and any future info lists.
 */
export const metaLabelStyle = (token: GlobalToken): CSSProperties => ({
  fontSize: 12,
  textTransform: "uppercase",
  letterSpacing: "0.1em",
  color: token.colorTextSecondary,
});

/**
 * Companion to metaLabelStyle, highlighting the primary value text.
 */
export const metaValueStyle = (token: GlobalToken): CSSProperties => ({
  fontSize: token.fontSize + 1,
  color: token.colorText,
  fontWeight: 500,
});
