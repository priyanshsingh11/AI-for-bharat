import { Roboto_Mono } from 'next/font/google';
import './globals.css';

const robotoMono = Roboto_Mono({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'],
  variable: '--font-roboto-mono',
  display: 'swap',
});

export const metadata = {
  title: 'AI Tender Evaluation System',
  description: 'Automated eligibility analysis with explainable AI engine',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={robotoMono.variable}>
      <body>{children}</body>
    </html>
  );
}
