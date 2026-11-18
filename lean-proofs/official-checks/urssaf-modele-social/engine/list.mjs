import rules from 'modele-social'
const ks=Object.keys(rules); console.log(ks.length)
const re=new RegExp(process.argv[2]); for(const k of ks) if(re.test(k)) console.log(k)
