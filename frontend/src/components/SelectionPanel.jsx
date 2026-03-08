import { useState, useEffect } from 'react'
import { getSelections, getCourses } from '../api'

export default function SelectionPanel({ onContextSet, activeContext }) {
  const [selections, setSelections] = useState({ programmes: [], semesters: [], regulation_years: [] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [selectedProgramme, setSelectedProgramme] = useState(null)
  const [selectedSemester, setSelectedSemester] = useState(null)
  const [selectedRegYear, setSelectedRegYear] = useState(null)

  const [courses, setCourses] = useState([])
  const [coursesLoading, setCoursesLoading] = useState(false)

  useEffect(() => {
    getSelections()
      .then(data => setSelections(data))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selectedProgramme || selectedSemester === null || selectedRegYear === null) {
      setCourses([])
      return
    }
    setCoursesLoading(true)
    getCourses(selectedProgramme.id, selectedSemester, selectedRegYear)
      .then(data => setCourses(data))
      .catch(err => setError(err.message))
      .finally(() => setCoursesLoading(false))
  }, [selectedProgramme, selectedSemester, selectedRegYear])

  function toggleProgramme(p) {
    setSelectedProgramme(prev => (prev?.id === p.id ? null : p))
    onContextSet(null)
  }

  function toggleSemester(s) {
    setSelectedSemester(prev => (prev === s ? null : s))
    onContextSet(null)
  }

  function toggleRegYear(y) {
    setSelectedRegYear(prev => (prev === y ? null : y))
    onContextSet(null)
  }

  function handleCourseSelect(course) {
    onContextSet({
      programme: selectedProgramme,
      semester: selectedSemester,
      regulationYear: selectedRegYear,
      course,
    })
  }

  if (loading) {
    return (
      <aside className="selection-panel">
        <div className="panel-header">
          <h1>Cognivault</h1>
        </div>
        <p className="panel-loading">Loading...</p>
      </aside>
    )
  }

  return (
    <aside className="selection-panel">
      <div className="panel-header">
        <h1>Cognivault</h1>
        <p>Course-aware AI Assistant</p>
      </div>

      {error && <p className="panel-error">{error}</p>}

      <div className="filter-section">
        <h3 className="filter-label">Programme</h3>
        <div className="chips">
          {selections.programmes.map(p => (
            <button
              key={p.id}
              className={`chip${selectedProgramme?.id === p.id ? ' active' : ''}`}
              onClick={() => toggleProgramme(p)}
              title={p.name}
            >
              {p.code}
            </button>
          ))}
          {selections.programmes.length === 0 && (
            <span className="no-data">None available</span>
          )}
        </div>
      </div>

      <div className="filter-section">
        <h3 className="filter-label">Semester</h3>
        <div className="chips">
          {selections.semesters.map(s => (
            <button
              key={s}
              className={`chip${selectedSemester === s ? ' active' : ''}`}
              onClick={() => toggleSemester(s)}
            >
              Sem {s}
            </button>
          ))}
          {selections.semesters.length === 0 && (
            <span className="no-data">None available</span>
          )}
        </div>
      </div>

      <div className="filter-section">
        <h3 className="filter-label">Regulation Year</h3>
        <div className="chips">
          {selections.regulation_years.map(y => (
            <button
              key={y}
              className={`chip${selectedRegYear === y ? ' active' : ''}`}
              onClick={() => toggleRegYear(y)}
            >
              {y}
            </button>
          ))}
          {selections.regulation_years.length === 0 && (
            <span className="no-data">None available</span>
          )}
        </div>
      </div>

      {selectedProgramme && selectedSemester !== null && selectedRegYear !== null && (
        <div className="courses-section">
          <h3 className="filter-label">Courses</h3>
          {coursesLoading ? (
            <p className="panel-loading">Loading courses...</p>
          ) : courses.length === 0 ? (
            <p className="no-data">No courses found for this selection</p>
          ) : (
            <div className="course-list">
              {courses.map(course => (
                <button
                  key={course.id}
                  className={`course-card${activeContext?.course?.id === course.id ? ' active' : ''}`}
                  onClick={() => handleCourseSelect(course)}
                >
                  <span className="course-code">{course.code}</span>
                  <span className="course-name">{course.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {activeContext && (
        <div className="context-indicator">
          <span className="context-dot" />
          Active: <strong>{activeContext.course.code}</strong>
        </div>
      )}
    </aside>
  )
}
