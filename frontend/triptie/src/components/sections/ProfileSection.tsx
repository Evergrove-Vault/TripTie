import styles from './ProfileSection.module.css';

export default function ProfileSection() {
  return (
    <section id="profile" className={styles.card}>
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.eyebrow}>Профиль</p>
          <h2 className={styles.sectionTitle}>Личный кабинет</h2>
          <p className={styles.subtext}>Данные хранятся локально в браузере.</p>
        </div>
      </div>
      <form className={styles.formGrid}>
        <div className={styles.formField}>
          <span className={styles.labelText}>Логин</span>
          <input
            type="text"
            name="username"
            className={styles.input}
            placeholder="username"
          />
        </div>

        <div className={styles.formField}>
          <span className={styles.labelText}>Email</span>
          <input
            type="email"
            name="email"
            className={styles.input}
            placeholder="you@mail.com"
          />
        </div>

        <div className={styles.formField}>
          <span className={styles.labelText}>Пароль</span>
          <input
            type="password"
            name="password"
            className={styles.input}
            placeholder="•••••••"
          />
        </div>

        <div className={styles.formField}>
          <span className={styles.labelText}>Имя</span>
          <input
            type="text"
            name="first_name"
            className={styles.input}
            placeholder="Алиса"
          />
        </div>

        <div className={styles.formField}>
          <span className={styles.labelText}>Фамилия</span>
          <input
            type="text"
            name="last_name"
            className={styles.input}
            placeholder="Иванова"
          />
        </div>

        <div className={styles.formActions}>
          <button className={`${styles.btn} ${styles.primary}`} type="submit">
            Сохранить
          </button>
          <span className={styles.hint}>Сохраняется в localStorage</span>
        </div>

        <div className={styles.feedback} id="profileMsg"></div>
      </form>
    </section>
  );
}