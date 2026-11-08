import { useEffect, useMemo, useRef, useState } from 'react'
import { Activity, ArrowDownToLine, ArrowRight, ArrowUpRight, Atom, BadgeCheck, Bell, CheckCircle2, ChevronDown, CircleHelp, Clock3, CloudUpload, Cpu, Database, FileText, FlaskConical, Gauge, Info, Layers3, Menu, Orbit, Play, Radio, RefreshCw, Search, ShieldAlert, Sparkles, Telescope, Upload, X, Zap } from 'lucide-react'
import Sidebar from './components/Sidebar'
import LightCurve from './components/LightCurve'
import { getDemo, getHealth, getMetrics, predictFile } from './api'
import type { Health, Prediction } from './types'

type Page = 'Overview' | 'Explore' | 'Analyze' | 'Model Lab' | 'Data Sources'

const initialHealth: Health = { status: 'connecting', model_loaded: false, model_name: 'Checking…', cnn_available: false }

function StatCard({ label, value, note, icon: Icon }: { label: string; value: string; note: string; icon: typeof Activity }) {
  return <div className="stat-card"><div className="stat-top"><span>{label}</span><span className="stat-icon"><Icon size={17}/></span></div><strong>{value}</strong><small>{note}</small></div>
}

function App() {
  const [page, setPage] = useState<Page>('Overview')
  const [health, setHealth] = useState<Health>(initialHealth)
  const [result, setResult] = useState<Prediction | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [metrics, setMetrics] = useState<any>(null)
  const [mobileNav, setMobileNav] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealth({ ...initialHealth, status: 'offline', model_name: 'API unavailable' }))
    getMetrics().then(setMetrics).catch(() => setMetrics(null))
  }, [])

  const runDemo = async () => {
    setBusy(true); setError('')
    try { setResult(await getDemo()); setPage('Analyze') }
    catch (e) { setError(e instanceof Error ? e.message : 'Could not load demo.') }
    finally { setBusy(false) }
  }

  const onFile = async (file?: File) => {
    if (!file) return
    setBusy(true); setError('')
    try { setResult(await predictFile(file)); setPage('Analyze') }
    catch (e) { setError(e instanceof Error ? e.message : 'Analysis failed.') }
    finally { setBusy(false); if (fileRef.current) fileRef.current.value = '' }
  }

  const downloadSample = () => {
    const rows = ['time,flux']
    for (let i = 0; i < 900; i++) {
      const t = i * .02
      let f = 1 + (Math.sin(i * 12.9898) * 0.0012)
      for (const c of [3, 8, 13]) { const d = Math.abs(t-c); if (d < .16) f -= .012 * Math.max(0, 1-(d/.16)**2) }
      rows.push(`${t.toFixed(4)},${f.toFixed(6)}`)
    }
    const url = URL.createObjectURL(new Blob([rows.join('\n')], { type: 'text/csv' }))
    const a = document.createElement('a'); a.href = url; a.download = 'astra_sample_lightcurve.csv'; a.click(); URL.revokeObjectURL(url)
  }

  const nav = (p: Page) => { setPage(p); setMobileNav(false) }
  const title = page === 'Overview' ? 'Mission overview' : page === 'Model Lab' ? 'Model laboratory' : page === 'Data Sources' ? 'Data & methodology' : page === 'Explore' ? 'Target explorer' : 'Signal analysis'

  return <div className="app-shell">
    <div className={`mobile-overlay ${mobileNav ? 'show' : ''}`} onClick={() => setMobileNav(false)}/>
    <div className={`side-wrap ${mobileNav ? 'open' : ''}`}><Sidebar page={page} setPage={nav} modelLoaded={health.model_loaded}/></div>
    <main className="main-area">
      <header className="topbar">
        <div className="top-left"><button className="icon-btn mobile-menu" onClick={() => setMobileNav(!mobileNav)}><Menu size={19}/></button><div className="breadcrumb">ASTRA <span>/</span> {title}</div></div>
        <div className="top-actions"><div className="system-status"><span className={`status-dot ${health.status === 'online' ? 'online' : ''}`}/>{health.status === 'online' ? 'API connected' : health.status === 'offline' ? 'API offline' : 'Connecting'}</div><button className="icon-btn" title="Notifications"><Bell size={17}/></button><div className="avatar">A</div></div>
      </header>
      <div className="page-content">
        {error && <div className="error-banner"><ShieldAlert size={17}/>{error}<button onClick={() => setError('')}><X size={15}/></button></div>}
        {page === 'Overview' && <Overview health={health} metrics={metrics} onDemo={runDemo} busy={busy} onAnalyze={() => nav('Analyze')} />}
        {page === 'Explore' && <Explore onDemo={runDemo} busy={busy} />}
        {page === 'Analyze' && <Analyze result={result} busy={busy} onDemo={runDemo} onUpload={() => fileRef.current?.click()} onDownload={downloadSample}/>}
        {page === 'Model Lab' && <ModelLab health={health} metrics={metrics}/>}
        {page === 'Data Sources' && <DataSources/>}
      </div>
      <footer className="footer"><span>ASTRA EXOPLANET INTELLIGENCE</span><span>Research prototype · Not an astronomical confirmation</span></footer>
    </main>
    <input ref={fileRef} type="file" accept=".csv,text/csv" hidden onChange={e => onFile(e.target.files?.[0])}/>
  </div>
}

