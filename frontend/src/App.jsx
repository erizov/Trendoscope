import { useState, useEffect } from 'react'
import axios from 'axios'
import NewsFeed from './components/NewsFeed'
import SearchBar from './components/SearchBar'
import Filters from './components/Filters'
import './App.css'

const API_BASE = '/api'

function App() {
  const [news, setNews] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({
    category: 'all',
    language: 'all',
    limit: 20
  })
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState(null)

  useEffect(() => {
    loadNews()
    connectWebSocket()
  }, [filters])

  const loadNews = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({
        category: filters.category,
        language: filters.language,
        limit: filters.limit.toString()
      })
      const response = await axios.get(`${API_BASE}/news/feed?${params}`)
      setNews(response.data.news || [])
      setError(null)
    } catch (err) {
      setError(err.message)
      console.error('Failed to load news:', err)
    } finally {
      setLoading(false)
    }
  }

  const connectWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/api/news/ws`
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log('WebSocket connected')
      ws.send(JSON.stringify({ type: 'subscribe', channel: 'news_updates' }))
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'news_batch' && data.data) {
        // Update news feed with new items
        setNews(prev => [...data.data, ...prev].slice(0, filters.limit))
      } else if (data.type === 'news_update' && data.data) {
        // Add single news item
        setNews(prev => [data.data, ...prev].slice(0, filters.limit))
      }
    }

    ws.onerror = (err) => {
      console.error('WebSocket error:', err)
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
      // Reconnect after 5 seconds
      setTimeout(connectWebSocket, 5000)
    }

    return () => ws.close()
  }

  const handleSearch = async (query) => {
    if (!query.trim()) {
      setSearchResults(null)
      return
    }

    try {
      setLoading(true)
      const params = new URLSearchParams({ q: query })
      const response = await axios.get(`${API_BASE}/news/search?${params}`)
      setSearchResults(response.data)
      setError(null)
    } catch (err) {
      setError(err.message)
      console.error('Search failed:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Trendoscope2</h1>
        <p>News Aggregation & Content Generation</p>
      </header>

      <div className="app-content">
        <div className="sidebar">
          <SearchBar onSearch={handleSearch} />
          <Filters
            filters={filters}
            onChange={setFilters}
          />
        </div>

        <main className="main-content">
          {error && (
            <div className="error-message">
              Error: {error}
            </div>
          )}

          {loading && !news.length && (
            <div className="loading">Loading news...</div>
          )}

          {searchResults ? (
            <div>
              <h2>Search Results</h2>
              <p>Found {searchResults.total} results</p>
              <NewsFeed news={searchResults.results} />
            </div>
          ) : (
            <NewsFeed news={news} loading={loading} />
          )}
        </main>
      </div>
    </div>
  )
}

export default App
