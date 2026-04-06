import Link from 'next/link';

export function CTASection() {
  return (
    <section className="mt-10 rounded-3xl bg-accent px-8 py-12 text-white">
      <h2 className="text-3xl font-semibold">
        Pronto para transformar governança em experiência de produto?
      </h2>

      <p className="mt-3 max-w-2xl text-indigo-100">
        Comece pela demonstração interativa e evolua para fluxos institucionais integrados.
      </p>

      <Link
        href="/demo"
        className="mt-6 inline-flex rounded-xl bg-white px-5 py-3 text-sm font-semibold text-accent"
      >
        Explorar demonstração
      </Link>
    </section>
  );
}
