import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'TripTie — розовый планировщик путешествий',
  description: 'Создавайте маршруты, присоединяйтесь по коду, храните план по дням',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}