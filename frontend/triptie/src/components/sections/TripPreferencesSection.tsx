'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import styles from './TripPreferencesSection.module.css';

export default function TripPreferencesSection() {
  const router = useRouter();
  const [tripId, setTripId] = useState<number | null>(null);
  const [joinCode, setJoinCode] = useState('');
  const [activities, setActivities] = useState<string[]>(['', '', '']); // Максимум 3 активности
  const [budget, setBudget] = useState('');
  const [userId, setUserId] = useState<number | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [joinLink, setJoinLink] = useState('');
  const [myTrips, setMyTrips] = useState<Array<{ id: number; name: string; join_code: string }>>([]);
  const [showTripSelector, setShowTripSelector] = useState(false);
  const [isLoadingPreferences, setIsLoadingPreferences] = useState(false);
  const [savedPreferences, setSavedPreferences] = useState<{ budget: number | null; activities: string[] } | null>(null);

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

  // Загружаем список поездок пользователя
  useEffect(() => {
    if (userId) {
      loadMyTrips();
    }
  }, [userId]);

  const loadMyTrips = async () => {
    if (!userId) return;
    
    try {
      const response = await fetch(`/api/trips/?user_id=${userId}`);
      if (response.ok) {
        const data = await response.json();
        setMyTrips(data);
      }
    } catch (error) {
      console.error('Ошибка загрузки поездок:', error);
    }
  };

  const handleSelectTrip = (selectedTripId: number) => {
    setTripId(selectedTripId);
    setShowTripSelector(false);
    setSavedPreferences(null);
    setBudget('');
    setActivities(['', '', '']);
    router.push(`/plan?trip=${selectedTripId}`);
    if (userId) {
      loadPreferences(selectedTripId);
    }
  };

  useEffect(() => {
    // Обновляем ссылку для друзей при изменении trip_id
    if (tripId) {
      const currentUrl = window.location.origin;
      setJoinLink(`${currentUrl}/plan?trip=${tripId}`);
    } else {
      setJoinLink('');
      setSavedPreferences(null);
      setBudget('');
      setActivities(['', '', '']);
    }
  }, [tripId]);

  // Загружаем trip_id из URL параметров и предпочтения
  useEffect(() => {
    if (typeof window !== 'undefined' && userId) {
      const params = new URLSearchParams(window.location.search);
      const tripParam = params.get('trip');
      if (tripParam) {
        const tripIdNum = parseInt(tripParam);
        if (!isNaN(tripIdNum) && tripIdNum !== tripId) {
          setTripId(tripIdNum);
        }
      }
    }
  }, [userId]);

  // Загружаем предпочтения когда tripId и userId доступны
  useEffect(() => {
    if (tripId && userId) {
      loadPreferences(tripId);
    }
  }, [tripId, userId]);

  // Закрываем выпадающий список при клике вне его
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (showTripSelector && !target.closest('[data-trip-selector]')) {
        setShowTripSelector(false);
      }
    };

    if (showTripSelector) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showTripSelector]);

  const loadPreferences = async (tripIdToLoad: number) => {
    if (!userId) return;

    setIsLoadingPreferences(true);
    try {
      const response = await fetch(`/api/preferences/trip/${tripIdToLoad}?user_id=${userId}`);
      if (response.ok) {
        const data = await response.json();
        // Сохраняем загруженные предпочтения для отображения
        setSavedPreferences({
          budget: data.budget || null,
          activities: data.activities || []
        });
        
        // Заполняем поля формы
        if (data.budget) {
          setBudget(String(data.budget));
        } else {
          setBudget('');
        }
        if (data.activities && data.activities.length > 0) {
          // Заполняем массив активностей (максимум 3)
          const activitiesArray = [...data.activities];
          while (activitiesArray.length < 3) {
            activitiesArray.push('');
          }
          setActivities(activitiesArray.slice(0, 3));
        } else {
          setActivities(['', '', '']);
        }
      } else {
        // Если предпочтений нет, очищаем поля
        setSavedPreferences(null);
        setBudget('');
        setActivities(['', '', '']);
      }
    } catch (error) {
      console.error('Ошибка загрузки предпочтений:', error);
      setSavedPreferences(null);
      setBudget('');
      setActivities(['', '', '']);
    } finally {
      setIsLoadingPreferences(false);
    }
  };

  const handleJoinTrip = async () => {
    if (!joinCode.trim()) {
      setMessage({ type: 'error', text: 'Введите код поездки' });
      return;
    }

    setIsLoading(true);
    setMessage(null);

    if (!userId) {
      setMessage({ type: 'error', text: 'Необходимо войти в аккаунт для присоединения к поездке' });
      setIsLoading(false);
      router.push('/auth');
      return;
    }

    try {
      const response = await fetch(`/api/trips/join?user_id=${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ join_code: joinCode.trim() }),
      });

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
        setMessage({ type: 'error', text: data.detail || 'Ошибка при присоединении к поездке' });
        setIsLoading(false);
        return;
      }

      // Обрабатываем ответ
      const tripIdValue = data.trip_id;
      const tripName = data.trip_name || 'поездка';

      if (tripIdValue) {
        setTripId(tripIdValue);
        setMessage({ type: 'success', text: `Вы присоединились к поездке "${tripName}"!` });
        setJoinCode('');
        
        // Обновляем URL
        router.push(`/plan?trip=${tripIdValue}`);
        
        // Загружаем предпочтения
        if (userId) {
          loadPreferences(tripIdValue);
        }
      } else {
        setMessage({ type: 'error', text: 'Не удалось получить ID поездки' });
      }
    } catch (error) {
      console.error('Ошибка при присоединении:', error);
      setMessage({ type: 'error', text: 'Ошибка подключения к серверу' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSavePreferences = async () => {
    if (!tripId) {
      setMessage({ type: 'error', text: 'Сначала создайте или выберите поездку' });
      return;
    }

    if (!userId) {
      setMessage({ type: 'error', text: 'Необходимо войти в аккаунт' });
      router.push('/auth');
      return;
    }

    setIsLoading(true);
    setMessage(null);

    try {
      // Фильтруем непустые активности из массива (максимум 3)
      const activityNames = activities
        .map(a => a.trim())
        .filter(a => a.length > 0)
        .slice(0, 3); // Ограничиваем до 3 активностей

      const preferencesData = {
        trip_id: tripId,
        budget: budget ? parseFloat(budget) : null,
        activity_names: activityNames.length > 0 ? activityNames : null,
      };

      const response = await fetch(`/api/preferences/?user_id=${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(preferencesData),
      });

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
        setMessage({ type: 'error', text: data.detail || data.message || 'Ошибка при сохранении предпочтений' });
        setIsLoading(false);
        return;
      }

      // Обновляем сохраненные предпочтения после успешного сохранения
      setSavedPreferences({
        budget: preferencesData.budget,
        activities: activityNames.length > 0 ? activityNames : []
      });

      setMessage({ type: 'success', text: 'Предпочтения сохранены!' });
      
      // Отправляем событие для обновления объединенных предпочтений
      window.dispatchEvent(new Event('preferencesUpdated'));
    } catch (error) {
      console.error('Ошибка при сохранении:', error);
      setMessage({ type: 'error', text: 'Ошибка подключения к серверу' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyLink = () => {
    if (!joinLink) {
      setMessage({ type: 'error', text: 'Сначала создайте или выберите поездку' });
      return;
    }

    navigator.clipboard.writeText(joinLink).then(() => {
      setMessage({ type: 'success', text: 'Ссылка скопирована в буфер обмена!' });
    }).catch(() => {
      setMessage({ type: 'error', text: 'Не удалось скопировать ссылку' });
    });
  };

  return (
    <section id="plan" className={styles.card}>
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.eyebrow}>Параметры</p>
          <h2 className={styles.sectionTitle}>Предпочтения по поездке</h2>
          <p className={styles.subtext}>Выберите активности, бюджет и получите ссылку для друзей.</p>
        </div>
        <div style={{ display: 'flex', gap: '12px', flexDirection: 'column', alignItems: 'flex-end' }}>
          {myTrips.length > 0 && (
            <div style={{ position: 'relative' }} data-trip-selector>
              <button
                className={styles.btn}
                onClick={() => setShowTripSelector(!showTripSelector)}
                style={{ marginBottom: '8px', whiteSpace: 'nowrap', minWidth: '180px', width: 'auto' }}
              >
                {tripId ? 'Изменить поездку' : 'Выбрать мою поездку'}
              </button>
              {showTripSelector && (
                <div data-trip-selector style={{
                  position: 'absolute',
                  top: '100%',
                  right: 0,
                  background: 'white',
                  borderRadius: '8px',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                  padding: '8px',
                  minWidth: '200px',
                  zIndex: 1000,
                  border: '1px solid rgba(255, 95, 162, 0.2)'
                }}>
                  {myTrips.map((trip) => (
                    <button
                      key={trip.id}
                      onClick={() => handleSelectTrip(trip.id)}
                      style={{
                        width: '100%',
                        padding: '8px 12px',
                        textAlign: 'left',
                        background: tripId === trip.id ? 'rgba(255, 95, 162, 0.1)' : 'transparent',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '14px'
                      }}
                      onMouseEnter={(e) => {
                        if (tripId !== trip.id) {
                          e.currentTarget.style.background = 'rgba(255, 95, 162, 0.05)';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (tripId !== trip.id) {
                          e.currentTarget.style.background = 'transparent';
                        }
                      }}
                    >
                      {trip.name} {tripId === trip.id && '✓'}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
          <div className={styles.joinInline}>
            <input
              type="text"
              className={styles.inputSmall}
              placeholder="Код поездки"
              value={joinCode}
              onChange={(e) => setJoinCode(e.target.value)}
              disabled={isLoading}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleJoinTrip();
                }
              }}
            />
            <button
              className={styles.btn}
              onClick={handleJoinTrip}
              disabled={isLoading}
            >
              Присоединиться
            </button>
          </div>
        </div>
      </div>

      {isLoadingPreferences && tripId ? (
        <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
          Загрузка предпочтений...
        </div>
      ) : (
        <>
          {savedPreferences && tripId && (
            <div style={{
              background: '#f8f9fa',
              borderRadius: '12px',
              padding: '16px',
              marginBottom: '24px',
              border: '1px solid #ffe1ef'
            }}>
              <p style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: 600, color: '#666' }}>
                Текущие сохраненные предпочтения:
              </p>
              <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
                {savedPreferences.budget && (
                  <div style={{ fontSize: '14px', color: '#1d1d1f' }}>
                    <strong>Бюджет:</strong> {savedPreferences.budget.toLocaleString('ru-RU')} ₽
                  </div>
                )}
                {savedPreferences.activities.length > 0 && (
                  <div style={{ fontSize: '14px', color: '#1d1d1f' }}>
                    <strong>Активности:</strong> {savedPreferences.activities.join(', ')}
                  </div>
                )}
                {!savedPreferences.budget && savedPreferences.activities.length === 0 && (
                  <div style={{ fontSize: '14px', color: '#999' }}>
                    Предпочтения еще не сохранены
                  </div>
                )}
              </div>
            </div>
          )}

          <div className={`${styles.grid}`}>
            <div style={{ width: '60%' }}>
              <h3 className={styles.sectionSubtitle}>Активности (максимум 3)</h3>
              {[0, 1, 2].map((index) => (
                <div key={index} style={{ marginBottom: '12px' }}>
                  <input
                    type="text"
                    className={styles.inputBudget}
                    placeholder={`Активность ${index + 1} (например, аквапарк)`}
                    value={activities[index] || ''}
                    onChange={(e) => {
                      const newActivities = [...activities];
                      newActivities[index] = e.target.value;
                      setActivities(newActivities);
                    }}
                    disabled={isLoading || isLoadingPreferences || !tripId}
                  />
                </div>
              ))}
              <p style={{ fontSize: '12px', color: '#666', margin: '4px 0 0 0' }}>
                Вы можете указать до 3 активностей
              </p>
            </div>
            <div style={{ width: '60%' }}>
              <h3 className={styles.sectionSubtitle}>Бюджет</h3>
              <input
                type="number"
                className={styles.inputBudget}
                placeholder="Например, 50000"
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                disabled={isLoading || isLoadingPreferences || !tripId}
              />
              <p style={{ fontSize: '12px', color: '#666', margin: '4px 0 12px 0' }}>
                Укажите бюджет в рублях
              </p>
              <div style={{ display: 'flex', gap: '8px', flexDirection: 'column' }}>
                <button
                  className={styles.btn}
                  onClick={handleSavePreferences}
                  disabled={isLoading || isLoadingPreferences || !tripId}
                >
                  {isLoading ? 'Сохранение...' : savedPreferences ? 'Обновить предпочтения' : 'Сохранить предпочтения'}
                </button>
                {savedPreferences && (
                  <button
                    className={`${styles.btn} ${styles.btnGhost}`}
                    onClick={() => {
                      setBudget('');
                      setActivities(['', '', '']);
                      setSavedPreferences(null);
                    }}
                    disabled={isLoading || isLoadingPreferences}
                    style={{ fontSize: '14px', padding: '8px 12px' }}
                  >
                    Очистить поля
                  </button>
                )}
              </div>
            </div>
          </div>
        </>
      )}

      <div className={styles.linkBox}>
        <div>
          <p className={styles.eyebrow}>Ссылка для друзей</p>
          <p id="joinLinkValue">
            {joinLink || 'Сначала создайте или выберите поездку'}
          </p>
        </div>
        <button
          className={`${styles.btn} ${styles.btnGhost}`}
          onClick={handleCopyLink}
          disabled={!joinLink}
        >
          Скопировать
        </button>
      </div>

      {message && (
        <div className={`${styles.feedback} ${message.type === 'success' ? styles.success : styles.error}`}>
          {message.text}
        </div>
      )}
    </section>
  );
}
