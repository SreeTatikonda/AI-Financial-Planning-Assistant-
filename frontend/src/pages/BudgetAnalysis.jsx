
import { useState } from 'react'
import { budgetAPI } from '../services/api'

export default function BudgetAnalysis() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [analysis, setAnalysis] = useState(null)
  const [error, setError] = useState(null)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile)
      setError(null)
    } else {
      setError('Please select a valid CSV file')
      setFile(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first')
      return
    }

    setLoading(true)
    setError(null)

    try {
      // Upload and categorize
      const uploadResult = await budgetAPI.uploadCSV(file)
      
      // Analyze
      const analysisResult = await budgetAPI.analyze(uploadResult.transactions)
      
      setAnalysis(analysisResult)
    } catch (err) {
      setError(err.message || 'Failed to process file')
      console.error('Upload error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Budget Analysis</h1>
      
      {/* Upload Section */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <p className="text-gray-600 mb-4">Upload your transactions CSV file to get started.</p>
        
        <div className="flex gap-4 items-center">
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          
          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed whitespace-nowrap"
          >
            {loading ? 'Processing...' : 'Analyze'}
          </button>
        </div>

        {file && (
          <p className="mt-2 text-sm text-green-600">
            ✓ {file.name} selected
          </p>
        )}

        {error && (
          <p className="mt-2 text-sm text-red-600">
            ✗ {error}
          </p>
        )}

        <div className="mt-4 p-3 bg-gray-50 rounded text-sm text-gray-600">
          <p className="font-semibold mb-1">CSV Format:</p>
          <code>date,description,amount</code>
          <p className="mt-1">Example: 2024-01-15,Starbucks,-5.50</p>
        </div>
      </div>

      {/* Results Section */}
      {analysis && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-gray-600 text-sm mb-2">Total Spent</h3>
              <p className="text-3xl font-bold text-red-600">
                ${analysis.total_spent.toFixed(2)}
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-gray-600 text-sm mb-2">Total Income</h3>
              <p className="text-3xl font-bold text-green-600">
                ${analysis.total_income.toFixed(2)}
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-gray-600 text-sm mb-2">Transactions</h3>
              <p className="text-3xl font-bold text-blue-600">
                {analysis.transaction_count}
              </p>
            </div>
          </div>

          {/* Spending by Category */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Spending by Category</h2>
            <div className="space-y-3">
              {analysis.top_categories.map((cat, idx) => (
                <div key={idx} className="flex justify-between items-center">
                  <span className="text-gray-700">{cat.category}</span>
                  <span className="font-semibold text-gray-900">
                    ${cat.amount.toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* AI Insights */}
          {analysis.insights && analysis.insights.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">💡 AI Insights</h2>
              <div className="space-y-3">
                {analysis.insights.map((insight, idx) => (
                  <div key={idx} className="flex gap-3">
                    <span className="text-blue-600 font-bold">{idx + 1}.</span>
                    <p className="text-gray-700">{insight}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
