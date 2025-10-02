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

const navItems = [
  {
    key: "live",
    label: (
      <Link to="/live">
        Transmisja live
      </Link>
    ),
  },
  {
    key: "contact",
    label: (
      <Link to="/contact">
        Kontakt
      </Link>
    ),
  },
];

const Layout = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const location = useLocation();
  const screens = Grid.useBreakpoint();
  const { token } = theme.useToken();
  const currentYear = useMemo(() => new Date().getFullYear(), []);

  const selectedKeys = useMemo(() => {
    if (location.pathname.startsWith("/live")) return ["live"];
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
          style={{
            margin: "0 auto",
            maxWidth: layoutConstants.maxWidth,
            width: "100%",
            paddingInline: isDesktop ? 32 : 20,
            height: layoutConstants.headerHeight,
            background: token.colorBgContainer,
          }}
        >
          <Title
            level={3}
            style={{
              margin: 0,
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
              items={navItems}
              style={{
                borderBottom: "none",
                background: "transparent",
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
          items={navItems.map((item) => ({
            ...item,
            label: (
              <Link
                to={`/${item.key === "live" ? "live" : item.key}`}
                onClick={() => setDrawerOpen(false)}
              >
                {item.key === "live" ? "Transmisja live" : "Kontakt"}
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
