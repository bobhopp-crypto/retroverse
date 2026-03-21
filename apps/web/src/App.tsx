import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AppShell from './components/AppShell'
import LandingPage from './pages/LandingPage'
import Hub from './pages/Hub'
import VideoLibrary from './pages/VideoLibrary'
import Playlists from './pages/Playlists'
import SetBuilder from './pages/SetBuilder'
import SurprisePage from './pages/SurprisePage'
import ChartsPage from './pages/ChartsPage'
import Matching from './pages/Matching'
import Games from './pages/Games'
import Tools from './pages/Tools'
import Analytics from './pages/Analytics'
import SetBuilderRingsV2 from './components/SetBuilderRingsV2'
import DisplayDesignLab from './pages/DisplayDesignLab'
import DecadePage from './pages/DecadePage'
import MagazineIndex from './pages/magazine/MagazineIndex'
import MagazineYear from './pages/magazine/MagazineYear'
import ArtDepartmentPage from './pages/magazine/ArtDepartmentPage'
import ArtDepartmentArtistPage from './pages/magazine/ArtDepartmentArtistPage'
import ArtDirectorPage from './pages/magazine/ArtDirectorPage'
import YearPage from './pages/YearPage'
import WeekPage from './pages/WeekPage'
import ArtistPage from './pages/ArtistPage'
import ChartClimberGame from './pages/games/ChartClimberGame'
import GuessPeakGame from './pages/games/GuessPeakGame'
import VideoTimeMachineGame from './pages/games/VideoTimeMachineGame'
import YearShuffleGame from './pages/games/YearShuffleGame'
import { PlaylistProvider } from './context/PlaylistContext'
import './App.css'

function App() {
  return (
    <PlaylistProvider>
      <BrowserRouter>
        <AppShell>
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
            <Route path="/magazine" element={<MagazineIndex />} />
            <Route path="/magazine/:year" element={<MagazineYear />} />
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
        </AppShell>
      </BrowserRouter>
    </PlaylistProvider>
  )
}

export default App
