import { useState } from 'react'
import './NewsFeed.css'

function NewsFeed({ news, loading }) {
  const [expandedId, setExpandedId] = useState(null)

  if (loading && !news.length) {
    return <div className="loading">Loading...</div>
  }

  if (!news.length) {
    return <div className="empty">No news available</div>
  }

  return (
    <div className="news-feed">
      {news.map((item, index) => (
        <article
          key={item.link || item.url || index}
          className="news-item"
          onClick={() => setExpandedId(expandedId === index ? null : index)}
        >
          <div className="news-header">
            <h3 className="news-title">{item.title}</h3>
            <span className="news-source">{item.source}</span>
          </div>
          
          {item.summary && (
            <p className="news-summary">{item.summary}</p>
          )}
          
          {expandedId === index && item.description && (
            <div className="news-description">
              {item.description}
            </div>
          )}
          
          <div className="news-footer">
            <span className="news-category">{item.category || 'general'}</span>
            {item.published && (
              <span className="news-date">
                {new Date(item.published).toLocaleDateString()}
              </span>
            )}
            {item.link && (
              <a
                href={item.link}
                target="_blank"
                rel="noopener noreferrer"
                className="news-link"
                onClick={(e) => e.stopPropagation()}
              >
                Read more
              </a>
            )}
          </div>
        </article>
      ))}
    </div>
  )
}

export default NewsFeed
