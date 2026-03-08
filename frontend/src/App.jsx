import { useState } from 'react'
import SelectionPanel from './components/SelectionPanel'
import ChatInterface from './components/ChatInterface'
import './App.css'

function App() {
  const [activeContext, setActiveContext] = useState(null)

  return (
    <div className="app">
      <SelectionPanel onContextSet={setActiveContext} activeContext={activeContext} />
      <ChatInterface activeContext={activeContext} />
    </div>
  )
}

export default App
