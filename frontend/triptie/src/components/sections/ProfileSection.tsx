'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import styles from './ProfileSection.module.css';

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
    return (parts[0][0] + parts[1][0]).toUpperCase();
  }
  
  if (trimmed.length >= 2) {
    return trimmed.substring(0, 2).toUpperCase();
  }
  return trimmed[0].toUpperCase();
}

export default function ProfileSection() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const loadUser = () => {
      const userData = localStorage.getItem('user');
      if (userData) {
        try {
          const parsedUser = JSON.parse(userData);
          setUser(parsedUser);
        } catch (e) {
          console.error('Ошибка при чтении данных пользователя:', e);
        }
      }
      setIsLoading(false);
    };

    loadUser();

    // Слушаем изменения localStorage
    const handleStorageChange = () => {
      loadUser();
    };

    window.addEventListener('userUpdated', handleStorageChange);
    window.addEventListener('storage', (e) => {
      if (e.key === 'user') {
        loadUser();
      }
    });

    return () => {
      window.removeEventListener('userUpdated', handleStorageChange);
    };
  }, []);

  if (isLoading) {
    return (
      <section id="profile" className={styles.card}>
        <div className={styles.sectionHeader}>
          <div>
            <p className={styles.eyebrow}>Профиль</p>
            <h2 className={styles.sectionTitle}>Загрузка...</h2>
          </div>
        </div>
      </section>
    );
  }

  if (!user) {
    return (
      <section id="profile" className={styles.card}>
        <div className={styles.sectionHeader}>
          <div>
            <p className={styles.eyebrow}>Профиль</p>
            <h2 className={styles.sectionTitle}>Необходима авторизация</h2>
          </div>
        </div>
        <div className={styles.notLoggedIn}>
          <p>Для просмотра профиля необходимо войти в аккаунт.</p>
          <button 
            className={`${styles.btn} ${styles.primary}`}
            onClick={() => router.push('/auth')}
          >
            Войти / Регистрация
          </button>
        </div>
      </section>
    );
  }

  return (
    <section id="profile" className={styles.card}>
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.eyebrow}>Профиль</p>
          <h2 className={styles.sectionTitle}>Личный кабинет</h2>
        </div>
      </div>

      <div className={styles.profileInfo}>
        <div className={styles.avatarSection}>
          <div className={styles.profileAvatar} title={user.username}>
            {getInitials(user.username)}
          </div>
          <h3 className={styles.profileName}>{user.username}</h3>
        </div>

        <div className={styles.infoGrid}>
          <div className={styles.infoItem}>
            <span className={styles.infoLabel}>Логин</span>
            <span className={styles.infoValue}>{user.username}</span>
          </div>

          <div className={styles.infoItem}>
            <span className={styles.infoLabel}>Email</span>
            <span className={styles.infoValue}>{user.email}</span>
          </div>
        </div>
      </div>
    </section>
  );
}