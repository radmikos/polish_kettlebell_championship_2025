import type { CSSProperties } from "react";
import {
  Card,
  Space,
  Grid,
  theme,
  Button,
} from "antd";
import { FilePdfOutlined } from "@ant-design/icons";

const HomePage = () => {
  const screens = Grid.useBreakpoint();
  const { token } = theme.useToken();
  const isMobile = !screens.md;

  const sectionCardStyle: CSSProperties = {
    background: token.colorBgContainer,
    border: `1px solid ${token.colorBorder}`,
    width: "100%",
  };

  const pageGap = isMobile ? 16 : 24;

  const linkDoRegulaminu = "/regulamin.pdf"; 
  const linkDoGrafiki = "/plakat.jpg"; // Twoja grafika

  return (
    <Space 
      direction="vertical" 
      size={pageGap} 
      style={{ width: "100%" }}
    >
      
      {/* GŁÓWNA ZAWARTOŚĆ: REGULAMIN I GRAFIKA */}
      <Card
        style={sectionCardStyle}
        bodyStyle={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 24,
          padding: isMobile ? 16 : 32,
          width: "100%",
        }}
      >
        {/* Przycisk do regulaminu */}
        <Button
          type="primary"
          size="large"
          icon={<FilePdfOutlined />}
          href={linkDoRegulaminu}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            fontFamily: "Oswald, sans-serif",
            fontSize: 18,
            height: "auto",
            padding: "12px 32px",
            textTransform: "uppercase",
            letterSpacing: "0.05em",
            width: isMobile ? "100%" : "auto",
            maxWidth: 400,
          }}
        >
          Zobacz Regulamin Zawodów
        </Button>

        {/* Grafika zawodów - TUTAJ ZMIANA NA 50% SZEROKOŚCI */}
        <div style={{ 
          width: isMobile ? "100%" : "30%", // Na komputerze 50%, na telefonie full szerokość
          borderRadius: 8, 
          overflow: "hidden", 
          boxShadow: "0 4px 12px rgba(0,0,0,0.08)" 
        }}>
          <img
            src={linkDoGrafiki}
            alt="Grafika Mistrzostw Polski Kettlebell 2026"
            style={{
              width: "100%",
              height: "auto",
              display: "block",
            }}
          />
        </div>
      </Card>

    </Space>
  );
};

export default HomePage;