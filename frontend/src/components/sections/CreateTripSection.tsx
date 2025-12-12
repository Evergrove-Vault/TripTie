'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import styles from './CreateTripSection.module.css';

export default function CreateTripSection() {
  const router = useRouter();
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setMessage(null);
    setIsLoading(true);

    const formData = new FormData(e.currentTarget);
    const tripData = {
      name: formData.get('name') as string,
      description: formData.get('description') as string || undefined,
      city_id: parseInt(formData.get('city_id') as string),
      start_date: formData.get('start_date') as string || undefined,
      end_date: formData.get('end_date') as string || undefined,
    };

    try {
      const response = await fetch('http://127.0.0.1:8001/trips/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(tripData),
      });

      const data = await response.json();

      if (!response.ok) {
        setMessage({ type: 'error', text: data.detail || 'Ошибка при создании поездки' });
        setIsLoading(false);
        return;
      }

      setMessage({ type: 'success', text: `Поездка "${data.name}" создана! Код: ${data.join_code}` });
      e.currentTarget.reset();
      
      setTimeout(() => {
        router.push('/');
      }, 2000);
    } catch (error) {
      setMessage({ type: 'error', text: 'Ошибка подключения к серверу' });
      setIsLoading(false);
    }
  };

  return (
    <section id="create" className={styles.card}>
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.eyebrow}>Новая поездка</p>
          <h2 className={styles.sectionTitle}>Создание путешествия</h2>
          <p className={styles.subtext}>
            Город задаётся по ID (из сидов: 1-Москва, 2-Санкт-Петербург, 3-Казань, 4-Екатеринбург, 5-Нижний
            Новгород, 6-Новосибирск, 7-Сочи, 8-Владивосток)
          </p>
        </div>
      </div>
      <form className={styles.formGrid} onSubmit={handleSubmit}>
        <div className={styles.formField}>
          <span className={styles.labelText}>Название поездки *</span>
          <input
            type="text"
            name="name"
            className={styles.input}
            placeholder="Весенний отпуск"
            required
            disabled={isLoading}
          />
        </div>

        <div className={styles.formField}>
          <span className={styles.labelText}>Описание</span>
          <input
            type="text"
            name="description"
            className={styles.input}
            placeholder="Лайт-план по музеям и еде"
            disabled={isLoading}
          />
        </div>

        <div className={styles.formField}>
          <span className={styles.labelText}>Город (ID) *</span>
          <input
            type="number"
            name="city_id"
            className={styles.input}
            placeholder="7"
            required
            min="1"
            disabled={isLoading}
          />
        </div>

        <div className={styles.formField}>
          <span className={styles.labelText}>Даты</span>
          <div className={styles.twoCols}>
            <input type="date" name="start_date" className={styles.inputDate} disabled={isLoading} />
            <input type="date" name="end_date" className={styles.inputDate} disabled={isLoading} />
          </div>
        </div>

        <div className={styles.formField}>
          <span className={styles.labelText}>Отель</span>
          <input
            type="text"
            name="hotel"
            className={styles.input}
            placeholder="Radisson Blu"
            disabled={isLoading}
          />
        </div>

        <div className={styles.formActions}>
          <button className={`${styles.btn} ${styles.primary}`} type="submit" disabled={isLoading}>
            {isLoading ? 'Создание...' : 'Создать'}
          </button>
          <span className={styles.hint}>Поля с * обязательны</span>
        </div>

        {message && (
          <div className={`${styles.feedback} ${message.type === 'success' ? styles.success : styles.error}`}>
            {message.text}
          </div>
        )}
      </form>
    </section>
  );
}
