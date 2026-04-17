import { sampleStats } from '@/lib/demo-data';

export function ValidationStats() {
  return (
    <section className="mt-10 rounded-2xl border border-slate-200 bg-white p-6">
      <h2 className="text-2xl font-semibold">Métricas de validação</h2>
      <div className="mt-6 grid gap-4 md:grid-cols-4">
        {sampleStats.map((stat) => (
          <div key={stat.label} className="rounded-xl bg-slate-50 p-4">
            <p className="text-2xl font-bold text-accent">{stat.value}</p>
            <p className="mt-1 text-sm text-slate-600">{stat.label}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
