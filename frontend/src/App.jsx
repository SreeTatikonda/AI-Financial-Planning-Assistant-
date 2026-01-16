import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import BudgetAnalysis from './pages/BudgetAnalysis'
import Goals from './pages/Goals'
import HealthScore from './pages/HealthScore'
import Chat from './pages/Chat'
import './App.css'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <Router>
      <div className="flex h-screen bg-gray-50">
        {/* Sidebar */}
        <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-white shadow-lg transition-all duration-300`}>
          <div className="p-6">
            <h1 className={`text-2xl font-bold text-blue-600 ${!sidebarOpen && 'text-center'}`}>
              {sidebarOpen ? 'AI Finance' : '💰'}
            </h1>
          </div>
          
          <nav className="mt-6">
            <NavLink to="/" icon="📊" label="Dashboard" compact={!sidebarOpen} />
            <NavLink to="/budget" icon="💳" label="Budget" compact={!sidebarOpen} />
            <NavLink to="/goals" icon="🎯" label="Goals" compact={!sidebarOpen} />
            <NavLink to="/health" icon="❤️" label="Health Score" compact={!sidebarOpen} />
            <NavLink to="/chat" icon="💬" label="Chat" compact={!sidebarOpen} />
          </nav>
          
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="absolute bottom-4 left-4 p-2 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            {sidebarOpen ? '◀' : '▶'}
          </button>
        </aside>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/budget" element={<BudgetAnalysis />} />
              <Route path="/goals" element={<Goals />} />
              <Route path="/health" element={<HealthScore />} />
              <Route path="/chat" element={<Chat />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  )
}

function NavLink({ to, icon, label, compact }) {
  return (
    <Link
      to={to}
      className={`flex items-center px-6 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors ${
        compact && 'justify-center'
      }`}
    >
      <span className="text-xl">{icon}</span>
      {!compact && <span className="ml-3">{label}</span>}
    </Link>
  )
}

export default App
