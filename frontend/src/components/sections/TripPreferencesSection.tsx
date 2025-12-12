import styles from './TripPreferencesSection.module.css';

export default function TripPreferencesSection() {
  return (
    <section id="plan" className={styles.card}>
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.eyebrow}>Параметры</p>
          <h2 className={styles.sectionTitle}>Предпочтения по поездке</h2>
          <p className={styles.subtext}>Выберите активности, бюджет и получите ссылку для друзей.</p>
        </div>
        <div className={styles.joinInline}>
          <input type="text" className={styles.inputSmall} placeholder="Код поездки" />
          <button className={styles.btn}>Присоединиться</button>
        </div>
      </div>

      <div className={`${styles.grid}`}>
        <div style={{width: '60%'}}>
          <h3 className={styles.sectionSubtitle}>Активности</h3>
          <input
            type="text"
            className={styles.inputBudget}
            placeholder="Например, аквапарк"
          />
        </div>
        <div style={{width: '60%'}}>
          <h3 className={styles.sectionSubtitle}>Бюджет</h3>
          <input
            type="number"
            className={styles.inputBudget}
            placeholder="Например, 50000"
          />
          <button className={styles.btn}>Сохранить</button>
        </div>
      </div>

      <div className={styles.linkBox}>
        <div>
          <p className={styles.eyebrow}>Ссылка для друзей</p>
          <p id="joinLinkValue">Сначала создайте или выберите поездку</p>
        </div>
        <button className={`${styles.btn} ${styles.btnGhost}`}>Скопировать</button>
      </div>

      <div className={styles.feedback} id="prefsMsg"></div>
    </section>
  );
}