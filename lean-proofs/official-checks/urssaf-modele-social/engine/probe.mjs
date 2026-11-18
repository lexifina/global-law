import Engine from 'publicodes'
import rules from 'modele-social'
const e = new Engine(rules, {logger:{log(){},warn(){},error:console.error}})
const names = Object.keys(e.getParsedRules()); console.log('parsed rules', names.length)
e.setSituation({ date: "'01/06/2025'", 'salarié . contrat . salaire brut': '3000 €/mois', 'salarié . contrat . statut cadre': 'non' })
const v = n => { const r = e.evaluate(n); return [r.nodeValue, r.unit && JSON.stringify(r.unit)] }
for (const n of ['date','plafond sécurité sociale','salarié . contrat','salarié . contrat . temps de travail','salarié . cotisations . prévoyances . santé . montant','salarié . cotisations . prévoyances . employeur','salarié . cotisations . salarié','salarié . cotisations . CSG-CRDS . assiette de base','salarié . rémunération . net . à payer avant impôt','salarié . rémunération . net . imposable', 'SMIC'])
  console.log(n, v(n))
const r = e.evaluate('salarié . rémunération . net . à payer avant impôt')
console.log('missing', Object.keys(r.missingVariables).slice(0,40))
