import { DemoFlowExplorer } from '@/components/DemoFlowExplorer';
import { ValidationStats } from '@/components/ValidationStats';

export default function DemoPage() {
  return (
    <div className="container-shell space-y-8">
      <h1 className="text-4xl font-semibold">Interactive Demo</h1>
      <p className="max-w-3xl text-slate-600">
        Explore a execução do TCRIA em cinco fases: input, classification, traceability, governance e output.
      </p>
      <DemoFlowExplorer />
      <ValidationStats />
    </div>
  );
}
