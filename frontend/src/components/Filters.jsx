import { useState, useEffect } from 'react'
import axios from 'axios'
import './Filters.css'

const API_BASE = '/api'

function Filters({ filters, onChange }) {
  const [availableFilters, setAvailableFilters] = useState({
    categories: [],
    languages: ['all', 'ru', 'en'],
    sources: []
  })

  useEffect(() => {
    loadFilters()
  }, [])

  const loadFilters = async () => {
    try {
      const response = await axios.get(`${API_BASE}/news/filters`)
      setAvailableFilters(response.data)
    } catch (err) {
      console.error('Failed to load filters:', err)
    }
  }

  const handleFilterChange = (key, value) => {
    onChange({ ...filters, [key]: value })
  }

  return (
    <div className="filters">
      <h3>Filters</h3>
      
      <div className="filter-group">
        <label>Category</label>
        <select
          value={filters.category}
          onChange={(e) => handleFilterChange('category', e.target.value)}
        >
          <option value="all">All Categories</option>
          {availableFilters.categories.map(cat => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Language</label>
        <select
          value={filters.language}
          onChange={(e) => handleFilterChange('language', e.target.value)}
        >
          {availableFilters.languages.map(lang => (
            <option key={lang} value={lang}>{lang}</option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label>Limit</label>
        <input
          type="number"
          min="5"
          max="100"
          value={filters.limit}
          onChange={(e) => handleFilterChange('limit', parseInt(e.target.value))}
        />
      </div>
    </div>
  )
}

export default Filters
