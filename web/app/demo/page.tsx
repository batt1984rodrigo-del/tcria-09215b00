import { DemoFlowExplorer } from '@/components/DemoFlowExplorer';
import { ValidationStats } from '@/components/ValidationStats';

export default function DemoPage() {
  return (
    <div className="container-shell space-y-8">
      <h1 className="text-4xl font-semibold">Demonstração Interativa</h1>

      <p className="max-w-3xl text-slate-600">
        Explore a execução do TCRIA em cinco fases: entrada, classificação, rastreabilidade, governança e saída.
      </p>

      <DemoFlowExplorer />
      <ValidationStats />
    </div>
  );
}
