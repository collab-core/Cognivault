import { useState, useEffect } from 'react'
import { getSelections, getCourses } from '../api'

const STORAGE_KEY_SELECTIONS = 'syllabase_selections'

function saveSelectionsToStorage(programme, semester, regYear, courseId) {
  const selections = {
    programmeId: programme?.id || null,
    programmeName: programme?.name || null,
    programmeCode: programme?.code || null,
    semester: semester ?? null,
    regulationYear: regYear ?? null,
    courseId: courseId || null,
  }
  try {
    localStorage.setItem(STORAGE_KEY_SELECTIONS, JSON.stringify(selections))
  } catch (err) {
    console.error('Failed to save selections to storage:', err)
  }
}

function loadSelectionsFromStorage() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY_SELECTIONS)
    return stored ? JSON.parse(stored) : null
  } catch (err) {
    console.error('Failed to load selections from storage:', err)
    return null
  }
}

export default function SelectionPanel({ onContextSet, activeContext }) {
  const [selections, setSelections] = useState({ programmes: [], semesters: [], regulation_years: [] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [selectedProgramme, setSelectedProgramme] = useState(null)
  const [selectedSemester, setSelectedSemester] = useState(null)
  const [selectedRegYear, setSelectedRegYear] = useState(null)

  const [courses, setCourses] = useState([])
  const [coursesLoading, setCoursesLoading] = useState(false)

  // Load initial selections from API, then restore from localStorage
  useEffect(() => {
    getSelections()
      .then(data => {
        setSelections(data)

        // Try to restore state from localStorage
        const saved = loadSelectionsFromStorage()
        if (saved && data.programmes) {
          // Find and restore programme
          const programme = data.programmes.find(p => p.id === saved.programmeId)
          if (programme) {
            setSelectedProgramme(programme)
            
            // Restore semester if available
            if (saved.semester !== null && data.semesters.includes(saved.semester)) {
              setSelectedSemester(saved.semester)
            }
            
            // Restore regulation year if available
            if (saved.regulationYear !== null && data.regulation_years.includes(saved.regulationYear)) {
              setSelectedRegYear(saved.regulationYear)
            }
          }
        }
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  // Auto-select and restore course when all filters are ready
  useEffect(() => {
    if (!selectedProgramme || selectedSemester === null || selectedRegYear === null) {
      setCourses([])
      return
    }

    setCoursesLoading(true)
    getCourses(selectedProgramme.id, selectedSemester, selectedRegYear)
      .then(data => {
        setCourses(data)
        
        // Try to restore the course selection
        const saved = loadSelectionsFromStorage()
        if (saved && saved.courseId) {
          const savedCourse = data.find(c => c.id === saved.courseId)
          if (savedCourse) {
            // Trigger course selection with slight delay to ensure state is ready
            setTimeout(() => {
              onContextSet({
                programme: selectedProgramme,
                semester: selectedSemester,
                regulationYear: selectedRegYear,
                course: savedCourse,
              })
            }, 0)
          }
        }
      })
      .catch(err => setError(err.message))
      .finally(() => setCoursesLoading(false))
  }, [selectedProgramme, selectedSemester, selectedRegYear, onContextSet])

  function toggleProgramme(p) {
    const newProgramme = selectedProgramme?.id === p.id ? null : p
    setSelectedProgramme(newProgramme)
    saveSelectionsToStorage(newProgramme, null, null, null)
    onContextSet(null)
  }

  function toggleSemester(s) {
    const newSemester = selectedSemester === s ? null : s
    setSelectedSemester(newSemester)
    saveSelectionsToStorage(selectedProgramme, newSemester, selectedRegYear, null)
    onContextSet(null)
  }

  function toggleRegYear(y) {
    const newRegYear = selectedRegYear === y ? null : y
    setSelectedRegYear(newRegYear)
    saveSelectionsToStorage(selectedProgramme, selectedSemester, newRegYear, null)
    onContextSet(null)
  }

  function handleCourseSelect(course) {
    const context = {
      programme: selectedProgramme,
      semester: selectedSemester,
      regulationYear: selectedRegYear,
      course,
    }
    saveSelectionsToStorage(selectedProgramme, selectedSemester, selectedRegYear, course.id)
    onContextSet(context)
  }

  if (loading) {
    return (
      <aside className="selection-panel">
        <div className="panel-header">
          <h1>Syllabase</h1>
        </div>
        <p className="panel-loading">Loading...</p>
      </aside>
    )
  }

  return (
    <aside className="selection-panel">
      <div className="panel-header">
        <h1>Syllabase</h1>
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
