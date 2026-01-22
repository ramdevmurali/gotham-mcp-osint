type FeatureCardProps = {
  title: string;
  copy: string;
  delay: number;
};

export default function FeatureCard({ title, copy, delay }: FeatureCardProps) {
  return (
    <div
      className={`reveal delay-${delay} rounded-3xl border border-[var(--surface-border)] bg-white/90 p-6 shadow-sm`}
    >
      <h3 className="font-[var(--font-display)] text-xl text-[var(--surface-ink)]">
        {title}
      </h3>
      <p className="mt-3 text-sm leading-6 text-[var(--surface-muted)]">{copy}</p>
    </div>
  );
}
