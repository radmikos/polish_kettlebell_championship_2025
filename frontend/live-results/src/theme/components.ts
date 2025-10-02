import type { ThemeConfig } from "antd";
import { aliasTokens, layoutConstants, seedTokens } from "./tokens";

const colorBgPanel = (seedTokens.colorBgContainer as string) ?? "#eb0000ff";
const colorBgBase = (seedTokens.colorBgBase as string) ?? "#0d0d0d";
const colorTextPrimary = (aliasTokens.colorText as string) ?? "#ffffffff";
const colorBorder = (seedTokens.colorBorder as string) ?? "#e62020ff";

export const componentTokens: ThemeConfig["components"] = {
  Layout: {
    bodyBg: colorBgBase,
    headerBg: colorBgPanel,
    headerHeight: layoutConstants.headerHeight,
    headerPadding: "0 24px",
    headerColor: colorTextPrimary,
    footerBg: "transparent",
    footerPadding: "16px 24px",
    siderBg: colorBgBase,
  },
  Menu: {
    colorItemBg: "transparent",
    colorItemText: colorTextPrimary,
    colorItemTextHover: (aliasTokens.colorLink as string) ?? "#069fe0ff",
    colorItemTextSelected: (seedTokens.colorPrimary as string) ?? "#0bb6ff",
    itemBorderRadius: 12,
    itemMarginInline: 4,
    itemPaddingInline: 12,
    horizontalItemBorderRadius: 12,
    horizontalItemHoverBg: "rgba(197, 3, 3, 0.08)",
    darkItemBg: "transparent",
    darkItemColor: colorTextPrimary,
    darkItemHoverColor: (aliasTokens.colorLink as string) ?? "#38bdf8",
    darkItemSelectedColor: (seedTokens.colorPrimary as string) ?? "#0bb6ff",
  },
  Button: {
    borderRadius: (seedTokens.borderRadius as number) ?? 12,
    controlHeight: (seedTokens.controlHeight as number) ?? 40,
  },
  Card: {
    colorBgContainer: colorBgPanel,
    borderRadiusLG: (seedTokens.borderRadiusLG as number) ?? 16,
    padding: 20,
    boxShadow: "none",
  },
  Table: {
    headerBg: (aliasTokens.colorPrimaryBg as string) ?? "#005a81ff",
    headerColor: (aliasTokens.colorTextHeading as string) ?? "#ffffff",
    colorBgContainer: colorBgPanel,
    rowHoverBg: (aliasTokens.colorPrimaryBgHover as string) ?? "#4d4d4dff",
    headerBorderRadius: (seedTokens.borderRadius as number) ?? 12,
    borderColor: colorBorder,
  },
  Tag: {
    borderRadiusSM: (seedTokens.borderRadiusSM as number) ?? 8,
    borderRadius: (seedTokens.borderRadiusSM as number) ?? 8,
    fontSizeSM: 12,
  },
};
