from policyengine_us import Simulation
y=2025
for force in (None, True, False):
    tu={"members":["a"]}
    if force is not None: tu["tax_unit_itemizes"]={y:force}
    sit={"people":{"a":{"age":{y:40},"employment_income":{y:400000}}},"tax_units":{"t":tu},"families":{"f":{"members":["a"]}},
         "spm_units":{"s":{"members":["a"]}},"marital_units":{"m":{"members":["a"]}},"households":{"h":{"members":["a"],"state_name":{y:"VA"}}}}
    s=Simulation(situation=sit)
    print(force,[ (v, round(float(s.calculate(v,y)[0]))) for v in ["tax_unit_itemizes","state_withheld_income_tax","salt_deduction","itemized_taxable_income_deductions","standard_deduction","taxable_income","income_tax","state_income_tax","alternative_minimum_tax"]])
