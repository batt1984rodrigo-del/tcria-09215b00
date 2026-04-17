import { CTASection } from '@/components/CTASection';
import { GateCard } from '@/components/GateCard';
import { Hero } from '@/components/Hero';
import { PipelineFlow } from '@/components/PipelineFlow';
import { ValidationStats } from '@/components/ValidationStats';
import { gateDescriptions } from '@/lib/demo-data';

export default function HomePage() {
  return (
    <div className="container-shell space-y-10">
      <Hero />
      <PipelineFlow />
      <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {gateDescriptions.map((gate) => (
          <GateCard key={gate.title} title={gate.title} description={gate.description} />
        ))}
      </section>
      <ValidationStats />
      <CTASection />
    </div>
  );
}
