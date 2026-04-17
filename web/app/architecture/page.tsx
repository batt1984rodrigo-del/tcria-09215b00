const modules = [
  'Núcleo Python (tcria/)',
  'Camada de API (api/)',
  'Aplicação interna Streamlit (app/)',
  'Front-end de produto Next.js (web/)',
  'Relatórios de auditoria e governança'
];

export default function ArchitecturePage() {
  return (
    <div className="container-shell space-y-8">
      <h1 className="text-4xl font-semibold">Arquitetura</h1>
      <p className="max-w-3xl text-slate-600">
        Front-end em Next.js desacoplado do core Python para evolução de produto sem comprometer a lógica institucional.
      </p>
      <section className="rounded-2xl border border-slate-200 bg-white p-6">
        <h2 className="text-2xl font-semibold">Módulos</h2>
        <ul className="mt-4 space-y-3 text-slate-700">
          {modules.map((module) => (
            <li key={module} className="rounded-lg bg-slate-50 px-4 py-3">
              {module}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
