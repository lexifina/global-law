/-!
# caselaw-lean-2: SHA-1 (FIPS 180-4)

A plain, total SHA-1 over `ByteArray`, used to check certificate windows (`cert_text.tsv`,
`holdings_cert_text.tsv`) against the audit copy's `window_sha.tsv`: the checker recomputes
`hex window` and compares it with the stored digest.

Cost: one padded copy of the message, then per 64-byte block one call of `block`, which is fully
unrolled (the 80-word schedule and the 80 rounds are `UInt32` `let` bindings; no arrays, no loop), so
it is cheap both compiled and under the IR interpreter (`lake env lean --run`). The only loops are
`for` loops over ranges, so every definition is total.

The `#guard` lines at the end are test vectors computed with Python's `hashlib.sha1` (FIPS examples,
padding edges at 55/63/64/65 bytes, multi-block and non-ASCII strings, and real windows copied from
`cert_text.tsv`).
-/

namespace CaseLaw2.Sha1

@[inline] private def rotl1 (x : UInt32) : UInt32 := (x <<< 1) ||| (x >>> 31)
@[inline] private def rotl5 (x : UInt32) : UInt32 := (x <<< 5) ||| (x >>> 27)
@[inline] private def rotl30 (x : UInt32) : UInt32 := (x <<< 30) ||| (x >>> 2)

/-- The message followed by `0x80`, zeros, and the 64-bit big-endian bit length, a multiple of 64 bytes. -/
def pad (b : ByteArray) : ByteArray := Id.run do
  let len := b.size
  let total := ((len + 8) / 64 + 1) * 64
  let mut out := ByteArray.emptyWithCapacity total
  out := out ++ b
  out := out.push 0x80
  for _ in [len + 1 : total - 8] do
    out := out.push 0
  let bits : UInt64 := (UInt64.ofNat len) * 8
  for i in [0:8] do
    out := out.push (bits >>> (UInt64.ofNat (56 - 8 * i))).toUInt8
  return out

/-- Big-endian 32-bit word at byte offset `o`. -/
@[inline] private def word (m : ByteArray) (o : Nat) : UInt32 :=
  (m[o]!.toUInt32 <<< 24) ||| (m[o+1]!.toUInt32 <<< 16) ||| (m[o+2]!.toUInt32 <<< 8) ||| m[o+3]!.toUInt32

private structure St where
  h0 : UInt32
  h1 : UInt32
  h2 : UInt32
  h3 : UInt32
  h4 : UInt32

/-- One compression of the 64-byte block at offset `o` of `m` (unrolled: 80 schedule words and 80 rounds as
    `let` bindings, so neither the compiler nor the interpreter runs a loop or touches an array here). -/
