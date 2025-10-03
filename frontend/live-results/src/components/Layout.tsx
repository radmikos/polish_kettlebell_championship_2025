import { useMemo, useState } from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import {
  Layout as AntLayout,
  Menu,
  Button,
  Drawer,
  Grid,
  Flex,
  Typography,
  theme,
} from "antd";
import { MenuOutlined } from "@ant-design/icons";
import { layoutConstants } from "../theme";

const { Header, Content, Footer } = AntLayout;
const { Title, Text } = Typography;

type NavEntry = {
  key: string;
  path: string;
  text: string;
};

const navConfig: NavEntry[] = [
  { key: "live", path: "/live", text: "Transmisja live" },
  { key: "start-lists", path: "/start-lists", text: "Listy startowe" },
  { key: "contact", path: "/contact", text: "Kontakt" },
];

const Layout = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const location = useLocation();
  const screens = Grid.useBreakpoint();
  const { token } = theme.useToken();
  const currentYear = useMemo(() => new Date().getFullYear(), []);

  const selectedKeys = useMemo(() => {
    if (location.pathname.startsWith("/live")) return ["live"];
    if (location.pathname.startsWith("/start-lists")) return ["start-lists"];
    if (location.pathname.startsWith("/contact")) return ["contact"];
    return [];
  }, [location.pathname]);

  const isDesktop = screens.md ?? false;

  return (
    <AntLayout
      style={{
        minHeight: "100vh",
        background: token.colorBgLayout,
      }}
    >
      <Header
        style={{
          position: "sticky",
          top: 0,
          zIndex: token.zIndexPopupBase ?? 1000,
          paddingInline: 0,
          backdropFilter: "blur(6px)",
          borderBottom: `1px solid ${token.colorBorder}`,
        }}
      >
        <Flex
          align="center"
          justify="space-between"
          wrap="wrap"
          gap={12}
          style={{
            margin: "0 auto",
            maxWidth: layoutConstants.maxWidth,
            width: "100%",
            paddingInline: isDesktop ? 32 : 20,
            minHeight: layoutConstants.headerHeight,
            background: token.colorBgContainer,
          }}
        >
          <Title
            level={3}
            style={{
              margin: 0,
              flex: "1 1 320px",
              minWidth: 0,
              color: token.colorTextHeading,
              letterSpacing: "0.08em",
              textTransform: "uppercase",
            }}
          >
            <Link
              to="/"
              style={{
                color: "inherit",
                textDecoration: "none",
              }}
            >
              Mistrzostwa Polski Kettlebell 2025
            </Link>
          </Title>

          {isDesktop ? (
            <Menu
              mode="horizontal"
              selectedKeys={selectedKeys}
              disabledOverflow
              items={navConfig.map((entry) => ({
                key: entry.key,
                label: (
                  <Link to={entry.path}>
                    {entry.text}
                  </Link>
                ),
              }))}
              className="layout-nav-menu"
              style={{
                borderBottom: "none",
                background: "transparent",
                marginLeft: "auto",
              }}
            />
          ) : (
            <Button
              icon={<MenuOutlined />}
              type="primary"
              onClick={() => setDrawerOpen(true)}
            />
          )}
        </Flex>
      </Header>

      <Drawer
        title="Nawigacja"
        placement="right"
        onClose={() => setDrawerOpen(false)}
        open={drawerOpen}
        styles={{
          body: {
            padding: 0,
            background: token.colorBgContainer,
          },
          header: {
            background: token.colorBgContainer,
            borderBottom: `1px solid ${token.colorBorder}`,
          },
          content: {
            background: token.colorBgContainer,
          },
        }}
      >
        <Menu
          mode="vertical"
          selectedKeys={selectedKeys}
          items={navConfig.map((entry) => ({
            key: entry.key,
            label: (
              <Link to={entry.path} onClick={() => setDrawerOpen(false)}>
                {entry.text}
              </Link>
            ),
          }))}
          style={{
            borderRight: "none",
            background: "transparent",
          }}
        />
      </Drawer>

      <Content
        style={{
          width: "100%",
          maxWidth: layoutConstants.maxWidth,
          margin: "24px auto",
          padding: isDesktop ? 32 : 20,
          borderRadius: token.borderRadiusLG,
          background: token.colorBgContainer,
          border: `1px solid ${token.colorBorder}`,
        }}
      >
        <Outlet />
      </Content>

      <Footer
        style={{
          textAlign: "center",
          color: token.colorTextDescription,
          background: "transparent",
          borderTop: `1px solid ${token.colorBorder}`,
          padding: "24px 16px",
        }}
      >
        <Text>
          © {currentYear} Mistrzostwa Polski Kettlebell. Wszelkie prawa zastrzeżone.
        </Text>
      </Footer>
    </AntLayout>
  );
};

export default Layout;
