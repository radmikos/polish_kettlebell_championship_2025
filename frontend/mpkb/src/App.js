import { Layout, Typography, Button, Space, Divider, Row, Col, Card } from "antd";
import { ArrowRightOutlined, CalendarOutlined } from "@ant-design/icons";
import "./App.css";

const { Header, Content, Footer } = Layout;
const { Title, Paragraph, Text } = Typography;

const highlightItems = [
  {
    title: "Klasyfikacje na żywo",
    description:
      "Każda konkurencja aktualizuje się automatycznie po wprowadzeniu wyniku.",
  },
  {
    title: "Panel organizatora",
    description:
      "Intuicyjne narzędzia do rejestracji, wprowadzania i weryfikacji rezultatów.",
  },
  {
    title: "Dark mode by design",
    description:
      "Dedykowany motyw oparty na tokenach Ant Design dopasowany do identyfikacji zawodów.",
  },
];

function App() {
  return (
    <Layout className="app-shell">
      <Header className="app-header">
        <div className="app-brand">MP KB 2025</div>
        <Space size={16} wrap>
          <Button type="text" className="app-nav-link">
            Wyniki live
          </Button>
          <Button type="text" className="app-nav-link">
            Regulamin
          </Button>
          <Button
            type="primary"
            shape="round"
            icon={<CalendarOutlined />}
          >
            Harmonogram
          </Button>
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

          <Space size="large" className="app-hero-actions" wrap>
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

        <Row gutter={[24, 24]} className="app-highlights">
          {highlightItems.map((item) => (
            <Col xs={24} md={8} key={item.title}>
              <Card className="app-feature-card" bordered={false}>
                <Title level={3}>{item.title}</Title>
                <Paragraph type="secondary">{item.description}</Paragraph>
              </Card>
            </Col>
          ))}
        </Row>
      </Content>

      <Footer className="app-footer">
        <Text type="secondary">© {new Date().getFullYear()} MP KB 2025 · Projekt i wdrożenie</Text>
      </Footer>
    </Layout>
  );
}

export default App;
