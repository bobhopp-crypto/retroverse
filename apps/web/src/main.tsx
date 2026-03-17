import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './theme/theme.css'
import './index.css'
import App from './App.tsx'
import { initTheme } from './theme/theme'

initTheme()

if (!import.meta.env.DEV && window.location.hostname === 'localhost') {
  console.warn('You are running a preview build (4173). Changes require rebuild.')
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
