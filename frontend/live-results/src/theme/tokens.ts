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
  colorPrimary: "#bd7100ff",
  colorSuccess: "#4ade80",
  colorWarning: "#facc15",
  colorError: "#ff0000ff",
  colorInfo: "#0bb6ff",
  colorBgBase: "#0d0d0d",
  colorBgContainer: "#202020ff",
  colorBgElevated: "#f09103ff",
  colorTextBase: "#ffffffff",
  colorBorder: "#ffc857",
  colorBorderSecondary: "#303b4d",
  colorLink: "#ffffffff",
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
  colorPrimaryBg: "#d37b17ff",
  colorPrimaryBorder: "#14f500ff",
  colorPrimaryHover: "#1d5a76",
  colorLinkActive: "#0ea5e9",
  colorText: "#ffffffff",
  colorTextSecondary: "rgba(46, 20, 20, 0.75)",
  colorBgLayout: "#0d0d0d",
  colorBgContainerDisabled: "#696969",
  colorTextLabel: "rgba(255, 255, 255, 0.72)",
  colorTextHeading: "#ffffffff",
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
