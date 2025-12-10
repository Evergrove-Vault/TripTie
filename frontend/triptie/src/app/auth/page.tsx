'use client';

import { useState } from 'react';
import Header from '@/components/layout/Header';
import styles from './auth.module.css';

export default function AuthPage() {
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);

    if (!username || !password) {
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
      const url = isRegisterMode ? 'http://127.0.0.1:8001/auth/register' : 'http://127.0.0.1:8001/auth/login';
      const body = isRegisterMode
        ? { username, email, password }
        : { username, password };

      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (!response.ok) {
        setMessage({ type: 'error', text: data.detail || 'Ошибка при выполнении запроса' });
        return;
      }

      const successMsg = isRegisterMode
        ? `Регистрация успешна! Добро пожаловать, ${data.username}!`
        : `Добро пожаловать, ${data.username}!`;

      setMessage({ type: 'success', text: successMsg });

      // Сохраняем данные пользователя
      localStorage.setItem('user', JSON.stringify(data));

      if (isRegisterMode) {
        setTimeout(() => {
          setIsRegisterMode(false);
          setEmail('');
          setMessage(null);
        }, 2000);
      } else {
        setTimeout(() => {
          window.location.href = '/';
        }, 1500);
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Ошибка подключения к серверу' });
    }
  };

  return (
    <>
      <Header />
      <main style={{ maxWidth: '600px', margin: '60px auto', padding: '0 16px' }}>
        <div className={styles.card}>
          <h2>{isRegisterMode ? 'Регистрация' : 'Вход'}</h2>
          <form onSubmit={handleSubmit}>
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
              <button type="submit" className={`${styles.btn} ${styles.primary}`}>
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
      </main>
    </>
  );
}



