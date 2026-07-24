import { motion } from 'framer-motion'
import { Activity, Database, Gauge } from 'lucide-react'

const cards = [
  {
    icon: Activity,
    title: 'Statistical Power',
    value: '87%',
    label: 'Across 10K virtual trials',
  },
  {
    icon: Database,
    title: 'Designs in Memory',
    value: '10',
    label: 'Pre-loaded disease areas',
  },
  {
    icon: Gauge,
    title: 'Feasibility Speed',
    value: '80%',
    label: 'Faster than manual methods',
  },
]

const cardVariants = {
  hidden: { opacity: 0, x: 40 },
  visible: (i: number) => ({
    opacity: 1,
    x: 0,
    transition: { duration: 0.5, delay: 0.15 * i, ease: 'easeOut' },
  }),
}

export default function HeroCards() {
  return (
    <div className="flex flex-col gap-4">
      {cards.map((card, i) => (
        <motion.div
          key={card.title}
          className="bg-canvas-white rounded-[20px] p-10 border border-mist"
          style={i === 1 ? { marginLeft: '40px' } : i === 2 ? { marginLeft: '20px' } : {}}
          variants={cardVariants}
          custom={i}
          initial="hidden"
          animate="visible"
          whileHover={{ y: -4, transition: { duration: 0.2 } }}
        >
          <div className="flex items-center gap-3 mb-4">
            <card.icon size={18} className="text-slate" strokeWidth={1.5} />
            <span className="font-polysans text-[18px] tracking-[-0.02em] text-graphite">
              {card.title}
            </span>
          </div>
          <div className="font-polysans text-[40px] tracking-[-0.02em] text-graphite leading-none">
            {card.value}
          </div>
          <div className="text-[14px] text-slate mt-2">{card.label}</div>
        </motion.div>
      ))}
    </div>
  )
}
