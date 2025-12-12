'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import styles from './FinalPlanSection.module.css';

interface MergedPreferences {
  trip_id: number;
  total_budget: number | null;
  avg_budget: number | null;
  all_activities: string[];
  participants_count: number;
  total_participants_count: number;
}

interface ParticipantPreference {
  user_id: number;
  username: string;
  email: string;
  budget: number | null;
  activities: string[];
  is_creator: boolean;
}

export default function FinalPlanSection() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [tripId, setTripId] = useState<number | null>(null);
  const [mergedPreferences, setMergedPreferences] = useState<MergedPreferences | null>(null);
  const [allParticipantsPreferences, setAllParticipantsPreferences] = useState<ParticipantPreference[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingParticipants, setIsLoadingParticipants] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Получаем trip_id из URL параметров
  useEffect(() => {
    const tripParam = searchParams.get('trip');
    if (tripParam) {
      const parsedTripId = parseInt(tripParam, 10);
      if (!isNaN(parsedTripId)) {
        setTripId(parsedTripId);
      }
    }
  }, [searchParams]);

  // Загружаем объединенные предпочтения и предпочтения всех участников
  useEffect(() => {
    if (tripId) {
      loadMergedPreferences();
      loadAllParticipantsPreferences();
    }
  }, [tripId]);

  // Слушаем события обновления предпочтений для автоматического обновления
  useEffect(() => {
    const handlePreferencesUpdate = () => {
      if (tripId) {
        loadMergedPreferences();
        loadAllParticipantsPreferences();
      }
    };

    window.addEventListener('preferencesUpdated', handlePreferencesUpdate);

    return () => {
      window.removeEventListener('preferencesUpdated', handlePreferencesUpdate);
    };
  }, [tripId]);

  const loadMergedPreferences = async () => {
    if (!tripId) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/preferences/trip/${tripId}/merged`);
      if (response.ok) {
        const data = await response.json();
        setMergedPreferences(data);
      } else {
        const errorText = await response.text();
        setError('Не удалось загрузить объединенные предпочтения');
        console.error('Ошибка загрузки объединенных предпочтений:', errorText);
      }
    } catch (error) {
      setError('Ошибка подключения к серверу');
      console.error('Ошибка загрузки объединенных предпочтений:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadAllParticipantsPreferences = async () => {
    if (!tripId) return;
    
    setIsLoadingParticipants(true);
    
    try {
      const response = await fetch(`/api/preferences/trip/${tripId}/all`);
      if (response.ok) {
        const data = await response.json();
        setAllParticipantsPreferences(data);
      } else {
        console.error('Ошибка загрузки предпочтений участников');
      }
    } catch (error) {
      console.error('Ошибка загрузки предпочтений участников:', error);
    } finally {
      setIsLoadingParticipants(false);
    }
  };

  return (
    <section id="final" className={styles.card}>
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.eyebrow}>Маршрут</p>
          <h2>План по дням</h2>
          <p className={styles.subtext}>
            {tripId 
              ? 'Объединенные предпочтения всех участников поездки'
              : 'Ниже — пример плана. После завершения поездки показываем итог.'}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          {tripId && (
            <button 
              className={`${styles.btn} ${styles.ghost}`}
              onClick={() => router.push(`/trip-details?trip=${tripId}`)}
            >
              Подробнее о поездке
            </button>
          )}
          <button className={`${styles.btn} ${styles.ghost}`}>Изменить маршрут</button>
        </div>
      </div>

      {tripId && (
        <div style={{ marginBottom: '24px' }}>
          {isLoading ? (
            <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
              Загрузка объединенных предпочтений...
            </div>
          ) : error ? (
            <div style={{ 
              padding: '16px', 
              background: '#fff3f3', 
              borderRadius: '12px', 
              color: '#d32f2f',
              border: '1px solid #ffcdd2'
            }}>
              {error}
            </div>
          ) : mergedPreferences ? (
            <div style={{
              background: '#f8f9fa',
              borderRadius: '12px',
              padding: '20px',
              border: '1px solid #ffe1ef'
            }}>
              <h3 style={{ 
                margin: '0 0 16px 0', 
                fontSize: '18px', 
                fontWeight: 600, 
                color: '#1d1d1f' 
              }}>
                Объединенные предпочтения участников
              </h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {mergedPreferences.participants_count > 0 ? (
                  <>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '24px' }}>
                      {mergedPreferences.total_budget !== null && (
                        <div>
                          <div style={{ 
                            fontSize: '12px', 
                            color: '#666', 
                            marginBottom: '4px',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px'
                          }}>
                            Общий бюджет
                          </div>
                          <div style={{ 
                            fontSize: '20px', 
                            fontWeight: 700, 
                            color: '#d6007a' 
                          }}>
                            {mergedPreferences.total_budget.toLocaleString('ru-RU')} ₽
                          </div>
                        </div>
                      )}
                      
                      {mergedPreferences.avg_budget !== null && (
                        <div>
                          <div style={{ 
                            fontSize: '12px', 
                            color: '#666', 
                            marginBottom: '4px',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px'
                          }}>
                            Средний бюджет
                          </div>
                          <div style={{ 
                            fontSize: '20px', 
                            fontWeight: 700, 
                            color: '#d6007a' 
                          }}>
                            {Math.round(mergedPreferences.avg_budget).toLocaleString('ru-RU')} ₽
                          </div>
                        </div>
                      )}
                      
                      <div>
                        <div style={{ 
                          fontSize: '12px', 
                          color: '#666', 
                          marginBottom: '4px',
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px'
                        }}>
                          Участников
                        </div>
                        <div style={{ 
                          fontSize: '20px', 
                          fontWeight: 700, 
                          color: '#d6007a' 
                        }}>
                          {mergedPreferences.participants_count} / {mergedPreferences.total_participants_count}
                        </div>
                        <div style={{ 
                          fontSize: '11px', 
                          color: '#999', 
                          marginTop: '2px'
                        }}>
                          указали предпочтения
                        </div>
                      </div>
                    </div>

                    {mergedPreferences.all_activities.length > 0 && (
                      <div>
                        <div style={{ 
                          fontSize: '12px', 
                          color: '#666', 
                          marginBottom: '8px',
                          textTransform: 'uppercase',
                          letterSpacing: '0.5px'
                        }}>
                          Все активности
                        </div>
                        <div style={{ 
                          display: 'flex', 
                          flexWrap: 'wrap', 
                          gap: '8px' 
                        }}>
                          {mergedPreferences.all_activities.map((activity, index) => (
                            <span
                              key={index}
                              style={{
                                background: '#fff',
                                padding: '6px 12px',
                                borderRadius: '8px',
                                fontSize: '14px',
                                color: '#1d1d1f',
                                border: '1px solid #ffe1ef',
                                fontWeight: 500
                              }}
                            >
                              {activity}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div style={{ 
                    padding: '16px', 
                    textAlign: 'center', 
                    color: '#999',
                    fontSize: '14px'
                  }}>
                    Пока никто из участников не указал предпочтения
                  </div>
                )}
              </div>
            </div>
          ) : null}

          {/* Индивидуальные предпочтения каждого участника */}
          {isLoadingParticipants ? (
            <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
              Загрузка предпочтений участников...
            </div>
          ) : allParticipantsPreferences.length > 0 ? (
            <div style={{
              background: '#f8f9fa',
              borderRadius: '12px',
              padding: '20px',
              border: '1px solid #ffe1ef',
              marginTop: '24px'
            }}>
              <h3 style={{ 
                margin: '0 0 20px 0', 
                fontSize: '18px', 
                fontWeight: 600, 
                color: '#1d1d1f' 
              }}>
                Предпочтения участников
              </h3>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {allParticipantsPreferences.map((participant) => (
                  <div
                    key={participant.user_id}
                    style={{
                      background: '#fff',
                      borderRadius: '12px',
                      padding: '16px',
                      border: '1px solid #ffe1ef'
                    }}
                  >
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '12px',
                      marginBottom: '12px'
                    }}>
                      <div style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '50%',
                        background: participant.is_creator ? '#d6007a' : '#ffc4df',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#fff',
                        fontWeight: 700,
                        fontSize: '16px'
                      }}>
                        {participant.username.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div style={{ 
                          fontSize: '16px', 
                          fontWeight: 600, 
                          color: '#1d1d1f' 
                        }}>
                          {participant.username}
                          {participant.is_creator && (
                            <span style={{
                              marginLeft: '8px',
                              fontSize: '12px',
                              color: '#d6007a',
                              fontWeight: 500
                            }}>
                              (Создатель)
                            </span>
                          )}
                        </div>
                        <div style={{ 
                          fontSize: '12px', 
                          color: '#666' 
                        }}>
                          {participant.email}
                        </div>
                      </div>
                    </div>
                    
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {participant.budget !== null && (
                        <div style={{ fontSize: '14px', color: '#1d1d1f' }}>
                          <strong>Бюджет:</strong> {participant.budget.toLocaleString('ru-RU')} ₽
                        </div>
                      )}
                      
                      {participant.activities.length > 0 && (
                        <div>
                          <div style={{ 
                            fontSize: '14px', 
                            color: '#1d1d1f', 
                            marginBottom: '6px',
                            fontWeight: 500
                          }}>
                            Активности:
                          </div>
                          <div style={{ 
                            display: 'flex', 
                            flexWrap: 'wrap', 
                            gap: '6px' 
                          }}>
                            {participant.activities.map((activity, index) => (
                              <span
                                key={index}
                                style={{
                                  background: '#f8f9fa',
                                  padding: '4px 10px',
                                  borderRadius: '6px',
                                  fontSize: '13px',
                                  color: '#1d1d1f',
                                  border: '1px solid #ffe1ef'
                                }}
                              >
                                {activity}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {participant.budget === null && participant.activities.length === 0 && (
                        <div style={{ fontSize: '13px', color: '#999', fontStyle: 'italic' }}>
                          Предпочтения не указаны
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      )}

      <div id="planDays" className={styles.timeline}></div>
    </section>
  );
}