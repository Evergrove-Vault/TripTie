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

  const handleSubmit = (e: React.FormEvent) => {
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

    // Имитация успешной регистрации/входа
    const successMsg = isRegisterMode
      ? `Регистрация успешна! Добро пожаловать, ${username}!`
      : `Добро пожаловать, ${username}!`;

    setMessage({ type: 'success', text: successMsg });

    if (isRegisterMode) {
      setTimeout(() => {
        setIsRegisterMode(false);
        setEmail('');
        setMessage(null);
      }, 2000);
    } else {
      setTimeout(onClose, 1500);
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
    </div>
  );
}