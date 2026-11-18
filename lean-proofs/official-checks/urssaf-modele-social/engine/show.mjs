import rules from 'modele-social'
for (const k of process.argv.slice(2)) { const ks = Object.keys(rules).filter(n => n===k || n.startsWith(k+' . ')); for (const n of ks) { const r={...rules[n]}; delete r.description; delete r.références; delete r.question; console.log('##', n, JSON.stringify(r)) } }
