import ReactMarkdown from 'react-markdown'
import { useEffect, useRef, useState } from 'react'
import './App.css'
import {
  sendMessage,
  uploadDocument,
  getDocuments,
  deleteDocument,
} from './services/api'

type Source = {
  document: string
  page: number
}

type Message = {
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  showSources?: boolean
}

type DocumentInfo = {
  pages: number
  chunks: number
  indexed_at: string
}

function useCursorLight() {
  useEffect(() => {
    const root = document.documentElement

    const onMove = (e: PointerEvent) => {
      root.style.setProperty('--mx', `${e.clientX}px`)
      root.style.setProperty('--my', `${e.clientY}px`)
    }

    window.addEventListener('pointermove', onMove, { passive: true })
    return () => window.removeEventListener('pointermove', onMove)
  }, [])
}

function useCard(index: number) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    el.style.setProperty('--fx', ['-90px', '0px', '90px'][index % 3])
    el.style.setProperty('--d', `${(index % 3) * 0.09}s`)

    el.classList.add('pre')

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          el.classList.remove('pre')
          el.classList.add('in')
          observer.disconnect()
        }
      },
      {
        threshold: 0.01,
        rootMargin: '0px 0px 0px 0px',
      }
    )

    observer.observe(el)

    return () => observer.disconnect()
  }, [index])

  return ref
}



const FEATURES = [
  {
    title: 'Research conversations',
    description:
      'Ask questions across multiple uploaded research papers and explore answers through contextual, multi-turn conversations.',
    wide: true,
  },
  {
    title: 'Multi-paper synthesis',
    description:
      'Compare findings, identify similarities and contradictions, and connect insights across multiple research papers.',
    wide: true,
  },
  {
    title: 'Semantic retrieval',
    description:
      'Discover relevant passages using contextual meaning rather than relying only on exact keyword matches.',
  },
  {
    title: 'Verifiable citations',
    description:
      'Trace AI-generated answers to their original research papers, with page numbers and source excerpts.',
  },
  {
    title: 'AI-powered explanations',
    description:
      'Simplify complex academic concepts, technical terminology, and research findings into understandable explanations.',
  },
]

const SCREENSHOTS = [
  {
    src: '/screenshots/workspace.jpeg',
    title: 'Your workspace',
    description: 'Documents on the left, conversation on the right.',
  },
  {
    src: '/screenshots/landing.jpeg',
    title: 'Clean, focused interface',
    description: 'A distraction-free design built for research.',
  },
]

const REPO_URL = 'https://github.com/roshinioffcl/ResearchPilot-AI'

const DEV_URL = 'https://github.com/roshinioffcl'
const LINKEDIN_URL = 'https://www.linkedin.com/in/roshinioffcl'
const CONTACT_EMAIL = 'mailto:roshini.offcl8307@example.com'

const ENGINE_CODE = `def generate_answer(question, chunks, history):
    context = build_context(chunks)
    prompt = build_prompt(question, context, history)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    return response.text`

const STEPS = [
  {
    title: 'Upload your PDFs',
    description:
      'Add research papers in the workspace. Each file is read page by page.',
  },
  {
    title: 'Index by meaning',
    description:
      'Pages are split into chunks and indexed so passages can be found by meaning, not just keywords.',
  },
  {
    title: 'Ask a question',
    description:
      'Your question is rewritten using the chat history, so follow-ups like "explain more" still work.',
  },
  {
    title: 'Get a grounded answer',
    description:
      'Gemini answers using only the retrieved passages. Ask for sources to see the document and page.',
  },
]

function StepCard({
  index,
  title,
  description,
}: {
  index: number
  title: string
  description: string
}) {
  const ref = useCard(index)

  return (
    <div ref={ref} className="card step">
      <span className="step-num">{String(index + 1).padStart(2, '0')}</span>
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  )
}

type Tech = {
  name: string
  tag: string
  description: string
  color: string
  mark: string
}

const TECH_ROW_ONE: Tech[] = [
  {
    name: 'React',
    tag: 'Frontend',
    description: 'Component-based library powering the whole interface.',
    color: '#61dafb',
    mark: 'R',
  },
  {
    name: 'TypeScript',
    tag: 'Language',
    description: 'Typed JavaScript for safer, more maintainable code.',
    color: '#3178c6',
    mark: 'TS',
  },
  {
    name: 'Vite',
    tag: 'Tooling',
    description: 'Fast dev server and build tool for the frontend.',
    color: '#a78bfa',
    mark: 'V',
  },
  {
    name: 'React Markdown',
    tag: 'Rendering',
    description: 'Renders formatted AI answers with headings and lists.',
    color: '#35d0ba',
    mark: 'M',
  },
  {
    name: 'CSS3',
    tag: 'Styling',
    description: 'Custom styling, animations and the glowing grid theme.',
    color: '#38bdf8',
    mark: 'C',
  },
]

