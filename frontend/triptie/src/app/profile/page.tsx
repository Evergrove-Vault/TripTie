'use client';

import Header from '@/components/layout/Header';
import ProfileSection from '@/components/sections/ProfileSection';

export default function ProfilePage() {
  return (
    <>
      <Header />
      <main style={{ maxWidth: '1200px', margin: '-40px auto 60px', padding: '0 16px' }}>
        <ProfileSection />
      </main>
    </>
  );
}



