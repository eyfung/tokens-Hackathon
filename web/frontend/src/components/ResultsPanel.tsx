import { motion } from 'framer-motion'
import { AlertCircle, CheckCircle, BarChart3, Users } from 'lucide-react'

interface Result {
  power: number
  advice?: string
  sample_size?: number
  ci_lower?: number
  ci_upper?: number
}

interface ResultsPanelProps {
  result: Result | null
  loading: boolean
}

export default function ResultsPanel({ result, loading }: ResultsPanelProps) {
  if (loading) {
    return (
      <div className="bg-ash p-10" style={{ borderRadius: '6px 0px 0px' }}>
        <h3 className="font-polysans text-[18px] tracking-[-0.02em] text-graphite mb-5">
          Results
        </h3>
        <motion.div
          className="flex flex-col items-center justify-center py-10 text-slate"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}
          >
            <BarChart3 size={32} strokeWidth={1.5} className="text-slate" />
          </motion.div>
          <p className="mt-4 text-steel">Running 10,000 virtual trials...</p>
          <p className="text-[14px] mt-2">Querying Actian for similar designs</p>
        </motion.div>
      </div>
    )
  }

  if (!result) {
    return (
      <div className="bg-ash p-10" style={{ borderRadius: '6px 0px 0px' }}>
        <h3 className="font-polysans text-[18px] tracking-[-0.02em] text-graphite mb-5">
          Results
        </h3>
        <p className="text-slate">Run a simulation to see results here.</p>
      </div>
    )
  }

  const viable = result.power >= 0.80

  return (
    <motion.div
      className="bg-ash p-10"
      style={{ borderRadius: '6px 0px 0px' }}
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4 }}
    >
      <h3 className="font-polysans text-[18px] tracking-[-0.02em] text-graphite mb-5">
        Results
      </h3>

      <div className="grid grid-cols-2 gap-5 mb-5">
        <div className="text-center">
          <div className="font-polysans text-[32px] tracking-[-0.02em] text-graphite leading-none">
            {(result.power * 100).toFixed(0)}%
          </div>
          <div className="text-[14px] text-slate mt-2">Statistical Power</div>
        </div>
        <div className="text-center">
          <div className="flex justify-center">
            {viable ? (
              <CheckCircle size={32} strokeWidth={1.5} className="text-ember-orange" />
            ) : (
              <AlertCircle size={32} strokeWidth={1.5} className="text-brass" />
            )}
          </div>
          <div className="text-[14px] text-slate mt-2">
            {viable ? 'Design viable' : 'Underpowered'}
          </div>
        </div>
      </div>

      <hr className="border-t border-mist my-5" />

      <p className="text-steel text-[15px] mb-5">
        {result.advice || 'Design meets the target power threshold.'}
      </p>

      <div className="flex gap-3">
        {result.sample_size && (
          <span className="inline-flex items-center gap-1.5 font-polysans text-[13px] tracking-[-0.02em] text-graphite bg-fog px-3.5 py-1 rounded-[20px]">
            <Users size={14} strokeWidth={1.5} /> n={result.sample_size}
          </span>
        )}
        {result.ci_lower !== undefined && result.ci_upper !== undefined && (
          <span className="inline-flex items-center gap-1.5 font-polysans text-[13px] tracking-[-0.02em] text-brass bg-fog px-3.5 py-1 rounded-[20px]">
            <BarChart3 size={14} strokeWidth={1.5} />
            CI: {(result.ci_lower * 100).toFixed(1)}&ndash;{(result.ci_upper * 100).toFixed(1)}%
          </span>
        )}
      </div>
    </motion.div>
  )
}
