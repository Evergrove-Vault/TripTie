'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Header from '@/components/layout/Header';
import styles from './trip-details.module.css';

interface TripDetails {
  id: number;
  name: string;
  description: string | null;
  join_code: string;
  start_date: string | null;
  end_date: string | null;
  is_completed: boolean;
  created_at: string | null;
  creator: {
    id: number;
    username: string;
    email: string;
  } | null;
  city: {
    id: number;
    name: string;
    country_code: string;
  } | null;
  participants: Array<{
    id: number;
    username: string;
    email: string;
    is_creator: boolean;
  }>;
  participants_count: number;
}

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

function TripDetailsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [tripId, setTripId] = useState<number | null>(null);
  const [tripDetails, setTripDetails] = useState<TripDetails | null>(null);
  const [mergedPreferences, setMergedPreferences] = useState<MergedPreferences | null>(null);
  const [allParticipantsPreferences, setAllParticipantsPreferences] = useState<ParticipantPreference[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const tripParam = searchParams.get('trip');
    if (tripParam) {
      const parsedTripId = parseInt(tripParam, 10);
      if (!isNaN(parsedTripId)) {
        setTripId(parsedTripId);
      }
    }
  }, [searchParams]);

  useEffect(() => {
    if (tripId) {
      loadTripDetails();
      loadMergedPreferences();
      loadAllParticipantsPreferences();
    }
  }, [tripId]);

  const loadTripDetails = async () => {
    if (!tripId) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/trips/${tripId}/details`);
      if (response.ok) {
        const data = await response.json();
        setTripDetails(data);
      } else {
        const errorText = await response.text();
        setError('Не удалось загрузить информацию о поездке');
        console.error('Ошибка загрузки поездки:', errorText);
      }
    } catch (error) {
      setError('Ошибка подключения к серверу');
      console.error('Ошибка загрузки поездки:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadMergedPreferences = async () => {
    if (!tripId) return;
    
    try {
      const response = await fetch(`/api/preferences/trip/${tripId}/merged`);
      if (response.ok) {
        const data = await response.json();
        setMergedPreferences(data);
      }
    } catch (error) {
      console.error('Ошибка загрузки объединенных предпочтений:', error);
    }
  };

  const loadAllParticipantsPreferences = async () => {
    if (!tripId) return;
    
    try {
      const response = await fetch(`/api/preferences/trip/${tripId}/all`);
      if (response.ok) {
        const data = await response.json();
        setAllParticipantsPreferences(data);
      }
    } catch (error) {
      console.error('Ошибка загрузки предпочтений участников:', error);
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Не указано';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  if (isLoading) {
    return (
      <>
        <Header />
        <main style={{ maxWidth: '1200px', margin: '-40px auto 60px', padding: '0 16px' }}>
          <div style={{ padding: '40px', textAlign: 'center', color: '#666' }}>
            Загрузка информации о поездке...
          </div>
        </main>
      </>
    );
  }

  if (error || !tripDetails) {
    return (
      <>
        <Header />
        <main style={{ maxWidth: '1200px', margin: '-40px auto 60px', padding: '0 16px' }}>
          <div style={{ 
            padding: '40px', 
            textAlign: 'center', 
            color: '#d32f2f',
            background: '#fff3f3',
            borderRadius: '12px',
            border: '1px solid #ffcdd2'
          }}>
            {error || 'Поездка не найдена'}
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <Header />
      <main style={{ maxWidth: '1200px', margin: '-40px auto 60px', padding: '0 16px' }}>
        {/* Основная информация о поездке */}
        <section className={styles.card}>
          <div style={{ marginBottom: '24px' }}>
            <button
              onClick={() => router.back()}
              style={{
                background: 'none',
                border: 'none',
                color: '#d6007a',
                cursor: 'pointer',
                fontSize: '14px',
                marginBottom: '16px',
                padding: '8px 0'
              }}
            >
              ← Назад
            </button>
            <h1 style={{ 
              margin: '0 0 8px 0', 
              fontSize: '32px', 
              fontWeight: 700, 
              color: '#1d1d1f' 
            }}>
              {tripDetails.name}
            </h1>
            {tripDetails.description && (
              <p style={{ 
                margin: '0 0 16px 0', 
                fontSize: '16px', 
                color: '#666',
                lineHeight: '1.6'
              }}>
                {tripDetails.description}
              </p>
            )}
          </div>

          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '16px',
            marginBottom: '24px'
          }}>
            {tripDetails.city && (
              <div>
                <div style={{ 
                  fontSize: '12px', 
                  color: '#666', 
                  marginBottom: '4px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }}>
                  Город
                </div>
                <div style={{ fontSize: '16px', fontWeight: 600, color: '#1d1d1f' }}>
                  {tripDetails.city.name}
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
                Дата начала
              </div>
              <div style={{ fontSize: '16px', fontWeight: 600, color: '#1d1d1f' }}>
                {formatDate(tripDetails.start_date)}
              </div>
            </div>
            
            <div>
              <div style={{ 
                fontSize: '12px', 
                color: '#666', 
                marginBottom: '4px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Дата окончания
              </div>
              <div style={{ fontSize: '16px', fontWeight: 600, color: '#1d1d1f' }}>
                {formatDate(tripDetails.end_date)}
              </div>
            </div>
            
            <div>
              <div style={{ 
                fontSize: '12px', 
                color: '#666', 
                marginBottom: '4px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Код поездки
              </div>
              <div style={{ fontSize: '16px', fontWeight: 600, color: '#d6007a' }}>
                {tripDetails.join_code}
              </div>
            </div>
          </div>

          {tripDetails.creator && (
            <div style={{
              padding: '16px',
              background: '#f8f9fa',
              borderRadius: '12px',
              border: '1px solid #ffe1ef'
            }}>
              <div style={{ 
                fontSize: '12px', 
                color: '#666', 
                marginBottom: '8px',
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
              }}>
                Создатель поездки
              </div>
              <div style={{ fontSize: '16px', fontWeight: 600, color: '#1d1d1f' }}>
                {tripDetails.creator.username} ({tripDetails.creator.email})
              </div>
            </div>
          )}
        </section>

        {/* Участники */}
        <section className={styles.card}>
          <h2 style={{ 
            margin: '0 0 20px 0', 
            fontSize: '24px', 
            fontWeight: 600, 
            color: '#1d1d1f' 
          }}>
            Участники ({tripDetails.participants_count})
          </h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {tripDetails.participants.map((participant) => (
              <div
                key={participant.id}
                style={{
                  padding: '16px',
                  background: '#f8f9fa',
                  borderRadius: '12px',
                  border: '1px solid #ffe1ef',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px'
                }}
              >
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
                  <div style={{ fontSize: '16px', fontWeight: 600, color: '#1d1d1f' }}>
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
                  <div style={{ fontSize: '14px', color: '#666' }}>
                    {participant.email}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Объединенные предпочтения */}
        {mergedPreferences && (
          <section className={styles.card}>
            <h2 style={{ 
              margin: '0 0 20px 0', 
              fontSize: '24px', 
              fontWeight: 600, 
              color: '#1d1d1f' 
            }}>
              Объединенные предпочтения
            </h2>
            
            {mergedPreferences.participants_count > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
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
                        fontSize: '24px', 
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
                        fontSize: '24px', 
                        fontWeight: 700, 
                        color: '#d6007a' 
                      }}>
                        {Math.round(mergedPreferences.avg_budget).toLocaleString('ru-RU')} ₽
                      </div>
                    </div>
                  )}
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
                            padding: '8px 16px',
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
              </div>
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
          </section>
        )}

        {/* Индивидуальные предпочтения участников */}
        {allParticipantsPreferences.length > 0 && (
          <section className={styles.card}>
            <h2 style={{ 
              margin: '0 0 20px 0', 
              fontSize: '24px', 
              fontWeight: 600, 
              color: '#1d1d1f' 
            }}>
              Предпочтения участников
            </h2>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {allParticipantsPreferences.map((participant) => (
                <div
                  key={participant.user_id}
                  style={{
                    background: '#f8f9fa',
                    borderRadius: '12px',
                    padding: '20px',
                    border: '1px solid #ffe1ef'
                  }}
                >
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '12px',
                    marginBottom: '16px'
                  }}>
                    <div style={{
                      width: '48px',
                      height: '48px',
                      borderRadius: '50%',
                      background: participant.is_creator ? '#d6007a' : '#ffc4df',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#fff',
                      fontWeight: 700,
                      fontSize: '18px'
                    }}>
                      {participant.username.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div style={{ 
                        fontSize: '18px', 
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
                        fontSize: '14px', 
                        color: '#666' 
                      }}>
                        {participant.email}
                      </div>
                    </div>
                  </div>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {participant.budget !== null && (
                      <div style={{ fontSize: '16px', color: '#1d1d1f' }}>
                        <strong>Бюджет:</strong> {participant.budget.toLocaleString('ru-RU')} ₽
                      </div>
                    )}
                    
                    {participant.activities.length > 0 && (
                      <div>
                        <div style={{ 
                          fontSize: '14px', 
                          color: '#1d1d1f', 
                          marginBottom: '8px',
                          fontWeight: 500
                        }}>
                          Активности:
                        </div>
                        <div style={{ 
                          display: 'flex', 
                          flexWrap: 'wrap', 
                          gap: '8px' 
                        }}>
                          {participant.activities.map((activity, index) => (
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
                    
                    {participant.budget === null && participant.activities.length === 0 && (
                      <div style={{ fontSize: '14px', color: '#999', fontStyle: 'italic' }}>
                        Предпочтения не указаны
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Кнопка для перехода к редактированию предпочтений */}
        <div style={{ marginTop: '24px', textAlign: 'center' }}>
          <button
            onClick={() => router.push(`/plan?trip=${tripId}`)}
            style={{
              background: '#d6007a',
              color: '#fff',
              border: 'none',
              padding: '14px 32px',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.background = '#b8006a';
              e.currentTarget.style.transform = 'translateY(-2px)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.background = '#d6007a';
              e.currentTarget.style.transform = 'translateY(0)';
            }}
          >
            Редактировать предпочтения
          </button>
        </div>
      </main>
    </>
  );
}

export default function TripDetailsPage() {
  return (
    <Suspense fallback={
      <>
        <Header />
        <main style={{ maxWidth: '1200px', margin: '-40px auto 60px', padding: '0 16px' }}>
          <div style={{ padding: '40px', textAlign: 'center', color: '#666' }}>
            Загрузка информации о поездке...
          </div>
        </main>
      </>
    }>
      <TripDetailsContent />
    </Suspense>
  );
}

