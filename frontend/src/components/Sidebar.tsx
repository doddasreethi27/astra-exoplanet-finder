import { Activity, Atom, ChartNoAxesCombined, Compass, Database, FlaskConical, HelpCircle, Orbit, Telescope, Upload } from 'lucide-react'

type Page = 'Overview' | 'Explore' | 'Analyze' | 'Model Lab' | 'Data Sources'
const items: { label: Page; icon: typeof Orbit }[] = [
  { label: 'Overview', icon: ChartNoAxesCombined },
  { label: 'Explore', icon: Compass },
  { label: 'Analyze', icon: Upload },
  { label: 'Model Lab', icon: FlaskConical },
  { label: 'Data Sources', icon: Database },
]

export default function Sidebar({ page, setPage, modelLoaded }: { page: Page; setPage: (p: Page) => void; modelLoaded: boolean }) {
  return <aside className="sidebar">
    <div className="brand"><div className="brand-mark"><Orbit size={21}/></div><div><strong>ASTRA</strong><span>EXOPLANET INTELLIGENCE</span></div></div>
    <div className="workspace-label">WORKSPACE</div>
    <nav>{items.map(item => {
      const Icon = item.icon
      return <button key={item.label} className={`nav-item ${page === item.label ? 'active' : ''}`} onClick={() => setPage(item.label)}>
        <Icon size={17}/><span>{item.label}</span>{item.label === 'Analyze' && <span className="nav-dot"/>}
      </button>
    })}</nav>
    <div className="sidebar-bottom">
      <div className="mission-card"><div className="mission-icon"><Telescope size={18}/></div><div><b>Mission control</b><span>{modelLoaded ? 'ML model ready' : 'Demo environment'}</span></div><span className={`status-dot ${modelLoaded ? 'online' : ''}`}/></div>
      <button className="nav-item muted" onClick={() => setPage('Data Sources')}><HelpCircle size={17}/>Documentation</button>
      <div className="sidebar-foot"><span>ASTRA v1.0.0</span><span>Built for exploration <Atom size={12}/></span></div>
    </div>
  </aside>
}