private def block (m : ByteArray) (o : Nat) (s : St) : St :=
  let w0 := word m (o + 0)
  let w1 := word m (o + 4)
  let w2 := word m (o + 8)
  let w3 := word m (o + 12)
  let w4 := word m (o + 16)
  let w5 := word m (o + 20)
  let w6 := word m (o + 24)
  let w7 := word m (o + 28)
  let w8 := word m (o + 32)
  let w9 := word m (o + 36)
  let w10 := word m (o + 40)
  let w11 := word m (o + 44)
  let w12 := word m (o + 48)
  let w13 := word m (o + 52)
  let w14 := word m (o + 56)
  let w15 := word m (o + 60)
  let w16 := rotl1 (w13 ^^^ w8 ^^^ w2 ^^^ w0)
  let w17 := rotl1 (w14 ^^^ w9 ^^^ w3 ^^^ w1)
  let w18 := rotl1 (w15 ^^^ w10 ^^^ w4 ^^^ w2)
  let w19 := rotl1 (w16 ^^^ w11 ^^^ w5 ^^^ w3)
  let w20 := rotl1 (w17 ^^^ w12 ^^^ w6 ^^^ w4)
  let w21 := rotl1 (w18 ^^^ w13 ^^^ w7 ^^^ w5)
  let w22 := rotl1 (w19 ^^^ w14 ^^^ w8 ^^^ w6)
  let w23 := rotl1 (w20 ^^^ w15 ^^^ w9 ^^^ w7)
  let w24 := rotl1 (w21 ^^^ w16 ^^^ w10 ^^^ w8)
  let w25 := rotl1 (w22 ^^^ w17 ^^^ w11 ^^^ w9)
  let w26 := rotl1 (w23 ^^^ w18 ^^^ w12 ^^^ w10)
  let w27 := rotl1 (w24 ^^^ w19 ^^^ w13 ^^^ w11)
  let w28 := rotl1 (w25 ^^^ w20 ^^^ w14 ^^^ w12)
  let w29 := rotl1 (w26 ^^^ w21 ^^^ w15 ^^^ w13)
  let w30 := rotl1 (w27 ^^^ w22 ^^^ w16 ^^^ w14)
  let w31 := rotl1 (w28 ^^^ w23 ^^^ w17 ^^^ w15)
  let w32 := rotl1 (w29 ^^^ w24 ^^^ w18 ^^^ w16)
  let w33 := rotl1 (w30 ^^^ w25 ^^^ w19 ^^^ w17)
  let w34 := rotl1 (w31 ^^^ w26 ^^^ w20 ^^^ w18)
  let w35 := rotl1 (w32 ^^^ w27 ^^^ w21 ^^^ w19)
  let w36 := rotl1 (w33 ^^^ w28 ^^^ w22 ^^^ w20)
  let w37 := rotl1 (w34 ^^^ w29 ^^^ w23 ^^^ w21)
  let w38 := rotl1 (w35 ^^^ w30 ^^^ w24 ^^^ w22)
  let w39 := rotl1 (w36 ^^^ w31 ^^^ w25 ^^^ w23)
  let w40 := rotl1 (w37 ^^^ w32 ^^^ w26 ^^^ w24)
  let w41 := rotl1 (w38 ^^^ w33 ^^^ w27 ^^^ w25)
  let w42 := rotl1 (w39 ^^^ w34 ^^^ w28 ^^^ w26)
  let w43 := rotl1 (w40 ^^^ w35 ^^^ w29 ^^^ w27)
  let w44 := rotl1 (w41 ^^^ w36 ^^^ w30 ^^^ w28)
  let w45 := rotl1 (w42 ^^^ w37 ^^^ w31 ^^^ w29)
  let w46 := rotl1 (w43 ^^^ w38 ^^^ w32 ^^^ w30)
  let w47 := rotl1 (w44 ^^^ w39 ^^^ w33 ^^^ w31)
  let w48 := rotl1 (w45 ^^^ w40 ^^^ w34 ^^^ w32)
  let w49 := rotl1 (w46 ^^^ w41 ^^^ w35 ^^^ w33)
  let w50 := rotl1 (w47 ^^^ w42 ^^^ w36 ^^^ w34)
  let w51 := rotl1 (w48 ^^^ w43 ^^^ w37 ^^^ w35)
  let w52 := rotl1 (w49 ^^^ w44 ^^^ w38 ^^^ w36)
  let w53 := rotl1 (w50 ^^^ w45 ^^^ w39 ^^^ w37)
  let w54 := rotl1 (w51 ^^^ w46 ^^^ w40 ^^^ w38)
  let w55 := rotl1 (w52 ^^^ w47 ^^^ w41 ^^^ w39)
  let w56 := rotl1 (w53 ^^^ w48 ^^^ w42 ^^^ w40)
  let w57 := rotl1 (w54 ^^^ w49 ^^^ w43 ^^^ w41)
  let w58 := rotl1 (w55 ^^^ w50 ^^^ w44 ^^^ w42)
  let w59 := rotl1 (w56 ^^^ w51 ^^^ w45 ^^^ w43)
  let w60 := rotl1 (w57 ^^^ w52 ^^^ w46 ^^^ w44)
  let w61 := rotl1 (w58 ^^^ w53 ^^^ w47 ^^^ w45)
  let w62 := rotl1 (w59 ^^^ w54 ^^^ w48 ^^^ w46)
  let w63 := rotl1 (w60 ^^^ w55 ^^^ w49 ^^^ w47)
  let w64 := rotl1 (w61 ^^^ w56 ^^^ w50 ^^^ w48)
  let w65 := rotl1 (w62 ^^^ w57 ^^^ w51 ^^^ w49)
  let w66 := rotl1 (w63 ^^^ w58 ^^^ w52 ^^^ w50)
  let w67 := rotl1 (w64 ^^^ w59 ^^^ w53 ^^^ w51)
  let w68 := rotl1 (w65 ^^^ w60 ^^^ w54 ^^^ w52)
  let w69 := rotl1 (w66 ^^^ w61 ^^^ w55 ^^^ w53)
  let w70 := rotl1 (w67 ^^^ w62 ^^^ w56 ^^^ w54)
  let w71 := rotl1 (w68 ^^^ w63 ^^^ w57 ^^^ w55)
  let w72 := rotl1 (w69 ^^^ w64 ^^^ w58 ^^^ w56)
  let w73 := rotl1 (w70 ^^^ w65 ^^^ w59 ^^^ w57)
  let w74 := rotl1 (w71 ^^^ w66 ^^^ w60 ^^^ w58)
  let w75 := rotl1 (w72 ^^^ w67 ^^^ w61 ^^^ w59)
  let w76 := rotl1 (w73 ^^^ w68 ^^^ w62 ^^^ w60)
  let w77 := rotl1 (w74 ^^^ w69 ^^^ w63 ^^^ w61)
  let w78 := rotl1 (w75 ^^^ w70 ^^^ w64 ^^^ w62)
  let w79 := rotl1 (w76 ^^^ w71 ^^^ w65 ^^^ w63)
  let a0 := s.h0
  let b0 := s.h1
  let c0 := s.h2
  let d0 := s.h3
  let e0 := s.h4
  let a1 := rotl5 a0 + (d0 ^^^ (b0 &&& (c0 ^^^ d0))) + e0 + 0x5A827999 + w0
  let b1 := a0
  let c1 := rotl30 b0
  let d1 := c0
  let e1 := d0
  let a2 := rotl5 a1 + (d1 ^^^ (b1 &&& (c1 ^^^ d1))) + e1 + 0x5A827999 + w1
  let b2 := a1
  let c2 := rotl30 b1
  let d2 := c1
  let e2 := d1
  let a3 := rotl5 a2 + (d2 ^^^ (b2 &&& (c2 ^^^ d2))) + e2 + 0x5A827999 + w2
  let b3 := a2
  let c3 := rotl30 b2
  let d3 := c2
  let e3 := d2
  let a4 := rotl5 a3 + (d3 ^^^ (b3 &&& (c3 ^^^ d3))) + e3 + 0x5A827999 + w3
  let b4 := a3
  let c4 := rotl30 b3
  let d4 := c3
  let e4 := d3
  let a5 := rotl5 a4 + (d4 ^^^ (b4 &&& (c4 ^^^ d4))) + e4 + 0x5A827999 + w4
  let b5 := a4
  let c5 := rotl30 b4
  let d5 := c4
  let e5 := d4
  let a6 := rotl5 a5 + (d5 ^^^ (b5 &&& (c5 ^^^ d5))) + e5 + 0x5A827999 + w5
  let b6 := a5
  let c6 := rotl30 b5
  let d6 := c5
  let e6 := d5
  let a7 := rotl5 a6 + (d6 ^^^ (b6 &&& (c6 ^^^ d6))) + e6 + 0x5A827999 + w6
  let b7 := a6
  let c7 := rotl30 b6
  let d7 := c6
  let e7 := d6
  let a8 := rotl5 a7 + (d7 ^^^ (b7 &&& (c7 ^^^ d7))) + e7 + 0x5A827999 + w7
  let b8 := a7
  let c8 := rotl30 b7
  let d8 := c7
  let e8 := d7
  let a9 := rotl5 a8 + (d8 ^^^ (b8 &&& (c8 ^^^ d8))) + e8 + 0x5A827999 + w8
  let b9 := a8
  let c9 := rotl30 b8
  let d9 := c8
  let e9 := d8
  let a10 := rotl5 a9 + (d9 ^^^ (b9 &&& (c9 ^^^ d9))) + e9 + 0x5A827999 + w9
  let b10 := a9
  let c10 := rotl30 b9
  let d10 := c9
  let e10 := d9
  let a11 := rotl5 a10 + (d10 ^^^ (b10 &&& (c10 ^^^ d10))) + e10 + 0x5A827999 + w10
  let b11 := a10
  let c11 := rotl30 b10
  let d11 := c10
  let e11 := d10
  let a12 := rotl5 a11 + (d11 ^^^ (b11 &&& (c11 ^^^ d11))) + e11 + 0x5A827999 + w11
  let b12 := a11
  let c12 := rotl30 b11
  let d12 := c11
  let e12 := d11
  let a13 := rotl5 a12 + (d12 ^^^ (b12 &&& (c12 ^^^ d12))) + e12 + 0x5A827999 + w12
  let b13 := a12
  let c13 := rotl30 b12
  let d13 := c12
  let e13 := d12
  let a14 := rotl5 a13 + (d13 ^^^ (b13 &&& (c13 ^^^ d13))) + e13 + 0x5A827999 + w13
  let b14 := a13
  let c14 := rotl30 b13
  let d14 := c13
  let e14 := d13
  let a15 := rotl5 a14 + (d14 ^^^ (b14 &&& (c14 ^^^ d14))) + e14 + 0x5A827999 + w14
  let b15 := a14
  let c15 := rotl30 b14
  let d15 := c14
  let e15 := d14
  let a16 := rotl5 a15 + (d15 ^^^ (b15 &&& (c15 ^^^ d15))) + e15 + 0x5A827999 + w15
  let b16 := a15
  let c16 := rotl30 b15
  let d16 := c15
  let e16 := d15
  let a17 := rotl5 a16 + (d16 ^^^ (b16 &&& (c16 ^^^ d16))) + e16 + 0x5A827999 + w16
  let b17 := a16
  let c17 := rotl30 b16
  let d17 := c16
  let e17 := d16
  let a18 := rotl5 a17 + (d17 ^^^ (b17 &&& (c17 ^^^ d17))) + e17 + 0x5A827999 + w17
  let b18 := a17
  let c18 := rotl30 b17
  let d18 := c17
  let e18 := d17
  let a19 := rotl5 a18 + (d18 ^^^ (b18 &&& (c18 ^^^ d18))) + e18 + 0x5A827999 + w18
  let b19 := a18
  let c19 := rotl30 b18
  let d19 := c18
  let e19 := d18
  let a20 := rotl5 a19 + (d19 ^^^ (b19 &&& (c19 ^^^ d19))) + e19 + 0x5A827999 + w19
  let b20 := a19
  let c20 := rotl30 b19
  let d20 := c19
  let e20 := d19
  let a21 := rotl5 a20 + (b20 ^^^ c20 ^^^ d20) + e20 + 0x6ED9EBA1 + w20
  let b21 := a20
  let c21 := rotl30 b20
  let d21 := c20
  let e21 := d20
  let a22 := rotl5 a21 + (b21 ^^^ c21 ^^^ d21) + e21 + 0x6ED9EBA1 + w21
  let b22 := a21
  let c22 := rotl30 b21
  let d22 := c21
  let e22 := d21
  let a23 := rotl5 a22 + (b22 ^^^ c22 ^^^ d22) + e22 + 0x6ED9EBA1 + w22
  let b23 := a22
  let c23 := rotl30 b22
  let d23 := c22
  let e23 := d22
  let a24 := rotl5 a23 + (b23 ^^^ c23 ^^^ d23) + e23 + 0x6ED9EBA1 + w23
  let b24 := a23
  let c24 := rotl30 b23
  let d24 := c23
  let e24 := d23
  let a25 := rotl5 a24 + (b24 ^^^ c24 ^^^ d24) + e24 + 0x6ED9EBA1 + w24
  let b25 := a24
  let c25 := rotl30 b24
  let d25 := c24
  let e25 := d24
  let a26 := rotl5 a25 + (b25 ^^^ c25 ^^^ d25) + e25 + 0x6ED9EBA1 + w25
  let b26 := a25
  let c26 := rotl30 b25
  let d26 := c25
  let e26 := d25
  let a27 := rotl5 a26 + (b26 ^^^ c26 ^^^ d26) + e26 + 0x6ED9EBA1 + w26
  let b27 := a26
  let c27 := rotl30 b26
  let d27 := c26
  let e27 := d26
  let a28 := rotl5 a27 + (b27 ^^^ c27 ^^^ d27) + e27 + 0x6ED9EBA1 + w27
  let b28 := a27
  let c28 := rotl30 b27
  let d28 := c27
  let e28 := d27
  let a29 := rotl5 a28 + (b28 ^^^ c28 ^^^ d28) + e28 + 0x6ED9EBA1 + w28
  let b29 := a28
  let c29 := rotl30 b28
  let d29 := c28
  let e29 := d28
  let a30 := rotl5 a29 + (b29 ^^^ c29 ^^^ d29) + e29 + 0x6ED9EBA1 + w29
  let b30 := a29
  let c30 := rotl30 b29
  let d30 := c29
  let e30 := d29
  let a31 := rotl5 a30 + (b30 ^^^ c30 ^^^ d30) + e30 + 0x6ED9EBA1 + w30
  let b31 := a30
  let c31 := rotl30 b30
  let d31 := c30
  let e31 := d30
  let a32 := rotl5 a31 + (b31 ^^^ c31 ^^^ d31) + e31 + 0x6ED9EBA1 + w31
  let b32 := a31
  let c32 := rotl30 b31
  let d32 := c31
  let e32 := d31
  let a33 := rotl5 a32 + (b32 ^^^ c32 ^^^ d32) + e32 + 0x6ED9EBA1 + w32
  let b33 := a32
  let c33 := rotl30 b32
  let d33 := c32
  let e33 := d32
  let a34 := rotl5 a33 + (b33 ^^^ c33 ^^^ d33) + e33 + 0x6ED9EBA1 + w33
  let b34 := a33
  let c34 := rotl30 b33
  let d34 := c33
  let e34 := d33
  let a35 := rotl5 a34 + (b34 ^^^ c34 ^^^ d34) + e34 + 0x6ED9EBA1 + w34
  let b35 := a34
  let c35 := rotl30 b34
  let d35 := c34
  let e35 := d34
  let a36 := rotl5 a35 + (b35 ^^^ c35 ^^^ d35) + e35 + 0x6ED9EBA1 + w35
  let b36 := a35
  let c36 := rotl30 b35
  let d36 := c35
  let e36 := d35
  let a37 := rotl5 a36 + (b36 ^^^ c36 ^^^ d36) + e36 + 0x6ED9EBA1 + w36
  let b37 := a36
  let c37 := rotl30 b36
  let d37 := c36
  let e37 := d36
  let a38 := rotl5 a37 + (b37 ^^^ c37 ^^^ d37) + e37 + 0x6ED9EBA1 + w37
  let b38 := a37
  let c38 := rotl30 b37
  let d38 := c37
  let e38 := d37
  let a39 := rotl5 a38 + (b38 ^^^ c38 ^^^ d38) + e38 + 0x6ED9EBA1 + w38
  let b39 := a38
  let c39 := rotl30 b38
  let d39 := c38
  let e39 := d38
  let a40 := rotl5 a39 + (b39 ^^^ c39 ^^^ d39) + e39 + 0x6ED9EBA1 + w39
  let b40 := a39
  let c40 := rotl30 b39
  let d40 := c39
  let e40 := d39
  let a41 := rotl5 a40 + ((b40 &&& c40) ||| (d40 &&& (b40 ||| c40))) + e40 + 0x8F1BBCDC + w40
  let b41 := a40
  let c41 := rotl30 b40
  let d41 := c40
  let e41 := d40
  let a42 := rotl5 a41 + ((b41 &&& c41) ||| (d41 &&& (b41 ||| c41))) + e41 + 0x8F1BBCDC + w41
  let b42 := a41
  let c42 := rotl30 b41
  let d42 := c41
  let e42 := d41
  let a43 := rotl5 a42 + ((b42 &&& c42) ||| (d42 &&& (b42 ||| c42))) + e42 + 0x8F1BBCDC + w42
  let b43 := a42
  let c43 := rotl30 b42
  let d43 := c42
  let e43 := d42
  let a44 := rotl5 a43 + ((b43 &&& c43) ||| (d43 &&& (b43 ||| c43))) + e43 + 0x8F1BBCDC + w43
  let b44 := a43
  let c44 := rotl30 b43
  let d44 := c43
  let e44 := d43
  let a45 := rotl5 a44 + ((b44 &&& c44) ||| (d44 &&& (b44 ||| c44))) + e44 + 0x8F1BBCDC + w44
  let b45 := a44
  let c45 := rotl30 b44
  let d45 := c44
  let e45 := d44
  let a46 := rotl5 a45 + ((b45 &&& c45) ||| (d45 &&& (b45 ||| c45))) + e45 + 0x8F1BBCDC + w45
  let b46 := a45
  let c46 := rotl30 b45
  let d46 := c45
  let e46 := d45
  let a47 := rotl5 a46 + ((b46 &&& c46) ||| (d46 &&& (b46 ||| c46))) + e46 + 0x8F1BBCDC + w46
  let b47 := a46
  let c47 := rotl30 b46
  let d47 := c46
  let e47 := d46
  let a48 := rotl5 a47 + ((b47 &&& c47) ||| (d47 &&& (b47 ||| c47))) + e47 + 0x8F1BBCDC + w47
  let b48 := a47
  let c48 := rotl30 b47
  let d48 := c47
  let e48 := d47
  let a49 := rotl5 a48 + ((b48 &&& c48) ||| (d48 &&& (b48 ||| c48))) + e48 + 0x8F1BBCDC + w48
  let b49 := a48
  let c49 := rotl30 b48
  let d49 := c48
  let e49 := d48
  let a50 := rotl5 a49 + ((b49 &&& c49) ||| (d49 &&& (b49 ||| c49))) + e49 + 0x8F1BBCDC + w49
  let b50 := a49
  let c50 := rotl30 b49
  let d50 := c49
  let e50 := d49
  let a51 := rotl5 a50 + ((b50 &&& c50) ||| (d50 &&& (b50 ||| c50))) + e50 + 0x8F1BBCDC + w50
  let b51 := a50
  let c51 := rotl30 b50
  let d51 := c50
  let e51 := d50
  let a52 := rotl5 a51 + ((b51 &&& c51) ||| (d51 &&& (b51 ||| c51))) + e51 + 0x8F1BBCDC + w51
  let b52 := a51
  let c52 := rotl30 b51
  let d52 := c51
  let e52 := d51
  let a53 := rotl5 a52 + ((b52 &&& c52) ||| (d52 &&& (b52 ||| c52))) + e52 + 0x8F1BBCDC + w52
  let b53 := a52
  let c53 := rotl30 b52
  let d53 := c52
  let e53 := d52
  let a54 := rotl5 a53 + ((b53 &&& c53) ||| (d53 &&& (b53 ||| c53))) + e53 + 0x8F1BBCDC + w53
  let b54 := a53
  let c54 := rotl30 b53
  let d54 := c53
  let e54 := d53
  let a55 := rotl5 a54 + ((b54 &&& c54) ||| (d54 &&& (b54 ||| c54))) + e54 + 0x8F1BBCDC + w54
  let b55 := a54
  let c55 := rotl30 b54
  let d55 := c54
  let e55 := d54
  let a56 := rotl5 a55 + ((b55 &&& c55) ||| (d55 &&& (b55 ||| c55))) + e55 + 0x8F1BBCDC + w55
  let b56 := a55
  let c56 := rotl30 b55
  let d56 := c55
  let e56 := d55
  let a57 := rotl5 a56 + ((b56 &&& c56) ||| (d56 &&& (b56 ||| c56))) + e56 + 0x8F1BBCDC + w56
  let b57 := a56
  let c57 := rotl30 b56
  let d57 := c56
  let e57 := d56
  let a58 := rotl5 a57 + ((b57 &&& c57) ||| (d57 &&& (b57 ||| c57))) + e57 + 0x8F1BBCDC + w57
  let b58 := a57
  let c58 := rotl30 b57
  let d58 := c57
  let e58 := d57
  let a59 := rotl5 a58 + ((b58 &&& c58) ||| (d58 &&& (b58 ||| c58))) + e58 + 0x8F1BBCDC + w58
  let b59 := a58
  let c59 := rotl30 b58
  let d59 := c58
  let e59 := d58
  let a60 := rotl5 a59 + ((b59 &&& c59) ||| (d59 &&& (b59 ||| c59))) + e59 + 0x8F1BBCDC + w59
  let b60 := a59
  let c60 := rotl30 b59
  let d60 := c59
  let e60 := d59
  let a61 := rotl5 a60 + (b60 ^^^ c60 ^^^ d60) + e60 + 0xCA62C1D6 + w60
  let b61 := a60
  let c61 := rotl30 b60
  let d61 := c60
  let e61 := d60
  let a62 := rotl5 a61 + (b61 ^^^ c61 ^^^ d61) + e61 + 0xCA62C1D6 + w61
  let b62 := a61
  let c62 := rotl30 b61
  let d62 := c61
  let e62 := d61
  let a63 := rotl5 a62 + (b62 ^^^ c62 ^^^ d62) + e62 + 0xCA62C1D6 + w62
  let b63 := a62
  let c63 := rotl30 b62
  let d63 := c62
  let e63 := d62
  let a64 := rotl5 a63 + (b63 ^^^ c63 ^^^ d63) + e63 + 0xCA62C1D6 + w63
  let b64 := a63
  let c64 := rotl30 b63
  let d64 := c63
  let e64 := d63
  let a65 := rotl5 a64 + (b64 ^^^ c64 ^^^ d64) + e64 + 0xCA62C1D6 + w64
  let b65 := a64
  let c65 := rotl30 b64
  let d65 := c64
  let e65 := d64
  let a66 := rotl5 a65 + (b65 ^^^ c65 ^^^ d65) + e65 + 0xCA62C1D6 + w65
  let b66 := a65
  let c66 := rotl30 b65
  let d66 := c65
  let e66 := d65
  let a67 := rotl5 a66 + (b66 ^^^ c66 ^^^ d66) + e66 + 0xCA62C1D6 + w66
  let b67 := a66
  let c67 := rotl30 b66
  let d67 := c66
  let e67 := d66
  let a68 := rotl5 a67 + (b67 ^^^ c67 ^^^ d67) + e67 + 0xCA62C1D6 + w67
  let b68 := a67
  let c68 := rotl30 b67
  let d68 := c67
  let e68 := d67
  let a69 := rotl5 a68 + (b68 ^^^ c68 ^^^ d68) + e68 + 0xCA62C1D6 + w68
  let b69 := a68
  let c69 := rotl30 b68
  let d69 := c68
  let e69 := d68
  let a70 := rotl5 a69 + (b69 ^^^ c69 ^^^ d69) + e69 + 0xCA62C1D6 + w69
  let b70 := a69
  let c70 := rotl30 b69
  let d70 := c69
  let e70 := d69
  let a71 := rotl5 a70 + (b70 ^^^ c70 ^^^ d70) + e70 + 0xCA62C1D6 + w70
  let b71 := a70
  let c71 := rotl30 b70
  let d71 := c70
  let e71 := d70
  let a72 := rotl5 a71 + (b71 ^^^ c71 ^^^ d71) + e71 + 0xCA62C1D6 + w71
  let b72 := a71
  let c72 := rotl30 b71
  let d72 := c71
  let e72 := d71
  let a73 := rotl5 a72 + (b72 ^^^ c72 ^^^ d72) + e72 + 0xCA62C1D6 + w72
  let b73 := a72
  let c73 := rotl30 b72
  let d73 := c72
  let e73 := d72
  let a74 := rotl5 a73 + (b73 ^^^ c73 ^^^ d73) + e73 + 0xCA62C1D6 + w73
  let b74 := a73
  let c74 := rotl30 b73
  let d74 := c73
  let e74 := d73
  let a75 := rotl5 a74 + (b74 ^^^ c74 ^^^ d74) + e74 + 0xCA62C1D6 + w74
  let b75 := a74
  let c75 := rotl30 b74
  let d75 := c74
  let e75 := d74
  let a76 := rotl5 a75 + (b75 ^^^ c75 ^^^ d75) + e75 + 0xCA62C1D6 + w75
  let b76 := a75
  let c76 := rotl30 b75
  let d76 := c75
  let e76 := d75
  let a77 := rotl5 a76 + (b76 ^^^ c76 ^^^ d76) + e76 + 0xCA62C1D6 + w76
  let b77 := a76
  let c77 := rotl30 b76
  let d77 := c76
  let e77 := d76
  let a78 := rotl5 a77 + (b77 ^^^ c77 ^^^ d77) + e77 + 0xCA62C1D6 + w77
  let b78 := a77
  let c78 := rotl30 b77
  let d78 := c77
  let e78 := d77
  let a79 := rotl5 a78 + (b78 ^^^ c78 ^^^ d78) + e78 + 0xCA62C1D6 + w78
  let b79 := a78
  let c79 := rotl30 b78
  let d79 := c78
  let e79 := d78
  let a80 := rotl5 a79 + (b79 ^^^ c79 ^^^ d79) + e79 + 0xCA62C1D6 + w79
  let b80 := a79
  let c80 := rotl30 b79
  let d80 := c79
  let e80 := d79
  ⟨s.h0 + a80, s.h1 + b80, s.h2 + c80, s.h3 + d80, s.h4 + e80⟩

