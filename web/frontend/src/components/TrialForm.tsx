import { useState } from 'react'
import { motion } from 'framer-motion'
import { Play, Info } from 'lucide-react'

interface TrialParams {
  disease: string
  endpoint: string
  effect: number
  variability: number
  n: number
}

interface TrialFormProps {
  onRun: (params: TrialParams) => void
  loading: boolean
}

export default function TrialForm({ onRun, loading }: TrialFormProps) {
  const [params, setParams] = useState<TrialParams>({
    disease: 'Hypertension',
    endpoint: 'Systolic BP Reduction (mmHg)',
    effect: 10,
    variability: 15,
    n: 100,
  })

  const update = (field: keyof TrialParams, value: string | number) => {
    setParams((prev) => ({ ...prev, [field]: value }))
  }

  return (
    <motion.div
      className="bg-ash p-10"
      style={{ borderRadius: '6px 0px 0px' }}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4 }}
    >
      <h3 className="font-polysans text-[18px] tracking-[-0.02em] text-graphite mb-5">
        Trial Parameters
      </h3>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-[14px] font-medium text-graphite mb-2">
            Disease Area
          </label>
          <input
            value={params.disease}
            onChange={(e) => update('disease', e.target.value)}
            className="w-full px-3 py-2.5 bg-canvas-white border border-mist font-inter text-[15px] text-graphite focus:outline-none focus:border-ember-orange"
            style={{ borderRadius: 0 }}
          />
        </div>
        <div>
          <label className="block text-[14px] font-medium text-graphite mb-2">
            Primary Endpoint
          </label>
          <input
            value={params.endpoint}
            onChange={(e) => update('endpoint', e.target.value)}
            className="w-full px-3 py-2.5 bg-canvas-white border border-mist font-inter text-[15px] text-graphite focus:outline-none focus:border-ember-orange"
            style={{ borderRadius: 0 }}
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mb-4">
        <div>
          <label className="block text-[14px] font-medium text-graphite mb-2">
            Treatment Effect
          </label>
          <input
            type="number"
            value={params.effect}
            onChange={(e) => update('effect', parseFloat(e.target.value) || 0)}
            min={0}
            step={0.5}
            className="w-full px-3 py-2.5 bg-canvas-white border border-mist font-inter text-[15px] text-graphite focus:outline-none focus:border-ember-orange"
            style={{ borderRadius: 0 }}
          />
        </div>
        <div>
          <label className="block text-[14px] font-medium text-graphite mb-2">
            Std Deviation
          </label>
          <input
            type="number"
            value={params.variability}
            onChange={(e) => update('variability', parseFloat(e.target.value) || 0)}
            min={1}
            step={0.5}
            className="w-full px-3 py-2.5 bg-canvas-white border border-mist font-inter text-[15px] text-graphite focus:outline-none focus:border-ember-orange"
            style={{ borderRadius: 0 }}
          />
        </div>
        <div>
          <label className="block text-[14px] font-medium text-graphite mb-2">
            Patients per Arm
          </label>
          <input
            type="number"
            value={params.n}
            onChange={(e) => update('n', parseInt(e.target.value) || 0)}
            min={10}
            step={10}
            className="w-full px-3 py-2.5 bg-canvas-white border border-mist font-inter text-[15px] text-graphite focus:outline-none focus:border-ember-orange"
            style={{ borderRadius: 0 }}
          />
        </div>
      </div>

      <div className="bg-ivory p-4 mb-5 rounded-[3px]">
        <div className="flex items-center gap-2 mb-1">
          <Info size={14} className="text-slate" strokeWidth={1.5} />
          <span className="font-polysans text-[14px] tracking-[-0.02em] text-graphite">
            How it works
          </span>
        </div>
        <p className="text-[14px] text-steel">
          The simulation runs thousands of virtual trials to estimate statistical
          power. The agent checks Actian memory for similar past designs, runs the
          simulation engine, and stores the result so it learns for next time.
        </p>
      </div>

      <motion.button
        onClick={() => onRun(params)}
        disabled={loading}
        className="w-full bg-graphite text-canvas-white font-polysans text-[16px] tracking-[-0.02em] px-5 py-2.5 flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
        style={{ borderRadius: 0 }}
        whileHover={{ opacity: 0.85 }}
        whileTap={{ scale: 0.98 }}
      >
        <Play size={16} strokeWidth={1.5} />
        {loading ? 'Simulating...' : 'Run Simulation'}
      </motion.button>
    </motion.div>
  )
}
