type MissionConsoleProps = {
  highlights: string[];
};

export default function MissionConsole({ highlights }: MissionConsoleProps) {
  return (
    <div className="reveal delay-1 rounded-3xl border border-[var(--surface-border)] bg-white/95 p-6 text-[var(--surface-ink)] shadow-lg backdrop-blur">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-[var(--surface-muted)]">
            Mission Console
          </p>
          <h2 className="font-[var(--font-display)] text-2xl text-[var(--surface-ink)]">
            New objective
          </h2>
        </div>
        <span className="rounded-full bg-[var(--surface-ink)]/10 px-3 py-1 text-xs font-semibold text-[var(--surface-ink)]">
          Thread: auto
        </span>
      </div>

      <div className="mt-6 space-y-4">
        <label className="text-xs uppercase tracking-[0.2em] text-[var(--surface-muted)]">
          Mission brief
        </label>
        <div className="rounded-2xl border border-[var(--surface-border)] bg-white px-4 py-3 shadow-inner">
          <textarea
            className="h-36 w-full resize-none bg-transparent text-sm text-[var(--surface-ink)] outline-none"
            placeholder="Identify the current CEO of Delta Air Lines and the year the company was founded."
          />
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button className="h-11 rounded-full bg-[var(--surface-ink)] px-5 text-sm font-semibold text-white transition hover:-translate-y-0.5 hover:shadow-lg">
            Dispatch mission
          </button>
          <button className="h-11 rounded-full border border-[var(--surface-border)] bg-white px-5 text-sm font-semibold text-[var(--surface-ink)]">
            Save draft
          </button>
        </div>
      </div>

      <div className="mt-6 grid gap-3 text-xs text-[var(--surface-muted)]">
        {highlights.map((item) => (
          <div key={item} className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-[var(--surface-ink)]" />
            {item}
          </div>
        ))}
      </div>
    </div>
  );
}
