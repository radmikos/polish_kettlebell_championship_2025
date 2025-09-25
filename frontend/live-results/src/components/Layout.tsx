import { useState } from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import { Layout as AntLayout, Menu, Button, Drawer } from "antd";
import { MenuOutlined } from "@ant-design/icons";
import styles from "./Layout.module.css";

const { Header, Content, Footer } = AntLayout;

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
  const currentYear = new Date().getFullYear();

  const selectedKeys = () => {
    if (location.pathname.startsWith("/live")) return ["live"];
    if (location.pathname.startsWith("/contact")) return ["contact"];
    return [];
  };

  return (
    <AntLayout className={styles.appContainer}>
      <Header className={styles.header}>
        <div className={styles.logoContainer}>
          <Link to="/" className={styles.logoLink}>
            Mistrzostwa Polski Kettlebell 2025
          </Link>
        </div>

        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={selectedKeys()}
          className={`${styles.navigationMenu} ${styles.desktopNav}`}
          items={navItems}
        />

        <Button
          className={styles.mobileNavButton}
          icon={<MenuOutlined />}
          type="primary"
          onClick={() => setDrawerOpen(true)}
        />
        <Drawer
          title="Nawigacja"
          placement="right"
          onClose={() => setDrawerOpen(false)}
          open={drawerOpen}
          className={styles.mobileDrawer}
        >
          <Menu
            mode="vertical"
            selectedKeys={selectedKeys()}
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
          />
        </Drawer>
      </Header>

      <Content className={styles.mainContent}>
        <Outlet />
      </Content>
      <Footer className={styles.footer}>
        © {currentYear} Mistrzostwa Polski Kettlebell. Wszelkie prawa zastrzeżone.
      </Footer>
    </AntLayout>
  );
};

export default Layout;