function PageHeading({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: React.ReactNode }) {
  return <div className="page-heading"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div>{action}</div>
}

function Overview({ health, metrics, onDemo, busy, onAnalyze }: { health: Health; metrics: any; onDemo: () => void; busy: boolean; onAnalyze: () => void }) {
  return <>
    <PageHeading eyebrow="SUNDAY, NOVEMBER 08 · MISSION CONTROL" title="Explore the unseen." description="A research workspace for identifying exoplanet-like transit signals in stellar light curves." action={<button className="button primary" onClick={onDemo} disabled={busy}><Play size={15}/>{busy ? 'Loading…' : 'Run demo analysis'}</button>}/>
    <section className="hero-panel">
      <div className="hero-orbit orbit-one"/><div className="hero-orbit orbit-two"/><div className="hero-planet"/>
      <div className="hero-copy"><div className="hero-kicker"><Sparkles size={14}/> AI-ASSISTED ASTRONOMY</div><h2>Every star has<br/>a story to tell.</h2><p>Analyse stellar brightness patterns, inspect transit-like events and explore the evidence behind every classification.</p><div className="hero-actions"><button className="button light" onClick={onAnalyze}>Analyse a light curve <ArrowRight size={15}/></button><span className="hero-caption"><Radio size={13}/> Kepler mission data workflow</span></div></div>
      <div className="hero-coordinate">RA 19h 12m 04s<br/>DEC +42° 18′ 11″</div>
    </section>
    <div className="section-row"><div><h2>System snapshot</h2><p>Live model and workspace status</p></div><span className="subtle-label">OVERVIEW</span></div>
    <div className="stats-grid">
      <StatCard label="Model status" value={health.model_loaded ? 'Trained' : 'Not trained'} note={health.model_loaded ? health.model_name : 'Demo mode available'} icon={Cpu}/>
      <StatCard label="CNN availability" value={health.cnn_available ? 'Available' : 'Not installed'} note="Optional deep learning model" icon={Layers3}/>
      <StatCard label="Test F1 score" value={metrics?.macro_f1 != null ? `${(metrics.macro_f1*100).toFixed(1)}%` : '—'} note={metrics?.available ? 'Held-out target-level test' : 'Train a model to populate'} icon={Gauge}/>
      <StatCard label="Data pipeline" value="Ready" note="CSV light-curve ingestion" icon={Activity}/>
    </div>
    <div className="two-column">
      <div className="panel feature-panel"><div className="panel-heading"><div><h3>From starlight to signal</h3><p>How ASTRA analyses an observation</p></div><span className="panel-icon"><Orbit size={18}/></span></div>
        <div className="pipeline">
          {[['01','OBSERVE','Kepler brightness measurements'],['02','PREPARE','Clean, normalize and inspect flux'],['03','CLASSIFY','Compare signal with learned patterns'],['04','EXPLAIN','Review measured evidence and caveats']].map((s,i)=><div className="pipeline-step" key={s[0]}><span className="step-num">{s[0]}</span><div><b>{s[1]}</b><small>{s[2]}</small></div>{i<3 && <ArrowRight className="step-arrow" size={15}/>}</div>)}
        </div>
      </div>
      <div className="panel quick-panel"><div className="panel-heading"><div><h3>Quick actions</h3><p>Start exploring the workspace</p></div><Zap size={18} className="accent-icon"/></div>
        <button className="quick-action" onClick={onDemo}><span className="quick-icon violet"><Play size={17}/></span><span><b>Try a demo analysis</b><small>Explore a simulated transit signal</small></span><ArrowUpRight size={16}/></button>
        <button className="quick-action" onClick={onAnalyze}><span className="quick-icon blue"><CloudUpload size={17}/></span><span><b>Upload a light curve</b><small>Analyse your own CSV measurements</small></span><ArrowUpRight size={16}/></button>
        <div className="notice"><Info size={15}/><span>Demo signals are simulated. Real predictions require a trained model and curated labels.</span></div>
      </div>
    </div>
  </>
}

