import { motion } from 'framer-motion'
import { Cpu, Network, Database as DatabaseIcon, MessageSquare, Box, Repeat } from 'lucide-react'

const partners = [
  { name: 'DeepMind', icon: Cpu },
  { name: 'Pioneer', icon: Box },
  { name: 'Actian', icon: DatabaseIcon },
  { name: 'Band', icon: MessageSquare },
  { name: 'Guild AI', icon: Network },
  { name: 'Replay', icon: Repeat },
]

const container = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08, delayChildren: 0.3 } },
}

const item = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: { opacity: 1, scale: 1 },
}

export default function PartnerStrip() {
  return (
    <div className="text-center py-10">
      <p className="font-polysans text-[13px] tracking-[-0.02em] text-brass mb-5">
        Built with
      </p>
      <motion.div
        className="flex justify-center flex-wrap gap-5"
        variants={container}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
      >
        {partners.map((p) => (
          <motion.span
            key={p.name}
            className="font-polysans text-[15px] tracking-[-0.02em] text-graphite inline-flex items-center gap-2"
            variants={item}
          >
            <p.icon size={16} strokeWidth={1.5} className="text-slate" />
            {p.name}
          </motion.span>
        ))}
      </motion.div>
    </div>
  )
}
