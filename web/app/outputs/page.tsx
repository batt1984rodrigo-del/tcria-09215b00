import { OutputTabs } from '@/components/OutputTabs';

export default function OutputsPage() {
  return (
    <div className="container-shell space-y-8">
      <h1 className="text-4xl font-semibold">Outputs</h1>
      <p className="max-w-3xl text-slate-600">
        Galeria de artefatos institucionais em formatos Markdown, JSON e PDF com foco em rastreabilidade e revisão.
      </p>
      <OutputTabs />
    </div>
  );
}