function Explore({ onDemo, busy }: { onDemo: () => void; busy: boolean }) {
  return <>
    <PageHeading eyebrow="CATALOGUE WORKSPACE" title="Target explorer" description="Explore the target-analysis workflow. Live catalogue search is a planned integration; use the demo target to inspect the analysis experience."/>
    <div className="explore-grid">
      <div className="panel target-card"><div className="target-visual"><div className="target-star"/><div className="target-ring r1"/><div className="target-ring r2"/><span className="target-tag">DEMO TARGET</span></div><div className="target-info"><div className="eyebrow">KEPLER-LIKE SIGNAL · SYNTHETIC</div><h2>DEMO-KIC-001</h2><p>A simulated stellar light curve with recurring transit-like dips. This is not an actual NASA target.</p><div className="target-meta"><span><Clock3 size={14}/> 18-day sample</span><span><Activity size={14}/> 900 observations</span></div><button className="button primary full" onClick={onDemo} disabled={busy}>Inspect demo target <ArrowRight size={15}/></button></div></div>
      <div className="panel target-guide"><div className="panel-heading"><div><h3>What to look for</h3><p>Signals that make a transit interesting</p></div><Telescope size={19} className="accent-icon"/></div>
        {[['Transit depth','A small decrease in measured stellar brightness.'],['Repeatability','Similar dips recurring at a consistent interval.'],['Signal quality','A detectable event relative to measurement scatter.'],['False-positive checks','Odd/even differences or secondary eclipses may warrant review.']].map(([a,b],i)=><div className="guide-row" key={a}><span className="guide-index">0{i+1}</span><div><b>{a}</b><p>{b}</p></div></div>)}
        <div className="notice"><Info size={15}/><span>These are screening clues, not sufficient criteria to confirm a planet.</span></div>
      </div>
    </div>
  </>
}