const TECH_ROW_TWO: Tech[] = [
  {
    name: 'Python',
    tag: 'Backend',
    description: 'Powers document processing and the answer pipeline.',
    color: '#facc15',
    mark: 'Py',
  },
  {
    name: 'Google Gemini',
    tag: 'AI model',
    description: 'Generates grounded answers from your retrieved passages.',
    color: '#60a5fa',
    mark: 'G',
  },
  {
    name: 'Semantic Search',
    tag: 'Retrieval',
    description: 'Finds relevant passages by meaning, not just keywords.',
    color: '#34d399',
    mark: 'S',
  },
  {
    name: 'python-dotenv',
    tag: 'Config',
    description: 'Keeps API keys in a .env file, out of the code.',
    color: '#f472b6',
    mark: 'E',
  },
  {
    name: 'Git & GitHub',
    tag: 'Workflow',
    description: 'Version control and open-source hosting for the project.',
    color: '#e5e7eb',
    mark: 'Gh',
  },
]

function Marquee({ items, reverse }: { items: Tech[]; reverse?: boolean }) {
  // Repeat the list so the track is always wider than the screen
  const repeated = Array.from({ length: 4 }).flatMap(() => items)

  return (
    <div className="marquee">
      <div className={`marquee-track${reverse ? ' reverse' : ''}`}>
        {repeated.map((tech, i) => (
          <div
            className="tech-card"
            key={`${tech.name}-${i}`}
            aria-hidden={i >= items.length}
            style={{ '--c': tech.color } as React.CSSProperties}
          >
            <div className="tech-top">
              <span className="tech-name">
                <i />
                {tech.name}
              </span>
              <span className="tech-tag">{tech.tag}</span>
            </div>

            <p>{tech.description}</p>

            <div className="tech-bottom">
              <span className="tech-icon">{tech.mark}</span>
              <span className="tech-line" />
            </div>

            <span className="tech-watermark" aria-hidden="true">
              {tech.mark}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

function FeatureCard({
  index,
  title,
  description,
  wide,
}: {
  index: number
  title: string
  description: string
  wide?: boolean
}) {
  const ref = useCard(index)

  return (
    <div ref={ref} className={`card${wide ? ' wide' : ''}`}>
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  )
}

function ScreenshotCard({
  index,
  src,
  title,
  description,
}: {
  index: number
  src: string
  title: string
  description: string
}) {
  const ref = useCard(index)

  return (
    <figure ref={ref as React.RefObject<HTMLElement>} className="card shot">
      <div className="shot-frame">
        <div className="shot-bar">
          <span /><span /><span />
        </div>
        <img src={src} alt={title} loading="lazy" />
      </div>
      <figcaption>
        <h3>{title}</h3>
        <p>{description}</p>
      </figcaption>
    </figure>
  )
}

export default function App() {
  useCursorLight()

  const fileInput = useRef<HTMLInputElement>(null)
  const chatMessagesRef = useRef<HTMLDivElement>(null)
  const [workspace, setWorkspace] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [question, setQuestion] = useState('')
  const [documents, setDocuments] = useState<Record<string, DocumentInfo>>({})
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')

  async function refreshDocuments() {
    const data = await getDocuments()
    setDocuments(data)
  }

  useEffect(() => {
    refreshDocuments().catch(() => {
      setError('Could not load your documents. Check your backend connection.')
    })
  }, [])

  useEffect(() => {
    const container = chatMessagesRef.current
    if (!container) return

    // Wait one frame so the markdown has finished rendering, then jump to the bottom
    const id = requestAnimationFrame(() => {
      container.scrollTop = container.scrollHeight
    })

    return () => cancelAnimationFrame(id)
  }, [messages, loading])

  async function handleUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (!file) return

    setUploading(true)
    setError('')

    try {
      await uploadDocument(file)
      await refreshDocuments()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Document upload failed.')
    } finally {
      setUploading(false)
      event.target.value = ''
    }
  }

  async function handleDelete(filename: string) {
    if (!window.confirm(`Delete ${filename}?`)) return

    try {
      await deleteDocument(filename)
      await refreshDocuments()
    } catch {
      setError('Could not delete this document.')
    }
  }

  async function handleSend() {
    const text = question.trim()
    if (!text || loading) return

    const previousMessages = messages
    setMessages(prev => [...prev, { role: 'user', content: text }])
    setQuestion('')
    setLoading(true)
    setError('')

    try {
      const history = previousMessages.map(({ role, content }) => ({
        role,
        content,
      }))

      const data = await sendMessage(text, history)

      const wantsSources =
        /\b(source|sources|citation|citations|references|reference|page number|which page|where did you get)\b/i.test(
          text
        )

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: data.answer,
          sources: data.sources ?? [],
          showSources: wantsSources,
        },
      ])
    } catch {
      setError('Could not get an answer. Check your backend connection.')
    } finally {
      setLoading(false)
    }
  }

  function startNewChat() {
    setMessages([])
    setQuestion('')
    setError('')
  }

  return (
    <>
      <div className="fx fx-grid" />
      <div className="fx fx-hot" />
      <div className="fx fx-glow" />

      <div className="pulse" style={{ top: 168 }} />
      <div className="pulse" style={{ top: 504, animationDelay: '-3s' }} />
      <div className="pulse" style={{ top: 840, animationDelay: '-5s' }} />

      <div className="app">
        <div className="wrap">
          <nav className="nav">
            <div className="logo">
              <i />
              ResearchPilot AI
            </div>

            {workspace ? (
              <button className="btn" onClick={() => setWorkspace(false)}>
                ← Home
              </button>
            ) : (
              <a href="#features">Features</a>
            )}
          </nav>

          {!workspace ? (
            <>
              <header className="hero">
                <p className="eyebrow">YOUR AI RESEARCH ASSISTANT</p>
                <h1>Research smarter. Discover more.</h1>
                <p className="sub">
                  Upload your research papers, ask questions, and get
                  AI-powered answers grounded in your documents.
                </p>

                <div className="hero-actions">
                  <button
                    className="btn main workspace-btn"
                    onClick={() => setWorkspace(true)}
                  >
                    Open Workspace <span>→</span>
                  </button>

                  <a className="btn explore-btn" href="#features">
                    Explore Features <span>↓</span>
                  </a>
                </div>
              </header>

              <section id="features">
                <h2>Research at the speed of thought.</h2>
                <p className="lede">
                  Everything you need to synthesize, analyze, and cite from thousands
                  of academic papers in a secure, local-first environment.
                </p>

                <div className="cards">
                  {FEATURES.map((feature, index) => (
                    <FeatureCard
                      key={feature.title}
                      index={index}
                      title={feature.title}
                      description={feature.description}
                      wide={feature.wide}
                    />
                  ))}
                </div>
              </section>

              {/* CTA panel now sits directly below features */}
              <section id="try-it" className="cta">
                <div className="cta-bg" aria-hidden="true" />

                <div className="cta-copy">
                  <p className="eyebrow">YOUR TURN</p>
                  <h2>See what your papers can tell you.</h2>
                  <p className="lede">
                    Upload a research PDF, ask a question, and get a grounded answer
                    in seconds. This is the workspace I built.
                  </p>

                  <button
                    className="btn main workspace-btn"
                    onClick={() => {
                      setWorkspace(true)
                      window.scrollTo({ top: 0 })
                    }}
                  >
                    Open Workspace <span>→</span>
                  </button>
                </div>

                <div className="cta-shot">
                  <div className="shot-frame">
                    <div className="shot-bar">
                      <span /><span /><span />
                    </div>
                    <img src="/screenshots/answer.jpeg" alt="ResearchPilot answering a question" loading="lazy" />
                  </div>
                </div>
              </section>

              <section id="how-it-works">
                <h2>How it works.</h2>
                <p className="lede">
                  From a pile of PDFs to a sourced answer in four steps.
                </p>

                <div className="steps">
                  {STEPS.map((step, index) => (
                    <StepCard
                      key={step.title}
                      index={index}
                      title={step.title}
                      description={step.description}
                    />
                  ))}
                </div>
              </section>

              <section id="showcase">
                <h2>See it in action.</h2>
                <p className="lede">
                  A look at the ResearchPilot workspace, built for focused research.
                </p>

                <div className="shots">
                  {SCREENSHOTS.map((shot, index) => (
                    <ScreenshotCard
                      key={shot.title}
                      index={index}
                      src={shot.src}
                      title={shot.title}
                      description={shot.description}
                    />
                  ))}
                </div>
              </section>

              <section id="stack" className="stack">
                <h2>Built with.</h2>
                <p className="lede">The tools and technologies behind ResearchPilot.</p>

                <Marquee items={TECH_ROW_ONE} />
                <Marquee items={TECH_ROW_TWO} reverse />
              </section>

              <section id="open-source" className="oss">
                <div className="oss-lily" aria-hidden="true" />

                <h2>Open Source Foundation.</h2>
                <p className="lede">
                  ResearchPilot is built for researchers. Explore the full-stack
                  architecture and contribute to it.
                </p>

                <div className="oss-grid">
                  <div className="oss-card oss-engine">
                    <div className="oss-bar">
                      <span /><span /><span />
                      <small>ResearchPilot-AI / answer_generator.py</small>
                    </div>
                    <pre className="oss-code">{ENGINE_CODE}</pre>
                    <div className="oss-engine-text">
                      <h3>Core Engine Architecture.</h3>
                      <p>Semantic retrieval, grounded prompts and page-level sources.</p>
                      <a
                        className="btn main"
                        href={REPO_URL}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Explore the Code →
                      </a>
                    </div>
                  </div>

                  <div className="oss-card oss-local">
                    <p className="oss-label">LOCAL-FIRST</p>
                    <h3>Your papers stay yours.</h3>
                    <p>Documents are indexed on your own backend, not a third-party library.</p>
                    <div className="oss-badges">
                      <span>PDF upload</span>
                      <span>Page references</span>
                    </div>
                  </div>

                  <div className="oss-card oss-fleet">
                    <h3>Join the Fleet.</h3>
                    <p>Submit PRs and improve retrieval together.</p>
                    <pre className="oss-term">{`$ git clone ResearchPilot-AI
$ npm install`}</pre>
                    <a
                      className="oss-link"
                      href={REPO_URL}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      View Repo ›
                    </a>
                  </div>

                  <div className="oss-card oss-trust">
                    <p className="oss-label">TRANSPARENT BY DESIGN</p>
                    <h3>No black boxes.</h3>
                    <p>
                      Every answer is grounded in your uploaded documents, with the
                      source pages available on request.
                    </p>
                    <div className="oss-badges">
                      <span>Grounded answers</span>
                      <span>Open code</span>
                    </div>
                  </div>
                </div>
              </section>
            </>
          ) : (
            <main className="workspace">
              <header className="workspace-header">
                <div>
                  <p className="eyebrow">RESEARCHPILOT AI</p>
                  <h1>Your workspace.</h1>
                  <p className="sub">
                    Your papers, your questions, your research.
                  </p>
                </div>
                <button className="btn" onClick={startNewChat}>
                  + New chat
                </button>
              </header>

              <div className="workspace-layout">
                <aside className="document-panel">
                  <div className="document-heading">
                    <h3>Your documents</h3>
                    <span>{Object.keys(documents).length}</span>
                  </div>

                  <button
                    className="btn upload-btn"
                    onClick={() => fileInput.current?.click()}
                    disabled={uploading}
                  >
                    {uploading ? 'Uploading...' : '+ Upload PDF'}
                  </button>

                  <input
                    ref={fileInput}
                    type="file"
                    accept="application/pdf"
                    hidden
                    onChange={handleUpload}
                  />

                  <div className="document-list">
                    {Object.entries(documents).map(([filename, info]) => (
                      <div className="document-item" key={filename}>
                        <div>
                          <p className="document-name">{filename}</p>
                          <small>{info.pages} pages · {info.chunks} chunks</small>
                        </div>
                        <button
                          className="delete-btn"
                          onClick={() => handleDelete(filename)}
                          title={`Delete ${filename}`}
                        >
                          ×
                        </button>
                      </div>
                    ))}

                    {Object.keys(documents).length === 0 && (
                      <p className="empty-docs">
                        No documents yet. Upload a research PDF to get started.
                      </p>
                    )}
                  </div>
                </aside>

                <section className="chat-panel">
                  <div className="chat-messages" ref={chatMessagesRef}>
                    {messages.length === 0 && (
                      <div className="chat-welcome">
                        <h2>What are we researching today?</h2>
                        <p>
                          Ask a question about the documents in your library.
                        </p>
                      </div>
                    )}

                    {messages.map((message, index) => (
                      <div
                        className={`message ${message.role}`}
                        key={index}
                      >
                        <div className="message-role">
                          {message.role === 'user' ? 'You' : 'ResearchPilot'}
                        </div>
                        <div className="message-content">
                          <ReactMarkdown>{message.content}</ReactMarkdown>
                        </div>

                        {message.showSources &&
                          message.sources &&
                          message.sources.length > 0 && (
                            <div className="message-sources">
                              <strong>Sources</strong>
                              {message.sources.map((source, i) => (
                                <span key={`${source.document}-${source.page}-${i}`}>
                                  {source.document} · Page {source.page}
                                </span>
                              ))}
                            </div>
                          )}
                      </div>
                    ))}

                    {loading && (
                      <p className="answer dots" aria-live="polite">
                        <span /><span /><span />
                      </p>
                    )}
                  </div>

                  {error && <p className="error" role="alert">{error}</p>}

                  <div className="chat-input">
                    <input
                      value={question}
                      onChange={e => setQuestion(e.target.value)}
                      placeholder="Ask something about your research..."
                      onKeyDown={e => e.key === 'Enter' && handleSend()}
                    />
                    <button
                      className="btn main"
                      onClick={handleSend}
                      disabled={loading || !question.trim()}
                    >
                      {loading ? 'Thinking...' : 'Ask →'}
                    </button>
                  </div>
                  <p className="chat-note">
                    AI-generated responses can make mistakes. Verify important information.
                  </p>
                </section>
              </div>
            </main>
          )}

          {workspace ? (
            <footer className="foot">
              © 2026 ResearchPilot AI · Your research, made easier.
            </footer>
          ) : (
            <footer className="site-footer">
              <div className="sf-brand">
                <span className="sf-logo">
                  <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M9 4a3 3 0 0 0-3 3v1a3 3 0 0 0-2 2.8A3 3 0 0 0 5.5 14 3 3 0 0 0 9 19h1V4Z" />
                    <path d="M15 4h-1v15h1a3 3 0 0 0 3.5-5A3 3 0 0 0 20 10.800 3 3 0 0 0 18 8V7a3 3 0 0 0-3-3Z" />
                  </svg>
                </span>
                <strong>ResearchPilot AI</strong>
              </div>

              <p className="sf-tag">
                Your AI-powered companion for exploring research papers, discovering
                insights, and accelerating knowledge.
              </p>

              <div className="sf-divider" />

              <div className="sf-cols">
                <div>
                  <h4>Product</h4>
                  <a href="#features">Features</a>
                  <a href="#how-it-works">How it works</a>
                  <a href={REPO_URL} target="_blank" rel="noopener noreferrer">Documentation</a>
                </div>
                <div>
                  <h4>Connect</h4>
                  <a href={REPO_URL} target="_blank" rel="noopener noreferrer">GitHub</a>
                  <a href={DEV_URL} target="_blank" rel="noopener noreferrer">Developer</a>
                  <a href={CONTACT_EMAIL}>Contact</a>
                </div>
              </div>

              <div className="sf-divider" />

              <div className="sf-bottom">
                <span>© 2026 ResearchPilot AI</span>
                <div className="sf-icons">
                  <a href={REPO_URL} target="_blank" rel="noopener noreferrer" aria-label="GitHub">
                    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M15 22v-4a4.800 4.800 0 0 0-1-3.500c3 0 6-2 6-5.500.080-1.250-.270-2.480-1-3.500.280-1.150.280-2.350 0-3.500 0 0-1 0-3 1.500-2.640-.5-5.360-.5-8 0C6 2 5 2 5 2c-.3 1.150-.3 2.350 0 3.500A5.400 5.400 0 0 0 4 9c0 3.500 3 5.500 6 5.500-.390.490-.680 1.050-.850 1.650-.170.600-.220 1.230-.150 1.850v4" /><path d="M9 18c-4.510 2-5-2-7-2" /></svg>
                  </a>
                  <a href={LINKEDIN_URL} target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
                    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-4 0v7h-4v-7a6 6 0 0 1 6-6Z" /><rect width="4" height="12" x="2" y="9" /><circle cx="4" cy="4" r="2" /></svg>
                  </a>
                  <a href={CONTACT_EMAIL} aria-label="Email">
                    <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><rect width="20" height="16" x="2" y="4" rx="2" /><path d="m22 7-8.970 5.700a1.940 1.940 0 0 1-2.060 0L2 7" /></svg>
                  </a>
                </div>
              </div>

              <p className="sf-built">Research smarter. Discover deeper. Think beyond papers.</p>
            </footer>
          )}
        </div>
      </div>
    </>
  )
}