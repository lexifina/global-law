from policyengine_us import Simulation
y=2025
def case(sit,cid,wages,force,state="VA"):
    p=cid+"a"; sit["people"][p]={"age":{y:40},"employment_income":{y:wages}}
    tu={"members":[p]}
    if force is not None: tu["tax_unit_itemizes"]={y:force}
    sit["tax_units"][cid]=tu
    for k in ("families","spm_units","marital_units"): sit[k][cid]={"members":[p]}
    sit["households"][cid]={"members":[p],"state_name":{y:state}}
for order in ([(45000,None),(400000,None),(400000,True)], [(400000,None),(400000,True)], [(400000,True),(400000,None)]):
    sit={k:{} for k in ("people","tax_units","families","spm_units","marital_units","households")}
    for i,(w,f) in enumerate(order): case(sit,f"c{i}",w,f)
    s=Simulation(situation=sit)
    print(order, [round(float(x)) for x in s.calculate("income_tax",y)], list(s.calculate("tax_unit_itemizes",y)))