function Analyze({ result, busy, onDemo, onUpload, onDownload }: { result: Prediction | null; busy: boolean; onDemo: () => void; onUpload: () => void; onDownload: () => void }) {
  return <>
    <PageHeading eyebrow="SIGNAL INTELLIGENCE" title="Analyse a light curve." description="Upload time-series flux measurements or run the simulated walkthrough to explore the analysis interface."/>
    <div className="upload-strip panel">
      <div className="upload-symbol"><CloudUpload size={22}/></div><div className="upload-text"><b>Import stellar observations</b><span>CSV format · Required columns: <code>time</code> and <code>flux</code> · Up to 15 MB</span></div>
      <div className="upload-actions"><button className="button secondary" onClick={onDownload}><ArrowDownToLine size={15}/>Sample CSV</button><button className="button primary" onClick={onUpload}><Upload size={15}/>Upload CSV</button></div>
    </div>
    {!result ? <div className="empty-state panel"><div className="empty-orbit"><Orbit size={34}/></div><h2>Your next discovery starts with a signal.</h2><p>No light curve has been analysed in this session. Load a simulated example or upload your own measurements.</p><button className="button primary" onClick={onDemo} disabled={busy}><Play size={15}/>{busy ? 'Preparing demo…' : 'Run simulated demo'}</button><small>Demo mode is clearly identified and does not use a trained model.</small></div> :
      <div className="analysis-layout">
        <div className="analysis-main">
          <div className="panel chart-panel"><div className="panel-heading"><div><div className="eyebrow">OBSERVATION PROFILE</div><h3>{result.target_name}</h3><p>Normalized stellar flux over observation time</p></div><span className={`mode-pill ${result.mode}`}>{result.mode === 'demo' ? 'SIMULATED' : 'MODEL INFERENCE'}</span></div><div className="chart-legend"><span><i/> Normalized flux</span><span>Reference baseline · 1.0</span></div><LightCurve points={result.points}/><div className="chart-axis-note"><span>OBSERVATION TIME</span><span>{result.points.length.toLocaleString()} measurements</span></div></div>
          <div className="panel evidence-panel"><div className="panel-heading"><div><h3>Evidence behind the analysis</h3><p>Measured signal characteristics and screening clues</p></div><Sparkles size={18} className="accent-icon"/></div><div className="evidence-list">{result.evidence.map((item,i)=><div className="evidence-item" key={item.title}><div className={`evidence-symbol ${item.status}`}>{item.status === 'supporting' ? <CheckCircle2 size={17}/> : item.status === 'caution' ? <ShieldAlert size={17}/> : <Info size={17}/>}</div><div className="evidence-copy"><b>{item.title}</b><p>{item.detail}</p></div><span className={`evidence-status ${item.status}`}>{item.status}</span></div>)}</div></div>
        </div>
        <aside className="analysis-side">
          <div className="panel prediction-panel"><div className="panel-heading"><div><div className="eyebrow">CLASSIFICATION RESULT</div><h3>Signal assessment</h3></div><Atom size={19} className="accent-icon"/></div><div className={`result-orb ${result.category === 'Planet candidate' ? 'candidate' : 'false'}`}><span>{Math.round(result.confidence*100)}<small>%</small></span><div className="orb-caption">MODEL SCORE</div></div><div className="result-label">{result.category}</div><p className="result-summary">{result.summary}</p><div className="result-divider"/><div className="result-meta"><span>Model</span><b>{result.model_name}</b></div><div className="result-meta"><span>Analysis mode</span><b>{result.mode === 'demo' ? 'Simulated demo' : 'Trained inference'}</b></div><div className="result-meta"><span>Measurements</span><b>{result.points.length.toLocaleString()}</b></div></div>
          <div className="panel feature-metrics"><div className="panel-heading"><div><h3>Signal metrics</h3><p>Extracted from this light curve</p></div></div>{[['Estimated dip depth','estimated_dip_depth'],['Robust scatter','robust_scatter'],['Periodicity proxy','periodicity_score'],['Signal-to-noise proxy','signal_to_noise'],['Dip fraction','dip_fraction']].map(([label,key])=><div className="metric-row" key={key}><span>{label}</span><b>{Number(result.features[key]).toFixed(4)}</b></div>)}</div>
          <div className="disclaimer"><ShieldAlert size={16}/><span>{result.disclaimer}</span></div>
        </aside>
      </div>}
  </>
}

