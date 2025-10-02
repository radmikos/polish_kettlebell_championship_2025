import type { GlobalToken } from "antd/es/theme/interface";

export type LayoutConstants = {
  maxWidth: number;
  headerHeight: number;
};

export const layoutConstants: LayoutConstants = {
  maxWidth: 1600,
  headerHeight: 64,
};

const fontFamilyUi =
  '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif';
const fontFamilyHeading = '"Bebas Neue", sans-serif';
const fontFamilyBody = '"Oswald", sans-serif';

export const seedTokens: Partial<GlobalToken> = {
  colorPrimary: "#64ff0bff",
  colorSuccess: "#4ade80",
  colorWarning: "#facc15",
  colorError: "#ef4444",
  colorInfo: "#0bb6ff",
  colorBgBase: "#0d0d0d",
  colorBgContainer: "#201913ff",
  colorBgElevated: "#d5a919",
  colorTextBase: "#f00000ff",
  colorBorder: "#ffc857",
  colorBorderSecondary: "#303b4d",
  colorLink: "#38bdf8",
  colorLinkHover: "#0ea5e9",
  borderRadius: 12,
  borderRadiusSM: 8,
  borderRadiusLG: 16,
  fontFamily: fontFamilyUi,
  fontSize: 16,
  fontSizeHeading1: 36,
  fontSizeHeading2: 28,
  fontSizeHeading3: 22,
  fontSizeHeading4: 18,
  fontSizeHeading5: 16,
  fontWeightStrong: 600,
  lineHeight: 1.6,
  controlHeight: 40,
  motionDurationMid: "0.2s",
  motionDurationSlow: "0.3s",
};

export const aliasTokens: Partial<GlobalToken> = {
  colorPrimaryBg: "#2c761dff",
  colorPrimaryBorder: "#697a81ff",
  colorPrimaryHover: "#1d5a76",
  colorLinkActive: "#0ea5e9",
  colorText: "#ff0000ff",
  colorTextSecondary: "rgba(46, 20, 20, 0.75)",
  colorBgLayout: "#0d0d0d",
  colorBgContainerDisabled: "#696969",
  colorTextLabel: "rgba(255, 255, 255, 0.72)",
  colorTextHeading: "#831515ff",
  controlHeightLG: 44,
  controlHeightSM: 32,
  fontFamily: fontFamilyUi,
  colorFillSecondary: "rgba(28, 104, 196, 0.3)",
  colorFillTertiary: "rgba(24, 24, 27, 0.64)",
  colorFillAlter: "rgba(255, 255, 255, 0.08)",
};

export const typography = {
  fontFamilyUi,
  fontFamilyHeading,
  fontFamilyBody,
};
