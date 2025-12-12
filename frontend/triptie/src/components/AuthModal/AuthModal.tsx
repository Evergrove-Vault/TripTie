'use client';

import { useState } from 'react';
import styles from './AuthModal.module.css';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleSubmit = async (e?: React.FormEvent<HTMLFormElement> | React.MouseEvent) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    console.log('AuthModal: handleSubmit вызван', { username, isRegisterMode, password: password ? '***' : '' });
    setMessage(null);

    if (!username || !password) {
      console.log('AuthModal: Валидация не прошла: пустые поля');
      setMessage({ type: 'error', text: 'Заполните все обязательные поля' });
      return;
    }

    if (isRegisterMode && !email) {
      setMessage({ type: 'error', text: 'Введите email' });
      return;
    }

    if (password.length > 72) {
      setMessage({ type: 'error', text: 'Пароль не может быть длиннее 72 символов' });
      return;
    }

    try {
      console.log('AuthModal: Начинаем запрос к API...');
      const url = isRegisterMode ? '/api/auth/register' : '/api/auth/login';
      const body = isRegisterMode
        ? { username, email, password }
        : { username, password };
      
      console.log('AuthModal: Отправляем запрос:', { url, body: { ...body, password: '***' } });

      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      let data;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        try {
          data = await response.json();
        } catch (e) {
          setMessage({ type: 'error', text: 'Ошибка при обработке ответа сервера' });
          return;
        }
      } else {
        const text = await response.text();
        setMessage({ type: 'error', text: text || 'Ошибка при выполнении запроса' });
        return;
      }

      if (!response.ok) {
        setMessage({ type: 'error', text: data.detail || data.message || 'Ошибка при выполнении запроса' });
        return;
      }

      const successMsg = isRegisterMode
        ? `Регистрация успешна! Добро пожаловать, ${data.username}!`
        : `Добро пожаловать, ${data.username}!`;

      setMessage({ type: 'success', text: successMsg });

      // Сохраняем данные пользователя
      localStorage.setItem('user', JSON.stringify(data));
      
      // Проверяем, что данные сохранились
      const saved = localStorage.getItem('user');
      if (!saved) {
        setMessage({ type: 'error', text: 'Ошибка сохранения данных. Попробуйте еще раз.' });
        return;
      }
      
      // Отправляем событие для обновления Header
      window.dispatchEvent(new Event('userUpdated'));

      // Небольшая задержка для гарантии сохранения
      setTimeout(() => {
        onClose();
        window.location.reload();
      }, 1000);
    } catch (error) {
      console.error('Ошибка при запросе:', error);
      const errorStr = String(error);
      const errorMessage = errorStr.includes('Failed to fetch') || errorStr.includes('NetworkError')
        ? 'Сервер не запущен. Убедитесь, что backend сервер работает на порту 8000. Запустите: uvicorn backend.main:app --reload --port 8000'
        : `Ошибка подключения к серверу: ${errorStr}`;
      setMessage({ type: 'error', text: errorMessage });
    }
  };

  if (!isOpen) return null;

  return (
    <div className={styles.modal}>
      <div className={styles.modalContent}>
        <button className={styles.modalClose} onClick={onClose}>
          ×
        </button>
        <h3>{isRegisterMode ? 'Регистрация' : 'Вход'}</h3>
        <form onSubmit={handleSubmit} noValidate>
          <div className={styles.formField}>
            <span className={styles.labelText}>Логин *</span>
            <input
              type="text"
              className={styles.input}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          {isRegisterMode && (
            <div className={styles.formField}>
              <span className={styles.labelText}>Email *</span>
              <input
                type="email"
                className={styles.input}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          )}

          <div className={styles.formField}>
            <span className={styles.labelText}>Пароль *</span>
            <input
              type="password"
              className={styles.input}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className={styles.formActions}>
            <button 
              type="button"
              className={`${styles.btn} ${styles.primary}`}
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('AuthModal: Кнопка нажата напрямую');
                handleSubmit(e);
              }}
            >
              {isRegisterMode ? 'Зарегистрироваться' : 'Войти'}
            </button>
            <button
              type="button"
              className={`${styles.btn} ${styles.ghost}`}
              onClick={() => setIsRegisterMode(!isRegisterMode)}
            >
              {isRegisterMode ? 'Уже есть аккаунт?' : 'Нет аккаунта?'}
            </button>
          </div>

          {message && (
            <div className={`${styles.feedback} ${styles[message.type]}`}>
              {message.text}
            </div>
          )}
        </form>
      </div>
    </div>
  );
}