function ModelLab({ health, metrics }: { health: Health; metrics: any }) {
  const available = metrics?.available
  const matrix = metrics?.confusion_matrix
  return <>
    <PageHeading eyebrow="MODEL EVALUATION" title="Model laboratory" description="Inspect the trained baseline model, evaluation metrics and experiment readiness."/>
    <div className="stats-grid">
      <StatCard label="Active baseline" value={health.model_loaded ? 'Random Forest' : 'Unavailable'} note="Feature-based classifier" icon={Cpu}/>
      <StatCard label="CNN model" value={health.cnn_available ? 'Installed' : 'Not trained'} note="Optional 1D CNN" icon={Layers3}/>
      <StatCard label="Training targets" value={available ? String(metrics.target_count) : '—'} note="Unique labelled targets" icon={Database}/>
      <StatCard label="Macro F1" value={available ? `${(metrics.macro_f1*100).toFixed(1)}%` : '—'} note="Held-out target-level test" icon={Gauge}/>
    </div>
    <div className="two-column lab-columns">
      <div className="panel"><div className="panel-heading"><div><h3>Evaluation metrics</h3><p>Test split results</p></div><FlaskConical size={18} className="accent-icon"/></div>{available ? <div className="metric-bars">{[['Accuracy',metrics.accuracy],['Macro precision',metrics.macro_precision],['Macro recall',metrics.macro_recall],['Macro F1',metrics.macro_f1]].map(([name,val])=><div className="bar-row" key={name as string}><div><span>{name}</span><b>{(Number(val)*100).toFixed(1)}%</b></div><div className="bar-track"><i style={{width:`${Math.max(0,Math.min(100,Number(val)*100))}%`}}/></div></div>)}</div> : <div className="empty-mini"><Database size={25}/><b>No evaluation report yet</b><span>Train the baseline model with a curated labelled dataset to populate this panel.</span></div>}</div>
      <div className="panel"><div className="panel-heading"><div><h3>Confusion matrix</h3><p>Rows = actual · Columns = predicted</p></div></div>{matrix ? <div className="confusion"><div/><b>PC</b><b>FP</b><b>PC</b><strong>{matrix[0][0]}</strong><strong>{matrix[0][1]}</strong><b>FP</b><strong>{matrix[1][0]}</strong><strong>{matrix[1][1]}</strong></div> : <div className="empty-mini"><Activity size={25}/><b>Awaiting model evaluation</b><span>Matrix will appear after training and testing.</span></div>}</div>
    </div>
    <div className="panel methodology-panel"><h3>Evaluation protocol</h3><div className="protocol-grid"><div><b>Target-level split</b><p>All observations belonging to one target stay in the same partition.</p></div><div><b>Class-aware metrics</b><p>Precision, recall and F1 complement accuracy when classes are imbalanced.</p></div><div><b>Scientific caution</b><p>Catalogue labels are imperfect proxies and model scores are not discovery probabilities.</p></div></div>{metrics?.note && <p className="metrics-note">{metrics.note}</p>}</div>
  </>
}

function DataSources() {
  return <>
    <PageHeading eyebrow="DATA PROVENANCE" title="Data & methodology." description="A transparent view of where the observations come from, how the model is trained and what its predictions mean."/>
    <div className="source-grid">
      <div className="panel source-card"><div className="source-icon"><Database size={20}/></div><div className="eyebrow">CATALOGUE & LABELS</div><h3>NASA Exoplanet Archive</h3><p>Kepler Objects of Interest catalogue and disposition metadata. Candidate and false-positive labels require careful interpretation.</p><a href="https://exoplanetarchive.ipac.caltech.edu/" target="_blank" rel="noreferrer">Open archive <ArrowUpRight size={14}/></a></div>
      <div className="panel source-card"><div className="source-icon"><Telescope size={20}/></div><div className="eyebrow">OBSERVATIONS</div><h3>MAST / Kepler</h3><p>Mission light curves contain time-stamped brightness measurements. The app accepts a prepared CSV with time and flux columns.</p><a href="https://archive.stsci.edu/missions-and-data/kepler" target="_blank" rel="noreferrer">Open MAST <ArrowUpRight size={14}/></a></div>
      <div className="panel source-card"><div className="source-icon"><Activity size={20}/></div><div className="eyebrow">DATA ACCESS</div><h3>Lightkurve</h3><p>Python toolkit for searching, downloading and inspecting Kepler light curves and other time-series observations.</p><a href="https://lightkurve.org/" target="_blank" rel="noreferrer">Open documentation <ArrowUpRight size={14}/></a></div>
    </div>
    <div className="panel methodology-panel"><h3>How the classification works</h3><div className="method-steps">{[['01','Input','A CSV containing observation time and stellar flux.'],['02','Preprocessing','Invalid samples are removed, time is sorted and flux is normalized.'],['03','Feature extraction','A compact set of signal descriptors is calculated.'],['04','Prediction','A trained Random Forest assigns PC or FP based on curated training labels.'],['05','Evidence summary','The app reports measured properties and screening cautions.']].map(([n,a,b])=><div className="method-step" key={n}><span>{n}</span><div><b>{a}</b><p>{b}</p></div></div>)}</div></div>
    <div className="notice large"><Info size={17}/><span><b>Scientific limitation:</b> ASTRA is an educational research prototype. The included feature heuristics are simplified. Candidate classification is not independent validation, and the evidence panel is not a causal explanation of the model's internal decision.</span></div>
  </>
}

export default App
