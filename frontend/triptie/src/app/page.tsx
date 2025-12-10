'use client';

import Header from '@/components/layout/Header';
import DashboardSection from '@/components/sections/DashboardSection';

export default function HomePage() {
  return (
    <>
      <Header />
      <main style={{ maxWidth: '1200px', margin: '-40px auto 60px', padding: '0 16px' }}>
        <DashboardSection />
      </main>
    </>
  );
}