/-- SHA-1 digest (20 bytes) of a byte array. -/
def sha1 (b : ByteArray) : ByteArray := Id.run do
  let m := pad b
  let mut s : St := ⟨0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0⟩
  for i in [0 : m.size / 64] do
    s := block m (64 * i) s
  let mut out := ByteArray.emptyWithCapacity 20
  for h in [s.h0, s.h1, s.h2, s.h3, s.h4] do
    out := out.push (h >>> 24).toUInt8
    out := out.push (h >>> 16).toUInt8
    out := out.push (h >>> 8).toUInt8
    out := out.push h.toUInt8
  return out

@[inline] private def hexDigit (n : UInt8) : Char :=
  if n < 10 then Char.ofNat (48 + n.toNat) else Char.ofNat (87 + n.toNat)

/-- Lowercase hex of a byte array. -/
def hexOfBytes (b : ByteArray) : String := Id.run do
  let mut s := ""
  for x in b do
    s := s.push (hexDigit (x >>> 4))
    s := s.push (hexDigit (x &&& 15))
  return s

/-- SHA-1 of the string's UTF-8 bytes, as 40 lowercase hex characters. -/
def hex (s : String) : String := hexOfBytes (sha1 s.toUTF8)

/-! ## Test vectors (expected digests from Python `hashlib.sha1`) -/

