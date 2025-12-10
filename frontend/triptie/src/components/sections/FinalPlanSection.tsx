import styles from './FinalPlanSection.module.css';

export default function FinalPlanSection() {
  return (
    <section id="final" className={styles.card}>
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.eyebrow}>Маршрут</p>
          <h2>План по дням</h2>
          <p className={styles.subtext}>Ниже — пример плана. После завершения поездки показываем итог.</p>
        </div>
        <button className={`${styles.btn} ${styles.ghost}`}>Изменить маршрут</button>
      </div>
      <div id="planDays" className={styles.timeline}></div>
    </section>
  );
}