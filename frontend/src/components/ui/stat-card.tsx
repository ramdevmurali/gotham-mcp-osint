type StatCardProps = {
  value: string;
  label: string;
};

export default function StatCard({ value, label }: StatCardProps) {
  return (
    <div className="reveal delay-2 rounded-2xl border border-[var(--surface-border)] bg-[var(--surface-bg)] p-4 shadow-sm backdrop-blur">
      <p className="font-[var(--font-display)] text-2xl text-[var(--surface-ink)]">
        {value}
      </p>
      <p className="text-xs uppercase tracking-[0.2em] text-[var(--surface-muted)]">
        {label}
      </p>
    </div>
  );
}
