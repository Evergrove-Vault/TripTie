'use client';

import Header from '@/components/layout/Header';
import TripPreferencesSection from '@/components/sections/TripPreferencesSection';
import FinalPlanSection from '@/components/sections/FinalPlanSection';

export default function PlanPage() {
  return (
    <>
      <Header />
      <main style={{ maxWidth: '1200px', margin: '-40px auto 60px', padding: '0 16px' }}>
        <TripPreferencesSection />
        <FinalPlanSection />
      </main>
    </>
  );
}



