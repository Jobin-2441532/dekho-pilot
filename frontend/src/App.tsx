import { lazy, Suspense } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import AppShell from './components/layout/AppShell'

/* ── Auth (always needed immediately) ── */
import Login from './pages/Login'

/* ── Main tab pages ── */
import Home from './pages/Home'
const Expenses     = lazy(() => import('./pages/Expenses'))
const Budgets      = lazy(() => import('./pages/Budgets'))
const Assets       = lazy(() => import('./pages/Assets'))
const Grow         = lazy(() => import('./pages/Grow'))
const Behavior     = lazy(() => import('./pages/Behavior'))

/* ── Transaction pages ── */
const ReviewQueue      = lazy(() => import('./pages/ReviewQueue'))
const TransactionsList = lazy(() => import('./pages/TransactionsList'))

/* ── Asset sub-pages ── */
const InvestmentsDetail = lazy(() => import('./pages/InvestmentsDetail'))
const MutualFundDetail  = lazy(() => import('./pages/MutualFundDetail'))
const SavingsDetail     = lazy(() => import('./pages/SavingsDetail'))
const LiabilitiesDetail = lazy(() => import('./pages/LiabilitiesDetail'))

/* ── Grow sub-pages ── */
const PersonalizedRecommendations = lazy(() => import('./pages/PersonalizedRecommendations'))
const PathDetailIndexFundSIP      = lazy(() => import('./pages/PathDetailIndexFundSIP'))

/* ── Special screens ── */
const Goals       = lazy(() => import('./pages/Goals'))
const MonthlyWrap = lazy(() => import('./pages/MonthlyWrap'))
const Settings    = lazy(() => import('./pages/Settings'))
const AskDekho    = lazy(() => import('./pages/AskDekho'))

/* ── Tiny spinner for Suspense fallback ── */
function PageLoader() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
      <div style={{ width: 28, height: 28, borderRadius: '50%', border: '3px solid var(--color-primary)', borderTopColor: 'transparent', animation: 'spin 0.7s linear infinite' }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}

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
                <Suspense fallback={<PageLoader />}>
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
                </Suspense>
              </AppShell>
            </RequireAuth>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}
