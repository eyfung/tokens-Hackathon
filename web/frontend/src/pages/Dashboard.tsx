import { useState } from 'react'
import { motion } from 'framer-motion'
import { FlaskConical } from 'lucide-react'
import TrialForm from '../components/TrialForm'
import ResultsPanel from '../components/ResultsPanel'

interface TrialParams {
  disease: string
  endpoint: string
  effect: number
  variability: number
  n: number
}

interface SimulationResult {
  power: number
  advice?: string
  sample_size?: number
  ci_lower?: number
  ci_upper?: number
}

export default function Dashboard() {
  const [result, setResult] = useState<SimulationResult | null>(null)
  const [loading, setLoading] = useState(false)

  const handleRun = async (params: TrialParams) => {
    setLoading(true)
    setResult(null)

    try {
      const res = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      })
      const data: SimulationResult = await res.json()
      setResult(data)
    } catch {
      setResult({
        power: 0,
        advice: 'Error connecting to simulation backend. Ensure the API server is running.',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-[1200px] mx-auto px-6">
      {/* Header */}
      <motion.div
        className="flex items-center justify-between py-6"
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <span className="font-polysans text-[18px] tracking-[-0.02em] text-graphite">
          Clarity
        </span>
        <div
          className="inline-flex items-center gap-4 bg-ash px-4 py-1"
          style={{ borderRadius: '200px' }}
        >
          <a href="/" className="font-polysans text-[16px] tracking-[-0.02em] text-graphite px-3 py-2">
            Design
          </a>
          <a href="#" className="font-polysans text-[16px] tracking-[-0.02em] text-slate px-3 py-2">
            Memory
          </a>
          <a href="#" className="font-polysans text-[16px] tracking-[-0.02em] text-slate px-3 py-2">
            EN
          </a>
        </div>
      </motion.div>

      <hr className="border-t border-mist" />

      {/* Title */}
      <motion.div
        className="py-10"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
      >
        <h1 className="font-polysans text-[32px] tracking-[-0.64px] text-graphite mb-2">
          Trial Design Agent
        </h1>
        <p className="font-inter text-[18px] leading-[1.25] text-slate">
          Enter parameters below. The agent simulates thousands of virtual
          trials, checks against stored memory, and recommends the optimal design.
        </p>
      </motion.div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        <TrialForm onRun={handleRun} loading={loading} />
        <ResultsPanel result={result} loading={loading} />
      </div>

      {/* Footer */}
      <div className="text-center py-10 text-[13px] text-slate">
        <p>Clarity — tokens Self-Evolving Agents Hackathon 2026</p>
      </div>
    </div>
  )
}
