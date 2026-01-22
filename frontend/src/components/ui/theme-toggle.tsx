"use client";

import { useEffect, useState } from "react";

const defaultIsDark = false;

export default function ThemeToggle() {
  const [isDark, setIsDark] = useState(defaultIsDark);

  useEffect(() => {
    if (!defaultIsDark) {
      document.documentElement.classList.remove("theme-dark");
    }
  }, []);

  const toggleTheme = () => {
    setIsDark((prev) => {
      const next = !prev;
      document.documentElement.classList.toggle("theme-dark", next);
      return next;
    });
  };

  return (
    <button
      type="button"
      onClick={toggleTheme}
      className="hidden items-center gap-2 rounded-full border border-[var(--fog)] bg-white/60 px-4 py-2 text-xs font-semibold text-[var(--ink-muted)] shadow-sm backdrop-blur transition hover:-translate-y-0.5 hover:shadow-md sm:flex"
      aria-label="Toggle dark mode"
    >
      <span className="h-2 w-2 rounded-full bg-[var(--copper)]" />
      {isDark ? "Light mode" : "Dark mode"}
    </button>
  );
}
