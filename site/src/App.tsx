import { motion, useScroll, useTransform } from 'framer-motion'
import { useRef } from 'react'
import {
  ArrowUpRight,
  Compass,
  Target,
  TrendingUp,
  ShoppingBag,
  Megaphone,
  Mail,
  CheckCircle2,
} from 'lucide-react'

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { duration: 0.7, ease: [0.22, 1, 0.36, 1] as const } },
}

function Section({
  id,
  eyebrow,
  children,
  className = '',
}: {
  id?: string
  eyebrow?: string
  children: React.ReactNode
  className?: string
}) {
  return (
    <section id={id} className={`px-6 md:px-12 lg:px-24 py-24 md:py-32 ${className}`}>
      <div className="mx-auto max-w-6xl">
        {eyebrow && (
          <motion.p
            initial="hidden"
            whileInView="show"
            viewport={{ once: true, margin: '-80px' }}
            variants={fadeUp}
            className="text-xs uppercase tracking-[0.3em] text-stone mb-6"
          >
            {eyebrow}
          </motion.p>
        )}
        {children}
      </div>
    </section>
  )
}

export default function App() {
  const heroRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ['start start', 'end start'] })
  const heroY = useTransform(scrollYProgress, [0, 1], [0, 120])
  const heroOpacity = useTransform(scrollYProgress, [0, 1], [1, 0])

  return (
    <div className="bg-bone text-ink">
      <header className="fixed top-0 inset-x-0 z-50 backdrop-blur-md bg-bone/70 border-b border-ink/5">
        <div className="mx-auto max-w-6xl flex items-center justify-between px-6 md:px-12 py-4">
          <div className="flex items-center gap-2">
            <span className="font-display text-xl">Ralph West</span>
            <span className="text-stone">×</span>
            <span className="font-display text-xl text-rust">Travoca</span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-sm">
            <a href="#thesis" className="hover:text-rust transition">Thesis</a>
            <a href="#plan" className="hover:text-rust transition">90-Day Plan</a>
            <a href="#proof" className="hover:text-rust transition">Proof</a>
            <a href="#contact" className="hover:text-rust transition">Contact</a>
          </nav>
        </div>
      </header>

      <div ref={heroRef} className="relative min-h-[100svh] flex items-end overflow-hidden">
        <motion.div
          style={{ y: heroY, opacity: heroOpacity }}
          className="absolute inset-0 -z-10"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-bone via-bone to-moss/10" />
          <div className="absolute -top-40 -right-40 w-[600px] h-[600px] rounded-full bg-rust/15 blur-3xl" />
          <div className="absolute bottom-0 -left-32 w-[500px] h-[500px] rounded-full bg-moss/20 blur-3xl" />
        </motion.div>

        <div className="mx-auto max-w-6xl px-6 md:px-12 lg:px-24 pb-20 pt-40 w-full">
          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-xs uppercase tracking-[0.3em] text-stone mb-8"
          >
            Built for the Travoca interview
          </motion.p>

          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
            className="font-display text-5xl md:text-7xl lg:text-8xl leading-[1.02] tracking-tight max-w-5xl"
          >
            I'm not here to interview.
            <br />
            <span className="italic text-rust">I'm here with a plan.</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.2 }}
            className="mt-10 max-w-2xl text-lg md:text-xl text-ink/70 leading-relaxed"
          >
            Travoca builds rugged outdoor gear that doesn't look it. I build DTC engines that
            scale that kind of brand without diluting it. This is the first 90 days, on the record.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.35 }}
            className="mt-12 flex flex-wrap items-center gap-4"
          >
            <a
              href="#plan"
              className="group inline-flex items-center gap-2 bg-ink text-bone px-6 py-3 rounded-full text-sm font-medium hover:bg-rust transition-colors"
            >
              See the 90-day plan
              <ArrowUpRight className="w-4 h-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition" />
            </a>
            <a
              href="#proof"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-full text-sm font-medium border border-ink/20 hover:border-ink transition"
            >
              Skip to proof
            </a>
          </motion.div>
        </div>

        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 text-stone text-xs tracking-[0.3em] uppercase">
          Scroll
        </div>
      </div>

      <Section id="thesis" eyebrow="The Thesis">
        <motion.div
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: '-80px' }}
          variants={fadeUp}
        >
          <h2 className="font-display text-4xl md:text-6xl leading-[1.05] tracking-tight max-w-4xl">
            Premium outdoor brands win when{' '}
            <span className="italic text-moss">story, product, and acquisition</span>{' '}
            move as one system.
          </h2>
          <p className="mt-8 max-w-3xl text-lg text-ink/70 leading-relaxed">
            Most challenger brands break in one of three places: the product is great but the
            story is generic, the story is great but acquisition is leaking money, or the
            funnel converts but the brand drifts toward the bottom of the market. Travoca's
            "rugged performance, elegant design" is rare positioning. The job is to protect it
            while compounding it.
          </p>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: '-80px' }}
          variants={fadeUp}
          className="grid md:grid-cols-3 gap-6 mt-16"
        >
          {[
            {
              icon: Compass,
              title: 'Brand integrity',
              body: 'Every paid creative, page, and campaign holds the line on premium positioning. No race to the discount floor.',
            },
            {
              icon: Target,
              title: 'Audience precision',
              body: 'Stop spraying. Find the 4–6 customer cohorts that actually buy at premium and build creative for each.',
            },
            {
              icon: TrendingUp,
              title: 'Compounding growth',
              body: 'SEO + organic story + paid that pays back. Owned channels first, paid as accelerant — not life support.',
            },
          ].map((p) => (
            <div
              key={p.title}
              className="p-8 rounded-2xl bg-ink/[0.03] border border-ink/5 hover:border-rust/40 transition group"
            >
              <p.icon className="w-6 h-6 text-rust mb-6 group-hover:scale-110 transition" />
              <h3 className="font-display text-2xl mb-3">{p.title}</h3>
              <p className="text-ink/70 leading-relaxed">{p.body}</p>
            </div>
          ))}
        </motion.div>
      </Section>

      <Section id="plan" eyebrow="The 90-Day Plan" className="bg-ink text-bone">
        <motion.div
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: '-80px' }}
          variants={fadeUp}
        >
          <h2 className="font-display text-4xl md:text-6xl leading-[1.05] tracking-tight max-w-4xl text-bone">
            Day 1 to Day 90.{' '}
            <span className="italic text-rust">Receipts, not promises.</span>
          </h2>
          <p className="mt-8 max-w-3xl text-lg text-bone/70 leading-relaxed">
            Each phase ends with deliverables you can grade me on.
          </p>
        </motion.div>

        <div className="mt-16 space-y-6">
          {[
            {
              window: 'Days 1–30',
              title: 'Diagnose. Stop the bleed.',
              icon: ShoppingBag,
              points: [
                'Full DTC audit — Shopify catalog, merchant feed integrity, product titles, pricing ladder, bundle logic.',
                'Acquisition forensic on Meta + Google + TikTok: which creatives, audiences, and SKUs actually pay back at 30/60/90-day LTV.',
                'Site teardown: PDP, cart, checkout, post-purchase. Identify the 5 highest-ROI conversion fixes — ship the top 2.',
                'Customer interview sprint: 10 buyers, 5 returners, 5 churned. Real language goes back into ad copy and PDPs.',
              ],
            },
            {
              window: 'Days 31–60',
              title: 'Build the engine.',
              icon: Megaphone,
              points: [
                'Rebuild the creative system: 4 thesis-led concepts × 3 hooks × 3 audiences. Test framework, not one-offs.',
                'SEO + content flywheel: 25 evergreen blog posts mapped to high-intent outdoor / gear-buyer queries.',
                'Lifecycle: Klaviyo flows audited and rewritten — abandoned cart, browse, post-purchase, win-back, VIP. Each one a brand moment, not a discount.',
                'Retention: introduce a soft loyalty mechanic that rewards repeat purchase without training the customer to wait for sales.',
              ],
            },
            {
              window: 'Days 61–90',
              title: 'Scale what pays back.',
              icon: TrendingUp,
              points: [
                'Pour fuel only on creatives, audiences, and channels that hit the LTV/CAC floor we set in week 1.',
                'Open one new channel intentionally — TikTok Shop, Amazon brand store, or wholesale — based on what the data says, not the trend cycle.',
                'Launch a hero seasonal campaign: integrated story, paid, organic, lifecycle, and PR — the Travoca worldview, full volume.',
                "Hand over a written playbook so this keeps running whether I'm in the room or not.",
              ],
            },
          ].map((phase, i) => (
            <motion.div
              key={phase.window}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.6, delay: i * 0.05, ease: [0.22, 1, 0.36, 1] }}
              className="grid md:grid-cols-[200px_1fr] gap-8 p-8 md:p-10 rounded-2xl bg-bone/5 border border-bone/10 hover:border-rust/40 transition"
            >
              <div>
                <phase.icon className="w-7 h-7 text-rust mb-4" />
                <p className="text-xs uppercase tracking-[0.3em] text-bone/50 mb-2">
                  {phase.window}
                </p>
                <h3 className="font-display text-3xl text-bone leading-tight">
                  {phase.title}
                </h3>
              </div>
              <ul className="space-y-4">
                {phase.points.map((pt) => (
                  <li key={pt} className="flex gap-3 text-bone/80 leading-relaxed">
                    <CheckCircle2 className="w-5 h-5 text-rust flex-shrink-0 mt-0.5" />
                    <span>{pt}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          ))}
        </div>
      </Section>

      <Section id="proof" eyebrow="Why this isn't theory">
        <motion.div
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: '-80px' }}
          variants={fadeUp}
        >
          <h2 className="font-display text-4xl md:text-6xl leading-[1.05] tracking-tight max-w-4xl">
            I've already run this play.{' '}
            <span className="italic text-moss">Twice.</span>
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-6 mt-16">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="p-8 md:p-10 rounded-2xl bg-moss/10 border border-moss/20"
          >
            <p className="text-xs uppercase tracking-[0.3em] text-moss mb-4">
              Cali Life Co.
            </p>
            <h3 className="font-display text-3xl mb-4">
              DTC operator, not consultant.
            </h3>
            <p className="text-ink/70 leading-relaxed mb-6">
              I run a Shopify lifestyle brand end-to-end: Google Shopping, Meta, TikTok,
              warranty ops, customer service, lifecycle email, inventory, and the launch-
              readiness checklist that catches problems before they hit revenue. I've felt
              every lever this job has.
            </p>
            <ul className="space-y-2 text-sm text-ink/70">
              <li className="flex gap-2"><span className="text-rust">•</span> Mission-control dashboard tracking ads-die-out signals across 5 vectors.</li>
              <li className="flex gap-2"><span className="text-rust">•</span> Inventory + merchant-feed audits that recover suspended SKUs.</li>
              <li className="flex gap-2"><span className="text-rust">•</span> 13-gate launch readiness checklist before any new campaign.</li>
            </ul>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="p-8 md:p-10 rounded-2xl bg-rust/10 border border-rust/20"
          >
            <p className="text-xs uppercase tracking-[0.3em] text-rust mb-4">
              Velora
            </p>
            <h3 className="font-display text-3xl mb-4">
              Built the agency I'd want to hire.
            </h3>
            <p className="text-ink/70 leading-relaxed mb-6">
              Velora is the marketing arm — graphic design, Meta + Google + YouTube ads,
              SEO and content, lead gen. Operating since 2004 with the institutional muscle
              of an agency and the speed of a founder. Travoca gets that team behind the work.
            </p>
            <ul className="space-y-2 text-sm text-ink/70">
              <li className="flex gap-2"><span className="text-moss">•</span> Creative + media buying under one roof — no finger-pointing.</li>
              <li className="flex gap-2"><span className="text-moss">•</span> 25-blog SEO sprints aligned to commercial-intent queries.</li>
              <li className="flex gap-2"><span className="text-moss">•</span> Dashboards over decks. We make the numbers visible weekly.</li>
            </ul>
          </motion.div>
        </div>
      </Section>

      <Section id="contact" eyebrow="Next move">
        <motion.div
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: '-80px' }}
          variants={fadeUp}
          className="text-center"
        >
          <h2 className="font-display text-5xl md:text-7xl leading-[1.05] tracking-tight max-w-4xl mx-auto">
            Let's go build it.
          </h2>
          <p className="mt-8 max-w-2xl mx-auto text-lg text-ink/70 leading-relaxed">
            If this plan reads like the operator you're looking for, the rest is a
            conversation. I'm ready to start day one.
          </p>
          <a
            href="mailto:ralphwestworld@gmail.com?subject=Travoca%20%E2%80%94%20next%20step"
            className="mt-12 inline-flex items-center gap-3 bg-ink text-bone px-8 py-4 rounded-full text-base font-medium hover:bg-rust transition-colors"
          >
            <Mail className="w-5 h-5" />
            ralphwestworld@gmail.com
          </a>
        </motion.div>
      </Section>

      <footer className="border-t border-ink/10 py-10 text-center text-sm text-stone">
        <p>Built for the Travoca conversation. Ralph West, {new Date().getFullYear()}.</p>
      </footer>
    </div>
  )
}
