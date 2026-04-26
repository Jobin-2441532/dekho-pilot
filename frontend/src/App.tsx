import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import AppShell from './components/layout/AppShell'

/* ── Main tab pages ── */
import Onboarding   from './pages/Onboarding'
import Home         from './pages/Home'
import Expenses     from './pages/Expenses'
import Budgets      from './pages/Budgets'
import Assets       from './pages/Assets'
import Grow         from './pages/Grow'

/* ── Asset sub-pages ── */
import InvestmentsDetail      from './pages/InvestmentsDetail'
import MutualFundDetail       from './pages/MutualFundDetail'
import SavingsDetail          from './pages/SavingsDetail'
import LiabilitiesDetail      from './pages/LiabilitiesDetail'

/* ── Grow sub-pages ── */
import PersonalizedRecommendations from './pages/PersonalizedRecommendations'
import PathDetailIndexFundSIP      from './pages/PathDetailIndexFundSIP'

/* ── Special screens ── */
import MonthlyWrap from './pages/MonthlyWrap'
import Settings    from './pages/Settings'
import AskDekho    from './pages/AskDekho'

/* ── Auth guard ── */
function RequireOnboarding({ children }: { children: React.ReactNode }) {
  const done = localStorage.getItem('dekho_onboarded')
  return done ? <>{children}</> : <Navigate to="/onboarding" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ── Onboarding — outside shell ── */}
        <Route path="/onboarding" element={<Onboarding />} />

        {/* ── Authenticated app — inside shell ── */}
        <Route
          path="/*"
          element={
            <RequireOnboarding>
              <AppShell>
                <Routes>
                  {/* Default redirect */}
                  <Route path="/" element={<Navigate to="/home" replace />} />

                  {/* ── Main tabs ── */}
                  <Route path="/home"     element={<Home />} />
                  <Route path="/expenses" element={<Expenses />} />
                  <Route path="/budgets"  element={<Budgets />} />
                  <Route path="/assets"   element={<Assets />} />
                  <Route path="/grow"     element={<Grow />} />

                  {/* ── Assets sub-pages ── */}
                  <Route path="/assets/investments"             element={<InvestmentsDetail />} />
                  <Route path="/assets/investments/mutual-fund" element={<MutualFundDetail />} />
                  <Route path="/assets/savings"                 element={<SavingsDetail />} />
                  <Route path="/assets/liabilities"             element={<LiabilitiesDetail />} />

                  {/* ── Grow sub-pages ── */}
                  <Route path="/grow/recommendations"  element={<PersonalizedRecommendations />} />
                  <Route path="/grow/index-fund-sip"   element={<PathDetailIndexFundSIP />} />

                  {/* ── Special ── */}
                  <Route path="/monthly-wrap" element={<MonthlyWrap />} />
                  <Route path="/settings"     element={<Settings />} />
                  <Route path="/ask"          element={<AskDekho />} />

                  {/* ── Legacy redirect ── */}
                  <Route path="/goals"         element={<Navigate to="/budgets" replace />} />
                  <Route path="/opportunities" element={<Navigate to="/grow" replace />} />
                  <Route path="/behavior"      element={<Navigate to="/home" replace />} />
                </Routes>
              </AppShell>
            </RequireOnboarding>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}
