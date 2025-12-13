'use client';

import { Suspense } from 'react';
import Header from '@/components/layout/Header';
import TripPreferencesSection from '@/components/sections/TripPreferencesSection';
import FinalPlanSection from '@/components/sections/FinalPlanSection';

function FinalPlanSectionWithSuspense() {
  return (
    <Suspense fallback={<div style={{ padding: '40px', textAlign: 'center' }}>Загрузка...</div>}>
      <FinalPlanSection />
    </Suspense>
  );
}

export default function PlanPage() {
  return (
    <>
      <Header />
      <main style={{ maxWidth: '1200px', margin: '-40px auto 60px', padding: '0 16px' }}>
        <TripPreferencesSection />
        <FinalPlanSectionWithSuspense />
      </main>
    </>
  );
}



