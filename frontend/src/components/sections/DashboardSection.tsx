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

  useEffect(() => {
    loadTrips();
  }, []);

  const loadTrips = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8001/trips/');
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
        <div className={styles.joinInline}>
          <input type="text" className={styles.joinInput} placeholder="Код поездки" />
          <button className={styles.btn}>Присоединиться</button>
        </div>
      </div>
      {isLoading ? (
        <div className={styles.empty}>Загрузка...</div>
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
