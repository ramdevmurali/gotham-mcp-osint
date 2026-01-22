type PillProps = {
  children: React.ReactNode;
};

export default function Pill({ children }: PillProps) {
  return (
    <div className="reveal flex w-fit items-center gap-3 rounded-full border border-[var(--surface-border)] bg-[var(--surface-bg-soft)] px-4 py-2 text-xs font-semibold text-[var(--surface-muted)] shadow-sm backdrop-blur">
      <span className="text-[var(--surface-ink)]">●</span>
      {children}
    </div>
  );
}
