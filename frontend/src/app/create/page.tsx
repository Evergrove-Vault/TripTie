'use client';

import Header from '@/components/layout/Header';
import CreateTripSection from '@/components/sections/CreateTripSection';

export default function CreateTripPage() {
  return (
    <>
      <Header />
      <main style={{ maxWidth: '1200px', margin: '-40px auto 60px', padding: '0 16px' }}>
        <CreateTripSection />
      </main>
    </>
  );
}
