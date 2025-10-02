import type { ThemeConfig } from "antd";
import { componentTokens } from "./components";
import { aliasTokens, layoutConstants, seedTokens, typography } from "./tokens";
export {
  pageSectionStyle,
  panelCardStyle,
  panelCardBodyStyle,
  metaLabelStyle,
  metaValueStyle,
} from "./sharedStyles";

const tokenOverrides = {
  ...seedTokens,
  ...aliasTokens,
} as ThemeConfig["token"];

export const themeConfig: ThemeConfig = {
  token: tokenOverrides,
  components: componentTokens,
};

export { layoutConstants, typography };
