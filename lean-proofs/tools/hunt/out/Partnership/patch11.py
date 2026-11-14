p='LegalProofs/USTax/Hunt/Partnership.lean'
s=open(p,encoding='utf-8',newline='').read()
a=s.index("* §751(b) is applied by the")
b=s.index("-/\n\nnamespace Legal.USTax.Hunt.Partnership")
s=s[:a]+'''* §751(b) is applied by the "hypothetical sale" method: a partner whose share of the gain in substantially
  appreciated inventory falls in a distribution has ordinary income equal to the fall; whoever takes the share over
  has a cost basis in it and gain on what he gave for it (taken in full, the conservative figure);
* §704(c)(1)(B) losses: §707(b)(1) is applied to the deemed sale to the distributee (T.D. 8642), with §267(c)
  family attribution; §267(a)(1) on a sale of an interest between related persons;
* a disguised sale of part of a property is taxed in proportion to the whole property each time (two part-sales
  of one property recognise slightly less than the whole gain; the remainder is still taxed under §731);
* §732(d), §736(a), §708(b)(2), §724, §735, §1061, §707(c), §1402(a)(13), §199A, §163(j)(4), §461(l), §7704 and
  the audit regime (§6221 ff.) were read but are not in the search: they change character, timing or procedure,
  not the amounts tracked here. Death of a partner (§1014, §743(b)) is not a move.

The search conserves gain: in none of the positions run does any plan lower the tax due once everything is sold
and the partnership wound up. Every plan it finds defers gain, moves it to another asset or person, or brings a
loss forward.
'''+s[b:]
open(p,'w',encoding='utf-8',newline='').write(s)
