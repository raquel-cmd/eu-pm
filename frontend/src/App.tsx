import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ProjectListPage from './pages/ProjectListPage';
import ProjectDetailPage from './pages/ProjectDetailPage';
import ProjectFormPage from './pages/ProjectFormPage';
import TimesheetPage from './pages/TimesheetPage';
import FinanceDashboardPage from './pages/FinanceDashboardPage';
import ReportingCalendarPage from './pages/ReportingCalendarPage';
import ReportEditorPage from './pages/ReportEditorPage';
import FinancialReportingPage from './pages/FinancialReportingPage';
import TemplateLibraryPage from './pages/TemplateLibraryPage';
import TemplateFillPage from './pages/TemplateFillPage';
import PIDashboardPage from './pages/PIDashboardPage';
import ResearcherDashboardPage from './pages/ResearcherDashboardPage';
import ProjectDashboardPage from './pages/ProjectDashboardPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
});

function NavLink({ to, children }: { to: string; children: React.ReactNode }) {
  const { pathname } = useLocation();
  const isActive = pathname === to || pathname.startsWith(to + '/');
  return (
    <Link
      to={to}
      className={`text-sm font-medium ${
        isActive ? 'text-blue-700' : 'text-gray-600 hover:text-blue-700'
      }`}
    >
      {children}
    </Link>
  );
}

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-3">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <Link to="/" className="text-xl font-bold text-blue-700">
            EU Project Management
          </Link>
          <div className="flex gap-6">
            <NavLink to="/projects">Projects</NavLink>
            <NavLink to="/timesheets">Timesheets</NavLink>
            <NavLink to="/reporting-calendar">Calendar</NavLink>
            <NavLink to="/templates">Templates</NavLink>
            <NavLink to="/dashboard/pi">Dashboards</NavLink>
            <NavLink to="/reports">Reports</NavLink>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-6 py-8">{children}</main>
    </div>
  );
}

function HomePage() {
  return (
    <div className="text-center py-20">
      <h1 className="text-4xl font-bold text-gray-900 mb-4">
        EU Research Project Management
      </h1>
      <p className="text-lg text-gray-600 mb-8">
        Manage Horizon Europe, Digital Europe, Erasmus+, CEF, and FCT projects
      </p>
      <Link
        to="/projects"
        className="inline-block bg-blue-700 text-white px-6 py-3 rounded-lg hover:bg-blue-800"
      >
        View Projects
      </Link>
    </div>
  );
}

function NotFoundPage() {
  return (
    <div className="text-center py-20">
      <h1 className="text-2xl font-bold text-gray-900">404 - Page Not Found</h1>
      <Link to="/" className="text-blue-700 hover:underline mt-4 inline-block">
        Go home
      </Link>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/projects" element={<ProjectListPage />} />
            <Route path="/projects/new" element={<ProjectFormPage />} />
            <Route path="/projects/:id" element={<ProjectDetailPage />} />
            <Route path="/projects/:id/edit" element={<ProjectFormPage />} />
            <Route path="/timesheets" element={<TimesheetPage />} />
            <Route path="/reporting-calendar" element={<ReportingCalendarPage />} />
            <Route path="/technical-reports/:reportId" element={<ReportEditorPage />} />
            <Route path="/projects/:id/financial-reporting" element={<FinancialReportingPage />} />
            <Route path="/templates" element={<TemplateLibraryPage />} />
            <Route path="/templates/:templateId/fill" element={<TemplateFillPage />} />
            <Route path="/dashboard/pi" element={<PIDashboardPage />} />
            <Route path="/dashboard/researcher/:researcherId" element={<ResearcherDashboardPage />} />
            <Route path="/projects/:id/dashboard" element={<ProjectDashboardPage />} />
            <Route path="/reports" element={<FinanceDashboardPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
