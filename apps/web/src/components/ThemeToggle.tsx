import { getTheme, setTheme, type ThemeId } from '../theme/theme'

const THEMES: { id: ThemeId; label: string }[] = [
  { id: 'retroverse', label: 'Retro' },
  { id: 'light', label: 'Light' },
  { id: 'dark', label: 'Dark' },
]

export default function ThemeToggle() {
  const current = getTheme()

  return (
    <div className="theme-toggle" role="group" aria-label="Theme">
      {THEMES.map(({ id, label }) => (
        <button
          key={id}
          type="button"
          onClick={() => setTheme(id)}
          className={current === id ? 'theme-toggle-btn active' : 'theme-toggle-btn'}
          aria-pressed={current === id}
        >
          {label}
        </button>
      ))}
    </div>
  )
}
