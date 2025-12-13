'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import styles from './Header.module.css';
import AuthModal from '../AuthModal/AuthModal';

interface User {
  id: number;
  username: string;
  email: string;
}

function getInitials(username: string): string {
  if (!username || !username.trim()) return '?';
  const trimmed = username.trim();
  const parts = trimmed.split(/\s+/).filter(p => p.length > 0);
  
  if (parts.length >= 2) {
    // Если есть два или более слова, берем первые буквы первых двух слов
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
  
  // Если одно слово, берем первые две буквы (или одну, если слово короткое)
  if (trimmed.length >= 2) {
    return trimmed.substring(0, 2).toUpperCase();
  }
  return trimmed[0].toUpperCase();
}

export default function Header() {
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const pathname = usePathname();
  const router = useRouter();
  const isHomePage = pathname === '/';

  useEffect(() => {
    // Функция для чтения данных пользователя
    const loadUser = () => {
      // Проверяем, что localStorage доступен (не SSR)
      if (typeof window === 'undefined' || !window.localStorage) {
        return;
      }
      
      const userData = localStorage.getItem('user');
      if (userData) {
        try {
          const parsedUser = JSON.parse(userData);
          setUser(parsedUser);
        } catch (e) {
          console.error('Ошибка при чтении данных пользователя:', e);
          setUser(null);
        }
      } else {
        setUser(null);
      }
    };

    // Загружаем данные при монтировании
    loadUser();

    // Слушаем изменения localStorage (когда пользователь входит/выходит из другого компонента)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'user') {
        loadUser();
      }
    };

    window.addEventListener('storage', handleStorageChange);

    // Также слушаем кастомное событие для обновления в той же вкладке
    const handleCustomStorageChange = () => {
      loadUser();
    };

    window.addEventListener('userUpdated', handleCustomStorageChange);

    // Проверяем при фокусе окна (когда пользователь возвращается на вкладку)
    const handleFocus = () => {
      loadUser();
    };

    window.addEventListener('focus', handleFocus);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('userUpdated', handleCustomStorageChange);
      window.removeEventListener('focus', handleFocus);
    };
  }, []);

  // Также обновляем при изменении pathname (навигация)
  useEffect(() => {
    if (typeof window === 'undefined' || !window.localStorage) {
      return;
    }
    
    const userData = localStorage.getItem('user');
    if (userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
      } catch (e) {
        setUser(null);
      }
    } else {
      setUser(null);
    }
  }, [pathname]);

  const handleLogout = () => {
    localStorage.removeItem('user');
    setUser(null);
    // Отправляем событие для обновления других компонентов
    window.dispatchEvent(new Event('userUpdated'));
    // Перезагружаем страницу для полного обновления состояния
    window.location.href = '/';
  };

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
            {user ? (
              <div className={styles.userMenu}>
                <div className={styles.userAvatar} title={user.username}>
                  {getInitials(user.username)}
                </div>
                <div className={styles.userDropdown}>
                  <div className={styles.userInfo}>
                    <div className={styles.userName}>{user.username}</div>
                    <div className={styles.userEmail}>{user.email}</div>
                  </div>
                  <button onClick={handleLogout} className={styles.logoutBtn}>
                    Выйти
                  </button>
                </div>
              </div>
            ) : (
              <Link href="/auth" className={`${styles.btn} ${styles.ghost}`}>
                Войти / Регистрация
              </Link>
            )}
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
