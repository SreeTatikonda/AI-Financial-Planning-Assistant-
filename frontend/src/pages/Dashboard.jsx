import { useState, useEffect } from 'react'
import { healthCheck } from '../services/api'

export default function Dashboard() {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkHealth()
  }, [])

  const checkHealth = async () => {
    try {
      const data = await healthCheck()
      setStatus(data)
    } catch (error) {
      console.error('Health check failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Balance"
          value="$12,450"
          change="+5.2%"
          positive={true}
          icon="💰"
        />
        <StatCard
          title="Monthly Spending"
          value="$3,280"
          change="-2.1%"
          positive={true}
          icon="💳"
        />
        <StatCard
          title="Active Goals"
          value="3"
          change="+1"
          positive={true}
          icon="🎯"
        />
        <StatCard
          title="Health Score"
          value="78/100"
          change="+6"
          positive={true}
          icon="❤️"
        />
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <ActionButton
            icon="📊"
            title="Analyze Budget"
            description="Upload and analyze transactions"
            link="/budget"
          />
          <ActionButton
            icon="🎯"
            title="Set a Goal"
            description="Create a new financial goal"
            link="/goals"
          />
          <ActionButton
            icon="💬"
            title="Ask AI"
            description="Get financial advice"
            link="/chat"
          />
        </div>
      </div>

      {!loading && status && (
        <div className="mt-6 p-4 bg-green-50 rounded-lg">
          <p className="text-sm text-green-800">
            ✅ System Status: {status.status} | LLM: {status.llm_provider}
          </p>
        </div>
      )}
    </div>
  )
}

function StatCard({ title, value, change, positive, icon }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl">{icon}</span>
        <span className={`text-sm ${positive ? 'text-green-600' : 'text-red-600'}`}>
          {change}
        </span>
      </div>
      <h3 className="text-gray-600 text-sm">{title}</h3>
      <p className="text-2xl font-bold text-gray-800">{value}</p>
    </div>
  )
}

function ActionButton({ icon, title, description, link }) {
  return (
    <a
      href={link}
      className="block p-4 bg-gray-50 rounded-lg hover:bg-blue-50 transition-colors"
    >
      <div className="text-3xl mb-2">{icon}</div>
      <h3 className="font-semibold text-gray-800">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </a>
  )
}
