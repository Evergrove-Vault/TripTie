'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import styles from './Header.module.css';
import AuthModal from '../AuthModal/AuthModal';

export default function Header() {
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const pathname = usePathname();
  const isHomePage = pathname === '/';

  return (
    <>
      <header className={styles.hero}>
        <div className={styles.heroTop}>
          <Link href="/" className={styles.logo}>
            TripTie
          </Link>
          <nav className={styles.nav}>
            <Link href="/" className={pathname === '/' ? styles.active : ''}>
              Главная
            </Link>
            <Link href="/create" className={pathname === '/create' ? styles.active : ''}>
              Создать поездку
            </Link>
            <Link href="/plan" className={pathname === '/plan' ? styles.active : ''}>
              План
            </Link>
            <Link href="/profile" className={pathname === '/profile' ? styles.active : ''}>
              Профиль
            </Link>
          </nav>
          <div className={styles.authLinks}>
            <Link href="/auth" className={`${styles.btn} ${styles.ghost}`}>
              Войти / Регистрация
            </Link>
          </div>
        </div>
        {isHomePage && (
          <div className={styles.heroContent}>
            <div>
              <p className={styles.eyebrow}>Розовый планировщик путешествий</p>
              <h1>Соберите поездку, поделитесь кодом, улетайте</h1>
              <p className={styles.subtext}>
                Создавайте маршруты, присоединяйтесь по коду, храните план по дням. Всё в одном месте.
              </p>
              <div className={styles.heroActions}>
                <Link href="/create" className={`${styles.btn} ${styles.primary}`}>
                  Создать путешествие
                </Link>
                <button className={`${styles.btn} ${styles.ghost}`}>Присоединиться</button>
              </div>
            </div>
            <div className={styles.heroCard}>
              <div className={styles.heroBadge}>Быстрый старт</div>
              <h3>Создай поездку за 30 секунд</h3>
              <ul>
                <li>✈️ Город и даты</li>
                <li>🏨 Отель (опционально)</li>
                <li>👥 Поделись кодом</li>
              </ul>
            </div>
          </div>
        )}
      </header>

      <AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} />
    </>
  );
}
