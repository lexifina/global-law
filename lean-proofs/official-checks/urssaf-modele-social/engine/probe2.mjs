import Engine from 'publicodes'
import rules from 'modele-social'
const e = new Engine(rules, {logger:{log(){},warn(){},error:console.error}})
const names = Object.keys(e.getParsedRules()).filter(n => n.startsWith('salarié . cotisations'))
for (const [g,c] of [['3000','non'],['30000','oui']]) {
  e.setSituation({ date: "'01/06/2025'", 'salarié . contrat . salaire brut': g+' €/mois', 'salarié . contrat . statut cadre': c, 'salarié . cotisations . prévoyances . santé . montant': '0 €/mois' })
  console.log('=== ', g, c)
  for (const n of names) { if (!/salarié$|salarié \.|CSG|CRDS|prévoyances \. employeur$|cadres$/.test(n.slice(22))) continue; const r = e.evaluate(n); if (typeof r.nodeValue==='number' && r.nodeValue!==0) console.log(n.slice(22), +r.nodeValue.toFixed(4)) }
  for (const n of ['salarié . cotisations . salarié','salarié . rémunération . net . à payer avant impôt','salarié . rémunération . net . imposable']) console.log(n, e.evaluate(n).nodeValue)
}
