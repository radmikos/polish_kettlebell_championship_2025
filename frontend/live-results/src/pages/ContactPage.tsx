import { Typography, Divider } from "antd";
import styles from "./ContactPage.module.css";

const { Title, Paragraph, Link } = Typography;

const ContactPage = () => {
  return (
    <div className={styles.contactPage}>
      <div className={styles.card}>
        <Title level={1}>Kontakt</Title>
        <Paragraph className={styles.tagline}>
          Masz pytania dotyczące wyników, transmisji lub harmonogramu? Skontaktuj
          się z zespołem organizacyjnym mistrzostw.
        </Paragraph>
      </div>

      <div className={styles.card}>
        <Title level={3} className={styles.cardTitle}>
          Główne kontakty
        </Title>
        <div className={styles.contactGrid}>
          <div className={styles.contactItem}>
            <span className={styles.label}>Biuro zawodów</span>
            <span className={styles.value}>+48 12345232</span>
          </div>
          <div className={styles.contactItem}>
            <span className={styles.label}>E-mail</span>
            <Link className={styles.value} href="mailto:wyniki@mpkb2025.pl">
              wyniki@mpkb2025.pl
            </Link>
          </div>
          <div className={styles.contactItem}>
            <span className={styles.label}>Media & PR</span>
            <span className={styles.value}>media@mpkb2025.pl</span>
          </div>
          <div className={styles.contactItem}>
            <span className={styles.label}>Adres hali</span>
            <span className={styles.value}>
              Hala Widowiskowo-Sportowa w Bochni, 
              Księcia Józefa Poniatowskiego 32, 32-700 Bochnia
            </span>
          </div>
        </div>
      </div>

      <div className={styles.card}>
        <Title level={3} className={styles.cardTitle}>
          Dodatkowe informacje
        </Title>
        <Paragraph>
          Aktualizacje na żywo pochodzą bezpośrednio z systemu sędziowskiego.
          Odświeżanie danych następuje automatycznie, ale w razie wątpliwości
          możesz przeładować stronę.
        </Paragraph>
        <Divider />
        <Paragraph>
          Oficjalne komunikaty znajdziesz na profilu społecznościowym klubu
          organizatora.
        </Paragraph>
      </div>
    </div>
  );
};

export default ContactPage;
