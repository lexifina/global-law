import Engine from 'publicodes'
import rules from 'modele-social'
const e = new Engine(rules, {logger:{log(){},warn(){},error(){}}})
const P = e.getParsedRules(); const re = new RegExp(process.argv[2]); const full = process.argv[3]==='full'
for (const n of Object.keys(P)) if (re.test(n)) { const r={...P[n].rawNode}; if(!full){delete r.description; delete r.question; delete r.note} console.log('##', n, JSON.stringify(r).slice(0, full?4000:700)) }
