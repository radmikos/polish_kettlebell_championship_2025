import { Layout, Typography, Button, Space, Divider } from "antd";
import { ArrowRightOutlined, CalendarOutlined } from "@ant-design/icons";
import "./App.css";

const { Header, Content, Footer } = Layout;
const { Title, Paragraph, Text } = Typography;

function App() {
  return (
    <Layout className="app-shell">
      <Header className="app-header">
        <div className="app-brand">MP KB 2025</div>
        <Space size={16}>
          <Button type="text" className="app-nav-link">
            Wyniki live
          </Button>
          <Button type="text" className="app-nav-link">
            Regulamin
          </Button>
          <Button type="primary" shape="round" icon={<CalendarOutlined />}>Harmonogram</Button>
        </Space>
      </Header>

      <Content className="app-content">
        <div className="app-hero">
          <Title level={1} className="app-title">
            Mistrzostwa Polski Kettlebell 2025
          </Title>
          <Paragraph className="app-lead">
            Oficjalna platforma zawodów. Śledź na bieżąco wyniki, klasyfikacje oraz harmonogram startów.
          </Paragraph>

          <Space size="large">
            <Button
              type="primary"
              size="large"
              shape="round"
              icon={<ArrowRightOutlined />}
            >
              Przejdź do wyników
            </Button>
            <Button size="large" shape="round" ghost>
              Pobierz regulamin
            </Button>
          </Space>
        </div>

        <Divider className="app-divider" />

        <section className="app-highlights">
          <article className="app-card">
            <Title level={3}>Klasyfikacje na żywo</Title>
            <Paragraph type="secondary">
              Każda konkurencja aktualizuje się automatycznie po wprowadzeniu wyniku.
            </Paragraph>
          </article>
          <article className="app-card">
            <Title level={3}>Panel organizatora</Title>
            <Paragraph type="secondary">
              Intuicyjne narzędzia do rejestracji, wprowadzania i weryfikacji rezultatów.
            </Paragraph>
          </article>
          <article className="app-card">
            <Title level={3}>Dark mode by design</Title>
            <Paragraph type="secondary">
              Dedykowany motyw oparty na tokenach Ant Design dopasowany do identyfikacji zawodów.
            </Paragraph>
          </article>
        </section>
      </Content>

      <Footer className="app-footer">
        <Text type="secondary">© {new Date().getFullYear()} MP KB 2025 · Projekt i wdrożenie</Text>
      </Footer>
    </Layout>
  );
}

export default App;
