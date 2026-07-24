import { motion } from 'framer-motion'

const navItems = ['Trials', 'Memory', 'Docs']
const navVariants = {
  hidden: { opacity: 0, y: -12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
}

export default function Nav() {
  return (
    <motion.nav
      className="flex items-center justify-center py-6"
      variants={navVariants}
      initial="hidden"
      animate="visible"
    >
      <div
        className="inline-flex items-center gap-6 bg-ash px-5 py-2"
        style={{ borderRadius: '200px' }}
      >
        <span className="font-polysans text-[18px] tracking-[-0.02em] text-graphite">
          Clarity
        </span>
        {navItems.map((item) => (
          <a
            key={item}
            href="#"
            className="font-polysans text-[16px] tracking-[-0.02em] text-graphite px-3 py-2"
          >
            {item}
          </a>
        ))}
        <a
          href="#"
          className="font-polysans text-[16px] tracking-[-0.02em] text-slate px-3 py-2"
        >
          EN
        </a>
      </div>
    </motion.nav>
  )
}
