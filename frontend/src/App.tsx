import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import AppShell from './components/layout/AppShell'

/* ── Auth ── */
import Login from './pages/Login'

/* ── Main tab pages ── */
import Home         from './pages/Home'
import Expenses     from './pages/Expenses'
import Budgets      from './pages/Budgets'
import Assets       from './pages/Assets'
import Grow         from './pages/Grow'
import Behavior     from './pages/Behavior'

/* ── Transaction pages ── */
import ReviewQueue      from './pages/ReviewQueue'
import TransactionsList from './pages/TransactionsList'

/* ── Asset sub-pages ── */
import InvestmentsDetail from './pages/InvestmentsDetail'
import MutualFundDetail  from './pages/MutualFundDetail'
import SavingsDetail     from './pages/SavingsDetail'
import LiabilitiesDetail from './pages/LiabilitiesDetail'

/* ── Grow sub-pages ── */
import PersonalizedRecommendations from './pages/PersonalizedRecommendations'
import PathDetailIndexFundSIP      from './pages/PathDetailIndexFundSIP'

/* ── Special screens ── */
import Goals       from './pages/Goals'
import MonthlyWrap from './pages/MonthlyWrap'
import Settings    from './pages/Settings'
import AskDekho    from './pages/AskDekho'

/* ── Auth guard — checks for JWT token ── */
function RequireAuth({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('dekho_token')
  const onboarded = localStorage.getItem('dekho_onboarded')
  return (token && onboarded) ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ── Login — outside shell ── */}
        <Route path="/login"      element={<Login />} />
        <Route path="/onboarding" element={<Navigate to="/login" replace />} />

        {/* ── Authenticated app — inside shell ── */}
        <Route
          path="/*"
          element={
            <RequireAuth>
              <AppShell>
                <Routes>
                  {/* Default redirect */}
                  <Route path="/" element={<Navigate to="/home" replace />} />

                  {/* ── Main tabs ── */}
                  <Route path="/home"         element={<Home />} />
                  <Route path="/expenses"     element={<Expenses />} />
                  <Route path="/budgets"      element={<Budgets />} />
                  <Route path="/assets"       element={<Assets />} />
                  <Route path="/grow"         element={<Grow />} />
                  <Route path="/behavior"     element={<Behavior />} />

                  {/* ── Transaction pages ── */}
                  <Route path="/transactions" element={<TransactionsList />} />
                  <Route path="/review"       element={<ReviewQueue />} />

                  {/* ── Goals (standalone) ── */}
                  <Route path="/goals"        element={<Goals />} />

                  {/* ── Assets sub-pages ── */}
                  <Route path="/assets/investments"             element={<InvestmentsDetail />} />
                  <Route path="/assets/investments/mutual-fund" element={<MutualFundDetail />} />
                  <Route path="/assets/savings"                 element={<SavingsDetail />} />
                  <Route path="/assets/liabilities"             element={<LiabilitiesDetail />} />

                  {/* ── Grow sub-pages ── */}
                  <Route path="/grow/recommendations" element={<PersonalizedRecommendations />} />
                  <Route path="/grow/index-fund-sip"  element={<PathDetailIndexFundSIP />} />

                  {/* ── Special ── */}
                  <Route path="/monthly-wrap" element={<MonthlyWrap />} />
                  <Route path="/settings"     element={<Settings />} />
                  <Route path="/ask"          element={<AskDekho />} />

                  {/* ── Legacy redirects ── */}
                  <Route path="/opportunities" element={<Navigate to="/grow" replace />} />
                </Routes>
              </AppShell>
            </RequireAuth>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}
