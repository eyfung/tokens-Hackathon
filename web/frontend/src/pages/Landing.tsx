import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import Nav from '../components/Nav'
import HeroCards from '../components/HeroCards'
import PartnerStrip from '../components/PartnerStrip'

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, delay: 0.15 * i, ease: 'easeOut' },
  }),
}

const problemCards = [
  { title: 'Months per design', body: 'A single clinical trial design requires weeks of manual simulation work by scarce biostatisticians. Getting it wrong means starting over.' },
  { title: 'Dollars at risk', body: 'A failed Phase III trial can cost $100M+. Poor trial design is a leading cause of failure.' },
  { title: 'Excluded teams', body: 'Small biotechs and academic researchers cannot afford dedicated biostatisticians. Good trial design is a luxury.' },
]

const agentCards = [
  { title: 'Searches memory', body: 'Before running a single simulation, the agent queries Actian for similar past designs — diseases, endpoints, sample sizes, outcomes.' },
  { title: 'Simulates patients', body: 'Using Pioneer and DeepMind, it generates thousands of virtual patient populations and evaluates statistical power.' },
  { title: 'Escalates to you', body: 'If the design is underpowered, it opens a Band room, explains the risks, and suggests concrete fixes.' },
]

const stats = [
  { value: '10', label: 'Pre-loaded disease areas' },
  { value: '10K', label: 'Virtual trials per design' },
  { value: '80%', label: 'Faster feasibility' },
  { value: '∞', label: 'Self-evolving' },
]

export default function Landing() {
  return (
    <div>
      <Nav />

      {/* Hero */}
      <div className="max-w-[1200px] mx-auto px-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center py-20">
          <motion.div
            className="hero-text"
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            custom={0}
          >
            <h1 className="font-polysans text-[66px] leading-[0.91] tracking-[-1.32px] text-graphite mb-5">
              Trial design.<br />Evolving.
            </h1>
            <p className="font-inter text-[18px] leading-[1.25] text-steel mb-9 max-w-[540px]">
              A self-evolving agent that compresses clinical trial feasibility
              analysis from weeks to minutes. Simulate thousands of virtual
              patients, find optimal sample sizes, and watch the agent learn
              from every design.
            </p>
            <div className="flex gap-3 items-center">
              <a
                href="/dashboard"
                className="inline-flex items-center gap-2 bg-graphite text-canvas-white font-polysans text-[16px] tracking-[-0.02em] px-5 py-2.5"
                style={{ borderRadius: 0 }}
              >
                Launch Simulator
                <ArrowRight size={16} strokeWidth={1.5} />
              </a>
              <a
                href="#"
                className="inline-flex items-center font-polysans text-[16px] tracking-[-0.02em] text-graphite px-5 py-2.5 border border-graphite"
                style={{ borderRadius: 0 }}
              >
                How it works
              </a>
            </div>
          </motion.div>

          <HeroCards />
        </div>
      </div>

      <PartnerStrip />

      {/* Problem Section */}
      <div className="bg-ash py-20">
        <div className="max-w-[1200px] mx-auto px-6">
          <h2 className="font-polysans text-[40px] tracking-[-0.8px] text-graphite mb-9">
            The problem
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {problemCards.map((card, i) => (
              <motion.div
                key={card.title}
                className={i === 0 ? 'bg-ash p-10' : 'bg-ash p-10 rounded-[8px]'}
                style={i === 0 ? { borderRadius: '6px 0px 0px' } : {}}
                variants={fadeUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                custom={i}
              >
                <h3 className="font-inter text-[18px] leading-[1.25] text-graphite mb-4">
                  {card.title}
                </h3>
                <p className="text-steel text-[15px]">{card.body}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Agent Section */}
      <div className="py-20">
        <div className="max-w-[1200px] mx-auto px-6">
          <h2 className="font-polysans text-[40px] tracking-[-0.8px] text-graphite mb-9">
            The agent
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {agentCards.map((card, i) => (
              <motion.div
                key={card.title}
                className={i === 0 ? 'bg-ash p-10' : 'bg-ash p-10 rounded-[8px]'}
                style={i === 0 ? { borderRadius: '6px 0px 0px' } : {}}
                variants={fadeUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                custom={i}
              >
                <h3 className="font-inter text-[18px] leading-[1.25] text-graphite mb-4">
                  {card.title}
                </h3>
                <p className="text-steel text-[15px]">{card.body}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-ash py-20">
        <div className="max-w-[1200px] mx-auto px-6">
          <h2 className="font-polysans text-[40px] tracking-[-0.8px] text-graphite mb-9">
            By the numbers
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
            {stats.map((stat, i) => (
              <motion.div
                key={stat.label}
                className="bg-canvas-white rounded-[20px] p-10 border border-mist text-center"
                variants={fadeUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
                custom={i}
              >
                <div className="font-polysans text-[40px] tracking-[-0.02em] text-graphite leading-none">
                  {stat.value}
                </div>
                <div className="text-[14px] text-slate mt-2">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Get Started */}
      <div className="py-20 text-center">
        <div className="max-w-[1200px] mx-auto px-6">
          <h2 className="font-polysans text-[40px] tracking-[-0.8px] text-graphite mb-5">
            Get started
          </h2>
          <p className="font-inter text-[18px] leading-[1.25] text-steel mb-9 max-w-[600px] mx-auto">
            Clone the repo, install dependencies, and launch the agent. No API
            keys required — runs fully offline with mock data.
          </p>
          <pre className="bg-ash p-5 rounded-[3px] font-mono text-[14px] text-graphite max-w-[560px] mx-auto text-left overflow-x-auto">
git clone https://github.com/eyfung/tokens-Hackathon.git
cd tokens-Hackathon
pip install -r requirements.txt
streamlit run web/app.py
          </pre>
          <p className="text-[14px] text-slate mt-5">
            Add your Pioneer / DeepMind / Band keys to config/partners.yaml for live inference.
          </p>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center py-10 text-[13px] text-slate border-t border-mist">
        <div className="flex justify-center gap-5 mb-3">
          <a href="#" className="text-[13px] text-slate">GitHub</a>
          <a href="#" className="text-[13px] text-slate">Documentation</a>
          <a href="#" className="text-[13px] text-slate">Cookie Preferences</a>
        </div>
        <p>Clarity — tokens Self-Evolving Agents Hackathon 2026</p>
      </div>
    </div>
  )
}
