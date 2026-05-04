import { Roboto_Mono } from 'next/font/google';
import './globals.css';

const robotoMono = Roboto_Mono({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'],
  variable: '--font-roboto-mono',
  display: 'swap',
});

export const metadata = {
  title: 'TrustGraph AI | Intelligent Procurement',
  description: 'Automated eligibility analysis and tender compliance with explainable AI',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={robotoMono.variable}>
      <body>{children}</body>
    </html>
  );
}
