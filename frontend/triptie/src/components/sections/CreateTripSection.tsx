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

    // Сохраняем ссылку на форму до асинхронной операции
    const form = e.currentTarget;
    const formData = new FormData(form);
    const tripData = {
      name: formData.get('name') as string,
      description: formData.get('description') as string || undefined,
      city_id: parseInt(formData.get('city_id') as string),
      start_date: formData.get('start_date') as string || undefined,
      end_date: formData.get('end_date') as string || undefined,
    };

    // Получаем user_id из localStorage
    let currentUserId = null;
    if (typeof window !== 'undefined') {
      const userData = localStorage.getItem('user');
      if (userData) {
        try {
          const user = JSON.parse(userData);
          currentUserId = user.id;
        } catch (e) {
          console.error('Ошибка при чтении данных пользователя:', e);
        }
      }
    }

    if (!currentUserId) {
      setMessage({ type: 'error', text: 'Необходимо войти в аккаунт для создания поездки' });
      setIsLoading(false);
      return;
    }

    try {
      console.log('Создание поездки:', tripData);
      const url = `/api/trips/?user_id=${currentUserId}`;
      console.log('Отправка запроса на:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(tripData),
      });
      
      console.log('Получен ответ:', response.status, response.statusText);

      let data;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        try {
          data = await response.json();
        } catch (e) {
          setMessage({ type: 'error', text: 'Ошибка при обработке ответа сервера' });
          setIsLoading(false);
          return;
        }
      } else {
        const text = await response.text();
        setMessage({ type: 'error', text: text || 'Ошибка при выполнении запроса' });
        setIsLoading(false);
        return;
      }

      if (!response.ok) {
        setMessage({ type: 'error', text: data.detail || data.message || 'Ошибка при создании поездки' });
        setIsLoading(false);
        return;
      }

      setMessage({ type: 'success', text: `Поездка "${data.name}" создана! Код: ${data.join_code}` });
      
      // Отправляем событие для обновления списка поездок
      window.dispatchEvent(new Event('tripsUpdated'));
      
      // Безопасный сброс формы
      try {
        if (form) {
          form.reset();
        }
      } catch (resetError) {
        console.warn('Не удалось сбросить форму:', resetError);
      }
      
      // Перенаправляем на страницу предпочтений для добавления своих предпочтений
      setTimeout(() => {
        router.push(`/plan?trip=${data.id}`);
      }, 2000);
    } catch (error) {
      console.error('Ошибка при создании поездки:', error);
      console.error('Тип ошибки:', error instanceof Error ? error.constructor.name : typeof error);
      console.error('Сообщение ошибки:', error instanceof Error ? error.message : String(error));
      console.error('Стек ошибки:', error instanceof Error ? error.stack : 'Нет стека');
      
      const errorStr = String(error);
      const errorMessage = errorStr.includes('Failed to fetch') || errorStr.includes('NetworkError') || errorStr.includes('ERR_CONNECTION_REFUSED')
        ? 'Сервер не запущен. Убедитесь, что backend сервер работает на порту 8000.'
        : `Ошибка подключения к серверу: ${errorStr}`;
      setMessage({ type: 'error', text: errorMessage });
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
