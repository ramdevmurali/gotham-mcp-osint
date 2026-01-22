type StatusPillProps = {
  label: string;
};

export default function StatusPill({ label }: StatusPillProps) {
  return (
    <div className="hidden items-center gap-3 rounded-full border border-[var(--surface-border)] bg-white/90 px-4 py-2 text-xs font-semibold text-[var(--surface-muted)] shadow-sm backdrop-blur sm:flex">
      <span className="h-2 w-2 rounded-full bg-[var(--surface-ink)]" />
      {label}
    </div>
  );
}
