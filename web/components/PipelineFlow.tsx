import { pipelineSteps } from '@/lib/demo-data';

export function PipelineFlow() {
  return (
    <section className="mt-10 rounded-2xl border border-slate-200 bg-white p-6">
      <h2 className="text-2xl font-semibold">Fluxo do pipeline</h2>
      <div className="mt-6 grid gap-4 md:grid-cols-5">
        {pipelineSteps.map((step) => (
          <div key={step} className="rounded-xl bg-slate-50 p-4 text-sm font-medium text-slate-700">
            {step}
          </div>
        ))}
      </div>
    </section>
  );
}
