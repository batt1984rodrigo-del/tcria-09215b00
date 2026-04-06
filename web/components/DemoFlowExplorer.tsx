'use client';

import { useState } from 'react';
import { demoFlow } from '@/lib/demo-data';

export function DemoFlowExplorer() {
  const [activeStep, setActiveStep] = useState(demoFlow[0]);

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6">
      <h2 className="text-2xl font-semibold">Visão guiada do pipeline</h2>

      <p className="mt-2 text-sm text-slate-600">
        Selecione cada etapa para entender como o TCRIA transforma evidência em decisão auditável.
      </p>

      <div className="mt-6 grid gap-3 md:grid-cols-5">
        {demoFlow.map((step) => {
          const isActive = step.id === activeStep.id;

          return (
            <button
              key={step.id}
              onClick={() => setActiveStep(step)}
              className={`rounded-xl border px-3 py-3 text-left text-sm font-medium transition ${
                isActive
                  ? 'border-accent bg-indigo-50 text-accent'
                  : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300'
              }`}
            >
              {step.title}
            </button>
          );
        })}
      </div>

      <article className="mt-6 rounded-xl bg-slate-50 p-5">
        <h3 className="text-lg font-semibold">{activeStep.title}</h3>
        <p className="mt-2 text-sm text-slate-700">{activeStep.detail}</p>
      </article>
    </section>
  );
}
