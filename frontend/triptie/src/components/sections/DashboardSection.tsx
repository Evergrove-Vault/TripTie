'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import styles from './DashboardSection.module.css';

interface Trip {
  id: number;
  name: string;
  join_code: string;
  creator_id: number;
  city_id: number;
}

export default function DashboardSection() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'active' | 'done'>('all');
  const [userId, setUserId] = useState<number | null>(null);

  useEffect(() => {
    // Загружаем user_id из localStorage
    if (typeof window !== 'undefined') {
      const userData = localStorage.getItem('user');
      if (userData) {
        try {
          const user = JSON.parse(userData);
          setUserId(user.id);
        } catch (e) {
          console.error('Ошибка при чтении данных пользователя:', e);
        }
      }
    }
  }, []);

  useEffect(() => {
    if (userId) {
      loadTrips();
    } else {
      setIsLoading(false);
    }
  }, [userId]);

  // Слушаем события обновления поездок
  useEffect(() => {
    const handleTripsUpdate = () => {
      if (userId) {
        loadTrips();
      }
    };

    window.addEventListener('tripsUpdated', handleTripsUpdate);
    window.addEventListener('userUpdated', handleTripsUpdate);

    return () => {
      window.removeEventListener('tripsUpdated', handleTripsUpdate);
      window.removeEventListener('userUpdated', handleTripsUpdate);
    };
  }, [userId]);

  const loadTrips = async () => {
    if (!userId) return;
    
    try {
      const response = await fetch(`/api/trips/?user_id=${userId}`);
      if (response.ok) {
        const data = await response.json();
        setTrips(data);
      }
    } catch (error) {
      console.error('Ошибка загрузки поездок:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredTrips = trips; // Можно добавить фильтрацию по статусу

  return (
    <section id="dashboard" className={styles.card}>
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.eyebrow}>Поездки</p>
          <h2 className={styles.sectionTitle}>Ваши путешествия</h2>
        </div>
        <div className={styles.chipGroup}>
          <button
            className={`${styles.chip} ${filter === 'all' ? styles.active : ''}`}
            onClick={() => setFilter('all')}
          >
            Все
          </button>
          <button
            className={`${styles.chip} ${filter === 'active' ? styles.active : ''}`}
            onClick={() => setFilter('active')}
          >
            Текущие
          </button>
          <button
            className={`${styles.chip} ${filter === 'done' ? styles.active : ''}`}
            onClick={() => setFilter('done')}
          >
            Завершённые
          </button>
        </div>
      </div>
      <div className={styles.actionsRow}>
        <Link href="/create" className={`${styles.btn} ${styles.primary}`}>
          Создать поездку
        </Link>
      </div>
      {isLoading ? (
        <div className={styles.empty}>Загрузка...</div>
      ) : !userId ? (
        <div className={styles.empty}>
          Войдите в аккаунт, чтобы увидеть свои поездки.
        </div>
      ) : filteredTrips.length === 0 ? (
        <div className={styles.empty}>
          Пока нет поездок. Создайте новую или введите код для присоединения.
        </div>
      ) : (
        <div className={styles.grid}>
          {filteredTrips.map((trip) => (
            <div key={trip.id} className={styles.tripCard}>
              <h3>{trip.name}</h3>
              <p className={styles.tripCode}>Код: {trip.join_code}</p>
              <p className={styles.tripId}>ID поездки: {trip.id}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