#guard hex "" == "da39a3ee5e6b4b0d3255bfef95601890afd80709"
#guard hex "abc" == "a9993e364706816aba3e25717850c26c9cd0d89d"
#guard hex "abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq" == "84983e441c3bd26ebaae4aa1f95129e5e54670f1"
#guard hex "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" == "c1c8bbdc22796e28c0e15163d20899b65621d65a"
#guard hex "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" == "956b36ade6e3e4b7818ced2d611fb95e8abc2bd0"
#guard hex "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc" == "b29fcb5f41614b4ec81c87e4614ffe8b9ace1d4e"
#guard hex "ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd" == "9b815bfbeb05280b696f4aee68066c6f98f59646"
#guard hex "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee" == "d3997b276bf9c5a7e3505c11261f3315f2defd2f"
#guard hex "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff" == "ca367c643a72964392cb0682bb7030753d62e6f4"
#guard hex "gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg" == "b6a87c63a76e8ba0463b25461e2d3e57952b5494"
#guard hex "The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jumps over the lazy dog. 0123456789 The quick brown fox jump" == "4436472cc32196e8a0d37f95304d5f5e10e62a1e"
#guard hex "Café § 1983 — résumé ’" == "9329695ae167099885fc2fd67ab483f4772da632"
#guard hex "na to defend Safeway in any suit or administrative proceeding for damages against the latter by any third person. Safeway thus has no claim for damages for breach of any agreement to defend. In our view, the district court properly allowed interest only from the date of judgment. Since Safeway recovered all that was due it under the policy, we agree that it had no basis to claim loss of earnings. Affirmed.  ## Dissent (WIDENER, Circuit Judge)  WIDENER, Circuit Judge (dissenting) : While I may be in general agreement with the reasoning of the majority, in that the net money result to Safeway is the same (not considering attorneys’ fees in this or the previous case), either on affirmance or after remand and an assumed successful prosecution of the action, I am of opinion we have not taken the proper " == "376fd23dfbb94ec6aefe73727dc370e26d07acfa"
#guard hex " of exposure. ¶ 43. We conclude that the circuit court properly issued its order compelling Care Concepts to answer the interrogatories filed by Crawford. The information sought pertaining to aggressive or assaultive behavior by D.D. is not protected by the physician-patient privilege. Additionally, the order of the circuit court on this matter was a lawful order under Wis. Stat. § 146.82(2)(a)4. By the Court. — The decision of the court of appeals is affirmed, and the cause remanded to the circuit court. Crawford, v. Care Concepts, Inc., 2000 WI App 59, 233 Wis. 2d 609, 608 N.W.2d 694. All subsequent references to the Wisconsin Statutes are to the 1997-98 version, -unless otherwise indicated. We note that Care Concepts does not dispute the relevance of the information sought by Crawford. The privilege set forth in Wis. Stat. § 905.04(2)(a) protects communications between a patient and a variety o" == "4678c0b294d562a186e823407aebba2e816b668b"
#guard hex "B. J. CHAUVIN, Sr.\"] source_url: \"https://static.case.law/so2d/244/cases/0609-03.json\" source: \"Caselaw Access Project (Harvard Law School Library), CC0\" cap_id: 9749032 cites_cases: [\"242 So.2d 340\"] ---  # Succession of Chauvin  ## Majority (DIXON, J.,)  In re: B. J. Chauvin, Jr. applying for certiorari, or writ of review to the Court of Appeal, Fourth Circuit, Parish of Orleans. 242 So.2d 340. Writ refused. On the facts found by the Court of Appeal, there is no error of law in its judgment. DIXON, J., is of the opinion that writs should be granted on whole case, instead of on one application only. " == "3d2bf88f413b6f84d556bb4bbb7f37573f546e19"
#guard hex "in the scope of his authority and is not covered by the provisions of W.Va.Code, 29-12A-1, et seq., is entitled to qualified immunity from personal liability for official acts if the involved conduct did not violate clearly established laws of which a reasonable official would have known. There is no immunity for an executive official whose acts are fraudulent, malicious, or otherwise oppressive. To the extent that State ex rel. Boone National Bank of Madison v. Manns, supra, is contrary, it is overruled. With regard to the immunity defense in this case, we do not make any distinction between the Governor, the Treasurer, and the Auditor. It may well be that the Governor has broader executive responsibilities than the other two officials. However, the United States Supreme Court in Scheuer v. Rhodes, supra, extended only a qualified immunity to the Governor of Ohio in a Section 1983 case. As we hav" == "a5af002110527b51144dd0b146d61d9abbf84d0d"

end CaseLaw2.Sha1
