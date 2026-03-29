import { motion } from 'framer-motion';

export function Hero() {
  return (
    <section className="rounded-3xl bg-ink px-8 py-16 text-white">
      <motion.p
        className="text-sm font-semibold uppercase tracking-[0.2em] text-indigo-200"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
      >
        Chaos → Structure → Evidence → Decision
      </motion.p>
      <motion.h1
        className="mt-4 max-w-3xl text-4xl font-semibold leading-tight md:text-5xl"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        Turn hidden documentary chaos into auditable decisions
      </motion.h1>
      <p className="mt-6 max-w-2xl text-lg text-slate-300">
        TCRIA organizes, correlates, and governs complex evidence flows before risk becomes crisis.
      </p>
    </section>
  );
}
