import { Card, Divider, Flex, Grid, Space, Typography, theme } from "antd";
import {
  pageSectionStyle,
  panelCardBodyStyle,
  panelCardStyle,
  metaLabelStyle,
  metaValueStyle,
} from "../theme";

const { Title, Paragraph, Link, Text } = Typography;

/**
 * ContactPage layout guide
 * - Intro panel: first `Card` with level-1 heading + support copy (see JSX top of return).
 * - Contact grid: middle `Card` containing `Flex` with `contactEntries` mapped to label/value blocks.
 * - Extra info: final `Card` with additional paragraphs and a divider.
 * Spacing + surfaces reference utilities exported from `theme/sharedStyles.ts`.
 */

const contactEntries = [
  {
    label: "Organizator Kacper",
    value: "+48 511 210 841",
  },
  {
    label: "E-mail",
    value: "ckbbochnia@gmail.com",
    isLink: true,
  },
  {
    label: "Adres hali",
    value:
      "Hala Widowiskowo-Sportowa w Bochni, Księcia Józefa Poniatowskiego 32, 32-700 Bochnia",
  },
];

const ContactPage = () => {
  const { token } = theme.useToken();
  const screens = Grid.useBreakpoint();
  const isDesktop = screens.md ?? false;
  const sectionGap = isDesktop ? "spacious" : "regular";
  const cardGap = isDesktop ? "regular" : "compact";

  return (
    <Space direction="vertical" style={pageSectionStyle(token, sectionGap)}>
      <Card style={panelCardStyle(token)} bodyStyle={panelCardBodyStyle(cardGap)}>
        <Title level={1}>Kontakt</Title>
        <Paragraph type="secondary" italic style={{ marginBottom: 0 }}>
          Masz pytania dotyczące wyników, transmisji lub harmonogramu? Skontaktuj
          się z zespołem organizacyjnym mistrzostw.
        </Paragraph>
      </Card>

      <Card style={panelCardStyle(token)} bodyStyle={panelCardBodyStyle(cardGap)}>
        <Title level={3} style={{ marginBottom: 0 }}>
          Główne kontakty
        </Title>
        <Flex
          gap={cardGap === "compact" ? 16 : 20}
          wrap="wrap"
          style={{ width: "100%" }}
        >
          {contactEntries.map((entry) => (
            <Flex
              key={entry.label}
              vertical
              gap={4}
              style={{ flex: "1 1 220px", minWidth: 200 }}
            >
              <Text style={metaLabelStyle(token)}>{entry.label}</Text>
              {entry.isLink ? (
                <Link style={metaValueStyle(token)} href={`mailto:${entry.value}`}>
                  {entry.value}
                </Link>
              ) : (
                <Text style={metaValueStyle(token)}>{entry.value}</Text>
              )}
            </Flex>
          ))}
        </Flex>
      </Card>

      <Card style={panelCardStyle(token)} bodyStyle={panelCardBodyStyle(cardGap)}>
        <Title level={3} style={{ marginBottom: 0 }}>
          Dodatkowe informacje
        </Title>
        <Paragraph>
          Aktualizacje na żywo pochodzą bezpośrednio z systemu sędziowskiego.
          Odświeżanie danych następuje automatycznie, ale w razie wątpliwości
          możesz przeładować stronę.
        </Paragraph>
        <Divider style={{ margin: 0 }} />
        <Paragraph style={{ marginBottom: 0 }}>
          Oficjalne komunikaty znajdziesz na profilu społecznościowym klubu
          organizatora.
        </Paragraph>
      </Card>
    </Space>
  );
};

export default ContactPage;
