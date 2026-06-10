import { Analytics } from '@vercel/analytics/next'
import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import './globals.css'
import { Toaster } from '@/components/ui/sonner'

const geistSans = Geist({ variable: '--font-geist-sans', subsets: ['latin'] })
const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
})

export const metadata: Metadata = {
  title: 'CreditGuard — Predicción de Riesgo Crediticio',
  description:
    'Plataforma de aprendizaje supervisado para entrenar, evaluar y ajustar modelos de predicción del riesgo crediticio.',
  generator: 'v0.app',
  icons: {
    icon: '/Icono.png',
    apple: '/Icono.png',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html
      lang="es"
      className={`dark ${geistSans.variable} ${geistMono.variable} bg-background`}
    >
      <body className="font-sans antialiased">
        {children}
        <Toaster theme="dark" richColors position="top-right" />
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
