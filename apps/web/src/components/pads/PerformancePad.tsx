import './PerformancePad.css'

type PadSize = 'small' | 'medium' | 'large'

type Props = {
  id: string
  label: string
  active: boolean
  group: string
  onPress: () => void
  size: PadSize
  colorGroup: string
  disabled?: boolean
  toneIndex?: number
  toneCount?: number
}

export default function PerformancePad({
  id,
  label,
  active,
  group,
  onPress,
  size,
  colorGroup,
  disabled = false,
}: Props) {
  return (
    <button
      type="button"
      id={id}
      className={`perf-pad perf-pad--${size} ${active ? 'is-active' : ''}`}
      data-color-group={colorGroup}
      data-group={group}
      aria-pressed={active}
      onClick={onPress}
      disabled={disabled}
    >
      {label}
    </button>
  )
}
