const outputTabs = ['Markdown', 'JSON', 'PDF'];

export function OutputTabs() {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6">
      <h2 className="text-2xl font-semibold">Output Gallery</h2>
      <div className="mt-4 flex flex-wrap gap-3">
        {outputTabs.map((tab) => (
          <button
            key={tab}
            type="button"
            className="rounded-full border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:border-accent hover:text-accent"
          >
            {tab}
          </button>
        ))}
      </div>
      <p className="mt-4 text-sm text-slate-600">
        Preview normalized institutional outputs with format-specific rendering blocks.
      </p>
    </section>
  );
}
