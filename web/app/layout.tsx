import type { Metadata } from 'next';
import Link from 'next/link';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'TCRIA | Front-end de Produto',
  description: 'Landing comercial e demonstração interativa para o pipeline de governança do TCRIA.'
};

const navItems = [
  { href: '/', label: 'Início' },
  { href: '/demo', label: 'Demonstração' },
  { href: '/architecture', label: 'Arquitetura' },
  { href: '/outputs', label: 'Saídas' }
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>
        <header className="border-b border-slate-200 bg-white/90 backdrop-blur">
          <div className="container-shell flex h-16 items-center justify-between">
            <span className="text-lg font-bold">TCRIA</span>
            <nav className="flex gap-5 text-sm font-medium text-slate-600">
              {navItems.map((item) => (
                <Link key={item.href} href={item.href} className="hover:text-accent transition">
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>
        <main className="py-10">{children}</main>
      </body>
    </html>
  );
}
