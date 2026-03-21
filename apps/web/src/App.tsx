import { lazy, Suspense } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AppShell from './components/AppShell'
import { PlaylistProvider } from './context/PlaylistContext'
import './App.css'

const LandingPage = lazy(() => import('./pages/LandingPage'))
const Hub = lazy(() => import('./pages/Hub'))
const VideoLibrary = lazy(() => import('./pages/VideoLibrary'))
const Playlists = lazy(() => import('./pages/Playlists'))
const SetBuilder = lazy(() => import('./pages/SetBuilder'))
const SurprisePage = lazy(() => import('./pages/SurprisePage'))
const ChartsPage = lazy(() => import('./pages/ChartsPage'))
const Matching = lazy(() => import('./pages/Matching'))
const Games = lazy(() => import('./pages/Games'))
const Tools = lazy(() => import('./pages/Tools'))
const Analytics = lazy(() => import('./pages/Analytics'))
const SetBuilderRingsV2 = lazy(() => import('./components/SetBuilderRingsV2'))
const DisplayDesignLab = lazy(() => import('./pages/DisplayDesignLab'))
const DecadePage = lazy(() => import('./pages/DecadePage'))
const MagazineArchivePage = lazy(() => import('./pages/magazine/MagazineArchivePage'))
const MagazineReaderPage = lazy(() => import('./pages/magazine/MagazineReaderPage'))
const ArtDepartmentPage = lazy(() => import('./pages/magazine/ArtDepartmentPage'))
const ArtDepartmentArtistPage = lazy(() => import('./pages/magazine/ArtDepartmentArtistPage'))
const ArtDirectorPage = lazy(() => import('./pages/magazine/ArtDirectorPage'))
const YearPage = lazy(() => import('./pages/YearPage'))
const WeekPage = lazy(() => import('./pages/WeekPage'))
const ArtistPage = lazy(() => import('./pages/ArtistPage'))
const ChartClimberGame = lazy(() => import('./pages/games/ChartClimberGame'))
const GuessPeakGame = lazy(() => import('./pages/games/GuessPeakGame'))
const VideoTimeMachineGame = lazy(() => import('./pages/games/VideoTimeMachineGame'))
const YearShuffleGame = lazy(() => import('./pages/games/YearShuffleGame'))

function RouteLoadingFallback() {
  return (
    <section className="stack">
      <div className="section">
        <p className="muted">Loading...</p>
      </div>
    </section>
  )
}

function App() {
  return (
    <PlaylistProvider>
      <BrowserRouter>
        <AppShell>
          <Suspense fallback={<RouteLoadingFallback />}>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/hub" element={<Hub />} />
              <Route path="/surprise" element={<SurprisePage />} />
              <Route path="/charts" element={<ChartsPage />} />
              <Route path="/video-library" element={<VideoLibrary />} />
              <Route path="/videolibrary" element={<Navigate to="/video-library" replace />} />
              <Route path="/playlists" element={<Playlists />} />
              <Route path="/setbuilder" element={<SetBuilder />} />
              <Route path="/random" element={<Navigate to="/setbuilder" replace />} />
              <Route path="/matching" element={<Matching />} />
              <Route path="/games" element={<Games />} />
              <Route path="/games/chart-climber" element={<ChartClimberGame />} />
              <Route path="/games/year-shuffle" element={<YearShuffleGame />} />
              <Route path="/games/video-time-machine" element={<VideoTimeMachineGame />} />
              <Route path="/games/guess-peak" element={<GuessPeakGame />} />
              <Route path="/arcade" element={<Navigate to="/games" replace />} />
              <Route path="/tools" element={<Tools />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/decade/:decade" element={<DecadePage />} />
              <Route path="/magazine" element={<MagazineArchivePage />} />
              <Route path="/magazine/:year" element={<MagazineReaderPage />} />
              <Route path="/magazine/:year/page/:page" element={<MagazineReaderPage />} />
              <Route path="/art-department" element={<ArtDepartmentPage />} />
              <Route path="/art-department/:artistId" element={<ArtDepartmentArtistPage />} />
              <Route path="/art-director" element={<ArtDirectorPage />} />
              <Route path="/year/:year" element={<YearPage />} />
              <Route path="/week/:date" element={<WeekPage />} />
              <Route path="/artist/:name" element={<ArtistPage />} />
              <Route path="/set-builder-rings" element={<SetBuilderRingsV2 />} />
              <Route path="/design-lab/display" element={<DisplayDesignLab />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        </AppShell>
      </BrowserRouter>
    </PlaylistProvider>
  )
}

export default App
