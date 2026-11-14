// Lean compiler output
// Module: BasisMain
// Imports: public import Init public meta import Init public import Std
#include <lean/lean.h>
#if defined(__clang__)
#pragma clang diagnostic ignored "-Wunused-parameter"
#pragma clang diagnostic ignored "-Wunused-label"
#elif defined(__GNUC__) && !defined(__CLANG__)
#pragma GCC diagnostic ignored "-Wunused-parameter"
#pragma GCC diagnostic ignored "-Wunused-label"
#pragma GCC diagnostic ignored "-Wunused-but-set-variable"
#endif
#ifdef __cplusplus
extern "C" {
#endif
lean_object* l_List_get_x3fInternal___redArg(lean_object*, lean_object*);
uint8_t lean_nat_dec_lt(lean_object*, lean_object*);
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
lean_object* lean_nat_mul(lean_object*, lean_object*);
lean_object* lean_nat_div(lean_object*, lean_object*);
lean_object* lean_nat_sub(lean_object*, lean_object*);
lean_object* lean_nat_to_int(lean_object*);
lean_object* lean_int_add(lean_object*, lean_object*);
lean_object* lean_nat_add(lean_object*, lean_object*);
uint8_t lean_nat_dec_le(lean_object*, lean_object*);
lean_object* lean_int_neg(lean_object*);
lean_object* lean_mk_empty_array_with_capacity(lean_object*);
lean_object* l___private_Init_Data_List_Impl_0__List_setTR_go___redArg(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* l_List_reverse___redArg(lean_object*);
lean_object* lean_int_sub(lean_object*, lean_object*);
lean_object* l_Int_toNat(lean_object*);
uint8_t lean_int_dec_lt(lean_object*, lean_object*);
uint8_t lean_int_dec_le(lean_object*, lean_object*);
lean_object* l_List_get_x21Internal___redArg(lean_object*, lean_object*, lean_object*);
lean_object* l_Nat_reprFast(lean_object*);
lean_object* lean_string_append(lean_object*, lean_object*);
lean_object* lean_array_get_size(lean_object*);
uint64_t lean_string_hash(lean_object*);
uint64_t lean_uint64_shift_right(uint64_t, uint64_t);
uint64_t lean_uint64_xor(uint64_t, uint64_t);
size_t lean_uint64_to_usize(uint64_t);
size_t lean_usize_of_nat(lean_object*);
size_t lean_usize_sub(size_t, size_t);
size_t lean_usize_land(size_t, size_t);
lean_object* lean_array_uget_borrowed(lean_object*, size_t);
uint8_t lean_string_dec_eq(lean_object*, lean_object*);
lean_object* lean_array_uset(lean_object*, size_t, lean_object*);
lean_object* lean_mk_array(lean_object*, lean_object*);
lean_object* lean_array_propagate_mark(lean_object*, lean_object*);
lean_object* lean_array_fget(lean_object*, lean_object*);
lean_object* lean_array_fset(lean_object*, lean_object*, lean_object*);
uint64_t lean_uint64_mix_hash(uint64_t, uint64_t);
uint64_t lean_uint64_of_nat(lean_object*);
lean_object* lean_nat_abs(lean_object*);
uint8_t lean_int_dec_eq(lean_object*, lean_object*);
lean_object* lean_array_push(lean_object*, lean_object*);
lean_object* l_String_intercalate(lean_object*, lean_object*);
uint8_t lean_string_dec_lt(lean_object*, lean_object*);
lean_object* lean_string_push(lean_object*, uint32_t);
lean_object* lean_get_stdout();
lean_object* l_List_zipIdxTR___redArg(lean_object*, lean_object*);
size_t lean_array_size(lean_object*);
size_t lean_usize_add(size_t, size_t);
uint8_t lean_usize_dec_lt(size_t, size_t);
lean_object* lean_array_uget(lean_object*, size_t);
lean_object* l_Int_repr(lean_object*);
uint8_t lean_usize_dec_eq(size_t, size_t);
lean_object* lean_array_fswap(lean_object*, lean_object*, lean_object*);
lean_object* lean_array_fget_borrowed(lean_object*, lean_object*);
lean_object* lean_string_length(lean_object*);
lean_object* lean_nat_shiftr(lean_object*, lean_object*);
lean_object* l_List_lengthTR___redArg(lean_object*);
lean_object* l_List_range(lean_object*);
lean_object* lean_array_to_list(lean_object*);
lean_object* l_List_foldl___at___00Array_appendList_spec__0___redArg(lean_object*, lean_object*);
lean_object* l_List_appendTR___redArg(lean_object*, lean_object*);
lean_object* lean_mk_empty_array_with_capacity(lean_object*);
lean_object* l_Repr_addAppParen(lean_object*, lean_object*);
lean_object* lean_string_length(lean_object*);
lean_object* l_List_replicateTR___redArg(lean_object*, lean_object*);
uint8_t lean_nat_dec_le(lean_object*, lean_object*);
lean_object* l_Bool_repr___redArg(uint8_t);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_ctorIdx(uint8_t);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_ctorIdx___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_ctorElim___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_ctorElim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_ctorElim(lean_object*, lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_ctorElim___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_T_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_T_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_T_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_T_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_S_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_S_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_S_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_S_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_K_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_K_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_K_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_K_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_A_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_A_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_A_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_A_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_P_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_P_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_P_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_P_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instBEqWho_beq(uint8_t, uint8_t);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instBEqWho_beq___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Legal_USTax_Hunt_Basis_instBEqWho___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Legal_USTax_Hunt_Basis_instBEqWho_beq___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Legal_USTax_Hunt_Basis_instBEqWho___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instBEqWho___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_instBEqWho = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instBEqWho___closed__0_value;
LEAN_EXPORT uint64_t l_Legal_USTax_Hunt_Basis_instHashableWho_hash(uint8_t);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instHashableWho_hash___boxed(lean_object*);
static const lean_closure_object l_Legal_USTax_Hunt_Basis_instHashableWho___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Legal_USTax_Hunt_Basis_instHashableWho_hash___boxed, .m_arity = 1, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Legal_USTax_Hunt_Basis_instHashableWho___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instHashableWho___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_instHashableWho = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instHashableWho___closed__0_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 29, .m_capacity = 29, .m_length = 28, .m_data = "Legal.USTax.Hunt.Basis.Who.T"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__0_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__0_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__1 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__1_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 29, .m_capacity = 29, .m_length = 28, .m_data = "Legal.USTax.Hunt.Basis.Who.S"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__2 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__2_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__2_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__3 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__3_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 29, .m_capacity = 29, .m_length = 28, .m_data = "Legal.USTax.Hunt.Basis.Who.K"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__4 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__4_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__4_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__5 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__5_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 29, .m_capacity = 29, .m_length = 28, .m_data = "Legal.USTax.Hunt.Basis.Who.A"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__6 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__6_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__6_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__7 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__7_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 29, .m_capacity = 29, .m_length = 28, .m_data = "Legal.USTax.Hunt.Basis.Who.P"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__8 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__8_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__8_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__9 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__9_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprWho_repr(uint8_t, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprWho_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Legal_USTax_Hunt_Basis_instReprWho___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Legal_USTax_Hunt_Basis_instReprWho_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprWho___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprWho___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_instReprWho = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprWho___closed__0_value;
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_Who_ofNat(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_ofNat___boxed(lean_object*);
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instDecidableEqWho(uint8_t, uint8_t);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instDecidableEqWho___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instInhabitedWho_default;
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instInhabitedWho;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_ctorIdx(uint8_t);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_ctorIdx___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_ctorElim___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_ctorElim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_ctorElim(lean_object*, lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_ctorElim___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_stock_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_stock_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_stock_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_stock_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_qsbs_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_qsbs_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_qsbs_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_qsbs_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_home_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_home_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_home_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_home_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instBEqKind_beq(uint8_t, uint8_t);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instBEqKind_beq___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Legal_USTax_Hunt_Basis_instBEqKind___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Legal_USTax_Hunt_Basis_instBEqKind_beq___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Legal_USTax_Hunt_Basis_instBEqKind___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instBEqKind___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_instBEqKind = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instBEqKind___closed__0_value;
LEAN_EXPORT uint64_t l_Legal_USTax_Hunt_Basis_instHashableKind_hash(uint8_t);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instHashableKind_hash___boxed(lean_object*);
static const lean_closure_object l_Legal_USTax_Hunt_Basis_instHashableKind___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Legal_USTax_Hunt_Basis_instHashableKind_hash___boxed, .m_arity = 1, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Legal_USTax_Hunt_Basis_instHashableKind___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instHashableKind___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_instHashableKind = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instHashableKind___closed__0_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 34, .m_capacity = 34, .m_length = 33, .m_data = "Legal.USTax.Hunt.Basis.Kind.stock"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__0_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__0_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__1 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__1_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 33, .m_capacity = 33, .m_length = 32, .m_data = "Legal.USTax.Hunt.Basis.Kind.qsbs"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__2 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__2_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__2_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__3 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__3_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 33, .m_capacity = 33, .m_length = 32, .m_data = "Legal.USTax.Hunt.Basis.Kind.home"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__4 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__4_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__4_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__5 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__5_value;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprKind_repr(uint8_t, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprKind_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Legal_USTax_Hunt_Basis_instReprKind___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Legal_USTax_Hunt_Basis_instReprKind_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprKind___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprKind___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_instReprKind = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprKind___closed__0_value;
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_Kind_ofNat(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_ofNat___boxed(lean_object*);
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instDecidableEqKind(uint8_t, uint8_t);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instDecidableEqKind___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instInhabitedKind_default;
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instInhabitedKind;
static const lean_string_object l_Legal_USTax_Hunt_Basis_Who_name___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "T"};
static const lean_object* l_Legal_USTax_Hunt_Basis_Who_name___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_Who_name___closed__0_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_Who_name___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "S"};
static const lean_object* l_Legal_USTax_Hunt_Basis_Who_name___closed__1 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_Who_name___closed__1_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_Who_name___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "K"};
static const lean_object* l_Legal_USTax_Hunt_Basis_Who_name___closed__2 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_Who_name___closed__2_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_Who_name___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "A"};
static const lean_object* l_Legal_USTax_Hunt_Basis_Who_name___closed__3 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_Who_name___closed__3_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_Who_name___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "P"};
static const lean_object* l_Legal_USTax_Hunt_Basis_Who_name___closed__4 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_Who_name___closed__4_value;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_name(uint8_t);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_name___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_idx(uint8_t);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_idx___boxed(lean_object*);
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_spouses(uint8_t, uint8_t);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_spouses___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_related267(uint8_t, uint8_t);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_related267___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Option_instBEq_beq___at___00Legal_USTax_Hunt_Basis_instBEqLot_beq_spec__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Option_instBEq_beq___at___00Legal_USTax_Hunt_Basis_instBEqLot_beq_spec__0___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instBEqLot_beq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instBEqLot_beq___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Legal_USTax_Hunt_Basis_instBEqLot___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Legal_USTax_Hunt_Basis_instBEqLot_beq___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Legal_USTax_Hunt_Basis_instBEqLot___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instBEqLot___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_instBEqLot = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instBEqLot___closed__0_value;
LEAN_EXPORT uint64_t l_Legal_USTax_Hunt_Basis_instHashableLot_hash(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instHashableLot_hash___boxed(lean_object*);
static const lean_closure_object l_Legal_USTax_Hunt_Basis_instHashableLot___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Legal_USTax_Hunt_Basis_instHashableLot_hash___boxed, .m_arity = 1, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Legal_USTax_Hunt_Basis_instHashableLot___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instHashableLot___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_instHashableLot = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instHashableLot___closed__0_value;
static const lean_string_object l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "none"};
static const lean_object* l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0___closed__0 = (const lean_object*)&l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0___closed__0_value;
static const lean_ctor_object l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0___closed__0_value)}};
static const lean_object* l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0___closed__1 = (const lean_object*)&l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0___closed__1_value;
static const lean_string_object l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "some "};
static const lean_object* l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0___closed__2 = (const lean_object*)&l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0___closed__2_value;
static const lean_ctor_object l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0___closed__2_value)}};
static const lean_object* l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0___closed__3 = (const lean_object*)&l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0___closed__3_value;
LEAN_EXPORT lean_object* l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0___boxed(lean_object*, lean_object*);
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "{ "};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__0_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "kind"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__1 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__1_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__1_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__2 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__2_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__2_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__3 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__3_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = " := "};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__4 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__4_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__4_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__5 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__5_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__3_value),((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__5_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__6 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__6_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__7;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = ","};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__8 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__8_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__8_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__9 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__9_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "owner"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__10 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__10_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__10_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__11 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__11_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__12_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__12;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "fmv"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__13 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__13_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__13_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__14 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__14_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__15_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__15;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "basis"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__16 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__16_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__17_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__16_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__17 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__17_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__18_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "lossBasis"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__18 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__18_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__19_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__18_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__19 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__19_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__20_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__20;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__21_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "held"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__21 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__21_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__22_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__21_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__22 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__22_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__23_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "owned"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__23 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__23_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__24_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__23_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__24 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__24_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__25_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "shield"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__25 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__25_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__26_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__25_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__26 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__26_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__27_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__27;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__28_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "donor"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__28 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__28_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__29_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__28_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__29 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__29_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__30_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "giftAge"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__30 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__30_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__31_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__30_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__31 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__31_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__32_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__32;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__33_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "inherited"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__33 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__33_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__34_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__33_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__34 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__34_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__35_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "gone"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__35 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__35_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__36_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__35_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__36 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__36_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__37_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = " }"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__37 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__37_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__38_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__38;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__39_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__39;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__40_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__0_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__40 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__40_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__41_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__37_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__41 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__41_value;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Legal_USTax_Hunt_Basis_instReprLot___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Legal_USTax_Hunt_Basis_instReprLot_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_instReprLot = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot___closed__0_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instInhabitedLot_default___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*8 + 8, .m_other = 8, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(0, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instInhabitedLot_default___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instInhabitedLot_default___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_instInhabitedLot_default = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instInhabitedLot_default___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_instInhabitedLot = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instInhabitedLot_default___closed__0_value;
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instBEqRet_beq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instBEqRet_beq___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Legal_USTax_Hunt_Basis_instBEqRet___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Legal_USTax_Hunt_Basis_instBEqRet_beq___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Legal_USTax_Hunt_Basis_instBEqRet___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instBEqRet___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_instBEqRet = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instBEqRet___closed__0_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0;
LEAN_EXPORT uint64_t l_Legal_USTax_Hunt_Basis_instHashableRet_hash(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instHashableRet_hash___boxed(lean_object*);
static const lean_closure_object l_Legal_USTax_Hunt_Basis_instHashableRet___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Legal_USTax_Hunt_Basis_instHashableRet_hash___boxed, .m_arity = 1, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Legal_USTax_Hunt_Basis_instHashableRet___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instHashableRet___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_instHashableRet = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instHashableRet___closed__0_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "st"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__0_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__0_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__1 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__1_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__1_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__2 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__2_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__2_value),((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__5_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__3 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__3_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__4;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "g28"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__5 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__5_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__5_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__6 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__6_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "cfS"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__7 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__7_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__7_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__8 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__8_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "cfL"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__9 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__9_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__9_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__10 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__10_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "x121"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__11 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__11_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__11_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__12 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__12_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "xQ"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__13 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__13_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__13_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__14 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__14_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__15_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "lt"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__15 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__15_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__15_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__16 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__16_value;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Legal_USTax_Hunt_Basis_instReprRet___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Legal_USTax_Hunt_Basis_instReprRet_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprRet___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_instReprRet = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprRet___closed__0_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instInhabitedRet_default;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instInhabitedRet;
LEAN_EXPORT uint8_t l_List_beq___at___00Legal_USTax_Hunt_Basis_instBEqSt_beq_spec__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_beq___at___00Legal_USTax_Hunt_Basis_instBEqSt_beq_spec__0___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instBEqSt_beq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instBEqSt_beq___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Legal_USTax_Hunt_Basis_instBEqSt___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Legal_USTax_Hunt_Basis_instBEqSt_beq___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Legal_USTax_Hunt_Basis_instBEqSt___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instBEqSt___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_instBEqSt = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instBEqSt___closed__0_value;
LEAN_EXPORT uint64_t l_List_foldl___at___00Legal_USTax_Hunt_Basis_instHashableSt_hash_spec__0(uint64_t, lean_object*);
LEAN_EXPORT lean_object* l_List_foldl___at___00Legal_USTax_Hunt_Basis_instHashableSt_hash_spec__0___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint64_t l_Legal_USTax_Hunt_Basis_instHashableSt_hash(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instHashableSt_hash___boxed(lean_object*);
static const lean_closure_object l_Legal_USTax_Hunt_Basis_instHashableSt___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Legal_USTax_Hunt_Basis_instHashableSt_hash___boxed, .m_arity = 1, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Legal_USTax_Hunt_Basis_instHashableSt___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instHashableSt___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_instHashableSt = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instHashableSt___closed__0_value;
LEAN_EXPORT lean_object* l_List_foldl___at___00List_foldl___at___00Std_Format_joinSep___at___00List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0_spec__0_spec__1_spec__2(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_foldl___at___00Std_Format_joinSep___at___00List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0_spec__0_spec__1(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_Format_joinSep___at___00List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0_spec__0(lean_object*, lean_object*);
static const lean_string_object l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "[]"};
static const lean_object* l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__0 = (const lean_object*)&l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__0_value;
static const lean_ctor_object l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__0_value)}};
static const lean_object* l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__1 = (const lean_object*)&l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__1_value;
static const lean_string_object l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "["};
static const lean_object* l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__2 = (const lean_object*)&l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__2_value;
static const lean_ctor_object l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__9_value),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__3 = (const lean_object*)&l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__3_value;
static const lean_string_object l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "]"};
static const lean_object* l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__4 = (const lean_object*)&l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__4_value;
static lean_once_cell_t l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__5;
static lean_once_cell_t l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__6;
static const lean_ctor_object l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__2_value)}};
static const lean_object* l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__7 = (const lean_object*)&l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__7_value;
static const lean_ctor_object l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__4_value)}};
static const lean_object* l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__8 = (const lean_object*)&l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__8_value;
LEAN_EXPORT lean_object* l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg(lean_object*);
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "lots"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__0_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__0_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__1 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__1_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__1_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__2 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__2_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__2_value),((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__5_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__3 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__3_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "year"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__4 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__4_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__4_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__5 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__5_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "cur"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__6 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__6_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__6_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__7 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__7_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "pAlive"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__8 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__8_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__8_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__9 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__9_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "pFinal"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__10 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__10_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__10_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__11 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__11_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "rJ"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__12 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__12_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__12_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__13 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__13_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "rK"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__14 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__14_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__15_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__14_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__15 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__15_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "rA"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__16 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__16_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__17_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__16_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__17 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__17_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__18_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "rP"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__18 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__18_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__19_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__18_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__19 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__19_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__20_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "charCash"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__20 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__20_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__21_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__20_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__21 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__21_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__22_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__22;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__23_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "charProp"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__23 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__23_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__24_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__23_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__24 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__24_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__25_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "cfChar"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__25 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__25_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__26_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__25_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__26 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__26_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__27_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "pledge"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__27 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__27_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__28_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__27_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__28 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__28_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__29_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "tax"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__29 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__29_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__30_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__29_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__30 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__30_value;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Legal_USTax_Hunt_Basis_instReprSt___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Legal_USTax_Hunt_Basis_instReprSt_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_instReprSt = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprSt___closed__0_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_instInhabitedSt_default___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_instInhabitedSt_default___closed__0;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instInhabitedSt_default;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instInhabitedSt;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_ctorIdx(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_ctorIdx___boxed(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_ctorElim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_ctorElim(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_ctorElim___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_sell_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_sell_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_gift_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_gift_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_sellTo_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_sellTo_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_donate_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_donate_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_donateCash_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_donateCash_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_die_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_die_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_nextYear_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_nextYear_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instBEqMove_beq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instBEqMove_beq___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Legal_USTax_Hunt_Basis_instBEqMove___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Legal_USTax_Hunt_Basis_instBEqMove_beq___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Legal_USTax_Hunt_Basis_instBEqMove___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instBEqMove___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_instBEqMove = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instBEqMove___closed__0_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 39, .m_capacity = 39, .m_length = 38, .m_data = "Legal.USTax.Hunt.Basis.Move.donateCash"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__0_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__0_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__1 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__1_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 37, .m_capacity = 37, .m_length = 36, .m_data = "Legal.USTax.Hunt.Basis.Move.nextYear"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__2 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__2_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__2_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__3 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__3_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 33, .m_capacity = 33, .m_length = 32, .m_data = "Legal.USTax.Hunt.Basis.Move.sell"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__4 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__4_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__4_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__5 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__5_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__5_value),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__6 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__6_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 33, .m_capacity = 33, .m_length = 32, .m_data = "Legal.USTax.Hunt.Basis.Move.gift"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__7 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__7_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__7_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__8 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__8_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__8_value),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__9 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__9_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 35, .m_capacity = 35, .m_length = 34, .m_data = "Legal.USTax.Hunt.Basis.Move.sellTo"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__10 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__10_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__10_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__11 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__11_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__11_value),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__12 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__12_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 35, .m_capacity = 35, .m_length = 34, .m_data = "Legal.USTax.Hunt.Basis.Move.donate"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__13 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__13_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__13_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__14 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__14_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__15_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__14_value),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__15 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__15_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 32, .m_capacity = 32, .m_length = 31, .m_data = "Legal.USTax.Hunt.Basis.Move.die"};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__16 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__16_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__17_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__16_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__17 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__17_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__18_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__17_value),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__18 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__18_value;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Legal_USTax_Hunt_Basis_instReprMove___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Legal_USTax_Hunt_Basis_instReprMove_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_instReprMove = (const lean_object*)&l_Legal_USTax_Hunt_Basis_instReprMove___closed__0_value;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_big;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_mfj___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(24800) << 1) | 1)),((lean_object*)(((size_t)(10) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_mfj___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_mfj___closed__0_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_mfj___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(100800) << 1) | 1)),((lean_object*)(((size_t)(12) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_mfj___closed__1 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_mfj___closed__1_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_mfj___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(211400) << 1) | 1)),((lean_object*)(((size_t)(22) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_mfj___closed__2 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_mfj___closed__2_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_mfj___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(403550) << 1) | 1)),((lean_object*)(((size_t)(24) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_mfj___closed__3 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_mfj___closed__3_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_mfj___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(512450) << 1) | 1)),((lean_object*)(((size_t)(32) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_mfj___closed__4 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_mfj___closed__4_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_mfj___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(768700) << 1) | 1)),((lean_object*)(((size_t)(35) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_mfj___closed__5 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_mfj___closed__5_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_mfj___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_mfj___closed__6;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_mfj___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_mfj___closed__7;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_mfj___closed__8_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_mfj___closed__8;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_mfj___closed__9_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_mfj___closed__9;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_mfj___closed__10_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_mfj___closed__10;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_mfj___closed__11_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_mfj___closed__11;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_mfj___closed__12_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_mfj___closed__12;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_mfj___closed__13_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_mfj___closed__13;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_mfj___closed__14_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_mfj___closed__14;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_mfj;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_single___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(12400) << 1) | 1)),((lean_object*)(((size_t)(10) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_single___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_single___closed__0_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_single___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(50400) << 1) | 1)),((lean_object*)(((size_t)(12) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_single___closed__1 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_single___closed__1_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_single___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(105700) << 1) | 1)),((lean_object*)(((size_t)(22) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_single___closed__2 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_single___closed__2_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_single___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(201775) << 1) | 1)),((lean_object*)(((size_t)(24) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_single___closed__3 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_single___closed__3_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_single___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(256225) << 1) | 1)),((lean_object*)(((size_t)(32) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_single___closed__4 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_single___closed__4_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_single___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(640600) << 1) | 1)),((lean_object*)(((size_t)(35) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_single___closed__5 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_single___closed__5_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_single___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_single___closed__6;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_single___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_single___closed__7;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_single___closed__8_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_single___closed__8;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_single___closed__9_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_single___closed__9;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_single___closed__10_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_single___closed__10;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_single___closed__11_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_single___closed__11;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_single___closed__12_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_single___closed__12;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_single;
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_ordTax_spec__0___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_ordTax_spec__0___redArg___boxed(lean_object*, lean_object*, lean_object*);
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_ordTax___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_ordTax___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_ordTax___closed__0_value;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_ordTax(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_ordTax___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_ordTax_spec__0(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_ordTax_spec__0___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_fullTax(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_fullTax___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_capNet(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_tiParts(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_tiParts___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_retTax(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_retTax___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_agiOf(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_agiOf___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_stdSingle;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_stdAged;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_seniorDed;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_stdDependent;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_giftExcl;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_qCap;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_top37;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_getRet(lean_object*, uint8_t);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_getRet___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_setRet(lean_object*, uint8_t, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_setRet___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_alive(lean_object*, uint8_t);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_alive___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_addGain(lean_object*, uint8_t, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_addGain___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_List_elem___at___00Legal_USTax_Hunt_Basis_limit121_spec__0(uint8_t, lean_object*);
LEAN_EXPORT lean_object* l_List_elem___at___00Legal_USTax_Hunt_Basis_limit121_spec__0___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_limit121(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_limit121___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_recognize(lean_object*, lean_object*, lean_object*, uint8_t);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_recognize___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_zeroYear(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_zeroYear___boxed(lean_object*, lean_object*);
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_deadLot___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*8 + 8, .m_other = 8, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(1) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(0, 0, 0, 1, 0, 0, 0, 0)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_deadLot___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_deadLot___closed__0_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_deadLot = (const lean_object*)&l_Legal_USTax_Hunt_Basis_deadLot___closed__0_value;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_norm(lean_object*, uint8_t, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_norm___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_mapTR_loop___at___00Legal_USTax_Hunt_Basis_closeYear_spec__0(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_mapTR_loop___at___00Legal_USTax_Hunt_Basis_closeYear_spec__0___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_closeYear(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_closeYear___boxed(lean_object*, lean_object*);
static const lean_array_object l_Legal_USTax_Hunt_Basis_touch___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_array_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 246}, .m_size = 0, .m_capacity = 0, .m_data = {}};
static const lean_object* l_Legal_USTax_Hunt_Basis_touch___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_touch___closed__0_value;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_touch(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_touch___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Option_instBEq_beq___at___00Legal_USTax_Hunt_Basis_step_spec__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Option_instBEq_beq___at___00Legal_USTax_Hunt_Basis_step_spec__0___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_mapTR_loop___at___00Legal_USTax_Hunt_Basis_step_spec__1(uint8_t, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_mapTR_loop___at___00Legal_USTax_Hunt_Basis_step_spec__1___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_mapTR_loop___at___00Legal_USTax_Hunt_Basis_step_spec__2(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_mapTR_loop___at___00Legal_USTax_Hunt_Basis_step_spec__2___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_List_any___at___00Legal_USTax_Hunt_Basis_step_spec__3(lean_object*, lean_object*, uint8_t, lean_object*);
LEAN_EXPORT lean_object* l_List_any___at___00Legal_USTax_Hunt_Basis_step_spec__3___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_step(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_step___boxed(lean_object*, lean_object*, lean_object*);
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_people___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(4) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_people___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_people___closed__0_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_people___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(3) << 1) | 1)),((lean_object*)&l_Legal_USTax_Hunt_Basis_people___closed__0_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_people___closed__1 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_people___closed__1_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_people___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(2) << 1) | 1)),((lean_object*)&l_Legal_USTax_Hunt_Basis_people___closed__1_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_people___closed__2 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_people___closed__2_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_people___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(1) << 1) | 1)),((lean_object*)&l_Legal_USTax_Hunt_Basis_people___closed__2_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_people___closed__3 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_people___closed__3_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_people___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Legal_USTax_Hunt_Basis_people___closed__3_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_people___closed__4 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_people___closed__4_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_people = (const lean_object*)&l_Legal_USTax_Hunt_Basis_people___closed__4_value;
LEAN_EXPORT lean_object* l___private_Init_Data_List_Impl_0__List_flatMapTR_go___at___00Legal_USTax_Hunt_Basis_moves_spec__0(lean_object*, lean_object*, lean_object*);
static const lean_array_object l___private_Init_Data_List_Impl_0__List_flatMapTR_go___at___00Legal_USTax_Hunt_Basis_moves_spec__1___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_array_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 246}, .m_size = 0, .m_capacity = 0, .m_data = {}};
static const lean_object* l___private_Init_Data_List_Impl_0__List_flatMapTR_go___at___00Legal_USTax_Hunt_Basis_moves_spec__1___closed__0 = (const lean_object*)&l___private_Init_Data_List_Impl_0__List_flatMapTR_go___at___00Legal_USTax_Hunt_Basis_moves_spec__1___closed__0_value;
LEAN_EXPORT lean_object* l___private_Init_Data_List_Impl_0__List_flatMapTR_go___at___00Legal_USTax_Hunt_Basis_moves_spec__1(lean_object*, lean_object*);
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_moves___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*0 + 8, .m_other = 0, .m_tag = 5}, .m_objs = {LEAN_SCALAR_PTR_LITERAL(0, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_moves___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_moves___closed__0_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_moves___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*0 + 8, .m_other = 0, .m_tag = 5}, .m_objs = {LEAN_SCALAR_PTR_LITERAL(3, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_moves___closed__1 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_moves___closed__1_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_moves___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*0 + 8, .m_other = 0, .m_tag = 5}, .m_objs = {LEAN_SCALAR_PTR_LITERAL(2, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_moves___closed__2 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_moves___closed__2_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_moves___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(6) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_moves___closed__3 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_moves___closed__3_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_moves___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_moves___closed__2_value),((lean_object*)&l_Legal_USTax_Hunt_Basis_moves___closed__3_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_moves___closed__4 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_moves___closed__4_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_moves___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_moves___closed__1_value),((lean_object*)&l_Legal_USTax_Hunt_Basis_moves___closed__4_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_moves___closed__5 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_moves___closed__5_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_moves___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_moves___closed__0_value),((lean_object*)&l_Legal_USTax_Hunt_Basis_moves___closed__5_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_moves___closed__6 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_moves___closed__6_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_moves___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(4) << 1) | 1)),((lean_object*)&l_Legal_USTax_Hunt_Basis_moves___closed__6_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_moves___closed__7 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_moves___closed__7_value;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_moves(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_moves___boxed(lean_object*);
static const lean_string_object l_Legal_USTax_Hunt_Basis_kindName___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "stock"};
static const lean_object* l_Legal_USTax_Hunt_Basis_kindName___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_kindName___closed__0_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_kindName___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "QSBS"};
static const lean_object* l_Legal_USTax_Hunt_Basis_kindName___closed__1 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_kindName___closed__1_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_kindName___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "home"};
static const lean_object* l_Legal_USTax_Hunt_Basis_kindName___closed__2 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_kindName___closed__2_value;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_kindName(uint8_t);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_kindName___boxed(lean_object*);
static const lean_string_object l_Legal_USTax_Hunt_Basis_describe___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "y"};
static const lean_object* l_Legal_USTax_Hunt_Basis_describe___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_describe___closed__0_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_describe___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = " "};
static const lean_object* l_Legal_USTax_Hunt_Basis_describe___closed__1 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_describe___closed__1_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_describe___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = " sells #"};
static const lean_object* l_Legal_USTax_Hunt_Basis_describe___closed__2 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_describe___closed__2_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_describe___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = " sells"};
static const lean_object* l_Legal_USTax_Hunt_Basis_describe___closed__3 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_describe___closed__3_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_describe___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = " gives #"};
static const lean_object* l_Legal_USTax_Hunt_Basis_describe___closed__4 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_describe___closed__4_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_describe___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = " to "};
static const lean_object* l_Legal_USTax_Hunt_Basis_describe___closed__5 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_describe___closed__5_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_describe___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 1, .m_data = "→"};
static const lean_object* l_Legal_USTax_Hunt_Basis_describe___closed__6 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_describe___closed__6_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_describe___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = " gift"};
static const lean_object* l_Legal_USTax_Hunt_Basis_describe___closed__7 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_describe___closed__7_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_describe___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = " sale"};
static const lean_object* l_Legal_USTax_Hunt_Basis_describe___closed__8 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_describe___closed__8_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_describe___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = " donate #"};
static const lean_object* l_Legal_USTax_Hunt_Basis_describe___closed__9 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_describe___closed__9_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_describe___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 16, .m_capacity = 16, .m_length = 15, .m_data = "donate property"};
static const lean_object* l_Legal_USTax_Hunt_Basis_describe___closed__10 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_describe___closed__10_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_describe___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = " donate cash"};
static const lean_object* l_Legal_USTax_Hunt_Basis_describe___closed__11 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_describe___closed__11_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_describe___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "donate cash"};
static const lean_object* l_Legal_USTax_Hunt_Basis_describe___closed__12 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_describe___closed__12_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_describe___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 15, .m_capacity = 15, .m_length = 14, .m_data = " P dies, heir "};
static const lean_object* l_Legal_USTax_Hunt_Basis_describe___closed__13 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_describe___closed__13_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_describe___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "heir "};
static const lean_object* l_Legal_USTax_Hunt_Basis_describe___closed__14 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_describe___closed__14_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_describe___closed__15_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 1, .m_capacity = 1, .m_length = 0, .m_data = ""};
static const lean_object* l_Legal_USTax_Hunt_Basis_describe___closed__15 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_describe___closed__15_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_describe___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)&l_Legal_USTax_Hunt_Basis_describe___closed__15_value),((lean_object*)&l_Legal_USTax_Hunt_Basis_describe___closed__15_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_describe___closed__16 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_describe___closed__16_value;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_describe(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_giftOver(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_giftOver___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_insertSorted(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_foldlM___at___00Legal_USTax_Hunt_Basis_runPath_spec__0(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_foldlM___at___00Legal_USTax_Hunt_Basis_runPath_spec__0___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_runPath(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_runPath___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__0___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__0___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__1___redArg(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__1___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_baseline(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_baseline___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__0(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__0___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__1(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__1___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT uint8_t l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11___redArg___lam__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11___redArg___lam__0___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Array_QSort_Basic_0__Array_qpartition_loop___at___00__private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11_spec__19___redArg(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Array_QSort_Basic_0__Array_qpartition_loop___at___00__private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11_spec__19___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2_spec__3___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2_spec__3___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_foldlM___at___00__private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3_spec__5_spec__6_spec__17___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3_spec__5_spec__6___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3_spec__5___redArg(lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_replace___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__9___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_foldlM___at___00__private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__8_spec__10_spec__21___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__8_spec__10___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__8___redArg(lean_object*);
LEAN_EXPORT uint8_t l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__7___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__7___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_get_x3f___at___00Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5_spec__11___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_get_x3f___at___00Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5_spec__11___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2___redArg___boxed(lean_object*, lean_object*);
static const lean_string_object l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__6___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = ", "};
static const lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__6___redArg___closed__0 = (const lean_object*)&l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__6___redArg___closed__0_value;
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__6___redArg(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__6___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__7(lean_object*, lean_object*, lean_object*, size_t, size_t, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__7___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
static const lean_array_object l___private_Init_While_0__repeatM_erased___at___00Legal_USTax_Hunt_Basis_search_spec__8___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_array_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 246}, .m_size = 0, .m_capacity = 0, .m_data = {}};
static const lean_object* l___private_Init_While_0__repeatM_erased___at___00Legal_USTax_Hunt_Basis_search_spec__8___redArg___closed__0 = (const lean_object*)&l___private_Init_While_0__repeatM_erased___at___00Legal_USTax_Hunt_Basis_search_spec__8___redArg___closed__0_value;
LEAN_EXPORT lean_object* l___private_Init_While_0__repeatM_erased___at___00Legal_USTax_Hunt_Basis_search_spec__8___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_While_0__repeatM_erased___at___00Legal_USTax_Hunt_Basis_search_spec__8___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_IO_print___at___00IO_println___at___00Legal_USTax_Hunt_Basis_search_spec__0_spec__0(lean_object*);
LEAN_EXPORT lean_object* l_IO_print___at___00IO_println___at___00Legal_USTax_Hunt_Basis_search_spec__0_spec__0___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_IO_println___at___00Legal_USTax_Hunt_Basis_search_spec__0(lean_object*);
LEAN_EXPORT lean_object* l_IO_println___at___00Legal_USTax_Hunt_Basis_search_spec__0___boxed(lean_object*, lean_object*);
static const lean_string_object l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "  #"};
static const lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__0 = (const lean_object*)&l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__0_value;
static const lean_string_object l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = " of "};
static const lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__1 = (const lean_object*)&l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__1_value;
static const lean_string_object l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = ": value "};
static const lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__2 = (const lean_object*)&l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__2_value;
static const lean_string_object l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = ", basis "};
static const lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__3 = (const lean_object*)&l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__3_value;
static const lean_string_object l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = ", held "};
static const lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__4 = (const lean_object*)&l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__4_value;
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_foldlMUnsafe_fold___at___00Legal_USTax_Hunt_Basis_search_spec__9(lean_object*, lean_object*, size_t, size_t, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_foldlMUnsafe_fold___at___00Legal_USTax_Hunt_Basis_search_spec__9___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
static const lean_string_object l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "tax "};
static const lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__0 = (const lean_object*)&l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__0_value;
static const lean_string_object l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = " (saves "};
static const lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__1 = (const lean_object*)&l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__1_value;
static const lean_string_object l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 28, .m_capacity = 28, .m_length = 27, .m_data = "; gifts over the exclusion "};
static const lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__2 = (const lean_object*)&l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__2_value;
static const lean_string_object l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 29, .m_capacity = 29, .m_length = 28, .m_data = "; joint loss carryover left "};
static const lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__3 = (const lean_object*)&l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__3_value;
static const lean_string_object l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "; "};
static const lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__4 = (const lean_object*)&l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__4_value;
static const lean_string_object l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = " families)  ["};
static const lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__5 = (const lean_object*)&l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__5_value;
static const lean_string_object l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "    "};
static const lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__6 = (const lean_object*)&l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__6_value;
static const lean_array_object l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_array_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 246}, .m_size = 0, .m_capacity = 0, .m_data = {}};
static const lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__7 = (const lean_object*)&l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__7_value;
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17(lean_object*, lean_object*, lean_object*, lean_object*, size_t, size_t, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10(lean_object*, lean_object*, lean_object*, lean_object*, size_t, size_t, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_foldlM___at___00Legal_USTax_Hunt_Basis_search_spec__12(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_foldlM___at___00Legal_USTax_Hunt_Basis_search_spec__12___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_foldlMUnsafe_fold___at___00Legal_USTax_Hunt_Basis_search_spec__13(lean_object*, size_t, size_t, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_foldlMUnsafe_fold___at___00Legal_USTax_Hunt_Basis_search_spec__13___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
static const lean_string_object l_Legal_USTax_Hunt_Basis_search___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "\n===== "};
static const lean_object* l_Legal_USTax_Hunt_Basis_search___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_search___closed__0_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_search___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = " ====="};
static const lean_object* l_Legal_USTax_Hunt_Basis_search___closed__1 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_search___closed__1_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_search___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_search___closed__2;
static const lean_string_object l_Legal_USTax_Hunt_Basis_search___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 40, .m_capacity = 40, .m_length = 39, .m_data = "baseline (owners sell, will to T): tax "};
static const lean_object* l_Legal_USTax_Hunt_Basis_search___closed__3 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_search___closed__3_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_search___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_search___closed__4 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_search___closed__4_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_search___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Legal_USTax_Hunt_Basis_search___closed__4_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_search___closed__5 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_search___closed__5_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_search___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_search___closed__6;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_search___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_search___closed__7;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_search___closed__8_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_search___closed__8;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_search___closed__9_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_search___closed__9;
static const lean_string_object l_Legal_USTax_Hunt_Basis_search___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "positions "};
static const lean_object* l_Legal_USTax_Hunt_Basis_search___closed__10 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_search___closed__10_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_search___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 18, .m_capacity = 18, .m_length = 17, .m_data = ", finished plans "};
static const lean_object* l_Legal_USTax_Hunt_Basis_search___closed__11 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_search___closed__11_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_search___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = ", families "};
static const lean_object* l_Legal_USTax_Hunt_Basis_search___closed__12 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_search___closed__12_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_search___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = ", depth "};
static const lean_object* l_Legal_USTax_Hunt_Basis_search___closed__13 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_search___closed__13_value;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_search(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_search___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__6(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__6___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_While_0__repeatM_erased___at___00Legal_USTax_Hunt_Basis_search_spec__8(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_While_0__repeatM_erased___at___00Legal_USTax_Hunt_Basis_search_spec__8___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2_spec__3(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2_spec__3___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3_spec__5(lean_object*, lean_object*);
LEAN_EXPORT uint8_t l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__7(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__7___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__8(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_replace___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__9(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_get_x3f___at___00Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5_spec__11(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_get_x3f___at___00Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5_spec__11___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Array_QSort_Basic_0__Array_qpartition_loop___at___00__private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11_spec__19(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Init_Data_Array_QSort_Basic_0__Array_qpartition_loop___at___00__private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11_spec__19___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3_spec__5_spec__6(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l___private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__8_spec__10(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_foldlM___at___00__private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3_spec__5_spec__6_spec__17(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_foldlM___at___00__private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__8_spec__10_spec__21(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_lot(uint8_t, uint8_t, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_lot___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_mk(lean_object*, lean_object*, lean_object*);
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_cfg0___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(2) << 1) | 1)),((lean_object*)&l_Legal_USTax_Hunt_Basis_people___closed__0_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_cfg0___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_cfg0___closed__0_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_cfg0___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(1) << 1) | 1)),((lean_object*)&l_Legal_USTax_Hunt_Basis_cfg0___closed__0_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_cfg0___closed__1 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_cfg0___closed__1_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_cfg0___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&l_Legal_USTax_Hunt_Basis_cfg0___closed__1_value)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_cfg0___closed__2 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_cfg0___closed__2_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_cfg0___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*6 + 8, .m_other = 6, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(450000) << 1) | 1)),((lean_object*)(((size_t)(40000) << 1) | 1)),((lean_object*)(((size_t)(30000) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(2) << 1) | 1)),((lean_object*)&l_Legal_USTax_Hunt_Basis_cfg0___closed__2_value),LEAN_SCALAR_PTR_LITERAL(0, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* l_Legal_USTax_Hunt_Basis_cfg0___closed__3 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_cfg0___closed__3_value;
LEAN_EXPORT const lean_object* l_Legal_USTax_Hunt_Basis_cfg0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_cfg0___closed__3_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc1___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc1___closed__0;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc1___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc1___closed__1;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc1___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc1___closed__2;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc1___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc1___closed__3;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc1___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc1___closed__4;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc1___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc1___closed__5;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc1___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc1___closed__6;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_sc1;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc2___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc2___closed__0;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc2___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc2___closed__1;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc2___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc2___closed__2;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc2___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc2___closed__3;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc2___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc2___closed__4;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc2___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc2___closed__5;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc2___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc2___closed__6;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_sc2;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc3___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc3___closed__0;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc3___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc3___closed__1;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_sc3;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc4___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc4___closed__0;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_sc4(lean_object*);
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc5___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc5___closed__0;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_sc5(lean_object*);
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc6___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc6___closed__0;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc6___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc6___closed__1;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc6___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc6___closed__2;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc6___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc6___closed__3;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc6___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc6___closed__4;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_sc6___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_sc6___closed__5;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_sc6;
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_all___redArg();
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_all___redArg___boxed(lean_object*);
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_all(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_all___boxed(lean_object*);
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_small___lam__0(lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_small___lam__0___boxed(lean_object*);
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_small___lam__1(uint8_t, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_small___lam__1___boxed(lean_object*, lean_object*);
static const lean_closure_object l_Legal_USTax_Hunt_Basis_small___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Legal_USTax_Hunt_Basis_small___lam__0___boxed, .m_arity = 1, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* l_Legal_USTax_Hunt_Basis_small___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_small___closed__0_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_small___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 23, .m_capacity = 23, .m_length = 22, .m_data = "1. no death, two years"};
static const lean_object* l_Legal_USTax_Hunt_Basis_small___closed__1 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_small___closed__1_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_small___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 49, .m_capacity = 49, .m_length = 48, .m_data = "2a. P dies in year 0 (inside a year of any gift)"};
static const lean_object* l_Legal_USTax_Hunt_Basis_small___closed__2 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_small___closed__2_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_small___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_small___closed__3 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_small___closed__3_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_small___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 39, .m_capacity = 39, .m_length = 38, .m_data = "3. no market sale before the last year"};
static const lean_object* l_Legal_USTax_Hunt_Basis_small___closed__4 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_small___closed__4_value;
static const lean_closure_object l_Legal_USTax_Hunt_Basis_small___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*1, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_Legal_USTax_Hunt_Basis_small___lam__1___boxed, .m_arity = 2, .m_num_fixed = 1, .m_objs = {((lean_object*)(((size_t)(1) << 1) | 1))} };
static const lean_object* l_Legal_USTax_Hunt_Basis_small___closed__5 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_small___closed__5_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_small___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 33, .m_capacity = 33, .m_length = 32, .m_data = "4a. QSBS, two blocks, four years"};
static const lean_object* l_Legal_USTax_Hunt_Basis_small___closed__6 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_small___closed__6_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_small___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_small___closed__7;
static const lean_string_object l_Legal_USTax_Hunt_Basis_small___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 59, .m_capacity = 59, .m_length = 58, .m_data = "2c. one winner, P dies in year 0, and the will must name T"};
static const lean_object* l_Legal_USTax_Hunt_Basis_small___closed__8 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_small___closed__8_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_small___closed__9_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_small___closed__9;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_small___closed__10_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_small___closed__10;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_small();
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_small___boxed(lean_object*);
static const lean_string_object l_Legal_USTax_Hunt_Basis_wide___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 60, .m_capacity = 60, .m_length = 59, .m_data = "2b. P dies in year 1 (more than a year after a year-0 gift)"};
static const lean_object* l_Legal_USTax_Hunt_Basis_wide___closed__0 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_wide___closed__0_value;
static const lean_ctor_object l_Legal_USTax_Hunt_Basis_wide___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* l_Legal_USTax_Hunt_Basis_wide___closed__1 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_wide___closed__1_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_wide___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 53, .m_capacity = 53, .m_length = 52, .m_data = "4b. QSBS, three blocks, four years, P dies in year 1"};
static const lean_object* l_Legal_USTax_Hunt_Basis_wide___closed__2 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_wide___closed__2_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_wide___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_wide___closed__3;
static const lean_string_object l_Legal_USTax_Hunt_Basis_wide___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 38, .m_capacity = 38, .m_length = 37, .m_data = "5a. home in three shares, three years"};
static const lean_object* l_Legal_USTax_Hunt_Basis_wide___closed__4 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_wide___closed__4_value;
static lean_once_cell_t l_Legal_USTax_Hunt_Basis_wide___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* l_Legal_USTax_Hunt_Basis_wide___closed__5;
static const lean_string_object l_Legal_USTax_Hunt_Basis_wide___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 43, .m_capacity = 43, .m_length = 42, .m_data = "5b. home in three shares, P dies in year 0"};
static const lean_object* l_Legal_USTax_Hunt_Basis_wide___closed__6 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_wide___closed__6_value;
static const lean_string_object l_Legal_USTax_Hunt_Basis_wide___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 46, .m_capacity = 46, .m_length = 45, .m_data = "6. wider: four lots, pledge, P dies in year 1"};
static const lean_object* l_Legal_USTax_Hunt_Basis_wide___closed__7 = (const lean_object*)&l_Legal_USTax_Hunt_Basis_wide___closed__7_value;
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_wide();
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_wide___boxed(lean_object*);
LEAN_EXPORT uint8_t l_List_elem___at___00main_spec__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_List_elem___at___00main_spec__0___boxed(lean_object*, lean_object*);
static const lean_string_object l_main___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "small"};
static const lean_object* l_main___closed__0 = (const lean_object*)&l_main___closed__0_value;
LEAN_EXPORT lean_object* _lean_main(lean_object*);
LEAN_EXPORT lean_object* l_main___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_ctorIdx(uint8_t v_x_1_){
_start:
{
switch(v_x_1_)
{
case 0:
{
lean_object* v___x_2_; 
v___x_2_ = lean_unsigned_to_nat(0u);
return v___x_2_;
}
case 1:
{
lean_object* v___x_3_; 
v___x_3_ = lean_unsigned_to_nat(1u);
return v___x_3_;
}
case 2:
{
lean_object* v___x_4_; 
v___x_4_ = lean_unsigned_to_nat(2u);
return v___x_4_;
}
case 3:
{
lean_object* v___x_5_; 
v___x_5_ = lean_unsigned_to_nat(3u);
return v___x_5_;
}
default: 
{
lean_object* v___x_6_; 
v___x_6_ = lean_unsigned_to_nat(4u);
return v___x_6_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_ctorIdx___boxed(lean_object* v_x_7_){
_start:
{
uint8_t v_x_boxed_8_; lean_object* v_res_9_; 
v_x_boxed_8_ = lean_unbox(v_x_7_);
v_res_9_ = l_Legal_USTax_Hunt_Basis_Who_ctorIdx(v_x_boxed_8_);
return v_res_9_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_ctorElim___redArg(lean_object* v_k_10_){
_start:
{
lean_inc(v_k_10_);
return v_k_10_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_ctorElim___redArg___boxed(lean_object* v_k_11_){
_start:
{
lean_object* v_res_12_; 
v_res_12_ = l_Legal_USTax_Hunt_Basis_Who_ctorElim___redArg(v_k_11_);
lean_dec(v_k_11_);
return v_res_12_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_ctorElim(lean_object* v_motive_13_, lean_object* v_ctorIdx_14_, uint8_t v_t_15_, lean_object* v_h_16_, lean_object* v_k_17_){
_start:
{
lean_inc(v_k_17_);
return v_k_17_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_ctorElim___boxed(lean_object* v_motive_18_, lean_object* v_ctorIdx_19_, lean_object* v_t_20_, lean_object* v_h_21_, lean_object* v_k_22_){
_start:
{
uint8_t v_t_boxed_23_; lean_object* v_res_24_; 
v_t_boxed_23_ = lean_unbox(v_t_20_);
v_res_24_ = l_Legal_USTax_Hunt_Basis_Who_ctorElim(v_motive_18_, v_ctorIdx_19_, v_t_boxed_23_, v_h_21_, v_k_22_);
lean_dec(v_k_22_);
lean_dec(v_ctorIdx_19_);
return v_res_24_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_T_elim___redArg(lean_object* v_T_25_){
_start:
{
lean_inc(v_T_25_);
return v_T_25_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_T_elim___redArg___boxed(lean_object* v_T_26_){
_start:
{
lean_object* v_res_27_; 
v_res_27_ = l_Legal_USTax_Hunt_Basis_Who_T_elim___redArg(v_T_26_);
lean_dec(v_T_26_);
return v_res_27_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_T_elim(lean_object* v_motive_28_, uint8_t v_t_29_, lean_object* v_h_30_, lean_object* v_T_31_){
_start:
{
lean_inc(v_T_31_);
return v_T_31_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_T_elim___boxed(lean_object* v_motive_32_, lean_object* v_t_33_, lean_object* v_h_34_, lean_object* v_T_35_){
_start:
{
uint8_t v_t_boxed_36_; lean_object* v_res_37_; 
v_t_boxed_36_ = lean_unbox(v_t_33_);
v_res_37_ = l_Legal_USTax_Hunt_Basis_Who_T_elim(v_motive_32_, v_t_boxed_36_, v_h_34_, v_T_35_);
lean_dec(v_T_35_);
return v_res_37_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_S_elim___redArg(lean_object* v_S_38_){
_start:
{
lean_inc(v_S_38_);
return v_S_38_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_S_elim___redArg___boxed(lean_object* v_S_39_){
_start:
{
lean_object* v_res_40_; 
v_res_40_ = l_Legal_USTax_Hunt_Basis_Who_S_elim___redArg(v_S_39_);
lean_dec(v_S_39_);
return v_res_40_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_S_elim(lean_object* v_motive_41_, uint8_t v_t_42_, lean_object* v_h_43_, lean_object* v_S_44_){
_start:
{
lean_inc(v_S_44_);
return v_S_44_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_S_elim___boxed(lean_object* v_motive_45_, lean_object* v_t_46_, lean_object* v_h_47_, lean_object* v_S_48_){
_start:
{
uint8_t v_t_boxed_49_; lean_object* v_res_50_; 
v_t_boxed_49_ = lean_unbox(v_t_46_);
v_res_50_ = l_Legal_USTax_Hunt_Basis_Who_S_elim(v_motive_45_, v_t_boxed_49_, v_h_47_, v_S_48_);
lean_dec(v_S_48_);
return v_res_50_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_K_elim___redArg(lean_object* v_K_51_){
_start:
{
lean_inc(v_K_51_);
return v_K_51_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_K_elim___redArg___boxed(lean_object* v_K_52_){
_start:
{
lean_object* v_res_53_; 
v_res_53_ = l_Legal_USTax_Hunt_Basis_Who_K_elim___redArg(v_K_52_);
lean_dec(v_K_52_);
return v_res_53_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_K_elim(lean_object* v_motive_54_, uint8_t v_t_55_, lean_object* v_h_56_, lean_object* v_K_57_){
_start:
{
lean_inc(v_K_57_);
return v_K_57_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_K_elim___boxed(lean_object* v_motive_58_, lean_object* v_t_59_, lean_object* v_h_60_, lean_object* v_K_61_){
_start:
{
uint8_t v_t_boxed_62_; lean_object* v_res_63_; 
v_t_boxed_62_ = lean_unbox(v_t_59_);
v_res_63_ = l_Legal_USTax_Hunt_Basis_Who_K_elim(v_motive_58_, v_t_boxed_62_, v_h_60_, v_K_61_);
lean_dec(v_K_61_);
return v_res_63_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_A_elim___redArg(lean_object* v_A_64_){
_start:
{
lean_inc(v_A_64_);
return v_A_64_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_A_elim___redArg___boxed(lean_object* v_A_65_){
_start:
{
lean_object* v_res_66_; 
v_res_66_ = l_Legal_USTax_Hunt_Basis_Who_A_elim___redArg(v_A_65_);
lean_dec(v_A_65_);
return v_res_66_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_A_elim(lean_object* v_motive_67_, uint8_t v_t_68_, lean_object* v_h_69_, lean_object* v_A_70_){
_start:
{
lean_inc(v_A_70_);
return v_A_70_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_A_elim___boxed(lean_object* v_motive_71_, lean_object* v_t_72_, lean_object* v_h_73_, lean_object* v_A_74_){
_start:
{
uint8_t v_t_boxed_75_; lean_object* v_res_76_; 
v_t_boxed_75_ = lean_unbox(v_t_72_);
v_res_76_ = l_Legal_USTax_Hunt_Basis_Who_A_elim(v_motive_71_, v_t_boxed_75_, v_h_73_, v_A_74_);
lean_dec(v_A_74_);
return v_res_76_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_P_elim___redArg(lean_object* v_P_77_){
_start:
{
lean_inc(v_P_77_);
return v_P_77_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_P_elim___redArg___boxed(lean_object* v_P_78_){
_start:
{
lean_object* v_res_79_; 
v_res_79_ = l_Legal_USTax_Hunt_Basis_Who_P_elim___redArg(v_P_78_);
lean_dec(v_P_78_);
return v_res_79_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_P_elim(lean_object* v_motive_80_, uint8_t v_t_81_, lean_object* v_h_82_, lean_object* v_P_83_){
_start:
{
lean_inc(v_P_83_);
return v_P_83_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_P_elim___boxed(lean_object* v_motive_84_, lean_object* v_t_85_, lean_object* v_h_86_, lean_object* v_P_87_){
_start:
{
uint8_t v_t_boxed_88_; lean_object* v_res_89_; 
v_t_boxed_88_ = lean_unbox(v_t_85_);
v_res_89_ = l_Legal_USTax_Hunt_Basis_Who_P_elim(v_motive_84_, v_t_boxed_88_, v_h_86_, v_P_87_);
lean_dec(v_P_87_);
return v_res_89_;
}
}
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instBEqWho_beq(uint8_t v_x_90_, uint8_t v_y_91_){
_start:
{
lean_object* v___x_92_; lean_object* v___x_93_; uint8_t v___x_94_; 
v___x_92_ = l_Legal_USTax_Hunt_Basis_Who_ctorIdx(v_x_90_);
v___x_93_ = l_Legal_USTax_Hunt_Basis_Who_ctorIdx(v_y_91_);
v___x_94_ = lean_nat_dec_eq(v___x_92_, v___x_93_);
lean_dec(v___x_93_);
lean_dec(v___x_92_);
return v___x_94_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instBEqWho_beq___boxed(lean_object* v_x_95_, lean_object* v_y_96_){
_start:
{
uint8_t v_x_21__boxed_97_; uint8_t v_y_22__boxed_98_; uint8_t v_res_99_; lean_object* v_r_100_; 
v_x_21__boxed_97_ = lean_unbox(v_x_95_);
v_y_22__boxed_98_ = lean_unbox(v_y_96_);
v_res_99_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_x_21__boxed_97_, v_y_22__boxed_98_);
v_r_100_ = lean_box(v_res_99_);
return v_r_100_;
}
}
LEAN_EXPORT uint64_t l_Legal_USTax_Hunt_Basis_instHashableWho_hash(uint8_t v_x_103_){
_start:
{
switch(v_x_103_)
{
case 0:
{
uint64_t v___x_104_; 
v___x_104_ = 0ULL;
return v___x_104_;
}
case 1:
{
uint64_t v___x_105_; 
v___x_105_ = 1ULL;
return v___x_105_;
}
case 2:
{
uint64_t v___x_106_; 
v___x_106_ = 2ULL;
return v___x_106_;
}
case 3:
{
uint64_t v___x_107_; 
v___x_107_ = 3ULL;
return v___x_107_;
}
default: 
{
uint64_t v___x_108_; 
v___x_108_ = 4ULL;
return v___x_108_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instHashableWho_hash___boxed(lean_object* v_x_109_){
_start:
{
uint8_t v_x_64__boxed_110_; uint64_t v_res_111_; lean_object* v_r_112_; 
v_x_64__boxed_110_ = lean_unbox(v_x_109_);
v_res_111_ = l_Legal_USTax_Hunt_Basis_instHashableWho_hash(v_x_64__boxed_110_);
v_r_112_ = lean_box_uint64(v_res_111_);
return v_r_112_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10(void){
_start:
{
lean_object* v___x_130_; lean_object* v___x_131_; 
v___x_130_ = lean_unsigned_to_nat(2u);
v___x_131_ = lean_nat_to_int(v___x_130_);
return v___x_131_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11(void){
_start:
{
lean_object* v___x_132_; lean_object* v___x_133_; 
v___x_132_ = lean_unsigned_to_nat(1u);
v___x_133_ = lean_nat_to_int(v___x_132_);
return v___x_133_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprWho_repr(uint8_t v_x_134_, lean_object* v_prec_135_){
_start:
{
lean_object* v___y_137_; lean_object* v___y_144_; lean_object* v___y_151_; lean_object* v___y_158_; lean_object* v___y_165_; 
switch(v_x_134_)
{
case 0:
{
lean_object* v___x_171_; uint8_t v___x_172_; 
v___x_171_ = lean_unsigned_to_nat(1024u);
v___x_172_ = lean_nat_dec_le(v___x_171_, v_prec_135_);
if (v___x_172_ == 0)
{
lean_object* v___x_173_; 
v___x_173_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10);
v___y_137_ = v___x_173_;
goto v___jp_136_;
}
else
{
lean_object* v___x_174_; 
v___x_174_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11);
v___y_137_ = v___x_174_;
goto v___jp_136_;
}
}
case 1:
{
lean_object* v___x_175_; uint8_t v___x_176_; 
v___x_175_ = lean_unsigned_to_nat(1024u);
v___x_176_ = lean_nat_dec_le(v___x_175_, v_prec_135_);
if (v___x_176_ == 0)
{
lean_object* v___x_177_; 
v___x_177_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10);
v___y_144_ = v___x_177_;
goto v___jp_143_;
}
else
{
lean_object* v___x_178_; 
v___x_178_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11);
v___y_144_ = v___x_178_;
goto v___jp_143_;
}
}
case 2:
{
lean_object* v___x_179_; uint8_t v___x_180_; 
v___x_179_ = lean_unsigned_to_nat(1024u);
v___x_180_ = lean_nat_dec_le(v___x_179_, v_prec_135_);
if (v___x_180_ == 0)
{
lean_object* v___x_181_; 
v___x_181_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10);
v___y_151_ = v___x_181_;
goto v___jp_150_;
}
else
{
lean_object* v___x_182_; 
v___x_182_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11);
v___y_151_ = v___x_182_;
goto v___jp_150_;
}
}
case 3:
{
lean_object* v___x_183_; uint8_t v___x_184_; 
v___x_183_ = lean_unsigned_to_nat(1024u);
v___x_184_ = lean_nat_dec_le(v___x_183_, v_prec_135_);
if (v___x_184_ == 0)
{
lean_object* v___x_185_; 
v___x_185_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10);
v___y_158_ = v___x_185_;
goto v___jp_157_;
}
else
{
lean_object* v___x_186_; 
v___x_186_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11);
v___y_158_ = v___x_186_;
goto v___jp_157_;
}
}
default: 
{
lean_object* v___x_187_; uint8_t v___x_188_; 
v___x_187_ = lean_unsigned_to_nat(1024u);
v___x_188_ = lean_nat_dec_le(v___x_187_, v_prec_135_);
if (v___x_188_ == 0)
{
lean_object* v___x_189_; 
v___x_189_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10);
v___y_165_ = v___x_189_;
goto v___jp_164_;
}
else
{
lean_object* v___x_190_; 
v___x_190_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11);
v___y_165_ = v___x_190_;
goto v___jp_164_;
}
}
}
v___jp_136_:
{
lean_object* v___x_138_; lean_object* v___x_139_; uint8_t v___x_140_; lean_object* v___x_141_; lean_object* v___x_142_; 
v___x_138_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__1));
lean_inc(v___y_137_);
v___x_139_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_139_, 0, v___y_137_);
lean_ctor_set(v___x_139_, 1, v___x_138_);
v___x_140_ = 0;
v___x_141_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_141_, 0, v___x_139_);
lean_ctor_set_uint8(v___x_141_, sizeof(void*)*1, v___x_140_);
v___x_142_ = l_Repr_addAppParen(v___x_141_, v_prec_135_);
return v___x_142_;
}
v___jp_143_:
{
lean_object* v___x_145_; lean_object* v___x_146_; uint8_t v___x_147_; lean_object* v___x_148_; lean_object* v___x_149_; 
v___x_145_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__3));
lean_inc(v___y_144_);
v___x_146_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_146_, 0, v___y_144_);
lean_ctor_set(v___x_146_, 1, v___x_145_);
v___x_147_ = 0;
v___x_148_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_148_, 0, v___x_146_);
lean_ctor_set_uint8(v___x_148_, sizeof(void*)*1, v___x_147_);
v___x_149_ = l_Repr_addAppParen(v___x_148_, v_prec_135_);
return v___x_149_;
}
v___jp_150_:
{
lean_object* v___x_152_; lean_object* v___x_153_; uint8_t v___x_154_; lean_object* v___x_155_; lean_object* v___x_156_; 
v___x_152_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__5));
lean_inc(v___y_151_);
v___x_153_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_153_, 0, v___y_151_);
lean_ctor_set(v___x_153_, 1, v___x_152_);
v___x_154_ = 0;
v___x_155_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_155_, 0, v___x_153_);
lean_ctor_set_uint8(v___x_155_, sizeof(void*)*1, v___x_154_);
v___x_156_ = l_Repr_addAppParen(v___x_155_, v_prec_135_);
return v___x_156_;
}
v___jp_157_:
{
lean_object* v___x_159_; lean_object* v___x_160_; uint8_t v___x_161_; lean_object* v___x_162_; lean_object* v___x_163_; 
v___x_159_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__7));
lean_inc(v___y_158_);
v___x_160_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_160_, 0, v___y_158_);
lean_ctor_set(v___x_160_, 1, v___x_159_);
v___x_161_ = 0;
v___x_162_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_162_, 0, v___x_160_);
lean_ctor_set_uint8(v___x_162_, sizeof(void*)*1, v___x_161_);
v___x_163_ = l_Repr_addAppParen(v___x_162_, v_prec_135_);
return v___x_163_;
}
v___jp_164_:
{
lean_object* v___x_166_; lean_object* v___x_167_; uint8_t v___x_168_; lean_object* v___x_169_; lean_object* v___x_170_; 
v___x_166_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__9));
lean_inc(v___y_165_);
v___x_167_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_167_, 0, v___y_165_);
lean_ctor_set(v___x_167_, 1, v___x_166_);
v___x_168_ = 0;
v___x_169_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_169_, 0, v___x_167_);
lean_ctor_set_uint8(v___x_169_, sizeof(void*)*1, v___x_168_);
v___x_170_ = l_Repr_addAppParen(v___x_169_, v_prec_135_);
return v___x_170_;
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprWho_repr___boxed(lean_object* v_x_191_, lean_object* v_prec_192_){
_start:
{
uint8_t v_x_279__boxed_193_; lean_object* v_res_194_; 
v_x_279__boxed_193_ = lean_unbox(v_x_191_);
v_res_194_ = l_Legal_USTax_Hunt_Basis_instReprWho_repr(v_x_279__boxed_193_, v_prec_192_);
lean_dec(v_prec_192_);
return v_res_194_;
}
}
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_Who_ofNat(lean_object* v_n_197_){
_start:
{
lean_object* v___x_198_; uint8_t v___x_199_; 
v___x_198_ = lean_unsigned_to_nat(1u);
v___x_199_ = lean_nat_dec_le(v_n_197_, v___x_198_);
if (v___x_199_ == 0)
{
lean_object* v___x_200_; uint8_t v___x_201_; 
v___x_200_ = lean_unsigned_to_nat(2u);
v___x_201_ = lean_nat_dec_le(v_n_197_, v___x_200_);
if (v___x_201_ == 0)
{
lean_object* v___x_202_; uint8_t v___x_203_; 
v___x_202_ = lean_unsigned_to_nat(3u);
v___x_203_ = lean_nat_dec_le(v_n_197_, v___x_202_);
if (v___x_203_ == 0)
{
uint8_t v___x_204_; 
v___x_204_ = 4;
return v___x_204_;
}
else
{
uint8_t v___x_205_; 
v___x_205_ = 3;
return v___x_205_;
}
}
else
{
uint8_t v___x_206_; 
v___x_206_ = 2;
return v___x_206_;
}
}
else
{
lean_object* v___x_207_; uint8_t v___x_208_; 
v___x_207_ = lean_unsigned_to_nat(0u);
v___x_208_ = lean_nat_dec_le(v_n_197_, v___x_207_);
if (v___x_208_ == 0)
{
uint8_t v___x_209_; 
v___x_209_ = 1;
return v___x_209_;
}
else
{
uint8_t v___x_210_; 
v___x_210_ = 0;
return v___x_210_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_ofNat___boxed(lean_object* v_n_211_){
_start:
{
uint8_t v_res_212_; lean_object* v_r_213_; 
v_res_212_ = l_Legal_USTax_Hunt_Basis_Who_ofNat(v_n_211_);
lean_dec(v_n_211_);
v_r_213_ = lean_box(v_res_212_);
return v_r_213_;
}
}
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instDecidableEqWho(uint8_t v_x_214_, uint8_t v_y_215_){
_start:
{
lean_object* v___x_216_; lean_object* v___x_217_; uint8_t v___x_218_; 
v___x_216_ = l_Legal_USTax_Hunt_Basis_Who_ctorIdx(v_x_214_);
v___x_217_ = l_Legal_USTax_Hunt_Basis_Who_ctorIdx(v_y_215_);
v___x_218_ = lean_nat_dec_eq(v___x_216_, v___x_217_);
lean_dec(v___x_217_);
lean_dec(v___x_216_);
return v___x_218_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instDecidableEqWho___boxed(lean_object* v_x_219_, lean_object* v_y_220_){
_start:
{
uint8_t v_x_20__boxed_221_; uint8_t v_y_21__boxed_222_; uint8_t v_res_223_; lean_object* v_r_224_; 
v_x_20__boxed_221_ = lean_unbox(v_x_219_);
v_y_21__boxed_222_ = lean_unbox(v_y_220_);
v_res_223_ = l_Legal_USTax_Hunt_Basis_instDecidableEqWho(v_x_20__boxed_221_, v_y_21__boxed_222_);
v_r_224_ = lean_box(v_res_223_);
return v_r_224_;
}
}
static uint8_t _init_l_Legal_USTax_Hunt_Basis_instInhabitedWho_default(void){
_start:
{
uint8_t v___x_225_; 
v___x_225_ = 0;
return v___x_225_;
}
}
static uint8_t _init_l_Legal_USTax_Hunt_Basis_instInhabitedWho(void){
_start:
{
uint8_t v___x_226_; 
v___x_226_ = 0;
return v___x_226_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_ctorIdx(uint8_t v_x_227_){
_start:
{
switch(v_x_227_)
{
case 0:
{
lean_object* v___x_228_; 
v___x_228_ = lean_unsigned_to_nat(0u);
return v___x_228_;
}
case 1:
{
lean_object* v___x_229_; 
v___x_229_ = lean_unsigned_to_nat(1u);
return v___x_229_;
}
default: 
{
lean_object* v___x_230_; 
v___x_230_ = lean_unsigned_to_nat(2u);
return v___x_230_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_ctorIdx___boxed(lean_object* v_x_231_){
_start:
{
uint8_t v_x_boxed_232_; lean_object* v_res_233_; 
v_x_boxed_232_ = lean_unbox(v_x_231_);
v_res_233_ = l_Legal_USTax_Hunt_Basis_Kind_ctorIdx(v_x_boxed_232_);
return v_res_233_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_ctorElim___redArg(lean_object* v_k_234_){
_start:
{
lean_inc(v_k_234_);
return v_k_234_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_ctorElim___redArg___boxed(lean_object* v_k_235_){
_start:
{
lean_object* v_res_236_; 
v_res_236_ = l_Legal_USTax_Hunt_Basis_Kind_ctorElim___redArg(v_k_235_);
lean_dec(v_k_235_);
return v_res_236_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_ctorElim(lean_object* v_motive_237_, lean_object* v_ctorIdx_238_, uint8_t v_t_239_, lean_object* v_h_240_, lean_object* v_k_241_){
_start:
{
lean_inc(v_k_241_);
return v_k_241_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_ctorElim___boxed(lean_object* v_motive_242_, lean_object* v_ctorIdx_243_, lean_object* v_t_244_, lean_object* v_h_245_, lean_object* v_k_246_){
_start:
{
uint8_t v_t_boxed_247_; lean_object* v_res_248_; 
v_t_boxed_247_ = lean_unbox(v_t_244_);
v_res_248_ = l_Legal_USTax_Hunt_Basis_Kind_ctorElim(v_motive_242_, v_ctorIdx_243_, v_t_boxed_247_, v_h_245_, v_k_246_);
lean_dec(v_k_246_);
lean_dec(v_ctorIdx_243_);
return v_res_248_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_stock_elim___redArg(lean_object* v_stock_249_){
_start:
{
lean_inc(v_stock_249_);
return v_stock_249_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_stock_elim___redArg___boxed(lean_object* v_stock_250_){
_start:
{
lean_object* v_res_251_; 
v_res_251_ = l_Legal_USTax_Hunt_Basis_Kind_stock_elim___redArg(v_stock_250_);
lean_dec(v_stock_250_);
return v_res_251_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_stock_elim(lean_object* v_motive_252_, uint8_t v_t_253_, lean_object* v_h_254_, lean_object* v_stock_255_){
_start:
{
lean_inc(v_stock_255_);
return v_stock_255_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_stock_elim___boxed(lean_object* v_motive_256_, lean_object* v_t_257_, lean_object* v_h_258_, lean_object* v_stock_259_){
_start:
{
uint8_t v_t_boxed_260_; lean_object* v_res_261_; 
v_t_boxed_260_ = lean_unbox(v_t_257_);
v_res_261_ = l_Legal_USTax_Hunt_Basis_Kind_stock_elim(v_motive_256_, v_t_boxed_260_, v_h_258_, v_stock_259_);
lean_dec(v_stock_259_);
return v_res_261_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_qsbs_elim___redArg(lean_object* v_qsbs_262_){
_start:
{
lean_inc(v_qsbs_262_);
return v_qsbs_262_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_qsbs_elim___redArg___boxed(lean_object* v_qsbs_263_){
_start:
{
lean_object* v_res_264_; 
v_res_264_ = l_Legal_USTax_Hunt_Basis_Kind_qsbs_elim___redArg(v_qsbs_263_);
lean_dec(v_qsbs_263_);
return v_res_264_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_qsbs_elim(lean_object* v_motive_265_, uint8_t v_t_266_, lean_object* v_h_267_, lean_object* v_qsbs_268_){
_start:
{
lean_inc(v_qsbs_268_);
return v_qsbs_268_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_qsbs_elim___boxed(lean_object* v_motive_269_, lean_object* v_t_270_, lean_object* v_h_271_, lean_object* v_qsbs_272_){
_start:
{
uint8_t v_t_boxed_273_; lean_object* v_res_274_; 
v_t_boxed_273_ = lean_unbox(v_t_270_);
v_res_274_ = l_Legal_USTax_Hunt_Basis_Kind_qsbs_elim(v_motive_269_, v_t_boxed_273_, v_h_271_, v_qsbs_272_);
lean_dec(v_qsbs_272_);
return v_res_274_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_home_elim___redArg(lean_object* v_home_275_){
_start:
{
lean_inc(v_home_275_);
return v_home_275_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_home_elim___redArg___boxed(lean_object* v_home_276_){
_start:
{
lean_object* v_res_277_; 
v_res_277_ = l_Legal_USTax_Hunt_Basis_Kind_home_elim___redArg(v_home_276_);
lean_dec(v_home_276_);
return v_res_277_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_home_elim(lean_object* v_motive_278_, uint8_t v_t_279_, lean_object* v_h_280_, lean_object* v_home_281_){
_start:
{
lean_inc(v_home_281_);
return v_home_281_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_home_elim___boxed(lean_object* v_motive_282_, lean_object* v_t_283_, lean_object* v_h_284_, lean_object* v_home_285_){
_start:
{
uint8_t v_t_boxed_286_; lean_object* v_res_287_; 
v_t_boxed_286_ = lean_unbox(v_t_283_);
v_res_287_ = l_Legal_USTax_Hunt_Basis_Kind_home_elim(v_motive_282_, v_t_boxed_286_, v_h_284_, v_home_285_);
lean_dec(v_home_285_);
return v_res_287_;
}
}
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instBEqKind_beq(uint8_t v_x_288_, uint8_t v_y_289_){
_start:
{
lean_object* v___x_290_; lean_object* v___x_291_; uint8_t v___x_292_; 
v___x_290_ = l_Legal_USTax_Hunt_Basis_Kind_ctorIdx(v_x_288_);
v___x_291_ = l_Legal_USTax_Hunt_Basis_Kind_ctorIdx(v_y_289_);
v___x_292_ = lean_nat_dec_eq(v___x_290_, v___x_291_);
lean_dec(v___x_291_);
lean_dec(v___x_290_);
return v___x_292_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instBEqKind_beq___boxed(lean_object* v_x_293_, lean_object* v_y_294_){
_start:
{
uint8_t v_x_21__boxed_295_; uint8_t v_y_22__boxed_296_; uint8_t v_res_297_; lean_object* v_r_298_; 
v_x_21__boxed_295_ = lean_unbox(v_x_293_);
v_y_22__boxed_296_ = lean_unbox(v_y_294_);
v_res_297_ = l_Legal_USTax_Hunt_Basis_instBEqKind_beq(v_x_21__boxed_295_, v_y_22__boxed_296_);
v_r_298_ = lean_box(v_res_297_);
return v_r_298_;
}
}
LEAN_EXPORT uint64_t l_Legal_USTax_Hunt_Basis_instHashableKind_hash(uint8_t v_x_301_){
_start:
{
switch(v_x_301_)
{
case 0:
{
uint64_t v___x_302_; 
v___x_302_ = 0ULL;
return v___x_302_;
}
case 1:
{
uint64_t v___x_303_; 
v___x_303_ = 1ULL;
return v___x_303_;
}
default: 
{
uint64_t v___x_304_; 
v___x_304_ = 2ULL;
return v___x_304_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instHashableKind_hash___boxed(lean_object* v_x_305_){
_start:
{
uint8_t v_x_40__boxed_306_; uint64_t v_res_307_; lean_object* v_r_308_; 
v_x_40__boxed_306_ = lean_unbox(v_x_305_);
v_res_307_ = l_Legal_USTax_Hunt_Basis_instHashableKind_hash(v_x_40__boxed_306_);
v_r_308_ = lean_box_uint64(v_res_307_);
return v_r_308_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprKind_repr(uint8_t v_x_320_, lean_object* v_prec_321_){
_start:
{
lean_object* v___y_323_; lean_object* v___y_330_; lean_object* v___y_337_; 
switch(v_x_320_)
{
case 0:
{
lean_object* v___x_343_; uint8_t v___x_344_; 
v___x_343_ = lean_unsigned_to_nat(1024u);
v___x_344_ = lean_nat_dec_le(v___x_343_, v_prec_321_);
if (v___x_344_ == 0)
{
lean_object* v___x_345_; 
v___x_345_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10);
v___y_323_ = v___x_345_;
goto v___jp_322_;
}
else
{
lean_object* v___x_346_; 
v___x_346_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11);
v___y_323_ = v___x_346_;
goto v___jp_322_;
}
}
case 1:
{
lean_object* v___x_347_; uint8_t v___x_348_; 
v___x_347_ = lean_unsigned_to_nat(1024u);
v___x_348_ = lean_nat_dec_le(v___x_347_, v_prec_321_);
if (v___x_348_ == 0)
{
lean_object* v___x_349_; 
v___x_349_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10);
v___y_330_ = v___x_349_;
goto v___jp_329_;
}
else
{
lean_object* v___x_350_; 
v___x_350_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11);
v___y_330_ = v___x_350_;
goto v___jp_329_;
}
}
default: 
{
lean_object* v___x_351_; uint8_t v___x_352_; 
v___x_351_ = lean_unsigned_to_nat(1024u);
v___x_352_ = lean_nat_dec_le(v___x_351_, v_prec_321_);
if (v___x_352_ == 0)
{
lean_object* v___x_353_; 
v___x_353_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10);
v___y_337_ = v___x_353_;
goto v___jp_336_;
}
else
{
lean_object* v___x_354_; 
v___x_354_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11);
v___y_337_ = v___x_354_;
goto v___jp_336_;
}
}
}
v___jp_322_:
{
lean_object* v___x_324_; lean_object* v___x_325_; uint8_t v___x_326_; lean_object* v___x_327_; lean_object* v___x_328_; 
v___x_324_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__1));
lean_inc(v___y_323_);
v___x_325_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_325_, 0, v___y_323_);
lean_ctor_set(v___x_325_, 1, v___x_324_);
v___x_326_ = 0;
v___x_327_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_327_, 0, v___x_325_);
lean_ctor_set_uint8(v___x_327_, sizeof(void*)*1, v___x_326_);
v___x_328_ = l_Repr_addAppParen(v___x_327_, v_prec_321_);
return v___x_328_;
}
v___jp_329_:
{
lean_object* v___x_331_; lean_object* v___x_332_; uint8_t v___x_333_; lean_object* v___x_334_; lean_object* v___x_335_; 
v___x_331_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__3));
lean_inc(v___y_330_);
v___x_332_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_332_, 0, v___y_330_);
lean_ctor_set(v___x_332_, 1, v___x_331_);
v___x_333_ = 0;
v___x_334_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_334_, 0, v___x_332_);
lean_ctor_set_uint8(v___x_334_, sizeof(void*)*1, v___x_333_);
v___x_335_ = l_Repr_addAppParen(v___x_334_, v_prec_321_);
return v___x_335_;
}
v___jp_336_:
{
lean_object* v___x_338_; lean_object* v___x_339_; uint8_t v___x_340_; lean_object* v___x_341_; lean_object* v___x_342_; 
v___x_338_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprKind_repr___closed__5));
lean_inc(v___y_337_);
v___x_339_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_339_, 0, v___y_337_);
lean_ctor_set(v___x_339_, 1, v___x_338_);
v___x_340_ = 0;
v___x_341_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_341_, 0, v___x_339_);
lean_ctor_set_uint8(v___x_341_, sizeof(void*)*1, v___x_340_);
v___x_342_ = l_Repr_addAppParen(v___x_341_, v_prec_321_);
return v___x_342_;
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprKind_repr___boxed(lean_object* v_x_355_, lean_object* v_prec_356_){
_start:
{
uint8_t v_x_167__boxed_357_; lean_object* v_res_358_; 
v_x_167__boxed_357_ = lean_unbox(v_x_355_);
v_res_358_ = l_Legal_USTax_Hunt_Basis_instReprKind_repr(v_x_167__boxed_357_, v_prec_356_);
lean_dec(v_prec_356_);
return v_res_358_;
}
}
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_Kind_ofNat(lean_object* v_n_361_){
_start:
{
lean_object* v___x_362_; uint8_t v___x_363_; 
v___x_362_ = lean_unsigned_to_nat(0u);
v___x_363_ = lean_nat_dec_le(v_n_361_, v___x_362_);
if (v___x_363_ == 0)
{
lean_object* v___x_364_; uint8_t v___x_365_; 
v___x_364_ = lean_unsigned_to_nat(1u);
v___x_365_ = lean_nat_dec_le(v_n_361_, v___x_364_);
if (v___x_365_ == 0)
{
uint8_t v___x_366_; 
v___x_366_ = 2;
return v___x_366_;
}
else
{
uint8_t v___x_367_; 
v___x_367_ = 1;
return v___x_367_;
}
}
else
{
uint8_t v___x_368_; 
v___x_368_ = 0;
return v___x_368_;
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Kind_ofNat___boxed(lean_object* v_n_369_){
_start:
{
uint8_t v_res_370_; lean_object* v_r_371_; 
v_res_370_ = l_Legal_USTax_Hunt_Basis_Kind_ofNat(v_n_369_);
lean_dec(v_n_369_);
v_r_371_ = lean_box(v_res_370_);
return v_r_371_;
}
}
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instDecidableEqKind(uint8_t v_x_372_, uint8_t v_y_373_){
_start:
{
lean_object* v___x_374_; lean_object* v___x_375_; uint8_t v___x_376_; 
v___x_374_ = l_Legal_USTax_Hunt_Basis_Kind_ctorIdx(v_x_372_);
v___x_375_ = l_Legal_USTax_Hunt_Basis_Kind_ctorIdx(v_y_373_);
v___x_376_ = lean_nat_dec_eq(v___x_374_, v___x_375_);
lean_dec(v___x_375_);
lean_dec(v___x_374_);
return v___x_376_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instDecidableEqKind___boxed(lean_object* v_x_377_, lean_object* v_y_378_){
_start:
{
uint8_t v_x_20__boxed_379_; uint8_t v_y_21__boxed_380_; uint8_t v_res_381_; lean_object* v_r_382_; 
v_x_20__boxed_379_ = lean_unbox(v_x_377_);
v_y_21__boxed_380_ = lean_unbox(v_y_378_);
v_res_381_ = l_Legal_USTax_Hunt_Basis_instDecidableEqKind(v_x_20__boxed_379_, v_y_21__boxed_380_);
v_r_382_ = lean_box(v_res_381_);
return v_r_382_;
}
}
static uint8_t _init_l_Legal_USTax_Hunt_Basis_instInhabitedKind_default(void){
_start:
{
uint8_t v___x_383_; 
v___x_383_ = 0;
return v___x_383_;
}
}
static uint8_t _init_l_Legal_USTax_Hunt_Basis_instInhabitedKind(void){
_start:
{
uint8_t v___x_384_; 
v___x_384_ = 0;
return v___x_384_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_name(uint8_t v_x_390_){
_start:
{
switch(v_x_390_)
{
case 0:
{
lean_object* v___x_391_; 
v___x_391_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_Who_name___closed__0));
return v___x_391_;
}
case 1:
{
lean_object* v___x_392_; 
v___x_392_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_Who_name___closed__1));
return v___x_392_;
}
case 2:
{
lean_object* v___x_393_; 
v___x_393_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_Who_name___closed__2));
return v___x_393_;
}
case 3:
{
lean_object* v___x_394_; 
v___x_394_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_Who_name___closed__3));
return v___x_394_;
}
default: 
{
lean_object* v___x_395_; 
v___x_395_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_Who_name___closed__4));
return v___x_395_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_name___boxed(lean_object* v_x_396_){
_start:
{
uint8_t v_x_49__boxed_397_; lean_object* v_res_398_; 
v_x_49__boxed_397_ = lean_unbox(v_x_396_);
v_res_398_ = l_Legal_USTax_Hunt_Basis_Who_name(v_x_49__boxed_397_);
return v_res_398_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_idx(uint8_t v_x_399_){
_start:
{
switch(v_x_399_)
{
case 0:
{
lean_object* v___x_400_; 
v___x_400_ = lean_unsigned_to_nat(0u);
return v___x_400_;
}
case 1:
{
lean_object* v___x_401_; 
v___x_401_ = lean_unsigned_to_nat(1u);
return v___x_401_;
}
case 2:
{
lean_object* v___x_402_; 
v___x_402_ = lean_unsigned_to_nat(2u);
return v___x_402_;
}
case 3:
{
lean_object* v___x_403_; 
v___x_403_ = lean_unsigned_to_nat(3u);
return v___x_403_;
}
default: 
{
lean_object* v___x_404_; 
v___x_404_ = lean_unsigned_to_nat(4u);
return v___x_404_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Who_idx___boxed(lean_object* v_x_405_){
_start:
{
uint8_t v_x_54__boxed_406_; lean_object* v_res_407_; 
v_x_54__boxed_406_ = lean_unbox(v_x_405_);
v_res_407_ = l_Legal_USTax_Hunt_Basis_Who_idx(v_x_54__boxed_406_);
return v_res_407_;
}
}
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_spouses(uint8_t v_a_408_, uint8_t v_b_409_){
_start:
{
uint8_t v___y_411_; uint8_t v___x_416_; uint8_t v___x_417_; 
v___x_416_ = 0;
v___x_417_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_a_408_, v___x_416_);
if (v___x_417_ == 0)
{
v___y_411_ = v___x_417_;
goto v___jp_410_;
}
else
{
uint8_t v___x_418_; uint8_t v___x_419_; 
v___x_418_ = 1;
v___x_419_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_b_409_, v___x_418_);
v___y_411_ = v___x_419_;
goto v___jp_410_;
}
v___jp_410_:
{
if (v___y_411_ == 0)
{
uint8_t v___x_412_; uint8_t v___x_413_; 
v___x_412_ = 1;
v___x_413_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_a_408_, v___x_412_);
if (v___x_413_ == 0)
{
return v___x_413_;
}
else
{
uint8_t v___x_414_; uint8_t v___x_415_; 
v___x_414_ = 0;
v___x_415_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_b_409_, v___x_414_);
return v___x_415_;
}
}
else
{
return v___y_411_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_spouses___boxed(lean_object* v_a_420_, lean_object* v_b_421_){
_start:
{
uint8_t v_a_boxed_422_; uint8_t v_b_boxed_423_; uint8_t v_res_424_; lean_object* v_r_425_; 
v_a_boxed_422_ = lean_unbox(v_a_420_);
v_b_boxed_423_ = lean_unbox(v_b_421_);
v_res_424_ = l_Legal_USTax_Hunt_Basis_spouses(v_a_boxed_422_, v_b_boxed_423_);
v_r_425_ = lean_box(v_res_424_);
return v_r_425_;
}
}
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_related267(uint8_t v_a_426_, uint8_t v_b_427_){
_start:
{
switch(v_a_426_)
{
case 0:
{
switch(v_b_427_)
{
case 1:
{
uint8_t v___x_428_; 
v___x_428_ = 1;
return v___x_428_;
}
case 2:
{
uint8_t v___x_429_; 
v___x_429_ = 1;
return v___x_429_;
}
case 3:
{
uint8_t v___x_430_; 
v___x_430_ = 1;
return v___x_430_;
}
case 4:
{
uint8_t v___x_431_; 
v___x_431_ = 1;
return v___x_431_;
}
default: 
{
uint8_t v___x_432_; 
v___x_432_ = 0;
return v___x_432_;
}
}
}
case 2:
{
switch(v_b_427_)
{
case 0:
{
uint8_t v___x_433_; 
v___x_433_ = 1;
return v___x_433_;
}
case 1:
{
uint8_t v___x_434_; 
v___x_434_ = 1;
return v___x_434_;
}
case 3:
{
uint8_t v___x_435_; 
v___x_435_ = 1;
return v___x_435_;
}
case 4:
{
uint8_t v___x_436_; 
v___x_436_ = 1;
return v___x_436_;
}
default: 
{
uint8_t v___x_437_; 
v___x_437_ = 0;
return v___x_437_;
}
}
}
case 3:
{
switch(v_b_427_)
{
case 0:
{
uint8_t v___x_438_; 
v___x_438_ = 1;
return v___x_438_;
}
case 1:
{
uint8_t v___x_439_; 
v___x_439_ = 1;
return v___x_439_;
}
case 2:
{
uint8_t v___x_440_; 
v___x_440_ = 1;
return v___x_440_;
}
case 4:
{
uint8_t v___x_441_; 
v___x_441_ = 1;
return v___x_441_;
}
default: 
{
uint8_t v___x_442_; 
v___x_442_ = 0;
return v___x_442_;
}
}
}
default: 
{
switch(v_b_427_)
{
case 0:
{
uint8_t v___x_443_; 
v___x_443_ = 1;
return v___x_443_;
}
case 2:
{
uint8_t v___x_444_; 
v___x_444_ = 1;
return v___x_444_;
}
case 3:
{
uint8_t v___x_445_; 
v___x_445_ = 1;
return v___x_445_;
}
default: 
{
uint8_t v___x_446_; 
v___x_446_ = 0;
return v___x_446_;
}
}
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_related267___boxed(lean_object* v_a_447_, lean_object* v_b_448_){
_start:
{
uint8_t v_a_boxed_449_; uint8_t v_b_boxed_450_; uint8_t v_res_451_; lean_object* v_r_452_; 
v_a_boxed_449_ = lean_unbox(v_a_447_);
v_b_boxed_450_ = lean_unbox(v_b_448_);
v_res_451_ = l_Legal_USTax_Hunt_Basis_related267(v_a_boxed_449_, v_b_boxed_450_);
v_r_452_ = lean_box(v_res_451_);
return v_r_452_;
}
}
LEAN_EXPORT uint8_t l_Option_instBEq_beq___at___00Legal_USTax_Hunt_Basis_instBEqLot_beq_spec__0(lean_object* v_x_453_, lean_object* v_x_454_){
_start:
{
if (lean_obj_tag(v_x_453_) == 0)
{
if (lean_obj_tag(v_x_454_) == 0)
{
uint8_t v___x_455_; 
v___x_455_ = 1;
return v___x_455_;
}
else
{
uint8_t v___x_456_; 
v___x_456_ = 0;
return v___x_456_;
}
}
else
{
if (lean_obj_tag(v_x_454_) == 0)
{
uint8_t v___x_457_; 
v___x_457_ = 0;
return v___x_457_;
}
else
{
lean_object* v_val_458_; lean_object* v_val_459_; uint8_t v___x_460_; uint8_t v___x_461_; uint8_t v___x_462_; 
v_val_458_ = lean_ctor_get(v_x_453_, 0);
v_val_459_ = lean_ctor_get(v_x_454_, 0);
v___x_460_ = lean_unbox(v_val_458_);
v___x_461_ = lean_unbox(v_val_459_);
v___x_462_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v___x_460_, v___x_461_);
return v___x_462_;
}
}
}
}
LEAN_EXPORT lean_object* l_Option_instBEq_beq___at___00Legal_USTax_Hunt_Basis_instBEqLot_beq_spec__0___boxed(lean_object* v_x_463_, lean_object* v_x_464_){
_start:
{
uint8_t v_res_465_; lean_object* v_r_466_; 
v_res_465_ = l_Option_instBEq_beq___at___00Legal_USTax_Hunt_Basis_instBEqLot_beq_spec__0(v_x_463_, v_x_464_);
lean_dec(v_x_464_);
lean_dec(v_x_463_);
v_r_466_ = lean_box(v_res_465_);
return v_r_466_;
}
}
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instBEqLot_beq(lean_object* v_x_467_, lean_object* v_x_468_){
_start:
{
uint8_t v_kind_469_; uint8_t v_owner_470_; lean_object* v_fmv_471_; lean_object* v_basis_472_; lean_object* v_lossBasis_473_; lean_object* v_held_474_; lean_object* v_owned_475_; lean_object* v_shield_476_; lean_object* v_donor_477_; lean_object* v_giftAge_478_; uint8_t v_inherited_479_; uint8_t v_gone_480_; uint8_t v_kind_481_; uint8_t v_owner_482_; lean_object* v_fmv_483_; lean_object* v_basis_484_; lean_object* v_lossBasis_485_; lean_object* v_held_486_; lean_object* v_owned_487_; lean_object* v_shield_488_; lean_object* v_donor_489_; lean_object* v_giftAge_490_; uint8_t v_inherited_491_; uint8_t v_gone_492_; uint8_t v___y_494_; uint8_t v___x_495_; 
v_kind_469_ = lean_ctor_get_uint8(v_x_467_, sizeof(void*)*8);
v_owner_470_ = lean_ctor_get_uint8(v_x_467_, sizeof(void*)*8 + 1);
v_fmv_471_ = lean_ctor_get(v_x_467_, 0);
v_basis_472_ = lean_ctor_get(v_x_467_, 1);
v_lossBasis_473_ = lean_ctor_get(v_x_467_, 2);
v_held_474_ = lean_ctor_get(v_x_467_, 3);
v_owned_475_ = lean_ctor_get(v_x_467_, 4);
v_shield_476_ = lean_ctor_get(v_x_467_, 5);
v_donor_477_ = lean_ctor_get(v_x_467_, 6);
v_giftAge_478_ = lean_ctor_get(v_x_467_, 7);
v_inherited_479_ = lean_ctor_get_uint8(v_x_467_, sizeof(void*)*8 + 2);
v_gone_480_ = lean_ctor_get_uint8(v_x_467_, sizeof(void*)*8 + 3);
v_kind_481_ = lean_ctor_get_uint8(v_x_468_, sizeof(void*)*8);
v_owner_482_ = lean_ctor_get_uint8(v_x_468_, sizeof(void*)*8 + 1);
v_fmv_483_ = lean_ctor_get(v_x_468_, 0);
v_basis_484_ = lean_ctor_get(v_x_468_, 1);
v_lossBasis_485_ = lean_ctor_get(v_x_468_, 2);
v_held_486_ = lean_ctor_get(v_x_468_, 3);
v_owned_487_ = lean_ctor_get(v_x_468_, 4);
v_shield_488_ = lean_ctor_get(v_x_468_, 5);
v_donor_489_ = lean_ctor_get(v_x_468_, 6);
v_giftAge_490_ = lean_ctor_get(v_x_468_, 7);
v_inherited_491_ = lean_ctor_get_uint8(v_x_468_, sizeof(void*)*8 + 2);
v_gone_492_ = lean_ctor_get_uint8(v_x_468_, sizeof(void*)*8 + 3);
v___x_495_ = l_Legal_USTax_Hunt_Basis_instBEqKind_beq(v_kind_469_, v_kind_481_);
if (v___x_495_ == 0)
{
return v___x_495_;
}
else
{
uint8_t v___x_496_; 
v___x_496_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_owner_470_, v_owner_482_);
if (v___x_496_ == 0)
{
return v___x_496_;
}
else
{
uint8_t v___x_497_; 
v___x_497_ = lean_nat_dec_eq(v_fmv_471_, v_fmv_483_);
if (v___x_497_ == 0)
{
return v___x_497_;
}
else
{
uint8_t v___x_498_; 
v___x_498_ = lean_nat_dec_eq(v_basis_472_, v_basis_484_);
if (v___x_498_ == 0)
{
return v___x_498_;
}
else
{
uint8_t v___x_499_; 
v___x_499_ = lean_nat_dec_eq(v_lossBasis_473_, v_lossBasis_485_);
if (v___x_499_ == 0)
{
return v___x_499_;
}
else
{
uint8_t v___x_500_; 
v___x_500_ = lean_nat_dec_eq(v_held_474_, v_held_486_);
if (v___x_500_ == 0)
{
return v___x_500_;
}
else
{
uint8_t v___x_501_; 
v___x_501_ = lean_nat_dec_eq(v_owned_475_, v_owned_487_);
if (v___x_501_ == 0)
{
return v___x_501_;
}
else
{
uint8_t v___x_502_; 
v___x_502_ = lean_nat_dec_eq(v_shield_476_, v_shield_488_);
if (v___x_502_ == 0)
{
return v___x_502_;
}
else
{
uint8_t v___x_503_; 
v___x_503_ = l_Option_instBEq_beq___at___00Legal_USTax_Hunt_Basis_instBEqLot_beq_spec__0(v_donor_477_, v_donor_489_);
if (v___x_503_ == 0)
{
return v___x_503_;
}
else
{
uint8_t v___x_504_; 
v___x_504_ = lean_nat_dec_eq(v_giftAge_478_, v_giftAge_490_);
if (v___x_504_ == 0)
{
return v___x_504_;
}
else
{
if (v_inherited_491_ == 0)
{
if (v_inherited_479_ == 0)
{
v___y_494_ = v___x_504_;
goto v___jp_493_;
}
else
{
return v_inherited_491_;
}
}
else
{
v___y_494_ = v_inherited_479_;
goto v___jp_493_;
}
}
}
}
}
}
}
}
}
}
}
v___jp_493_:
{
if (v___y_494_ == 0)
{
return v___y_494_;
}
else
{
if (v_gone_492_ == 0)
{
if (v_gone_480_ == 0)
{
return v___y_494_;
}
else
{
return v_gone_492_;
}
}
else
{
return v_gone_480_;
}
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instBEqLot_beq___boxed(lean_object* v_x_505_, lean_object* v_x_506_){
_start:
{
uint8_t v_res_507_; lean_object* v_r_508_; 
v_res_507_ = l_Legal_USTax_Hunt_Basis_instBEqLot_beq(v_x_505_, v_x_506_);
lean_dec_ref(v_x_506_);
lean_dec_ref(v_x_505_);
v_r_508_ = lean_box(v_res_507_);
return v_r_508_;
}
}
LEAN_EXPORT uint64_t l_Legal_USTax_Hunt_Basis_instHashableLot_hash(lean_object* v_x_511_){
_start:
{
uint8_t v_kind_512_; uint8_t v_owner_513_; lean_object* v_fmv_514_; lean_object* v_basis_515_; lean_object* v_lossBasis_516_; lean_object* v_held_517_; lean_object* v_owned_518_; lean_object* v_shield_519_; lean_object* v_donor_520_; lean_object* v_giftAge_521_; uint8_t v_inherited_522_; uint8_t v_gone_523_; uint64_t v___y_525_; uint64_t v___y_526_; uint64_t v___x_532_; uint64_t v___x_533_; uint64_t v___x_534_; uint64_t v___x_535_; uint64_t v___x_536_; uint64_t v___x_537_; uint64_t v___x_538_; uint64_t v___x_539_; uint64_t v___x_540_; uint64_t v___x_541_; uint64_t v___x_542_; uint64_t v___x_543_; uint64_t v___x_544_; uint64_t v___x_545_; uint64_t v___x_546_; uint64_t v___x_547_; uint64_t v___x_548_; uint64_t v___y_550_; 
v_kind_512_ = lean_ctor_get_uint8(v_x_511_, sizeof(void*)*8);
v_owner_513_ = lean_ctor_get_uint8(v_x_511_, sizeof(void*)*8 + 1);
v_fmv_514_ = lean_ctor_get(v_x_511_, 0);
v_basis_515_ = lean_ctor_get(v_x_511_, 1);
v_lossBasis_516_ = lean_ctor_get(v_x_511_, 2);
v_held_517_ = lean_ctor_get(v_x_511_, 3);
v_owned_518_ = lean_ctor_get(v_x_511_, 4);
v_shield_519_ = lean_ctor_get(v_x_511_, 5);
v_donor_520_ = lean_ctor_get(v_x_511_, 6);
v_giftAge_521_ = lean_ctor_get(v_x_511_, 7);
v_inherited_522_ = lean_ctor_get_uint8(v_x_511_, sizeof(void*)*8 + 2);
v_gone_523_ = lean_ctor_get_uint8(v_x_511_, sizeof(void*)*8 + 3);
v___x_532_ = 0ULL;
v___x_533_ = l_Legal_USTax_Hunt_Basis_instHashableKind_hash(v_kind_512_);
v___x_534_ = lean_uint64_mix_hash(v___x_532_, v___x_533_);
v___x_535_ = l_Legal_USTax_Hunt_Basis_instHashableWho_hash(v_owner_513_);
v___x_536_ = lean_uint64_mix_hash(v___x_534_, v___x_535_);
v___x_537_ = lean_uint64_of_nat(v_fmv_514_);
v___x_538_ = lean_uint64_mix_hash(v___x_536_, v___x_537_);
v___x_539_ = lean_uint64_of_nat(v_basis_515_);
v___x_540_ = lean_uint64_mix_hash(v___x_538_, v___x_539_);
v___x_541_ = lean_uint64_of_nat(v_lossBasis_516_);
v___x_542_ = lean_uint64_mix_hash(v___x_540_, v___x_541_);
v___x_543_ = lean_uint64_of_nat(v_held_517_);
v___x_544_ = lean_uint64_mix_hash(v___x_542_, v___x_543_);
v___x_545_ = lean_uint64_of_nat(v_owned_518_);
v___x_546_ = lean_uint64_mix_hash(v___x_544_, v___x_545_);
v___x_547_ = lean_uint64_of_nat(v_shield_519_);
v___x_548_ = lean_uint64_mix_hash(v___x_546_, v___x_547_);
if (lean_obj_tag(v_donor_520_) == 0)
{
uint64_t v___x_556_; 
v___x_556_ = 11ULL;
v___y_550_ = v___x_556_;
goto v___jp_549_;
}
else
{
lean_object* v_val_557_; uint8_t v___x_558_; uint64_t v___x_559_; uint64_t v___x_560_; uint64_t v___x_561_; 
v_val_557_ = lean_ctor_get(v_donor_520_, 0);
v___x_558_ = lean_unbox(v_val_557_);
v___x_559_ = l_Legal_USTax_Hunt_Basis_instHashableWho_hash(v___x_558_);
v___x_560_ = 13ULL;
v___x_561_ = lean_uint64_mix_hash(v___x_559_, v___x_560_);
v___y_550_ = v___x_561_;
goto v___jp_549_;
}
v___jp_524_:
{
uint64_t v___x_527_; 
v___x_527_ = lean_uint64_mix_hash(v___y_525_, v___y_526_);
if (v_gone_523_ == 0)
{
uint64_t v___x_528_; uint64_t v___x_529_; 
v___x_528_ = 13ULL;
v___x_529_ = lean_uint64_mix_hash(v___x_527_, v___x_528_);
return v___x_529_;
}
else
{
uint64_t v___x_530_; uint64_t v___x_531_; 
v___x_530_ = 11ULL;
v___x_531_ = lean_uint64_mix_hash(v___x_527_, v___x_530_);
return v___x_531_;
}
}
v___jp_549_:
{
uint64_t v___x_551_; uint64_t v___x_552_; uint64_t v___x_553_; 
v___x_551_ = lean_uint64_mix_hash(v___x_548_, v___y_550_);
v___x_552_ = lean_uint64_of_nat(v_giftAge_521_);
v___x_553_ = lean_uint64_mix_hash(v___x_551_, v___x_552_);
if (v_inherited_522_ == 0)
{
uint64_t v___x_554_; 
v___x_554_ = 13ULL;
v___y_525_ = v___x_553_;
v___y_526_ = v___x_554_;
goto v___jp_524_;
}
else
{
uint64_t v___x_555_; 
v___x_555_ = 11ULL;
v___y_525_ = v___x_553_;
v___y_526_ = v___x_555_;
goto v___jp_524_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instHashableLot_hash___boxed(lean_object* v_x_562_){
_start:
{
uint64_t v_res_563_; lean_object* v_r_564_; 
v_res_563_ = l_Legal_USTax_Hunt_Basis_instHashableLot_hash(v_x_562_);
lean_dec_ref(v_x_562_);
v_r_564_ = lean_box_uint64(v_res_563_);
return v_r_564_;
}
}
LEAN_EXPORT lean_object* l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0(lean_object* v_x_573_, lean_object* v_x_574_){
_start:
{
if (lean_obj_tag(v_x_573_) == 0)
{
lean_object* v___x_575_; 
v___x_575_ = ((lean_object*)(l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0___closed__1));
return v___x_575_;
}
else
{
lean_object* v_val_576_; lean_object* v___x_577_; lean_object* v___x_578_; uint8_t v___x_579_; lean_object* v___x_580_; lean_object* v___x_581_; lean_object* v___x_582_; 
v_val_576_ = lean_ctor_get(v_x_573_, 0);
v___x_577_ = ((lean_object*)(l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0___closed__3));
v___x_578_ = lean_unsigned_to_nat(1024u);
v___x_579_ = lean_unbox(v_val_576_);
v___x_580_ = l_Legal_USTax_Hunt_Basis_instReprWho_repr(v___x_579_, v___x_578_);
v___x_581_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_581_, 0, v___x_577_);
lean_ctor_set(v___x_581_, 1, v___x_580_);
v___x_582_ = l_Repr_addAppParen(v___x_581_, v_x_574_);
return v___x_582_;
}
}
}
LEAN_EXPORT lean_object* l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0___boxed(lean_object* v_x_583_, lean_object* v_x_584_){
_start:
{
lean_object* v_res_585_; 
v_res_585_ = l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0(v_x_583_, v_x_584_);
lean_dec(v_x_584_);
lean_dec(v_x_583_);
return v_res_585_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__7(void){
_start:
{
lean_object* v___x_599_; lean_object* v___x_600_; 
v___x_599_ = lean_unsigned_to_nat(8u);
v___x_600_ = lean_nat_to_int(v___x_599_);
return v___x_600_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__12(void){
_start:
{
lean_object* v___x_607_; lean_object* v___x_608_; 
v___x_607_ = lean_unsigned_to_nat(9u);
v___x_608_ = lean_nat_to_int(v___x_607_);
return v___x_608_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__15(void){
_start:
{
lean_object* v___x_612_; lean_object* v___x_613_; 
v___x_612_ = lean_unsigned_to_nat(7u);
v___x_613_ = lean_nat_to_int(v___x_612_);
return v___x_613_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__20(void){
_start:
{
lean_object* v___x_620_; lean_object* v___x_621_; 
v___x_620_ = lean_unsigned_to_nat(13u);
v___x_621_ = lean_nat_to_int(v___x_620_);
return v___x_621_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__27(void){
_start:
{
lean_object* v___x_631_; lean_object* v___x_632_; 
v___x_631_ = lean_unsigned_to_nat(10u);
v___x_632_ = lean_nat_to_int(v___x_631_);
return v___x_632_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__32(void){
_start:
{
lean_object* v___x_639_; lean_object* v___x_640_; 
v___x_639_ = lean_unsigned_to_nat(11u);
v___x_640_ = lean_nat_to_int(v___x_639_);
return v___x_640_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__38(void){
_start:
{
lean_object* v___x_648_; lean_object* v___x_649_; 
v___x_648_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__0));
v___x_649_ = lean_string_length(v___x_648_);
return v___x_649_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__39(void){
_start:
{
lean_object* v___x_650_; lean_object* v___x_651_; 
v___x_650_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__38, &l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__38_once, _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__38);
v___x_651_ = lean_nat_to_int(v___x_650_);
return v___x_651_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg(lean_object* v_x_656_){
_start:
{
uint8_t v_kind_657_; uint8_t v_owner_658_; lean_object* v_fmv_659_; lean_object* v_basis_660_; lean_object* v_lossBasis_661_; lean_object* v_held_662_; lean_object* v_owned_663_; lean_object* v_shield_664_; lean_object* v_donor_665_; lean_object* v_giftAge_666_; uint8_t v_inherited_667_; uint8_t v_gone_668_; lean_object* v___x_669_; lean_object* v___x_670_; lean_object* v___x_671_; lean_object* v___x_672_; lean_object* v___x_673_; lean_object* v___x_674_; uint8_t v___x_675_; lean_object* v___x_676_; lean_object* v___x_677_; lean_object* v___x_678_; lean_object* v___x_679_; lean_object* v___x_680_; lean_object* v___x_681_; lean_object* v___x_682_; lean_object* v___x_683_; lean_object* v___x_684_; lean_object* v___x_685_; lean_object* v___x_686_; lean_object* v___x_687_; lean_object* v___x_688_; lean_object* v___x_689_; lean_object* v___x_690_; lean_object* v___x_691_; lean_object* v___x_692_; lean_object* v___x_693_; lean_object* v___x_694_; lean_object* v___x_695_; lean_object* v___x_696_; lean_object* v___x_697_; lean_object* v___x_698_; lean_object* v___x_699_; lean_object* v___x_700_; lean_object* v___x_701_; lean_object* v___x_702_; lean_object* v___x_703_; lean_object* v___x_704_; lean_object* v___x_705_; lean_object* v___x_706_; lean_object* v___x_707_; lean_object* v___x_708_; lean_object* v___x_709_; lean_object* v___x_710_; lean_object* v___x_711_; lean_object* v___x_712_; lean_object* v___x_713_; lean_object* v___x_714_; lean_object* v___x_715_; lean_object* v___x_716_; lean_object* v___x_717_; lean_object* v___x_718_; lean_object* v___x_719_; lean_object* v___x_720_; lean_object* v___x_721_; lean_object* v___x_722_; lean_object* v___x_723_; lean_object* v___x_724_; lean_object* v___x_725_; lean_object* v___x_726_; lean_object* v___x_727_; lean_object* v___x_728_; lean_object* v___x_729_; lean_object* v___x_730_; lean_object* v___x_731_; lean_object* v___x_732_; lean_object* v___x_733_; lean_object* v___x_734_; lean_object* v___x_735_; lean_object* v___x_736_; lean_object* v___x_737_; lean_object* v___x_738_; lean_object* v___x_739_; lean_object* v___x_740_; lean_object* v___x_741_; lean_object* v___x_742_; lean_object* v___x_743_; lean_object* v___x_744_; lean_object* v___x_745_; lean_object* v___x_746_; lean_object* v___x_747_; lean_object* v___x_748_; lean_object* v___x_749_; lean_object* v___x_750_; lean_object* v___x_751_; lean_object* v___x_752_; lean_object* v___x_753_; lean_object* v___x_754_; lean_object* v___x_755_; lean_object* v___x_756_; lean_object* v___x_757_; lean_object* v___x_758_; lean_object* v___x_759_; lean_object* v___x_760_; lean_object* v___x_761_; lean_object* v___x_762_; lean_object* v___x_763_; lean_object* v___x_764_; lean_object* v___x_765_; lean_object* v___x_766_; lean_object* v___x_767_; lean_object* v___x_768_; lean_object* v___x_769_; lean_object* v___x_770_; lean_object* v___x_771_; lean_object* v___x_772_; lean_object* v___x_773_; lean_object* v___x_774_; lean_object* v___x_775_; lean_object* v___x_776_; lean_object* v___x_777_; lean_object* v___x_778_; lean_object* v___x_779_; lean_object* v___x_780_; lean_object* v___x_781_; lean_object* v___x_782_; lean_object* v___x_783_; lean_object* v___x_784_; lean_object* v___x_785_; lean_object* v___x_786_; lean_object* v___x_787_; lean_object* v___x_788_; lean_object* v___x_789_; lean_object* v___x_790_; lean_object* v___x_791_; lean_object* v___x_792_; lean_object* v___x_793_; lean_object* v___x_794_; lean_object* v___x_795_; lean_object* v___x_796_; lean_object* v___x_797_; 
v_kind_657_ = lean_ctor_get_uint8(v_x_656_, sizeof(void*)*8);
v_owner_658_ = lean_ctor_get_uint8(v_x_656_, sizeof(void*)*8 + 1);
v_fmv_659_ = lean_ctor_get(v_x_656_, 0);
lean_inc(v_fmv_659_);
v_basis_660_ = lean_ctor_get(v_x_656_, 1);
lean_inc(v_basis_660_);
v_lossBasis_661_ = lean_ctor_get(v_x_656_, 2);
lean_inc(v_lossBasis_661_);
v_held_662_ = lean_ctor_get(v_x_656_, 3);
lean_inc(v_held_662_);
v_owned_663_ = lean_ctor_get(v_x_656_, 4);
lean_inc(v_owned_663_);
v_shield_664_ = lean_ctor_get(v_x_656_, 5);
lean_inc(v_shield_664_);
v_donor_665_ = lean_ctor_get(v_x_656_, 6);
lean_inc(v_donor_665_);
v_giftAge_666_ = lean_ctor_get(v_x_656_, 7);
lean_inc(v_giftAge_666_);
v_inherited_667_ = lean_ctor_get_uint8(v_x_656_, sizeof(void*)*8 + 2);
v_gone_668_ = lean_ctor_get_uint8(v_x_656_, sizeof(void*)*8 + 3);
lean_dec_ref(v_x_656_);
v___x_669_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__5));
v___x_670_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__6));
v___x_671_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__7, &l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__7_once, _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__7);
v___x_672_ = lean_unsigned_to_nat(0u);
v___x_673_ = l_Legal_USTax_Hunt_Basis_instReprKind_repr(v_kind_657_, v___x_672_);
v___x_674_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_674_, 0, v___x_671_);
lean_ctor_set(v___x_674_, 1, v___x_673_);
v___x_675_ = 0;
v___x_676_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_676_, 0, v___x_674_);
lean_ctor_set_uint8(v___x_676_, sizeof(void*)*1, v___x_675_);
v___x_677_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_677_, 0, v___x_670_);
lean_ctor_set(v___x_677_, 1, v___x_676_);
v___x_678_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__9));
v___x_679_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_679_, 0, v___x_677_);
lean_ctor_set(v___x_679_, 1, v___x_678_);
v___x_680_ = lean_box(1);
v___x_681_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_681_, 0, v___x_679_);
lean_ctor_set(v___x_681_, 1, v___x_680_);
v___x_682_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__11));
v___x_683_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_683_, 0, v___x_681_);
lean_ctor_set(v___x_683_, 1, v___x_682_);
v___x_684_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_684_, 0, v___x_683_);
lean_ctor_set(v___x_684_, 1, v___x_669_);
v___x_685_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__12, &l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__12_once, _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__12);
v___x_686_ = l_Legal_USTax_Hunt_Basis_instReprWho_repr(v_owner_658_, v___x_672_);
v___x_687_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_687_, 0, v___x_685_);
lean_ctor_set(v___x_687_, 1, v___x_686_);
v___x_688_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_688_, 0, v___x_687_);
lean_ctor_set_uint8(v___x_688_, sizeof(void*)*1, v___x_675_);
v___x_689_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_689_, 0, v___x_684_);
lean_ctor_set(v___x_689_, 1, v___x_688_);
v___x_690_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_690_, 0, v___x_689_);
lean_ctor_set(v___x_690_, 1, v___x_678_);
v___x_691_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_691_, 0, v___x_690_);
lean_ctor_set(v___x_691_, 1, v___x_680_);
v___x_692_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__14));
v___x_693_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_693_, 0, v___x_691_);
lean_ctor_set(v___x_693_, 1, v___x_692_);
v___x_694_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_694_, 0, v___x_693_);
lean_ctor_set(v___x_694_, 1, v___x_669_);
v___x_695_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__15, &l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__15_once, _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__15);
v___x_696_ = l_Nat_reprFast(v_fmv_659_);
v___x_697_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_697_, 0, v___x_696_);
v___x_698_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_698_, 0, v___x_695_);
lean_ctor_set(v___x_698_, 1, v___x_697_);
v___x_699_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_699_, 0, v___x_698_);
lean_ctor_set_uint8(v___x_699_, sizeof(void*)*1, v___x_675_);
v___x_700_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_700_, 0, v___x_694_);
lean_ctor_set(v___x_700_, 1, v___x_699_);
v___x_701_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_701_, 0, v___x_700_);
lean_ctor_set(v___x_701_, 1, v___x_678_);
v___x_702_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_702_, 0, v___x_701_);
lean_ctor_set(v___x_702_, 1, v___x_680_);
v___x_703_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__17));
v___x_704_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_704_, 0, v___x_702_);
lean_ctor_set(v___x_704_, 1, v___x_703_);
v___x_705_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_705_, 0, v___x_704_);
lean_ctor_set(v___x_705_, 1, v___x_669_);
v___x_706_ = l_Nat_reprFast(v_basis_660_);
v___x_707_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_707_, 0, v___x_706_);
v___x_708_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_708_, 0, v___x_685_);
lean_ctor_set(v___x_708_, 1, v___x_707_);
v___x_709_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_709_, 0, v___x_708_);
lean_ctor_set_uint8(v___x_709_, sizeof(void*)*1, v___x_675_);
v___x_710_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_710_, 0, v___x_705_);
lean_ctor_set(v___x_710_, 1, v___x_709_);
v___x_711_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_711_, 0, v___x_710_);
lean_ctor_set(v___x_711_, 1, v___x_678_);
v___x_712_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_712_, 0, v___x_711_);
lean_ctor_set(v___x_712_, 1, v___x_680_);
v___x_713_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__19));
v___x_714_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_714_, 0, v___x_712_);
lean_ctor_set(v___x_714_, 1, v___x_713_);
v___x_715_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_715_, 0, v___x_714_);
lean_ctor_set(v___x_715_, 1, v___x_669_);
v___x_716_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__20, &l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__20_once, _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__20);
v___x_717_ = l_Nat_reprFast(v_lossBasis_661_);
v___x_718_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_718_, 0, v___x_717_);
v___x_719_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_719_, 0, v___x_716_);
lean_ctor_set(v___x_719_, 1, v___x_718_);
v___x_720_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_720_, 0, v___x_719_);
lean_ctor_set_uint8(v___x_720_, sizeof(void*)*1, v___x_675_);
v___x_721_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_721_, 0, v___x_715_);
lean_ctor_set(v___x_721_, 1, v___x_720_);
v___x_722_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_722_, 0, v___x_721_);
lean_ctor_set(v___x_722_, 1, v___x_678_);
v___x_723_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_723_, 0, v___x_722_);
lean_ctor_set(v___x_723_, 1, v___x_680_);
v___x_724_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__22));
v___x_725_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_725_, 0, v___x_723_);
lean_ctor_set(v___x_725_, 1, v___x_724_);
v___x_726_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_726_, 0, v___x_725_);
lean_ctor_set(v___x_726_, 1, v___x_669_);
v___x_727_ = l_Nat_reprFast(v_held_662_);
v___x_728_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_728_, 0, v___x_727_);
v___x_729_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_729_, 0, v___x_671_);
lean_ctor_set(v___x_729_, 1, v___x_728_);
v___x_730_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_730_, 0, v___x_729_);
lean_ctor_set_uint8(v___x_730_, sizeof(void*)*1, v___x_675_);
v___x_731_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_731_, 0, v___x_726_);
lean_ctor_set(v___x_731_, 1, v___x_730_);
v___x_732_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_732_, 0, v___x_731_);
lean_ctor_set(v___x_732_, 1, v___x_678_);
v___x_733_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_733_, 0, v___x_732_);
lean_ctor_set(v___x_733_, 1, v___x_680_);
v___x_734_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__24));
v___x_735_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_735_, 0, v___x_733_);
lean_ctor_set(v___x_735_, 1, v___x_734_);
v___x_736_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_736_, 0, v___x_735_);
lean_ctor_set(v___x_736_, 1, v___x_669_);
v___x_737_ = l_Nat_reprFast(v_owned_663_);
v___x_738_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_738_, 0, v___x_737_);
v___x_739_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_739_, 0, v___x_685_);
lean_ctor_set(v___x_739_, 1, v___x_738_);
v___x_740_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_740_, 0, v___x_739_);
lean_ctor_set_uint8(v___x_740_, sizeof(void*)*1, v___x_675_);
v___x_741_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_741_, 0, v___x_736_);
lean_ctor_set(v___x_741_, 1, v___x_740_);
v___x_742_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_742_, 0, v___x_741_);
lean_ctor_set(v___x_742_, 1, v___x_678_);
v___x_743_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_743_, 0, v___x_742_);
lean_ctor_set(v___x_743_, 1, v___x_680_);
v___x_744_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__26));
v___x_745_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_745_, 0, v___x_743_);
lean_ctor_set(v___x_745_, 1, v___x_744_);
v___x_746_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_746_, 0, v___x_745_);
lean_ctor_set(v___x_746_, 1, v___x_669_);
v___x_747_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__27, &l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__27_once, _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__27);
v___x_748_ = l_Nat_reprFast(v_shield_664_);
v___x_749_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_749_, 0, v___x_748_);
v___x_750_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_750_, 0, v___x_747_);
lean_ctor_set(v___x_750_, 1, v___x_749_);
v___x_751_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_751_, 0, v___x_750_);
lean_ctor_set_uint8(v___x_751_, sizeof(void*)*1, v___x_675_);
v___x_752_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_752_, 0, v___x_746_);
lean_ctor_set(v___x_752_, 1, v___x_751_);
v___x_753_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_753_, 0, v___x_752_);
lean_ctor_set(v___x_753_, 1, v___x_678_);
v___x_754_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_754_, 0, v___x_753_);
lean_ctor_set(v___x_754_, 1, v___x_680_);
v___x_755_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__29));
v___x_756_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_756_, 0, v___x_754_);
lean_ctor_set(v___x_756_, 1, v___x_755_);
v___x_757_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_757_, 0, v___x_756_);
lean_ctor_set(v___x_757_, 1, v___x_669_);
v___x_758_ = l_Option_repr___at___00Legal_USTax_Hunt_Basis_instReprLot_repr_spec__0(v_donor_665_, v___x_672_);
lean_dec(v_donor_665_);
v___x_759_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_759_, 0, v___x_685_);
lean_ctor_set(v___x_759_, 1, v___x_758_);
v___x_760_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_760_, 0, v___x_759_);
lean_ctor_set_uint8(v___x_760_, sizeof(void*)*1, v___x_675_);
v___x_761_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_761_, 0, v___x_757_);
lean_ctor_set(v___x_761_, 1, v___x_760_);
v___x_762_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_762_, 0, v___x_761_);
lean_ctor_set(v___x_762_, 1, v___x_678_);
v___x_763_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_763_, 0, v___x_762_);
lean_ctor_set(v___x_763_, 1, v___x_680_);
v___x_764_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__31));
v___x_765_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_765_, 0, v___x_763_);
lean_ctor_set(v___x_765_, 1, v___x_764_);
v___x_766_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_766_, 0, v___x_765_);
lean_ctor_set(v___x_766_, 1, v___x_669_);
v___x_767_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__32, &l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__32_once, _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__32);
v___x_768_ = l_Nat_reprFast(v_giftAge_666_);
v___x_769_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_769_, 0, v___x_768_);
v___x_770_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_770_, 0, v___x_767_);
lean_ctor_set(v___x_770_, 1, v___x_769_);
v___x_771_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_771_, 0, v___x_770_);
lean_ctor_set_uint8(v___x_771_, sizeof(void*)*1, v___x_675_);
v___x_772_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_772_, 0, v___x_766_);
lean_ctor_set(v___x_772_, 1, v___x_771_);
v___x_773_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_773_, 0, v___x_772_);
lean_ctor_set(v___x_773_, 1, v___x_678_);
v___x_774_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_774_, 0, v___x_773_);
lean_ctor_set(v___x_774_, 1, v___x_680_);
v___x_775_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__34));
v___x_776_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_776_, 0, v___x_774_);
lean_ctor_set(v___x_776_, 1, v___x_775_);
v___x_777_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_777_, 0, v___x_776_);
lean_ctor_set(v___x_777_, 1, v___x_669_);
v___x_778_ = l_Bool_repr___redArg(v_inherited_667_);
v___x_779_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_779_, 0, v___x_716_);
lean_ctor_set(v___x_779_, 1, v___x_778_);
v___x_780_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_780_, 0, v___x_779_);
lean_ctor_set_uint8(v___x_780_, sizeof(void*)*1, v___x_675_);
v___x_781_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_781_, 0, v___x_777_);
lean_ctor_set(v___x_781_, 1, v___x_780_);
v___x_782_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_782_, 0, v___x_781_);
lean_ctor_set(v___x_782_, 1, v___x_678_);
v___x_783_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_783_, 0, v___x_782_);
lean_ctor_set(v___x_783_, 1, v___x_680_);
v___x_784_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__36));
v___x_785_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_785_, 0, v___x_783_);
lean_ctor_set(v___x_785_, 1, v___x_784_);
v___x_786_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_786_, 0, v___x_785_);
lean_ctor_set(v___x_786_, 1, v___x_669_);
v___x_787_ = l_Bool_repr___redArg(v_gone_668_);
v___x_788_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_788_, 0, v___x_671_);
lean_ctor_set(v___x_788_, 1, v___x_787_);
v___x_789_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_789_, 0, v___x_788_);
lean_ctor_set_uint8(v___x_789_, sizeof(void*)*1, v___x_675_);
v___x_790_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_790_, 0, v___x_786_);
lean_ctor_set(v___x_790_, 1, v___x_789_);
v___x_791_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__39, &l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__39_once, _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__39);
v___x_792_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__40));
v___x_793_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_793_, 0, v___x_792_);
lean_ctor_set(v___x_793_, 1, v___x_790_);
v___x_794_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__41));
v___x_795_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_795_, 0, v___x_793_);
lean_ctor_set(v___x_795_, 1, v___x_794_);
v___x_796_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_796_, 0, v___x_791_);
lean_ctor_set(v___x_796_, 1, v___x_795_);
v___x_797_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_797_, 0, v___x_796_);
lean_ctor_set_uint8(v___x_797_, sizeof(void*)*1, v___x_675_);
return v___x_797_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr(lean_object* v_x_798_, lean_object* v_prec_799_){
_start:
{
lean_object* v___x_800_; 
v___x_800_ = l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg(v_x_798_);
return v___x_800_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprLot_repr___boxed(lean_object* v_x_801_, lean_object* v_prec_802_){
_start:
{
lean_object* v_res_803_; 
v_res_803_ = l_Legal_USTax_Hunt_Basis_instReprLot_repr(v_x_801_, v_prec_802_);
lean_dec(v_prec_802_);
return v_res_803_;
}
}
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instBEqRet_beq(lean_object* v_x_814_, lean_object* v_x_815_){
_start:
{
lean_object* v_st_816_; lean_object* v_lt_817_; lean_object* v_g28_818_; lean_object* v_cfS_819_; lean_object* v_cfL_820_; lean_object* v_00x121_821_; lean_object* v_xQ_822_; lean_object* v_st_823_; lean_object* v_lt_824_; lean_object* v_g28_825_; lean_object* v_cfS_826_; lean_object* v_cfL_827_; lean_object* v_00x121_828_; lean_object* v_xQ_829_; uint8_t v___x_830_; 
v_st_816_ = lean_ctor_get(v_x_814_, 0);
v_lt_817_ = lean_ctor_get(v_x_814_, 1);
v_g28_818_ = lean_ctor_get(v_x_814_, 2);
v_cfS_819_ = lean_ctor_get(v_x_814_, 3);
v_cfL_820_ = lean_ctor_get(v_x_814_, 4);
v_00x121_821_ = lean_ctor_get(v_x_814_, 5);
v_xQ_822_ = lean_ctor_get(v_x_814_, 6);
v_st_823_ = lean_ctor_get(v_x_815_, 0);
v_lt_824_ = lean_ctor_get(v_x_815_, 1);
v_g28_825_ = lean_ctor_get(v_x_815_, 2);
v_cfS_826_ = lean_ctor_get(v_x_815_, 3);
v_cfL_827_ = lean_ctor_get(v_x_815_, 4);
v_00x121_828_ = lean_ctor_get(v_x_815_, 5);
v_xQ_829_ = lean_ctor_get(v_x_815_, 6);
v___x_830_ = lean_int_dec_eq(v_st_816_, v_st_823_);
if (v___x_830_ == 0)
{
return v___x_830_;
}
else
{
uint8_t v___x_831_; 
v___x_831_ = lean_int_dec_eq(v_lt_817_, v_lt_824_);
if (v___x_831_ == 0)
{
return v___x_831_;
}
else
{
uint8_t v___x_832_; 
v___x_832_ = lean_nat_dec_eq(v_g28_818_, v_g28_825_);
if (v___x_832_ == 0)
{
return v___x_832_;
}
else
{
uint8_t v___x_833_; 
v___x_833_ = lean_nat_dec_eq(v_cfS_819_, v_cfS_826_);
if (v___x_833_ == 0)
{
return v___x_833_;
}
else
{
uint8_t v___x_834_; 
v___x_834_ = lean_nat_dec_eq(v_cfL_820_, v_cfL_827_);
if (v___x_834_ == 0)
{
return v___x_834_;
}
else
{
uint8_t v___x_835_; 
v___x_835_ = lean_nat_dec_eq(v_00x121_821_, v_00x121_828_);
if (v___x_835_ == 0)
{
return v___x_835_;
}
else
{
uint8_t v___x_836_; 
v___x_836_ = lean_nat_dec_eq(v_xQ_822_, v_xQ_829_);
return v___x_836_;
}
}
}
}
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instBEqRet_beq___boxed(lean_object* v_x_837_, lean_object* v_x_838_){
_start:
{
uint8_t v_res_839_; lean_object* v_r_840_; 
v_res_839_ = l_Legal_USTax_Hunt_Basis_instBEqRet_beq(v_x_837_, v_x_838_);
lean_dec_ref(v_x_838_);
lean_dec_ref(v_x_837_);
v_r_840_ = lean_box(v_res_839_);
return v_r_840_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0(void){
_start:
{
lean_object* v_natZero_843_; lean_object* v_intZero_844_; 
v_natZero_843_ = lean_unsigned_to_nat(0u);
v_intZero_844_ = lean_nat_to_int(v_natZero_843_);
return v_intZero_844_;
}
}
LEAN_EXPORT uint64_t l_Legal_USTax_Hunt_Basis_instHashableRet_hash(lean_object* v_x_845_){
_start:
{
lean_object* v_st_846_; lean_object* v_lt_847_; lean_object* v_g28_848_; lean_object* v_cfS_849_; lean_object* v_cfL_850_; lean_object* v_00x121_851_; lean_object* v_xQ_852_; uint64_t v___y_854_; uint64_t v___y_855_; uint64_t v___x_867_; uint64_t v___y_869_; lean_object* v_intZero_884_; uint8_t v_isNeg_885_; 
v_st_846_ = lean_ctor_get(v_x_845_, 0);
v_lt_847_ = lean_ctor_get(v_x_845_, 1);
v_g28_848_ = lean_ctor_get(v_x_845_, 2);
v_cfS_849_ = lean_ctor_get(v_x_845_, 3);
v_cfL_850_ = lean_ctor_get(v_x_845_, 4);
v_00x121_851_ = lean_ctor_get(v_x_845_, 5);
v_xQ_852_ = lean_ctor_get(v_x_845_, 6);
v___x_867_ = 0ULL;
v_intZero_884_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0, &l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0);
v_isNeg_885_ = lean_int_dec_lt(v_st_846_, v_intZero_884_);
if (v_isNeg_885_ == 0)
{
lean_object* v_a_886_; lean_object* v___x_887_; lean_object* v___x_888_; uint64_t v___x_889_; 
v_a_886_ = lean_nat_abs(v_st_846_);
v___x_887_ = lean_unsigned_to_nat(2u);
v___x_888_ = lean_nat_mul(v___x_887_, v_a_886_);
lean_dec(v_a_886_);
v___x_889_ = lean_uint64_of_nat(v___x_888_);
lean_dec(v___x_888_);
v___y_869_ = v___x_889_;
goto v___jp_868_;
}
else
{
lean_object* v_abs_890_; lean_object* v_one_891_; lean_object* v_a_892_; lean_object* v___x_893_; lean_object* v___x_894_; lean_object* v___x_895_; uint64_t v___x_896_; 
v_abs_890_ = lean_nat_abs(v_st_846_);
v_one_891_ = lean_unsigned_to_nat(1u);
v_a_892_ = lean_nat_sub(v_abs_890_, v_one_891_);
lean_dec(v_abs_890_);
v___x_893_ = lean_unsigned_to_nat(2u);
v___x_894_ = lean_nat_mul(v___x_893_, v_a_892_);
lean_dec(v_a_892_);
v___x_895_ = lean_nat_add(v___x_894_, v_one_891_);
lean_dec(v___x_894_);
v___x_896_ = lean_uint64_of_nat(v___x_895_);
lean_dec(v___x_895_);
v___y_869_ = v___x_896_;
goto v___jp_868_;
}
v___jp_853_:
{
uint64_t v___x_856_; uint64_t v___x_857_; uint64_t v___x_858_; uint64_t v___x_859_; uint64_t v___x_860_; uint64_t v___x_861_; uint64_t v___x_862_; uint64_t v___x_863_; uint64_t v___x_864_; uint64_t v___x_865_; uint64_t v___x_866_; 
v___x_856_ = lean_uint64_mix_hash(v___y_854_, v___y_855_);
v___x_857_ = lean_uint64_of_nat(v_g28_848_);
v___x_858_ = lean_uint64_mix_hash(v___x_856_, v___x_857_);
v___x_859_ = lean_uint64_of_nat(v_cfS_849_);
v___x_860_ = lean_uint64_mix_hash(v___x_858_, v___x_859_);
v___x_861_ = lean_uint64_of_nat(v_cfL_850_);
v___x_862_ = lean_uint64_mix_hash(v___x_860_, v___x_861_);
v___x_863_ = lean_uint64_of_nat(v_00x121_851_);
v___x_864_ = lean_uint64_mix_hash(v___x_862_, v___x_863_);
v___x_865_ = lean_uint64_of_nat(v_xQ_852_);
v___x_866_ = lean_uint64_mix_hash(v___x_864_, v___x_865_);
return v___x_866_;
}
v___jp_868_:
{
uint64_t v___x_870_; lean_object* v_intZero_871_; uint8_t v_isNeg_872_; 
v___x_870_ = lean_uint64_mix_hash(v___x_867_, v___y_869_);
v_intZero_871_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0, &l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0);
v_isNeg_872_ = lean_int_dec_lt(v_lt_847_, v_intZero_871_);
if (v_isNeg_872_ == 0)
{
lean_object* v_a_873_; lean_object* v___x_874_; lean_object* v___x_875_; uint64_t v___x_876_; 
v_a_873_ = lean_nat_abs(v_lt_847_);
v___x_874_ = lean_unsigned_to_nat(2u);
v___x_875_ = lean_nat_mul(v___x_874_, v_a_873_);
lean_dec(v_a_873_);
v___x_876_ = lean_uint64_of_nat(v___x_875_);
lean_dec(v___x_875_);
v___y_854_ = v___x_870_;
v___y_855_ = v___x_876_;
goto v___jp_853_;
}
else
{
lean_object* v_abs_877_; lean_object* v_one_878_; lean_object* v_a_879_; lean_object* v___x_880_; lean_object* v___x_881_; lean_object* v___x_882_; uint64_t v___x_883_; 
v_abs_877_ = lean_nat_abs(v_lt_847_);
v_one_878_ = lean_unsigned_to_nat(1u);
v_a_879_ = lean_nat_sub(v_abs_877_, v_one_878_);
lean_dec(v_abs_877_);
v___x_880_ = lean_unsigned_to_nat(2u);
v___x_881_ = lean_nat_mul(v___x_880_, v_a_879_);
lean_dec(v_a_879_);
v___x_882_ = lean_nat_add(v___x_881_, v_one_878_);
lean_dec(v___x_881_);
v___x_883_ = lean_uint64_of_nat(v___x_882_);
lean_dec(v___x_882_);
v___y_854_ = v___x_870_;
v___y_855_ = v___x_883_;
goto v___jp_853_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instHashableRet_hash___boxed(lean_object* v_x_897_){
_start:
{
uint64_t v_res_898_; lean_object* v_r_899_; 
v_res_898_ = l_Legal_USTax_Hunt_Basis_instHashableRet_hash(v_x_897_);
lean_dec_ref(v_x_897_);
v_r_899_ = lean_box_uint64(v_res_898_);
return v_r_899_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__4(void){
_start:
{
lean_object* v___x_911_; lean_object* v___x_912_; 
v___x_911_ = lean_unsigned_to_nat(6u);
v___x_912_ = lean_nat_to_int(v___x_911_);
return v___x_912_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg(lean_object* v_x_931_){
_start:
{
lean_object* v_st_932_; lean_object* v_lt_933_; lean_object* v_g28_934_; lean_object* v_cfS_935_; lean_object* v_cfL_936_; lean_object* v_00x121_937_; lean_object* v_xQ_938_; lean_object* v___x_939_; lean_object* v___x_940_; lean_object* v___x_941_; lean_object* v___y_943_; uint8_t v___y_944_; lean_object* v___y_945_; lean_object* v___y_946_; lean_object* v___y_947_; lean_object* v___y_1011_; lean_object* v___x_1031_; lean_object* v___x_1032_; uint8_t v___x_1033_; 
v_st_932_ = lean_ctor_get(v_x_931_, 0);
lean_inc(v_st_932_);
v_lt_933_ = lean_ctor_get(v_x_931_, 1);
lean_inc(v_lt_933_);
v_g28_934_ = lean_ctor_get(v_x_931_, 2);
lean_inc(v_g28_934_);
v_cfS_935_ = lean_ctor_get(v_x_931_, 3);
lean_inc(v_cfS_935_);
v_cfL_936_ = lean_ctor_get(v_x_931_, 4);
lean_inc(v_cfL_936_);
v_00x121_937_ = lean_ctor_get(v_x_931_, 5);
lean_inc(v_00x121_937_);
v_xQ_938_ = lean_ctor_get(v_x_931_, 6);
lean_inc(v_xQ_938_);
lean_dec_ref(v_x_931_);
v___x_939_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__5));
v___x_940_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__3));
v___x_941_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__4, &l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__4_once, _init_l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__4);
v___x_1031_ = lean_unsigned_to_nat(0u);
v___x_1032_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0, &l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0);
v___x_1033_ = lean_int_dec_lt(v_st_932_, v___x_1032_);
if (v___x_1033_ == 0)
{
lean_object* v___x_1034_; lean_object* v___x_1035_; 
v___x_1034_ = l_Int_repr(v_st_932_);
lean_dec(v_st_932_);
v___x_1035_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1035_, 0, v___x_1034_);
v___y_1011_ = v___x_1035_;
goto v___jp_1010_;
}
else
{
lean_object* v___x_1036_; lean_object* v___x_1037_; lean_object* v___x_1038_; 
v___x_1036_ = l_Int_repr(v_st_932_);
lean_dec(v_st_932_);
v___x_1037_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1037_, 0, v___x_1036_);
v___x_1038_ = l_Repr_addAppParen(v___x_1037_, v___x_1031_);
v___y_1011_ = v___x_1038_;
goto v___jp_1010_;
}
v___jp_942_:
{
lean_object* v___x_948_; lean_object* v___x_949_; lean_object* v___x_950_; lean_object* v___x_951_; lean_object* v___x_952_; lean_object* v___x_953_; lean_object* v___x_954_; lean_object* v___x_955_; lean_object* v___x_956_; lean_object* v___x_957_; lean_object* v___x_958_; lean_object* v___x_959_; lean_object* v___x_960_; lean_object* v___x_961_; lean_object* v___x_962_; lean_object* v___x_963_; lean_object* v___x_964_; lean_object* v___x_965_; lean_object* v___x_966_; lean_object* v___x_967_; lean_object* v___x_968_; lean_object* v___x_969_; lean_object* v___x_970_; lean_object* v___x_971_; lean_object* v___x_972_; lean_object* v___x_973_; lean_object* v___x_974_; lean_object* v___x_975_; lean_object* v___x_976_; lean_object* v___x_977_; lean_object* v___x_978_; lean_object* v___x_979_; lean_object* v___x_980_; lean_object* v___x_981_; lean_object* v___x_982_; lean_object* v___x_983_; lean_object* v___x_984_; lean_object* v___x_985_; lean_object* v___x_986_; lean_object* v___x_987_; lean_object* v___x_988_; lean_object* v___x_989_; lean_object* v___x_990_; lean_object* v___x_991_; lean_object* v___x_992_; lean_object* v___x_993_; lean_object* v___x_994_; lean_object* v___x_995_; lean_object* v___x_996_; lean_object* v___x_997_; lean_object* v___x_998_; lean_object* v___x_999_; lean_object* v___x_1000_; lean_object* v___x_1001_; lean_object* v___x_1002_; lean_object* v___x_1003_; lean_object* v___x_1004_; lean_object* v___x_1005_; lean_object* v___x_1006_; lean_object* v___x_1007_; lean_object* v___x_1008_; lean_object* v___x_1009_; 
v___x_948_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_948_, 0, v___x_941_);
lean_ctor_set(v___x_948_, 1, v___y_947_);
v___x_949_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_949_, 0, v___x_948_);
lean_ctor_set_uint8(v___x_949_, sizeof(void*)*1, v___y_944_);
v___x_950_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_950_, 0, v___y_946_);
lean_ctor_set(v___x_950_, 1, v___x_949_);
lean_inc_n(v___y_943_, 5);
v___x_951_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_951_, 0, v___x_950_);
lean_ctor_set(v___x_951_, 1, v___y_943_);
lean_inc_n(v___y_945_, 5);
v___x_952_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_952_, 0, v___x_951_);
lean_ctor_set(v___x_952_, 1, v___y_945_);
v___x_953_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__6));
v___x_954_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_954_, 0, v___x_952_);
lean_ctor_set(v___x_954_, 1, v___x_953_);
v___x_955_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_955_, 0, v___x_954_);
lean_ctor_set(v___x_955_, 1, v___x_939_);
v___x_956_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__15, &l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__15_once, _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__15);
v___x_957_ = l_Nat_reprFast(v_g28_934_);
v___x_958_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_958_, 0, v___x_957_);
v___x_959_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_959_, 0, v___x_956_);
lean_ctor_set(v___x_959_, 1, v___x_958_);
v___x_960_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_960_, 0, v___x_959_);
lean_ctor_set_uint8(v___x_960_, sizeof(void*)*1, v___y_944_);
v___x_961_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_961_, 0, v___x_955_);
lean_ctor_set(v___x_961_, 1, v___x_960_);
v___x_962_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_962_, 0, v___x_961_);
lean_ctor_set(v___x_962_, 1, v___y_943_);
v___x_963_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_963_, 0, v___x_962_);
lean_ctor_set(v___x_963_, 1, v___y_945_);
v___x_964_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__8));
v___x_965_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_965_, 0, v___x_963_);
lean_ctor_set(v___x_965_, 1, v___x_964_);
v___x_966_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_966_, 0, v___x_965_);
lean_ctor_set(v___x_966_, 1, v___x_939_);
v___x_967_ = l_Nat_reprFast(v_cfS_935_);
v___x_968_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_968_, 0, v___x_967_);
v___x_969_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_969_, 0, v___x_956_);
lean_ctor_set(v___x_969_, 1, v___x_968_);
v___x_970_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_970_, 0, v___x_969_);
lean_ctor_set_uint8(v___x_970_, sizeof(void*)*1, v___y_944_);
v___x_971_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_971_, 0, v___x_966_);
lean_ctor_set(v___x_971_, 1, v___x_970_);
v___x_972_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_972_, 0, v___x_971_);
lean_ctor_set(v___x_972_, 1, v___y_943_);
v___x_973_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_973_, 0, v___x_972_);
lean_ctor_set(v___x_973_, 1, v___y_945_);
v___x_974_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__10));
v___x_975_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_975_, 0, v___x_973_);
lean_ctor_set(v___x_975_, 1, v___x_974_);
v___x_976_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_976_, 0, v___x_975_);
lean_ctor_set(v___x_976_, 1, v___x_939_);
v___x_977_ = l_Nat_reprFast(v_cfL_936_);
v___x_978_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_978_, 0, v___x_977_);
v___x_979_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_979_, 0, v___x_956_);
lean_ctor_set(v___x_979_, 1, v___x_978_);
v___x_980_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_980_, 0, v___x_979_);
lean_ctor_set_uint8(v___x_980_, sizeof(void*)*1, v___y_944_);
v___x_981_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_981_, 0, v___x_976_);
lean_ctor_set(v___x_981_, 1, v___x_980_);
v___x_982_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_982_, 0, v___x_981_);
lean_ctor_set(v___x_982_, 1, v___y_943_);
v___x_983_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_983_, 0, v___x_982_);
lean_ctor_set(v___x_983_, 1, v___y_945_);
v___x_984_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__12));
v___x_985_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_985_, 0, v___x_983_);
lean_ctor_set(v___x_985_, 1, v___x_984_);
v___x_986_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_986_, 0, v___x_985_);
lean_ctor_set(v___x_986_, 1, v___x_939_);
v___x_987_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__7, &l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__7_once, _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__7);
v___x_988_ = l_Nat_reprFast(v_00x121_937_);
v___x_989_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_989_, 0, v___x_988_);
v___x_990_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_990_, 0, v___x_987_);
lean_ctor_set(v___x_990_, 1, v___x_989_);
v___x_991_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_991_, 0, v___x_990_);
lean_ctor_set_uint8(v___x_991_, sizeof(void*)*1, v___y_944_);
v___x_992_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_992_, 0, v___x_986_);
lean_ctor_set(v___x_992_, 1, v___x_991_);
v___x_993_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_993_, 0, v___x_992_);
lean_ctor_set(v___x_993_, 1, v___y_943_);
v___x_994_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_994_, 0, v___x_993_);
lean_ctor_set(v___x_994_, 1, v___y_945_);
v___x_995_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__14));
v___x_996_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_996_, 0, v___x_994_);
lean_ctor_set(v___x_996_, 1, v___x_995_);
v___x_997_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_997_, 0, v___x_996_);
lean_ctor_set(v___x_997_, 1, v___x_939_);
v___x_998_ = l_Nat_reprFast(v_xQ_938_);
v___x_999_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_999_, 0, v___x_998_);
v___x_1000_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1000_, 0, v___x_941_);
lean_ctor_set(v___x_1000_, 1, v___x_999_);
v___x_1001_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1001_, 0, v___x_1000_);
lean_ctor_set_uint8(v___x_1001_, sizeof(void*)*1, v___y_944_);
v___x_1002_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1002_, 0, v___x_997_);
lean_ctor_set(v___x_1002_, 1, v___x_1001_);
v___x_1003_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__39, &l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__39_once, _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__39);
v___x_1004_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__40));
v___x_1005_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1005_, 0, v___x_1004_);
lean_ctor_set(v___x_1005_, 1, v___x_1002_);
v___x_1006_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__41));
v___x_1007_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1007_, 0, v___x_1005_);
lean_ctor_set(v___x_1007_, 1, v___x_1006_);
v___x_1008_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1008_, 0, v___x_1003_);
lean_ctor_set(v___x_1008_, 1, v___x_1007_);
v___x_1009_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1009_, 0, v___x_1008_);
lean_ctor_set_uint8(v___x_1009_, sizeof(void*)*1, v___y_944_);
return v___x_1009_;
}
v___jp_1010_:
{
lean_object* v___x_1012_; uint8_t v___x_1013_; lean_object* v___x_1014_; lean_object* v___x_1015_; lean_object* v___x_1016_; lean_object* v___x_1017_; lean_object* v___x_1018_; lean_object* v___x_1019_; lean_object* v___x_1020_; lean_object* v___x_1021_; lean_object* v___x_1022_; lean_object* v___x_1023_; lean_object* v___x_1024_; uint8_t v___x_1025_; 
v___x_1012_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1012_, 0, v___x_941_);
lean_ctor_set(v___x_1012_, 1, v___y_1011_);
v___x_1013_ = 0;
v___x_1014_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1014_, 0, v___x_1012_);
lean_ctor_set_uint8(v___x_1014_, sizeof(void*)*1, v___x_1013_);
v___x_1015_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1015_, 0, v___x_940_);
lean_ctor_set(v___x_1015_, 1, v___x_1014_);
v___x_1016_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__9));
v___x_1017_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1017_, 0, v___x_1015_);
lean_ctor_set(v___x_1017_, 1, v___x_1016_);
v___x_1018_ = lean_box(1);
v___x_1019_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1019_, 0, v___x_1017_);
lean_ctor_set(v___x_1019_, 1, v___x_1018_);
v___x_1020_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__16));
v___x_1021_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1021_, 0, v___x_1019_);
lean_ctor_set(v___x_1021_, 1, v___x_1020_);
v___x_1022_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1022_, 0, v___x_1021_);
lean_ctor_set(v___x_1022_, 1, v___x_939_);
v___x_1023_ = lean_unsigned_to_nat(0u);
v___x_1024_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0, &l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0);
v___x_1025_ = lean_int_dec_lt(v_lt_933_, v___x_1024_);
if (v___x_1025_ == 0)
{
lean_object* v___x_1026_; lean_object* v___x_1027_; 
v___x_1026_ = l_Int_repr(v_lt_933_);
lean_dec(v_lt_933_);
v___x_1027_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1027_, 0, v___x_1026_);
v___y_943_ = v___x_1016_;
v___y_944_ = v___x_1013_;
v___y_945_ = v___x_1018_;
v___y_946_ = v___x_1022_;
v___y_947_ = v___x_1027_;
goto v___jp_942_;
}
else
{
lean_object* v___x_1028_; lean_object* v___x_1029_; lean_object* v___x_1030_; 
v___x_1028_ = l_Int_repr(v_lt_933_);
lean_dec(v_lt_933_);
v___x_1029_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1029_, 0, v___x_1028_);
v___x_1030_ = l_Repr_addAppParen(v___x_1029_, v___x_1023_);
v___y_943_ = v___x_1016_;
v___y_944_ = v___x_1013_;
v___y_945_ = v___x_1018_;
v___y_946_ = v___x_1022_;
v___y_947_ = v___x_1030_;
goto v___jp_942_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr(lean_object* v_x_1039_, lean_object* v_prec_1040_){
_start:
{
lean_object* v___x_1041_; 
v___x_1041_ = l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg(v_x_1039_);
return v___x_1041_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprRet_repr___boxed(lean_object* v_x_1042_, lean_object* v_prec_1043_){
_start:
{
lean_object* v_res_1044_; 
v_res_1044_ = l_Legal_USTax_Hunt_Basis_instReprRet_repr(v_x_1042_, v_prec_1043_);
lean_dec(v_prec_1043_);
return v_res_1044_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0(void){
_start:
{
lean_object* v___x_1047_; lean_object* v___x_1048_; lean_object* v___x_1049_; 
v___x_1047_ = lean_unsigned_to_nat(0u);
v___x_1048_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0, &l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0);
v___x_1049_ = lean_alloc_ctor(0, 7, 0);
lean_ctor_set(v___x_1049_, 0, v___x_1048_);
lean_ctor_set(v___x_1049_, 1, v___x_1048_);
lean_ctor_set(v___x_1049_, 2, v___x_1047_);
lean_ctor_set(v___x_1049_, 3, v___x_1047_);
lean_ctor_set(v___x_1049_, 4, v___x_1047_);
lean_ctor_set(v___x_1049_, 5, v___x_1047_);
lean_ctor_set(v___x_1049_, 6, v___x_1047_);
return v___x_1049_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_instInhabitedRet_default(void){
_start:
{
lean_object* v___x_1050_; 
v___x_1050_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0, &l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0);
return v___x_1050_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_instInhabitedRet(void){
_start:
{
lean_object* v___x_1051_; 
v___x_1051_ = l_Legal_USTax_Hunt_Basis_instInhabitedRet_default;
return v___x_1051_;
}
}
LEAN_EXPORT uint8_t l_List_beq___at___00Legal_USTax_Hunt_Basis_instBEqSt_beq_spec__0(lean_object* v_x_1052_, lean_object* v_x_1053_){
_start:
{
if (lean_obj_tag(v_x_1052_) == 0)
{
if (lean_obj_tag(v_x_1053_) == 0)
{
uint8_t v___x_1054_; 
v___x_1054_ = 1;
return v___x_1054_;
}
else
{
uint8_t v___x_1055_; 
v___x_1055_ = 0;
return v___x_1055_;
}
}
else
{
if (lean_obj_tag(v_x_1053_) == 0)
{
uint8_t v___x_1056_; 
v___x_1056_ = 0;
return v___x_1056_;
}
else
{
lean_object* v_head_1057_; lean_object* v_tail_1058_; lean_object* v_head_1059_; lean_object* v_tail_1060_; uint8_t v___x_1061_; 
v_head_1057_ = lean_ctor_get(v_x_1052_, 0);
v_tail_1058_ = lean_ctor_get(v_x_1052_, 1);
v_head_1059_ = lean_ctor_get(v_x_1053_, 0);
v_tail_1060_ = lean_ctor_get(v_x_1053_, 1);
v___x_1061_ = l_Legal_USTax_Hunt_Basis_instBEqLot_beq(v_head_1057_, v_head_1059_);
if (v___x_1061_ == 0)
{
return v___x_1061_;
}
else
{
v_x_1052_ = v_tail_1058_;
v_x_1053_ = v_tail_1060_;
goto _start;
}
}
}
}
}
LEAN_EXPORT lean_object* l_List_beq___at___00Legal_USTax_Hunt_Basis_instBEqSt_beq_spec__0___boxed(lean_object* v_x_1063_, lean_object* v_x_1064_){
_start:
{
uint8_t v_res_1065_; lean_object* v_r_1066_; 
v_res_1065_ = l_List_beq___at___00Legal_USTax_Hunt_Basis_instBEqSt_beq_spec__0(v_x_1063_, v_x_1064_);
lean_dec(v_x_1064_);
lean_dec(v_x_1063_);
v_r_1066_ = lean_box(v_res_1065_);
return v_r_1066_;
}
}
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instBEqSt_beq(lean_object* v_x_1067_, lean_object* v_x_1068_){
_start:
{
lean_object* v_lots_1069_; lean_object* v_year_1070_; lean_object* v_cur_1071_; uint8_t v_pAlive_1072_; uint8_t v_pFinal_1073_; lean_object* v_rJ_1074_; lean_object* v_rK_1075_; lean_object* v_rA_1076_; lean_object* v_rP_1077_; lean_object* v_charCash_1078_; lean_object* v_charProp_1079_; lean_object* v_cfChar_1080_; lean_object* v_pledge_1081_; lean_object* v_tax_1082_; lean_object* v_lots_1083_; lean_object* v_year_1084_; lean_object* v_cur_1085_; uint8_t v_pAlive_1086_; uint8_t v_pFinal_1087_; lean_object* v_rJ_1088_; lean_object* v_rK_1089_; lean_object* v_rA_1090_; lean_object* v_rP_1091_; lean_object* v_charCash_1092_; lean_object* v_charProp_1093_; lean_object* v_cfChar_1094_; lean_object* v_pledge_1095_; lean_object* v_tax_1096_; uint8_t v___y_1108_; uint8_t v___x_1109_; 
v_lots_1069_ = lean_ctor_get(v_x_1067_, 0);
v_year_1070_ = lean_ctor_get(v_x_1067_, 1);
v_cur_1071_ = lean_ctor_get(v_x_1067_, 2);
v_pAlive_1072_ = lean_ctor_get_uint8(v_x_1067_, sizeof(void*)*12);
v_pFinal_1073_ = lean_ctor_get_uint8(v_x_1067_, sizeof(void*)*12 + 1);
v_rJ_1074_ = lean_ctor_get(v_x_1067_, 3);
v_rK_1075_ = lean_ctor_get(v_x_1067_, 4);
v_rA_1076_ = lean_ctor_get(v_x_1067_, 5);
v_rP_1077_ = lean_ctor_get(v_x_1067_, 6);
v_charCash_1078_ = lean_ctor_get(v_x_1067_, 7);
v_charProp_1079_ = lean_ctor_get(v_x_1067_, 8);
v_cfChar_1080_ = lean_ctor_get(v_x_1067_, 9);
v_pledge_1081_ = lean_ctor_get(v_x_1067_, 10);
v_tax_1082_ = lean_ctor_get(v_x_1067_, 11);
v_lots_1083_ = lean_ctor_get(v_x_1068_, 0);
v_year_1084_ = lean_ctor_get(v_x_1068_, 1);
v_cur_1085_ = lean_ctor_get(v_x_1068_, 2);
v_pAlive_1086_ = lean_ctor_get_uint8(v_x_1068_, sizeof(void*)*12);
v_pFinal_1087_ = lean_ctor_get_uint8(v_x_1068_, sizeof(void*)*12 + 1);
v_rJ_1088_ = lean_ctor_get(v_x_1068_, 3);
v_rK_1089_ = lean_ctor_get(v_x_1068_, 4);
v_rA_1090_ = lean_ctor_get(v_x_1068_, 5);
v_rP_1091_ = lean_ctor_get(v_x_1068_, 6);
v_charCash_1092_ = lean_ctor_get(v_x_1068_, 7);
v_charProp_1093_ = lean_ctor_get(v_x_1068_, 8);
v_cfChar_1094_ = lean_ctor_get(v_x_1068_, 9);
v_pledge_1095_ = lean_ctor_get(v_x_1068_, 10);
v_tax_1096_ = lean_ctor_get(v_x_1068_, 11);
v___x_1109_ = l_List_beq___at___00Legal_USTax_Hunt_Basis_instBEqSt_beq_spec__0(v_lots_1069_, v_lots_1083_);
if (v___x_1109_ == 0)
{
return v___x_1109_;
}
else
{
uint8_t v___x_1110_; 
v___x_1110_ = lean_nat_dec_eq(v_year_1070_, v_year_1084_);
if (v___x_1110_ == 0)
{
return v___x_1110_;
}
else
{
uint8_t v___x_1111_; 
v___x_1111_ = lean_nat_dec_eq(v_cur_1071_, v_cur_1085_);
if (v___x_1111_ == 0)
{
return v___x_1111_;
}
else
{
if (v_pAlive_1086_ == 0)
{
if (v_pAlive_1072_ == 0)
{
v___y_1108_ = v___x_1111_;
goto v___jp_1107_;
}
else
{
return v_pAlive_1086_;
}
}
else
{
v___y_1108_ = v_pAlive_1072_;
goto v___jp_1107_;
}
}
}
}
v___jp_1097_:
{
uint8_t v___x_1098_; 
v___x_1098_ = l_Legal_USTax_Hunt_Basis_instBEqRet_beq(v_rJ_1074_, v_rJ_1088_);
if (v___x_1098_ == 0)
{
return v___x_1098_;
}
else
{
uint8_t v___x_1099_; 
v___x_1099_ = l_Legal_USTax_Hunt_Basis_instBEqRet_beq(v_rK_1075_, v_rK_1089_);
if (v___x_1099_ == 0)
{
return v___x_1099_;
}
else
{
uint8_t v___x_1100_; 
v___x_1100_ = l_Legal_USTax_Hunt_Basis_instBEqRet_beq(v_rA_1076_, v_rA_1090_);
if (v___x_1100_ == 0)
{
return v___x_1100_;
}
else
{
uint8_t v___x_1101_; 
v___x_1101_ = l_Legal_USTax_Hunt_Basis_instBEqRet_beq(v_rP_1077_, v_rP_1091_);
if (v___x_1101_ == 0)
{
return v___x_1101_;
}
else
{
uint8_t v___x_1102_; 
v___x_1102_ = lean_nat_dec_eq(v_charCash_1078_, v_charCash_1092_);
if (v___x_1102_ == 0)
{
return v___x_1102_;
}
else
{
uint8_t v___x_1103_; 
v___x_1103_ = lean_nat_dec_eq(v_charProp_1079_, v_charProp_1093_);
if (v___x_1103_ == 0)
{
return v___x_1103_;
}
else
{
uint8_t v___x_1104_; 
v___x_1104_ = lean_nat_dec_eq(v_cfChar_1080_, v_cfChar_1094_);
if (v___x_1104_ == 0)
{
return v___x_1104_;
}
else
{
uint8_t v___x_1105_; 
v___x_1105_ = lean_nat_dec_eq(v_pledge_1081_, v_pledge_1095_);
if (v___x_1105_ == 0)
{
return v___x_1105_;
}
else
{
uint8_t v___x_1106_; 
v___x_1106_ = lean_nat_dec_eq(v_tax_1082_, v_tax_1096_);
return v___x_1106_;
}
}
}
}
}
}
}
}
}
v___jp_1107_:
{
if (v___y_1108_ == 0)
{
return v___y_1108_;
}
else
{
if (v_pFinal_1087_ == 0)
{
if (v_pFinal_1073_ == 0)
{
goto v___jp_1097_;
}
else
{
return v_pFinal_1087_;
}
}
else
{
if (v_pFinal_1073_ == 0)
{
return v_pFinal_1073_;
}
else
{
goto v___jp_1097_;
}
}
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instBEqSt_beq___boxed(lean_object* v_x_1112_, lean_object* v_x_1113_){
_start:
{
uint8_t v_res_1114_; lean_object* v_r_1115_; 
v_res_1114_ = l_Legal_USTax_Hunt_Basis_instBEqSt_beq(v_x_1112_, v_x_1113_);
lean_dec_ref(v_x_1113_);
lean_dec_ref(v_x_1112_);
v_r_1115_ = lean_box(v_res_1114_);
return v_r_1115_;
}
}
LEAN_EXPORT uint64_t l_List_foldl___at___00Legal_USTax_Hunt_Basis_instHashableSt_hash_spec__0(uint64_t v_x_1118_, lean_object* v_x_1119_){
_start:
{
if (lean_obj_tag(v_x_1119_) == 0)
{
return v_x_1118_;
}
else
{
lean_object* v_head_1120_; lean_object* v_tail_1121_; uint64_t v___x_1122_; uint64_t v___x_1123_; 
v_head_1120_ = lean_ctor_get(v_x_1119_, 0);
v_tail_1121_ = lean_ctor_get(v_x_1119_, 1);
v___x_1122_ = l_Legal_USTax_Hunt_Basis_instHashableLot_hash(v_head_1120_);
v___x_1123_ = lean_uint64_mix_hash(v_x_1118_, v___x_1122_);
v_x_1118_ = v___x_1123_;
v_x_1119_ = v_tail_1121_;
goto _start;
}
}
}
LEAN_EXPORT lean_object* l_List_foldl___at___00Legal_USTax_Hunt_Basis_instHashableSt_hash_spec__0___boxed(lean_object* v_x_1125_, lean_object* v_x_1126_){
_start:
{
uint64_t v_x_173__boxed_1127_; uint64_t v_res_1128_; lean_object* v_r_1129_; 
v_x_173__boxed_1127_ = lean_unbox_uint64(v_x_1125_);
lean_dec_ref(v_x_1125_);
v_res_1128_ = l_List_foldl___at___00Legal_USTax_Hunt_Basis_instHashableSt_hash_spec__0(v_x_173__boxed_1127_, v_x_1126_);
lean_dec(v_x_1126_);
v_r_1129_ = lean_box_uint64(v_res_1128_);
return v_r_1129_;
}
}
LEAN_EXPORT uint64_t l_Legal_USTax_Hunt_Basis_instHashableSt_hash(lean_object* v_x_1130_){
_start:
{
lean_object* v_lots_1131_; lean_object* v_year_1132_; lean_object* v_cur_1133_; uint8_t v_pAlive_1134_; uint8_t v_pFinal_1135_; lean_object* v_rJ_1136_; lean_object* v_rK_1137_; lean_object* v_rA_1138_; lean_object* v_rP_1139_; lean_object* v_charCash_1140_; lean_object* v_charProp_1141_; lean_object* v_cfChar_1142_; lean_object* v_pledge_1143_; lean_object* v_tax_1144_; uint64_t v___y_1146_; uint64_t v___y_1147_; uint64_t v___x_1167_; uint64_t v___x_1168_; uint64_t v___x_1169_; uint64_t v___x_1170_; uint64_t v___x_1171_; uint64_t v___x_1172_; uint64_t v___x_1173_; uint64_t v___x_1174_; uint64_t v___y_1176_; 
v_lots_1131_ = lean_ctor_get(v_x_1130_, 0);
v_year_1132_ = lean_ctor_get(v_x_1130_, 1);
v_cur_1133_ = lean_ctor_get(v_x_1130_, 2);
v_pAlive_1134_ = lean_ctor_get_uint8(v_x_1130_, sizeof(void*)*12);
v_pFinal_1135_ = lean_ctor_get_uint8(v_x_1130_, sizeof(void*)*12 + 1);
v_rJ_1136_ = lean_ctor_get(v_x_1130_, 3);
v_rK_1137_ = lean_ctor_get(v_x_1130_, 4);
v_rA_1138_ = lean_ctor_get(v_x_1130_, 5);
v_rP_1139_ = lean_ctor_get(v_x_1130_, 6);
v_charCash_1140_ = lean_ctor_get(v_x_1130_, 7);
v_charProp_1141_ = lean_ctor_get(v_x_1130_, 8);
v_cfChar_1142_ = lean_ctor_get(v_x_1130_, 9);
v_pledge_1143_ = lean_ctor_get(v_x_1130_, 10);
v_tax_1144_ = lean_ctor_get(v_x_1130_, 11);
v___x_1167_ = 0ULL;
v___x_1168_ = 7ULL;
v___x_1169_ = l_List_foldl___at___00Legal_USTax_Hunt_Basis_instHashableSt_hash_spec__0(v___x_1168_, v_lots_1131_);
v___x_1170_ = lean_uint64_mix_hash(v___x_1167_, v___x_1169_);
v___x_1171_ = lean_uint64_of_nat(v_year_1132_);
v___x_1172_ = lean_uint64_mix_hash(v___x_1170_, v___x_1171_);
v___x_1173_ = lean_uint64_of_nat(v_cur_1133_);
v___x_1174_ = lean_uint64_mix_hash(v___x_1172_, v___x_1173_);
if (v_pAlive_1134_ == 0)
{
uint64_t v___x_1180_; 
v___x_1180_ = 13ULL;
v___y_1176_ = v___x_1180_;
goto v___jp_1175_;
}
else
{
uint64_t v___x_1181_; 
v___x_1181_ = 11ULL;
v___y_1176_ = v___x_1181_;
goto v___jp_1175_;
}
v___jp_1145_:
{
uint64_t v___x_1148_; uint64_t v___x_1149_; uint64_t v___x_1150_; uint64_t v___x_1151_; uint64_t v___x_1152_; uint64_t v___x_1153_; uint64_t v___x_1154_; uint64_t v___x_1155_; uint64_t v___x_1156_; uint64_t v___x_1157_; uint64_t v___x_1158_; uint64_t v___x_1159_; uint64_t v___x_1160_; uint64_t v___x_1161_; uint64_t v___x_1162_; uint64_t v___x_1163_; uint64_t v___x_1164_; uint64_t v___x_1165_; uint64_t v___x_1166_; 
v___x_1148_ = lean_uint64_mix_hash(v___y_1146_, v___y_1147_);
v___x_1149_ = l_Legal_USTax_Hunt_Basis_instHashableRet_hash(v_rJ_1136_);
v___x_1150_ = lean_uint64_mix_hash(v___x_1148_, v___x_1149_);
v___x_1151_ = l_Legal_USTax_Hunt_Basis_instHashableRet_hash(v_rK_1137_);
v___x_1152_ = lean_uint64_mix_hash(v___x_1150_, v___x_1151_);
v___x_1153_ = l_Legal_USTax_Hunt_Basis_instHashableRet_hash(v_rA_1138_);
v___x_1154_ = lean_uint64_mix_hash(v___x_1152_, v___x_1153_);
v___x_1155_ = l_Legal_USTax_Hunt_Basis_instHashableRet_hash(v_rP_1139_);
v___x_1156_ = lean_uint64_mix_hash(v___x_1154_, v___x_1155_);
v___x_1157_ = lean_uint64_of_nat(v_charCash_1140_);
v___x_1158_ = lean_uint64_mix_hash(v___x_1156_, v___x_1157_);
v___x_1159_ = lean_uint64_of_nat(v_charProp_1141_);
v___x_1160_ = lean_uint64_mix_hash(v___x_1158_, v___x_1159_);
v___x_1161_ = lean_uint64_of_nat(v_cfChar_1142_);
v___x_1162_ = lean_uint64_mix_hash(v___x_1160_, v___x_1161_);
v___x_1163_ = lean_uint64_of_nat(v_pledge_1143_);
v___x_1164_ = lean_uint64_mix_hash(v___x_1162_, v___x_1163_);
v___x_1165_ = lean_uint64_of_nat(v_tax_1144_);
v___x_1166_ = lean_uint64_mix_hash(v___x_1164_, v___x_1165_);
return v___x_1166_;
}
v___jp_1175_:
{
uint64_t v___x_1177_; 
v___x_1177_ = lean_uint64_mix_hash(v___x_1174_, v___y_1176_);
if (v_pFinal_1135_ == 0)
{
uint64_t v___x_1178_; 
v___x_1178_ = 13ULL;
v___y_1146_ = v___x_1177_;
v___y_1147_ = v___x_1178_;
goto v___jp_1145_;
}
else
{
uint64_t v___x_1179_; 
v___x_1179_ = 11ULL;
v___y_1146_ = v___x_1177_;
v___y_1147_ = v___x_1179_;
goto v___jp_1145_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instHashableSt_hash___boxed(lean_object* v_x_1182_){
_start:
{
uint64_t v_res_1183_; lean_object* v_r_1184_; 
v_res_1183_ = l_Legal_USTax_Hunt_Basis_instHashableSt_hash(v_x_1182_);
lean_dec_ref(v_x_1182_);
v_r_1184_ = lean_box_uint64(v_res_1183_);
return v_r_1184_;
}
}
LEAN_EXPORT lean_object* l_List_foldl___at___00List_foldl___at___00Std_Format_joinSep___at___00List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0_spec__0_spec__1_spec__2(lean_object* v_x_1187_, lean_object* v_x_1188_, lean_object* v_x_1189_){
_start:
{
if (lean_obj_tag(v_x_1189_) == 0)
{
lean_dec(v_x_1187_);
return v_x_1188_;
}
else
{
lean_object* v_head_1190_; lean_object* v_tail_1191_; lean_object* v___x_1193_; uint8_t v_isShared_1194_; uint8_t v_isSharedCheck_1201_; 
v_head_1190_ = lean_ctor_get(v_x_1189_, 0);
v_tail_1191_ = lean_ctor_get(v_x_1189_, 1);
v_isSharedCheck_1201_ = !lean_is_exclusive(v_x_1189_);
if (v_isSharedCheck_1201_ == 0)
{
v___x_1193_ = v_x_1189_;
v_isShared_1194_ = v_isSharedCheck_1201_;
goto v_resetjp_1192_;
}
else
{
lean_inc(v_tail_1191_);
lean_inc(v_head_1190_);
lean_dec(v_x_1189_);
v___x_1193_ = lean_box(0);
v_isShared_1194_ = v_isSharedCheck_1201_;
goto v_resetjp_1192_;
}
v_resetjp_1192_:
{
lean_object* v___x_1196_; 
lean_inc(v_x_1187_);
if (v_isShared_1194_ == 0)
{
lean_ctor_set_tag(v___x_1193_, 5);
lean_ctor_set(v___x_1193_, 1, v_x_1187_);
lean_ctor_set(v___x_1193_, 0, v_x_1188_);
v___x_1196_ = v___x_1193_;
goto v_reusejp_1195_;
}
else
{
lean_object* v_reuseFailAlloc_1200_; 
v_reuseFailAlloc_1200_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v_reuseFailAlloc_1200_, 0, v_x_1188_);
lean_ctor_set(v_reuseFailAlloc_1200_, 1, v_x_1187_);
v___x_1196_ = v_reuseFailAlloc_1200_;
goto v_reusejp_1195_;
}
v_reusejp_1195_:
{
lean_object* v___x_1197_; lean_object* v___x_1198_; 
v___x_1197_ = l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg(v_head_1190_);
v___x_1198_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1198_, 0, v___x_1196_);
lean_ctor_set(v___x_1198_, 1, v___x_1197_);
v_x_1188_ = v___x_1198_;
v_x_1189_ = v_tail_1191_;
goto _start;
}
}
}
}
}
LEAN_EXPORT lean_object* l_List_foldl___at___00Std_Format_joinSep___at___00List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0_spec__0_spec__1(lean_object* v_x_1202_, lean_object* v_x_1203_, lean_object* v_x_1204_){
_start:
{
if (lean_obj_tag(v_x_1204_) == 0)
{
lean_dec(v_x_1202_);
return v_x_1203_;
}
else
{
lean_object* v_head_1205_; lean_object* v_tail_1206_; lean_object* v___x_1208_; uint8_t v_isShared_1209_; uint8_t v_isSharedCheck_1216_; 
v_head_1205_ = lean_ctor_get(v_x_1204_, 0);
v_tail_1206_ = lean_ctor_get(v_x_1204_, 1);
v_isSharedCheck_1216_ = !lean_is_exclusive(v_x_1204_);
if (v_isSharedCheck_1216_ == 0)
{
v___x_1208_ = v_x_1204_;
v_isShared_1209_ = v_isSharedCheck_1216_;
goto v_resetjp_1207_;
}
else
{
lean_inc(v_tail_1206_);
lean_inc(v_head_1205_);
lean_dec(v_x_1204_);
v___x_1208_ = lean_box(0);
v_isShared_1209_ = v_isSharedCheck_1216_;
goto v_resetjp_1207_;
}
v_resetjp_1207_:
{
lean_object* v___x_1211_; 
lean_inc(v_x_1202_);
if (v_isShared_1209_ == 0)
{
lean_ctor_set_tag(v___x_1208_, 5);
lean_ctor_set(v___x_1208_, 1, v_x_1202_);
lean_ctor_set(v___x_1208_, 0, v_x_1203_);
v___x_1211_ = v___x_1208_;
goto v_reusejp_1210_;
}
else
{
lean_object* v_reuseFailAlloc_1215_; 
v_reuseFailAlloc_1215_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v_reuseFailAlloc_1215_, 0, v_x_1203_);
lean_ctor_set(v_reuseFailAlloc_1215_, 1, v_x_1202_);
v___x_1211_ = v_reuseFailAlloc_1215_;
goto v_reusejp_1210_;
}
v_reusejp_1210_:
{
lean_object* v___x_1212_; lean_object* v___x_1213_; lean_object* v___x_1214_; 
v___x_1212_ = l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg(v_head_1205_);
v___x_1213_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1213_, 0, v___x_1211_);
lean_ctor_set(v___x_1213_, 1, v___x_1212_);
v___x_1214_ = l_List_foldl___at___00List_foldl___at___00Std_Format_joinSep___at___00List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0_spec__0_spec__1_spec__2(v_x_1202_, v___x_1213_, v_tail_1206_);
return v___x_1214_;
}
}
}
}
}
LEAN_EXPORT lean_object* l_Std_Format_joinSep___at___00List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0_spec__0(lean_object* v_x_1217_, lean_object* v_x_1218_){
_start:
{
if (lean_obj_tag(v_x_1217_) == 0)
{
lean_object* v___x_1219_; 
lean_dec(v_x_1218_);
v___x_1219_ = lean_box(0);
return v___x_1219_;
}
else
{
lean_object* v_tail_1220_; 
v_tail_1220_ = lean_ctor_get(v_x_1217_, 1);
if (lean_obj_tag(v_tail_1220_) == 0)
{
lean_object* v_head_1221_; lean_object* v___x_1222_; 
lean_dec(v_x_1218_);
v_head_1221_ = lean_ctor_get(v_x_1217_, 0);
lean_inc(v_head_1221_);
lean_dec_ref_known(v_x_1217_, 2);
v___x_1222_ = l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg(v_head_1221_);
return v___x_1222_;
}
else
{
lean_object* v_head_1223_; lean_object* v___x_1224_; lean_object* v___x_1225_; 
lean_inc(v_tail_1220_);
v_head_1223_ = lean_ctor_get(v_x_1217_, 0);
lean_inc(v_head_1223_);
lean_dec_ref_known(v_x_1217_, 2);
v___x_1224_ = l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg(v_head_1223_);
v___x_1225_ = l_List_foldl___at___00Std_Format_joinSep___at___00List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0_spec__0_spec__1(v_x_1218_, v___x_1224_, v_tail_1220_);
return v___x_1225_;
}
}
}
}
static lean_object* _init_l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__5(void){
_start:
{
lean_object* v___x_1234_; lean_object* v___x_1235_; 
v___x_1234_ = ((lean_object*)(l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__2));
v___x_1235_ = lean_string_length(v___x_1234_);
return v___x_1235_;
}
}
static lean_object* _init_l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__6(void){
_start:
{
lean_object* v___x_1236_; lean_object* v___x_1237_; 
v___x_1236_ = lean_obj_once(&l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__5, &l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__5_once, _init_l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__5);
v___x_1237_ = lean_nat_to_int(v___x_1236_);
return v___x_1237_;
}
}
LEAN_EXPORT lean_object* l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg(lean_object* v_a_1242_){
_start:
{
if (lean_obj_tag(v_a_1242_) == 0)
{
lean_object* v___x_1243_; 
v___x_1243_ = ((lean_object*)(l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__1));
return v___x_1243_;
}
else
{
lean_object* v___x_1244_; lean_object* v___x_1245_; lean_object* v___x_1246_; lean_object* v___x_1247_; lean_object* v___x_1248_; lean_object* v___x_1249_; lean_object* v___x_1250_; lean_object* v___x_1251_; uint8_t v___x_1252_; lean_object* v___x_1253_; 
v___x_1244_ = ((lean_object*)(l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__3));
v___x_1245_ = l_Std_Format_joinSep___at___00List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0_spec__0(v_a_1242_, v___x_1244_);
v___x_1246_ = lean_obj_once(&l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__6, &l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__6_once, _init_l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__6);
v___x_1247_ = ((lean_object*)(l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__7));
v___x_1248_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1248_, 0, v___x_1247_);
lean_ctor_set(v___x_1248_, 1, v___x_1245_);
v___x_1249_ = ((lean_object*)(l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__8));
v___x_1250_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1250_, 0, v___x_1248_);
lean_ctor_set(v___x_1250_, 1, v___x_1249_);
v___x_1251_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1251_, 0, v___x_1246_);
lean_ctor_set(v___x_1251_, 1, v___x_1250_);
v___x_1252_ = 0;
v___x_1253_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1253_, 0, v___x_1251_);
lean_ctor_set_uint8(v___x_1253_, sizeof(void*)*1, v___x_1252_);
return v___x_1253_;
}
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__22(void){
_start:
{
lean_object* v___x_1290_; lean_object* v___x_1291_; 
v___x_1290_ = lean_unsigned_to_nat(12u);
v___x_1291_ = lean_nat_to_int(v___x_1290_);
return v___x_1291_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg(lean_object* v_x_1304_){
_start:
{
lean_object* v_lots_1305_; lean_object* v_year_1306_; lean_object* v_cur_1307_; uint8_t v_pAlive_1308_; uint8_t v_pFinal_1309_; lean_object* v_rJ_1310_; lean_object* v_rK_1311_; lean_object* v_rA_1312_; lean_object* v_rP_1313_; lean_object* v_charCash_1314_; lean_object* v_charProp_1315_; lean_object* v_cfChar_1316_; lean_object* v_pledge_1317_; lean_object* v_tax_1318_; lean_object* v___x_1319_; lean_object* v___x_1320_; lean_object* v___x_1321_; lean_object* v___x_1322_; lean_object* v___x_1323_; uint8_t v___x_1324_; lean_object* v___x_1325_; lean_object* v___x_1326_; lean_object* v___x_1327_; lean_object* v___x_1328_; lean_object* v___x_1329_; lean_object* v___x_1330_; lean_object* v___x_1331_; lean_object* v___x_1332_; lean_object* v___x_1333_; lean_object* v___x_1334_; lean_object* v___x_1335_; lean_object* v___x_1336_; lean_object* v___x_1337_; lean_object* v___x_1338_; lean_object* v___x_1339_; lean_object* v___x_1340_; lean_object* v___x_1341_; lean_object* v___x_1342_; lean_object* v___x_1343_; lean_object* v___x_1344_; lean_object* v___x_1345_; lean_object* v___x_1346_; lean_object* v___x_1347_; lean_object* v___x_1348_; lean_object* v___x_1349_; lean_object* v___x_1350_; lean_object* v___x_1351_; lean_object* v___x_1352_; lean_object* v___x_1353_; lean_object* v___x_1354_; lean_object* v___x_1355_; lean_object* v___x_1356_; lean_object* v___x_1357_; lean_object* v___x_1358_; lean_object* v___x_1359_; lean_object* v___x_1360_; lean_object* v___x_1361_; lean_object* v___x_1362_; lean_object* v___x_1363_; lean_object* v___x_1364_; lean_object* v___x_1365_; lean_object* v___x_1366_; lean_object* v___x_1367_; lean_object* v___x_1368_; lean_object* v___x_1369_; lean_object* v___x_1370_; lean_object* v___x_1371_; lean_object* v___x_1372_; lean_object* v___x_1373_; lean_object* v___x_1374_; lean_object* v___x_1375_; lean_object* v___x_1376_; lean_object* v___x_1377_; lean_object* v___x_1378_; lean_object* v___x_1379_; lean_object* v___x_1380_; lean_object* v___x_1381_; lean_object* v___x_1382_; lean_object* v___x_1383_; lean_object* v___x_1384_; lean_object* v___x_1385_; lean_object* v___x_1386_; lean_object* v___x_1387_; lean_object* v___x_1388_; lean_object* v___x_1389_; lean_object* v___x_1390_; lean_object* v___x_1391_; lean_object* v___x_1392_; lean_object* v___x_1393_; lean_object* v___x_1394_; lean_object* v___x_1395_; lean_object* v___x_1396_; lean_object* v___x_1397_; lean_object* v___x_1398_; lean_object* v___x_1399_; lean_object* v___x_1400_; lean_object* v___x_1401_; lean_object* v___x_1402_; lean_object* v___x_1403_; lean_object* v___x_1404_; lean_object* v___x_1405_; lean_object* v___x_1406_; lean_object* v___x_1407_; lean_object* v___x_1408_; lean_object* v___x_1409_; lean_object* v___x_1410_; lean_object* v___x_1411_; lean_object* v___x_1412_; lean_object* v___x_1413_; lean_object* v___x_1414_; lean_object* v___x_1415_; lean_object* v___x_1416_; lean_object* v___x_1417_; lean_object* v___x_1418_; lean_object* v___x_1419_; lean_object* v___x_1420_; lean_object* v___x_1421_; lean_object* v___x_1422_; lean_object* v___x_1423_; lean_object* v___x_1424_; lean_object* v___x_1425_; lean_object* v___x_1426_; lean_object* v___x_1427_; lean_object* v___x_1428_; lean_object* v___x_1429_; lean_object* v___x_1430_; lean_object* v___x_1431_; lean_object* v___x_1432_; lean_object* v___x_1433_; lean_object* v___x_1434_; lean_object* v___x_1435_; lean_object* v___x_1436_; lean_object* v___x_1437_; lean_object* v___x_1438_; lean_object* v___x_1439_; lean_object* v___x_1440_; lean_object* v___x_1441_; lean_object* v___x_1442_; lean_object* v___x_1443_; lean_object* v___x_1444_; lean_object* v___x_1445_; lean_object* v___x_1446_; lean_object* v___x_1447_; lean_object* v___x_1448_; lean_object* v___x_1449_; lean_object* v___x_1450_; lean_object* v___x_1451_; lean_object* v___x_1452_; lean_object* v___x_1453_; lean_object* v___x_1454_; lean_object* v___x_1455_; lean_object* v___x_1456_; lean_object* v___x_1457_; lean_object* v___x_1458_; lean_object* v___x_1459_; lean_object* v___x_1460_; lean_object* v___x_1461_; lean_object* v___x_1462_; lean_object* v___x_1463_; 
v_lots_1305_ = lean_ctor_get(v_x_1304_, 0);
lean_inc(v_lots_1305_);
v_year_1306_ = lean_ctor_get(v_x_1304_, 1);
lean_inc(v_year_1306_);
v_cur_1307_ = lean_ctor_get(v_x_1304_, 2);
lean_inc(v_cur_1307_);
v_pAlive_1308_ = lean_ctor_get_uint8(v_x_1304_, sizeof(void*)*12);
v_pFinal_1309_ = lean_ctor_get_uint8(v_x_1304_, sizeof(void*)*12 + 1);
v_rJ_1310_ = lean_ctor_get(v_x_1304_, 3);
lean_inc_ref(v_rJ_1310_);
v_rK_1311_ = lean_ctor_get(v_x_1304_, 4);
lean_inc_ref(v_rK_1311_);
v_rA_1312_ = lean_ctor_get(v_x_1304_, 5);
lean_inc_ref(v_rA_1312_);
v_rP_1313_ = lean_ctor_get(v_x_1304_, 6);
lean_inc_ref(v_rP_1313_);
v_charCash_1314_ = lean_ctor_get(v_x_1304_, 7);
lean_inc(v_charCash_1314_);
v_charProp_1315_ = lean_ctor_get(v_x_1304_, 8);
lean_inc(v_charProp_1315_);
v_cfChar_1316_ = lean_ctor_get(v_x_1304_, 9);
lean_inc(v_cfChar_1316_);
v_pledge_1317_ = lean_ctor_get(v_x_1304_, 10);
lean_inc(v_pledge_1317_);
v_tax_1318_ = lean_ctor_get(v_x_1304_, 11);
lean_inc(v_tax_1318_);
lean_dec_ref(v_x_1304_);
v___x_1319_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__5));
v___x_1320_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__3));
v___x_1321_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__7, &l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__7_once, _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__7);
v___x_1322_ = l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg(v_lots_1305_);
v___x_1323_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1323_, 0, v___x_1321_);
lean_ctor_set(v___x_1323_, 1, v___x_1322_);
v___x_1324_ = 0;
v___x_1325_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1325_, 0, v___x_1323_);
lean_ctor_set_uint8(v___x_1325_, sizeof(void*)*1, v___x_1324_);
v___x_1326_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1326_, 0, v___x_1320_);
lean_ctor_set(v___x_1326_, 1, v___x_1325_);
v___x_1327_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__9));
v___x_1328_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1328_, 0, v___x_1326_);
lean_ctor_set(v___x_1328_, 1, v___x_1327_);
v___x_1329_ = lean_box(1);
v___x_1330_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1330_, 0, v___x_1328_);
lean_ctor_set(v___x_1330_, 1, v___x_1329_);
v___x_1331_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__5));
v___x_1332_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1332_, 0, v___x_1330_);
lean_ctor_set(v___x_1332_, 1, v___x_1331_);
v___x_1333_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1333_, 0, v___x_1332_);
lean_ctor_set(v___x_1333_, 1, v___x_1319_);
v___x_1334_ = l_Nat_reprFast(v_year_1306_);
v___x_1335_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1335_, 0, v___x_1334_);
v___x_1336_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1336_, 0, v___x_1321_);
lean_ctor_set(v___x_1336_, 1, v___x_1335_);
v___x_1337_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1337_, 0, v___x_1336_);
lean_ctor_set_uint8(v___x_1337_, sizeof(void*)*1, v___x_1324_);
v___x_1338_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1338_, 0, v___x_1333_);
lean_ctor_set(v___x_1338_, 1, v___x_1337_);
v___x_1339_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1339_, 0, v___x_1338_);
lean_ctor_set(v___x_1339_, 1, v___x_1327_);
v___x_1340_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1340_, 0, v___x_1339_);
lean_ctor_set(v___x_1340_, 1, v___x_1329_);
v___x_1341_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__7));
v___x_1342_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1342_, 0, v___x_1340_);
lean_ctor_set(v___x_1342_, 1, v___x_1341_);
v___x_1343_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1343_, 0, v___x_1342_);
lean_ctor_set(v___x_1343_, 1, v___x_1319_);
v___x_1344_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__15, &l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__15_once, _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__15);
v___x_1345_ = l_Nat_reprFast(v_cur_1307_);
v___x_1346_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1346_, 0, v___x_1345_);
v___x_1347_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1347_, 0, v___x_1344_);
lean_ctor_set(v___x_1347_, 1, v___x_1346_);
v___x_1348_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1348_, 0, v___x_1347_);
lean_ctor_set_uint8(v___x_1348_, sizeof(void*)*1, v___x_1324_);
v___x_1349_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1349_, 0, v___x_1343_);
lean_ctor_set(v___x_1349_, 1, v___x_1348_);
v___x_1350_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1350_, 0, v___x_1349_);
lean_ctor_set(v___x_1350_, 1, v___x_1327_);
v___x_1351_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1351_, 0, v___x_1350_);
lean_ctor_set(v___x_1351_, 1, v___x_1329_);
v___x_1352_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__9));
v___x_1353_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1353_, 0, v___x_1351_);
lean_ctor_set(v___x_1353_, 1, v___x_1352_);
v___x_1354_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1354_, 0, v___x_1353_);
lean_ctor_set(v___x_1354_, 1, v___x_1319_);
v___x_1355_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__27, &l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__27_once, _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__27);
v___x_1356_ = l_Bool_repr___redArg(v_pAlive_1308_);
v___x_1357_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1357_, 0, v___x_1355_);
lean_ctor_set(v___x_1357_, 1, v___x_1356_);
v___x_1358_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1358_, 0, v___x_1357_);
lean_ctor_set_uint8(v___x_1358_, sizeof(void*)*1, v___x_1324_);
v___x_1359_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1359_, 0, v___x_1354_);
lean_ctor_set(v___x_1359_, 1, v___x_1358_);
v___x_1360_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1360_, 0, v___x_1359_);
lean_ctor_set(v___x_1360_, 1, v___x_1327_);
v___x_1361_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1361_, 0, v___x_1360_);
lean_ctor_set(v___x_1361_, 1, v___x_1329_);
v___x_1362_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__11));
v___x_1363_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1363_, 0, v___x_1361_);
lean_ctor_set(v___x_1363_, 1, v___x_1362_);
v___x_1364_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1364_, 0, v___x_1363_);
lean_ctor_set(v___x_1364_, 1, v___x_1319_);
v___x_1365_ = l_Bool_repr___redArg(v_pFinal_1309_);
v___x_1366_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1366_, 0, v___x_1355_);
lean_ctor_set(v___x_1366_, 1, v___x_1365_);
v___x_1367_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1367_, 0, v___x_1366_);
lean_ctor_set_uint8(v___x_1367_, sizeof(void*)*1, v___x_1324_);
v___x_1368_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1368_, 0, v___x_1364_);
lean_ctor_set(v___x_1368_, 1, v___x_1367_);
v___x_1369_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1369_, 0, v___x_1368_);
lean_ctor_set(v___x_1369_, 1, v___x_1327_);
v___x_1370_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1370_, 0, v___x_1369_);
lean_ctor_set(v___x_1370_, 1, v___x_1329_);
v___x_1371_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__13));
v___x_1372_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1372_, 0, v___x_1370_);
lean_ctor_set(v___x_1372_, 1, v___x_1371_);
v___x_1373_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1373_, 0, v___x_1372_);
lean_ctor_set(v___x_1373_, 1, v___x_1319_);
v___x_1374_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__4, &l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__4_once, _init_l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg___closed__4);
v___x_1375_ = l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg(v_rJ_1310_);
v___x_1376_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1376_, 0, v___x_1374_);
lean_ctor_set(v___x_1376_, 1, v___x_1375_);
v___x_1377_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1377_, 0, v___x_1376_);
lean_ctor_set_uint8(v___x_1377_, sizeof(void*)*1, v___x_1324_);
v___x_1378_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1378_, 0, v___x_1373_);
lean_ctor_set(v___x_1378_, 1, v___x_1377_);
v___x_1379_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1379_, 0, v___x_1378_);
lean_ctor_set(v___x_1379_, 1, v___x_1327_);
v___x_1380_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1380_, 0, v___x_1379_);
lean_ctor_set(v___x_1380_, 1, v___x_1329_);
v___x_1381_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__15));
v___x_1382_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1382_, 0, v___x_1380_);
lean_ctor_set(v___x_1382_, 1, v___x_1381_);
v___x_1383_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1383_, 0, v___x_1382_);
lean_ctor_set(v___x_1383_, 1, v___x_1319_);
v___x_1384_ = l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg(v_rK_1311_);
v___x_1385_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1385_, 0, v___x_1374_);
lean_ctor_set(v___x_1385_, 1, v___x_1384_);
v___x_1386_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1386_, 0, v___x_1385_);
lean_ctor_set_uint8(v___x_1386_, sizeof(void*)*1, v___x_1324_);
v___x_1387_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1387_, 0, v___x_1383_);
lean_ctor_set(v___x_1387_, 1, v___x_1386_);
v___x_1388_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1388_, 0, v___x_1387_);
lean_ctor_set(v___x_1388_, 1, v___x_1327_);
v___x_1389_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1389_, 0, v___x_1388_);
lean_ctor_set(v___x_1389_, 1, v___x_1329_);
v___x_1390_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__17));
v___x_1391_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1391_, 0, v___x_1389_);
lean_ctor_set(v___x_1391_, 1, v___x_1390_);
v___x_1392_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1392_, 0, v___x_1391_);
lean_ctor_set(v___x_1392_, 1, v___x_1319_);
v___x_1393_ = l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg(v_rA_1312_);
v___x_1394_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1394_, 0, v___x_1374_);
lean_ctor_set(v___x_1394_, 1, v___x_1393_);
v___x_1395_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1395_, 0, v___x_1394_);
lean_ctor_set_uint8(v___x_1395_, sizeof(void*)*1, v___x_1324_);
v___x_1396_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1396_, 0, v___x_1392_);
lean_ctor_set(v___x_1396_, 1, v___x_1395_);
v___x_1397_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1397_, 0, v___x_1396_);
lean_ctor_set(v___x_1397_, 1, v___x_1327_);
v___x_1398_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1398_, 0, v___x_1397_);
lean_ctor_set(v___x_1398_, 1, v___x_1329_);
v___x_1399_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__19));
v___x_1400_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1400_, 0, v___x_1398_);
lean_ctor_set(v___x_1400_, 1, v___x_1399_);
v___x_1401_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1401_, 0, v___x_1400_);
lean_ctor_set(v___x_1401_, 1, v___x_1319_);
v___x_1402_ = l_Legal_USTax_Hunt_Basis_instReprRet_repr___redArg(v_rP_1313_);
v___x_1403_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1403_, 0, v___x_1374_);
lean_ctor_set(v___x_1403_, 1, v___x_1402_);
v___x_1404_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1404_, 0, v___x_1403_);
lean_ctor_set_uint8(v___x_1404_, sizeof(void*)*1, v___x_1324_);
v___x_1405_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1405_, 0, v___x_1401_);
lean_ctor_set(v___x_1405_, 1, v___x_1404_);
v___x_1406_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1406_, 0, v___x_1405_);
lean_ctor_set(v___x_1406_, 1, v___x_1327_);
v___x_1407_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1407_, 0, v___x_1406_);
lean_ctor_set(v___x_1407_, 1, v___x_1329_);
v___x_1408_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__21));
v___x_1409_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1409_, 0, v___x_1407_);
lean_ctor_set(v___x_1409_, 1, v___x_1408_);
v___x_1410_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1410_, 0, v___x_1409_);
lean_ctor_set(v___x_1410_, 1, v___x_1319_);
v___x_1411_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__22, &l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__22_once, _init_l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__22);
v___x_1412_ = l_Nat_reprFast(v_charCash_1314_);
v___x_1413_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1413_, 0, v___x_1412_);
v___x_1414_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1414_, 0, v___x_1411_);
lean_ctor_set(v___x_1414_, 1, v___x_1413_);
v___x_1415_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1415_, 0, v___x_1414_);
lean_ctor_set_uint8(v___x_1415_, sizeof(void*)*1, v___x_1324_);
v___x_1416_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1416_, 0, v___x_1410_);
lean_ctor_set(v___x_1416_, 1, v___x_1415_);
v___x_1417_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1417_, 0, v___x_1416_);
lean_ctor_set(v___x_1417_, 1, v___x_1327_);
v___x_1418_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1418_, 0, v___x_1417_);
lean_ctor_set(v___x_1418_, 1, v___x_1329_);
v___x_1419_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__24));
v___x_1420_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1420_, 0, v___x_1418_);
lean_ctor_set(v___x_1420_, 1, v___x_1419_);
v___x_1421_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1421_, 0, v___x_1420_);
lean_ctor_set(v___x_1421_, 1, v___x_1319_);
v___x_1422_ = l_Nat_reprFast(v_charProp_1315_);
v___x_1423_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1423_, 0, v___x_1422_);
v___x_1424_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1424_, 0, v___x_1411_);
lean_ctor_set(v___x_1424_, 1, v___x_1423_);
v___x_1425_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1425_, 0, v___x_1424_);
lean_ctor_set_uint8(v___x_1425_, sizeof(void*)*1, v___x_1324_);
v___x_1426_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1426_, 0, v___x_1421_);
lean_ctor_set(v___x_1426_, 1, v___x_1425_);
v___x_1427_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1427_, 0, v___x_1426_);
lean_ctor_set(v___x_1427_, 1, v___x_1327_);
v___x_1428_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1428_, 0, v___x_1427_);
lean_ctor_set(v___x_1428_, 1, v___x_1329_);
v___x_1429_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__26));
v___x_1430_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1430_, 0, v___x_1428_);
lean_ctor_set(v___x_1430_, 1, v___x_1429_);
v___x_1431_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1431_, 0, v___x_1430_);
lean_ctor_set(v___x_1431_, 1, v___x_1319_);
v___x_1432_ = l_Nat_reprFast(v_cfChar_1316_);
v___x_1433_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1433_, 0, v___x_1432_);
v___x_1434_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1434_, 0, v___x_1355_);
lean_ctor_set(v___x_1434_, 1, v___x_1433_);
v___x_1435_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1435_, 0, v___x_1434_);
lean_ctor_set_uint8(v___x_1435_, sizeof(void*)*1, v___x_1324_);
v___x_1436_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1436_, 0, v___x_1431_);
lean_ctor_set(v___x_1436_, 1, v___x_1435_);
v___x_1437_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1437_, 0, v___x_1436_);
lean_ctor_set(v___x_1437_, 1, v___x_1327_);
v___x_1438_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1438_, 0, v___x_1437_);
lean_ctor_set(v___x_1438_, 1, v___x_1329_);
v___x_1439_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__28));
v___x_1440_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1440_, 0, v___x_1438_);
lean_ctor_set(v___x_1440_, 1, v___x_1439_);
v___x_1441_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1441_, 0, v___x_1440_);
lean_ctor_set(v___x_1441_, 1, v___x_1319_);
v___x_1442_ = l_Nat_reprFast(v_pledge_1317_);
v___x_1443_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1443_, 0, v___x_1442_);
v___x_1444_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1444_, 0, v___x_1355_);
lean_ctor_set(v___x_1444_, 1, v___x_1443_);
v___x_1445_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1445_, 0, v___x_1444_);
lean_ctor_set_uint8(v___x_1445_, sizeof(void*)*1, v___x_1324_);
v___x_1446_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1446_, 0, v___x_1441_);
lean_ctor_set(v___x_1446_, 1, v___x_1445_);
v___x_1447_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1447_, 0, v___x_1446_);
lean_ctor_set(v___x_1447_, 1, v___x_1327_);
v___x_1448_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1448_, 0, v___x_1447_);
lean_ctor_set(v___x_1448_, 1, v___x_1329_);
v___x_1449_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg___closed__30));
v___x_1450_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1450_, 0, v___x_1448_);
lean_ctor_set(v___x_1450_, 1, v___x_1449_);
v___x_1451_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1451_, 0, v___x_1450_);
lean_ctor_set(v___x_1451_, 1, v___x_1319_);
v___x_1452_ = l_Nat_reprFast(v_tax_1318_);
v___x_1453_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1453_, 0, v___x_1452_);
v___x_1454_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1454_, 0, v___x_1344_);
lean_ctor_set(v___x_1454_, 1, v___x_1453_);
v___x_1455_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1455_, 0, v___x_1454_);
lean_ctor_set_uint8(v___x_1455_, sizeof(void*)*1, v___x_1324_);
v___x_1456_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1456_, 0, v___x_1451_);
lean_ctor_set(v___x_1456_, 1, v___x_1455_);
v___x_1457_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__39, &l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__39_once, _init_l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__39);
v___x_1458_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__40));
v___x_1459_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1459_, 0, v___x_1458_);
lean_ctor_set(v___x_1459_, 1, v___x_1456_);
v___x_1460_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprLot_repr___redArg___closed__41));
v___x_1461_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1461_, 0, v___x_1459_);
lean_ctor_set(v___x_1461_, 1, v___x_1460_);
v___x_1462_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1462_, 0, v___x_1457_);
lean_ctor_set(v___x_1462_, 1, v___x_1461_);
v___x_1463_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1463_, 0, v___x_1462_);
lean_ctor_set_uint8(v___x_1463_, sizeof(void*)*1, v___x_1324_);
return v___x_1463_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr(lean_object* v_x_1464_, lean_object* v_prec_1465_){
_start:
{
lean_object* v___x_1466_; 
v___x_1466_ = l_Legal_USTax_Hunt_Basis_instReprSt_repr___redArg(v_x_1464_);
return v___x_1466_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprSt_repr___boxed(lean_object* v_x_1467_, lean_object* v_prec_1468_){
_start:
{
lean_object* v_res_1469_; 
v_res_1469_ = l_Legal_USTax_Hunt_Basis_instReprSt_repr(v_x_1467_, v_prec_1468_);
lean_dec(v_prec_1468_);
return v_res_1469_;
}
}
LEAN_EXPORT lean_object* l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0(lean_object* v_a_1470_, lean_object* v_n_1471_){
_start:
{
lean_object* v___x_1472_; 
v___x_1472_ = l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg(v_a_1470_);
return v___x_1472_;
}
}
LEAN_EXPORT lean_object* l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___boxed(lean_object* v_a_1473_, lean_object* v_n_1474_){
_start:
{
lean_object* v_res_1475_; 
v_res_1475_ = l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0(v_a_1473_, v_n_1474_);
lean_dec(v_n_1474_);
return v_res_1475_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_instInhabitedSt_default___closed__0(void){
_start:
{
lean_object* v___x_1478_; uint8_t v___x_1479_; lean_object* v___x_1480_; lean_object* v___x_1481_; lean_object* v___x_1482_; 
v___x_1478_ = l_Legal_USTax_Hunt_Basis_instInhabitedRet_default;
v___x_1479_ = 0;
v___x_1480_ = lean_unsigned_to_nat(0u);
v___x_1481_ = lean_box(0);
v___x_1482_ = lean_alloc_ctor(0, 12, 2);
lean_ctor_set(v___x_1482_, 0, v___x_1481_);
lean_ctor_set(v___x_1482_, 1, v___x_1480_);
lean_ctor_set(v___x_1482_, 2, v___x_1480_);
lean_ctor_set(v___x_1482_, 3, v___x_1478_);
lean_ctor_set(v___x_1482_, 4, v___x_1478_);
lean_ctor_set(v___x_1482_, 5, v___x_1478_);
lean_ctor_set(v___x_1482_, 6, v___x_1478_);
lean_ctor_set(v___x_1482_, 7, v___x_1480_);
lean_ctor_set(v___x_1482_, 8, v___x_1480_);
lean_ctor_set(v___x_1482_, 9, v___x_1480_);
lean_ctor_set(v___x_1482_, 10, v___x_1480_);
lean_ctor_set(v___x_1482_, 11, v___x_1480_);
lean_ctor_set_uint8(v___x_1482_, sizeof(void*)*12, v___x_1479_);
lean_ctor_set_uint8(v___x_1482_, sizeof(void*)*12 + 1, v___x_1479_);
return v___x_1482_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_instInhabitedSt_default(void){
_start:
{
lean_object* v___x_1483_; 
v___x_1483_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instInhabitedSt_default___closed__0, &l_Legal_USTax_Hunt_Basis_instInhabitedSt_default___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_instInhabitedSt_default___closed__0);
return v___x_1483_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_instInhabitedSt(void){
_start:
{
lean_object* v___x_1484_; 
v___x_1484_ = l_Legal_USTax_Hunt_Basis_instInhabitedSt_default;
return v___x_1484_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_ctorIdx(lean_object* v_x_1485_){
_start:
{
switch(lean_obj_tag(v_x_1485_))
{
case 0:
{
lean_object* v___x_1486_; 
v___x_1486_ = lean_unsigned_to_nat(0u);
return v___x_1486_;
}
case 1:
{
lean_object* v___x_1487_; 
v___x_1487_ = lean_unsigned_to_nat(1u);
return v___x_1487_;
}
case 2:
{
lean_object* v___x_1488_; 
v___x_1488_ = lean_unsigned_to_nat(2u);
return v___x_1488_;
}
case 3:
{
lean_object* v___x_1489_; 
v___x_1489_ = lean_unsigned_to_nat(3u);
return v___x_1489_;
}
case 4:
{
lean_object* v___x_1490_; 
v___x_1490_ = lean_unsigned_to_nat(4u);
return v___x_1490_;
}
case 5:
{
lean_object* v___x_1491_; 
v___x_1491_ = lean_unsigned_to_nat(5u);
return v___x_1491_;
}
default: 
{
lean_object* v___x_1492_; 
v___x_1492_ = lean_unsigned_to_nat(6u);
return v___x_1492_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_ctorIdx___boxed(lean_object* v_x_1493_){
_start:
{
lean_object* v_res_1494_; 
v_res_1494_ = l_Legal_USTax_Hunt_Basis_Move_ctorIdx(v_x_1493_);
lean_dec(v_x_1493_);
return v_res_1494_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_ctorElim___redArg(lean_object* v_t_1495_, lean_object* v_k_1496_){
_start:
{
switch(lean_obj_tag(v_t_1495_))
{
case 0:
{
lean_object* v_i_1497_; lean_object* v___x_1498_; 
v_i_1497_ = lean_ctor_get(v_t_1495_, 0);
lean_inc(v_i_1497_);
lean_dec_ref_known(v_t_1495_, 1);
v___x_1498_ = lean_apply_1(v_k_1496_, v_i_1497_);
return v___x_1498_;
}
case 1:
{
lean_object* v_i_1499_; uint8_t v_to_1500_; lean_object* v___x_1501_; lean_object* v___x_1502_; 
v_i_1499_ = lean_ctor_get(v_t_1495_, 0);
lean_inc(v_i_1499_);
v_to_1500_ = lean_ctor_get_uint8(v_t_1495_, sizeof(void*)*1);
lean_dec_ref_known(v_t_1495_, 1);
v___x_1501_ = lean_box(v_to_1500_);
v___x_1502_ = lean_apply_2(v_k_1496_, v_i_1499_, v___x_1501_);
return v___x_1502_;
}
case 2:
{
lean_object* v_i_1503_; uint8_t v_to_1504_; lean_object* v___x_1505_; lean_object* v___x_1506_; 
v_i_1503_ = lean_ctor_get(v_t_1495_, 0);
lean_inc(v_i_1503_);
v_to_1504_ = lean_ctor_get_uint8(v_t_1495_, sizeof(void*)*1);
lean_dec_ref_known(v_t_1495_, 1);
v___x_1505_ = lean_box(v_to_1504_);
v___x_1506_ = lean_apply_2(v_k_1496_, v_i_1503_, v___x_1505_);
return v___x_1506_;
}
case 3:
{
lean_object* v_i_1507_; lean_object* v___x_1508_; 
v_i_1507_ = lean_ctor_get(v_t_1495_, 0);
lean_inc(v_i_1507_);
lean_dec_ref_known(v_t_1495_, 1);
v___x_1508_ = lean_apply_1(v_k_1496_, v_i_1507_);
return v___x_1508_;
}
case 5:
{
uint8_t v_heir_1509_; lean_object* v___x_1510_; lean_object* v___x_1511_; 
v_heir_1509_ = lean_ctor_get_uint8(v_t_1495_, 0);
lean_dec_ref_known(v_t_1495_, 0);
v___x_1510_ = lean_box(v_heir_1509_);
v___x_1511_ = lean_apply_1(v_k_1496_, v___x_1510_);
return v___x_1511_;
}
default: 
{
lean_dec(v_t_1495_);
return v_k_1496_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_ctorElim(lean_object* v_motive_1512_, lean_object* v_ctorIdx_1513_, lean_object* v_t_1514_, lean_object* v_h_1515_, lean_object* v_k_1516_){
_start:
{
lean_object* v___x_1517_; 
v___x_1517_ = l_Legal_USTax_Hunt_Basis_Move_ctorElim___redArg(v_t_1514_, v_k_1516_);
return v___x_1517_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_ctorElim___boxed(lean_object* v_motive_1518_, lean_object* v_ctorIdx_1519_, lean_object* v_t_1520_, lean_object* v_h_1521_, lean_object* v_k_1522_){
_start:
{
lean_object* v_res_1523_; 
v_res_1523_ = l_Legal_USTax_Hunt_Basis_Move_ctorElim(v_motive_1518_, v_ctorIdx_1519_, v_t_1520_, v_h_1521_, v_k_1522_);
lean_dec(v_ctorIdx_1519_);
return v_res_1523_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_sell_elim___redArg(lean_object* v_t_1524_, lean_object* v_sell_1525_){
_start:
{
lean_object* v___x_1526_; 
v___x_1526_ = l_Legal_USTax_Hunt_Basis_Move_ctorElim___redArg(v_t_1524_, v_sell_1525_);
return v___x_1526_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_sell_elim(lean_object* v_motive_1527_, lean_object* v_t_1528_, lean_object* v_h_1529_, lean_object* v_sell_1530_){
_start:
{
lean_object* v___x_1531_; 
v___x_1531_ = l_Legal_USTax_Hunt_Basis_Move_ctorElim___redArg(v_t_1528_, v_sell_1530_);
return v___x_1531_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_gift_elim___redArg(lean_object* v_t_1532_, lean_object* v_gift_1533_){
_start:
{
lean_object* v___x_1534_; 
v___x_1534_ = l_Legal_USTax_Hunt_Basis_Move_ctorElim___redArg(v_t_1532_, v_gift_1533_);
return v___x_1534_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_gift_elim(lean_object* v_motive_1535_, lean_object* v_t_1536_, lean_object* v_h_1537_, lean_object* v_gift_1538_){
_start:
{
lean_object* v___x_1539_; 
v___x_1539_ = l_Legal_USTax_Hunt_Basis_Move_ctorElim___redArg(v_t_1536_, v_gift_1538_);
return v___x_1539_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_sellTo_elim___redArg(lean_object* v_t_1540_, lean_object* v_sellTo_1541_){
_start:
{
lean_object* v___x_1542_; 
v___x_1542_ = l_Legal_USTax_Hunt_Basis_Move_ctorElim___redArg(v_t_1540_, v_sellTo_1541_);
return v___x_1542_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_sellTo_elim(lean_object* v_motive_1543_, lean_object* v_t_1544_, lean_object* v_h_1545_, lean_object* v_sellTo_1546_){
_start:
{
lean_object* v___x_1547_; 
v___x_1547_ = l_Legal_USTax_Hunt_Basis_Move_ctorElim___redArg(v_t_1544_, v_sellTo_1546_);
return v___x_1547_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_donate_elim___redArg(lean_object* v_t_1548_, lean_object* v_donate_1549_){
_start:
{
lean_object* v___x_1550_; 
v___x_1550_ = l_Legal_USTax_Hunt_Basis_Move_ctorElim___redArg(v_t_1548_, v_donate_1549_);
return v___x_1550_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_donate_elim(lean_object* v_motive_1551_, lean_object* v_t_1552_, lean_object* v_h_1553_, lean_object* v_donate_1554_){
_start:
{
lean_object* v___x_1555_; 
v___x_1555_ = l_Legal_USTax_Hunt_Basis_Move_ctorElim___redArg(v_t_1552_, v_donate_1554_);
return v___x_1555_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_donateCash_elim___redArg(lean_object* v_t_1556_, lean_object* v_donateCash_1557_){
_start:
{
lean_object* v___x_1558_; 
v___x_1558_ = l_Legal_USTax_Hunt_Basis_Move_ctorElim___redArg(v_t_1556_, v_donateCash_1557_);
return v___x_1558_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_donateCash_elim(lean_object* v_motive_1559_, lean_object* v_t_1560_, lean_object* v_h_1561_, lean_object* v_donateCash_1562_){
_start:
{
lean_object* v___x_1563_; 
v___x_1563_ = l_Legal_USTax_Hunt_Basis_Move_ctorElim___redArg(v_t_1560_, v_donateCash_1562_);
return v___x_1563_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_die_elim___redArg(lean_object* v_t_1564_, lean_object* v_die_1565_){
_start:
{
lean_object* v___x_1566_; 
v___x_1566_ = l_Legal_USTax_Hunt_Basis_Move_ctorElim___redArg(v_t_1564_, v_die_1565_);
return v___x_1566_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_die_elim(lean_object* v_motive_1567_, lean_object* v_t_1568_, lean_object* v_h_1569_, lean_object* v_die_1570_){
_start:
{
lean_object* v___x_1571_; 
v___x_1571_ = l_Legal_USTax_Hunt_Basis_Move_ctorElim___redArg(v_t_1568_, v_die_1570_);
return v___x_1571_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_nextYear_elim___redArg(lean_object* v_t_1572_, lean_object* v_nextYear_1573_){
_start:
{
lean_object* v___x_1574_; 
v___x_1574_ = l_Legal_USTax_Hunt_Basis_Move_ctorElim___redArg(v_t_1572_, v_nextYear_1573_);
return v___x_1574_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_Move_nextYear_elim(lean_object* v_motive_1575_, lean_object* v_t_1576_, lean_object* v_h_1577_, lean_object* v_nextYear_1578_){
_start:
{
lean_object* v___x_1579_; 
v___x_1579_ = l_Legal_USTax_Hunt_Basis_Move_ctorElim___redArg(v_t_1576_, v_nextYear_1578_);
return v___x_1579_;
}
}
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_instBEqMove_beq(lean_object* v_x_1580_, lean_object* v_x_1581_){
_start:
{
lean_object* v_a_1583_; uint8_t v_a_1584_; lean_object* v_b_1585_; uint8_t v_b_1586_; 
switch(lean_obj_tag(v_x_1580_))
{
case 0:
{
if (lean_obj_tag(v_x_1581_) == 0)
{
lean_object* v_i_1589_; lean_object* v_i_1590_; uint8_t v___x_1591_; 
v_i_1589_ = lean_ctor_get(v_x_1580_, 0);
v_i_1590_ = lean_ctor_get(v_x_1581_, 0);
v___x_1591_ = lean_nat_dec_eq(v_i_1589_, v_i_1590_);
return v___x_1591_;
}
else
{
uint8_t v___x_1592_; 
v___x_1592_ = 0;
return v___x_1592_;
}
}
case 1:
{
if (lean_obj_tag(v_x_1581_) == 1)
{
lean_object* v_i_1593_; uint8_t v_to_1594_; lean_object* v_i_1595_; uint8_t v_to_1596_; 
v_i_1593_ = lean_ctor_get(v_x_1580_, 0);
v_to_1594_ = lean_ctor_get_uint8(v_x_1580_, sizeof(void*)*1);
v_i_1595_ = lean_ctor_get(v_x_1581_, 0);
v_to_1596_ = lean_ctor_get_uint8(v_x_1581_, sizeof(void*)*1);
v_a_1583_ = v_i_1593_;
v_a_1584_ = v_to_1594_;
v_b_1585_ = v_i_1595_;
v_b_1586_ = v_to_1596_;
goto v___jp_1582_;
}
else
{
uint8_t v___x_1597_; 
v___x_1597_ = 0;
return v___x_1597_;
}
}
case 2:
{
if (lean_obj_tag(v_x_1581_) == 2)
{
lean_object* v_i_1598_; uint8_t v_to_1599_; lean_object* v_i_1600_; uint8_t v_to_1601_; 
v_i_1598_ = lean_ctor_get(v_x_1580_, 0);
v_to_1599_ = lean_ctor_get_uint8(v_x_1580_, sizeof(void*)*1);
v_i_1600_ = lean_ctor_get(v_x_1581_, 0);
v_to_1601_ = lean_ctor_get_uint8(v_x_1581_, sizeof(void*)*1);
v_a_1583_ = v_i_1598_;
v_a_1584_ = v_to_1599_;
v_b_1585_ = v_i_1600_;
v_b_1586_ = v_to_1601_;
goto v___jp_1582_;
}
else
{
uint8_t v___x_1602_; 
v___x_1602_ = 0;
return v___x_1602_;
}
}
case 3:
{
if (lean_obj_tag(v_x_1581_) == 3)
{
lean_object* v_i_1603_; lean_object* v_i_1604_; uint8_t v___x_1605_; 
v_i_1603_ = lean_ctor_get(v_x_1580_, 0);
v_i_1604_ = lean_ctor_get(v_x_1581_, 0);
v___x_1605_ = lean_nat_dec_eq(v_i_1603_, v_i_1604_);
return v___x_1605_;
}
else
{
uint8_t v___x_1606_; 
v___x_1606_ = 0;
return v___x_1606_;
}
}
case 4:
{
if (lean_obj_tag(v_x_1581_) == 4)
{
uint8_t v___x_1607_; 
v___x_1607_ = 1;
return v___x_1607_;
}
else
{
uint8_t v___x_1608_; 
v___x_1608_ = 0;
return v___x_1608_;
}
}
case 5:
{
if (lean_obj_tag(v_x_1581_) == 5)
{
uint8_t v_heir_1609_; uint8_t v_heir_1610_; uint8_t v___x_1611_; 
v_heir_1609_ = lean_ctor_get_uint8(v_x_1580_, 0);
v_heir_1610_ = lean_ctor_get_uint8(v_x_1581_, 0);
v___x_1611_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_heir_1609_, v_heir_1610_);
return v___x_1611_;
}
else
{
uint8_t v___x_1612_; 
v___x_1612_ = 0;
return v___x_1612_;
}
}
default: 
{
if (lean_obj_tag(v_x_1581_) == 6)
{
uint8_t v___x_1613_; 
v___x_1613_ = 1;
return v___x_1613_;
}
else
{
uint8_t v___x_1614_; 
v___x_1614_ = 0;
return v___x_1614_;
}
}
}
v___jp_1582_:
{
uint8_t v___x_1587_; 
v___x_1587_ = lean_nat_dec_eq(v_a_1583_, v_b_1585_);
if (v___x_1587_ == 0)
{
return v___x_1587_;
}
else
{
uint8_t v___x_1588_; 
v___x_1588_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_a_1584_, v_b_1586_);
return v___x_1588_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instBEqMove_beq___boxed(lean_object* v_x_1615_, lean_object* v_x_1616_){
_start:
{
uint8_t v_res_1617_; lean_object* v_r_1618_; 
v_res_1617_ = l_Legal_USTax_Hunt_Basis_instBEqMove_beq(v_x_1615_, v_x_1616_);
lean_dec(v_x_1616_);
lean_dec(v_x_1615_);
v_r_1618_ = lean_box(v_res_1617_);
return v_r_1618_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr(lean_object* v_x_1657_, lean_object* v_prec_1658_){
_start:
{
lean_object* v___y_1660_; lean_object* v___y_1667_; 
switch(lean_obj_tag(v_x_1657_))
{
case 0:
{
lean_object* v_i_1673_; lean_object* v___x_1675_; uint8_t v_isShared_1676_; uint8_t v_isSharedCheck_1693_; 
v_i_1673_ = lean_ctor_get(v_x_1657_, 0);
v_isSharedCheck_1693_ = !lean_is_exclusive(v_x_1657_);
if (v_isSharedCheck_1693_ == 0)
{
v___x_1675_ = v_x_1657_;
v_isShared_1676_ = v_isSharedCheck_1693_;
goto v_resetjp_1674_;
}
else
{
lean_inc(v_i_1673_);
lean_dec(v_x_1657_);
v___x_1675_ = lean_box(0);
v_isShared_1676_ = v_isSharedCheck_1693_;
goto v_resetjp_1674_;
}
v_resetjp_1674_:
{
lean_object* v___y_1678_; lean_object* v___x_1689_; uint8_t v___x_1690_; 
v___x_1689_ = lean_unsigned_to_nat(1024u);
v___x_1690_ = lean_nat_dec_le(v___x_1689_, v_prec_1658_);
if (v___x_1690_ == 0)
{
lean_object* v___x_1691_; 
v___x_1691_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10);
v___y_1678_ = v___x_1691_;
goto v___jp_1677_;
}
else
{
lean_object* v___x_1692_; 
v___x_1692_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11);
v___y_1678_ = v___x_1692_;
goto v___jp_1677_;
}
v___jp_1677_:
{
lean_object* v___x_1679_; lean_object* v___x_1680_; lean_object* v___x_1682_; 
v___x_1679_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__6));
v___x_1680_ = l_Nat_reprFast(v_i_1673_);
if (v_isShared_1676_ == 0)
{
lean_ctor_set_tag(v___x_1675_, 3);
lean_ctor_set(v___x_1675_, 0, v___x_1680_);
v___x_1682_ = v___x_1675_;
goto v_reusejp_1681_;
}
else
{
lean_object* v_reuseFailAlloc_1688_; 
v_reuseFailAlloc_1688_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v_reuseFailAlloc_1688_, 0, v___x_1680_);
v___x_1682_ = v_reuseFailAlloc_1688_;
goto v_reusejp_1681_;
}
v_reusejp_1681_:
{
lean_object* v___x_1683_; lean_object* v___x_1684_; uint8_t v___x_1685_; lean_object* v___x_1686_; lean_object* v___x_1687_; 
v___x_1683_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1683_, 0, v___x_1679_);
lean_ctor_set(v___x_1683_, 1, v___x_1682_);
lean_inc(v___y_1678_);
v___x_1684_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1684_, 0, v___y_1678_);
lean_ctor_set(v___x_1684_, 1, v___x_1683_);
v___x_1685_ = 0;
v___x_1686_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1686_, 0, v___x_1684_);
lean_ctor_set_uint8(v___x_1686_, sizeof(void*)*1, v___x_1685_);
v___x_1687_ = l_Repr_addAppParen(v___x_1686_, v_prec_1658_);
return v___x_1687_;
}
}
}
}
case 1:
{
lean_object* v_i_1694_; uint8_t v_to_1695_; lean_object* v___x_1697_; uint8_t v_isShared_1698_; uint8_t v_isSharedCheck_1720_; 
v_i_1694_ = lean_ctor_get(v_x_1657_, 0);
v_to_1695_ = lean_ctor_get_uint8(v_x_1657_, sizeof(void*)*1);
v_isSharedCheck_1720_ = !lean_is_exclusive(v_x_1657_);
if (v_isSharedCheck_1720_ == 0)
{
v___x_1697_ = v_x_1657_;
v_isShared_1698_ = v_isSharedCheck_1720_;
goto v_resetjp_1696_;
}
else
{
lean_inc(v_i_1694_);
lean_dec(v_x_1657_);
v___x_1697_ = lean_box(0);
v_isShared_1698_ = v_isSharedCheck_1720_;
goto v_resetjp_1696_;
}
v_resetjp_1696_:
{
lean_object* v___y_1700_; lean_object* v___x_1716_; uint8_t v___x_1717_; 
v___x_1716_ = lean_unsigned_to_nat(1024u);
v___x_1717_ = lean_nat_dec_le(v___x_1716_, v_prec_1658_);
if (v___x_1717_ == 0)
{
lean_object* v___x_1718_; 
v___x_1718_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10);
v___y_1700_ = v___x_1718_;
goto v___jp_1699_;
}
else
{
lean_object* v___x_1719_; 
v___x_1719_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11);
v___y_1700_ = v___x_1719_;
goto v___jp_1699_;
}
v___jp_1699_:
{
lean_object* v___x_1701_; lean_object* v___x_1702_; lean_object* v___x_1703_; lean_object* v___x_1704_; lean_object* v___x_1705_; lean_object* v___x_1706_; lean_object* v___x_1707_; lean_object* v___x_1708_; lean_object* v___x_1709_; lean_object* v___x_1710_; uint8_t v___x_1711_; lean_object* v___x_1713_; 
v___x_1701_ = lean_box(1);
v___x_1702_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__9));
v___x_1703_ = l_Nat_reprFast(v_i_1694_);
v___x_1704_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1704_, 0, v___x_1703_);
v___x_1705_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1705_, 0, v___x_1702_);
lean_ctor_set(v___x_1705_, 1, v___x_1704_);
v___x_1706_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1706_, 0, v___x_1705_);
lean_ctor_set(v___x_1706_, 1, v___x_1701_);
v___x_1707_ = lean_unsigned_to_nat(1024u);
v___x_1708_ = l_Legal_USTax_Hunt_Basis_instReprWho_repr(v_to_1695_, v___x_1707_);
v___x_1709_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1709_, 0, v___x_1706_);
lean_ctor_set(v___x_1709_, 1, v___x_1708_);
lean_inc(v___y_1700_);
v___x_1710_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1710_, 0, v___y_1700_);
lean_ctor_set(v___x_1710_, 1, v___x_1709_);
v___x_1711_ = 0;
if (v_isShared_1698_ == 0)
{
lean_ctor_set_tag(v___x_1697_, 6);
lean_ctor_set(v___x_1697_, 0, v___x_1710_);
v___x_1713_ = v___x_1697_;
goto v_reusejp_1712_;
}
else
{
lean_object* v_reuseFailAlloc_1715_; 
v_reuseFailAlloc_1715_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v_reuseFailAlloc_1715_, 0, v___x_1710_);
v___x_1713_ = v_reuseFailAlloc_1715_;
goto v_reusejp_1712_;
}
v_reusejp_1712_:
{
lean_object* v___x_1714_; 
lean_ctor_set_uint8(v___x_1713_, sizeof(void*)*1, v___x_1711_);
v___x_1714_ = l_Repr_addAppParen(v___x_1713_, v_prec_1658_);
return v___x_1714_;
}
}
}
}
case 2:
{
lean_object* v_i_1721_; uint8_t v_to_1722_; lean_object* v___x_1724_; uint8_t v_isShared_1725_; uint8_t v_isSharedCheck_1747_; 
v_i_1721_ = lean_ctor_get(v_x_1657_, 0);
v_to_1722_ = lean_ctor_get_uint8(v_x_1657_, sizeof(void*)*1);
v_isSharedCheck_1747_ = !lean_is_exclusive(v_x_1657_);
if (v_isSharedCheck_1747_ == 0)
{
v___x_1724_ = v_x_1657_;
v_isShared_1725_ = v_isSharedCheck_1747_;
goto v_resetjp_1723_;
}
else
{
lean_inc(v_i_1721_);
lean_dec(v_x_1657_);
v___x_1724_ = lean_box(0);
v_isShared_1725_ = v_isSharedCheck_1747_;
goto v_resetjp_1723_;
}
v_resetjp_1723_:
{
lean_object* v___y_1727_; lean_object* v___x_1743_; uint8_t v___x_1744_; 
v___x_1743_ = lean_unsigned_to_nat(1024u);
v___x_1744_ = lean_nat_dec_le(v___x_1743_, v_prec_1658_);
if (v___x_1744_ == 0)
{
lean_object* v___x_1745_; 
v___x_1745_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10);
v___y_1727_ = v___x_1745_;
goto v___jp_1726_;
}
else
{
lean_object* v___x_1746_; 
v___x_1746_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11);
v___y_1727_ = v___x_1746_;
goto v___jp_1726_;
}
v___jp_1726_:
{
lean_object* v___x_1728_; lean_object* v___x_1729_; lean_object* v___x_1730_; lean_object* v___x_1731_; lean_object* v___x_1732_; lean_object* v___x_1733_; lean_object* v___x_1734_; lean_object* v___x_1735_; lean_object* v___x_1736_; lean_object* v___x_1737_; uint8_t v___x_1738_; lean_object* v___x_1740_; 
v___x_1728_ = lean_box(1);
v___x_1729_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__12));
v___x_1730_ = l_Nat_reprFast(v_i_1721_);
v___x_1731_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_1731_, 0, v___x_1730_);
v___x_1732_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1732_, 0, v___x_1729_);
lean_ctor_set(v___x_1732_, 1, v___x_1731_);
v___x_1733_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1733_, 0, v___x_1732_);
lean_ctor_set(v___x_1733_, 1, v___x_1728_);
v___x_1734_ = lean_unsigned_to_nat(1024u);
v___x_1735_ = l_Legal_USTax_Hunt_Basis_instReprWho_repr(v_to_1722_, v___x_1734_);
v___x_1736_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1736_, 0, v___x_1733_);
lean_ctor_set(v___x_1736_, 1, v___x_1735_);
lean_inc(v___y_1727_);
v___x_1737_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1737_, 0, v___y_1727_);
lean_ctor_set(v___x_1737_, 1, v___x_1736_);
v___x_1738_ = 0;
if (v_isShared_1725_ == 0)
{
lean_ctor_set_tag(v___x_1724_, 6);
lean_ctor_set(v___x_1724_, 0, v___x_1737_);
v___x_1740_ = v___x_1724_;
goto v_reusejp_1739_;
}
else
{
lean_object* v_reuseFailAlloc_1742_; 
v_reuseFailAlloc_1742_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v_reuseFailAlloc_1742_, 0, v___x_1737_);
v___x_1740_ = v_reuseFailAlloc_1742_;
goto v_reusejp_1739_;
}
v_reusejp_1739_:
{
lean_object* v___x_1741_; 
lean_ctor_set_uint8(v___x_1740_, sizeof(void*)*1, v___x_1738_);
v___x_1741_ = l_Repr_addAppParen(v___x_1740_, v_prec_1658_);
return v___x_1741_;
}
}
}
}
case 3:
{
lean_object* v_i_1748_; lean_object* v___x_1750_; uint8_t v_isShared_1751_; uint8_t v_isSharedCheck_1768_; 
v_i_1748_ = lean_ctor_get(v_x_1657_, 0);
v_isSharedCheck_1768_ = !lean_is_exclusive(v_x_1657_);
if (v_isSharedCheck_1768_ == 0)
{
v___x_1750_ = v_x_1657_;
v_isShared_1751_ = v_isSharedCheck_1768_;
goto v_resetjp_1749_;
}
else
{
lean_inc(v_i_1748_);
lean_dec(v_x_1657_);
v___x_1750_ = lean_box(0);
v_isShared_1751_ = v_isSharedCheck_1768_;
goto v_resetjp_1749_;
}
v_resetjp_1749_:
{
lean_object* v___y_1753_; lean_object* v___x_1764_; uint8_t v___x_1765_; 
v___x_1764_ = lean_unsigned_to_nat(1024u);
v___x_1765_ = lean_nat_dec_le(v___x_1764_, v_prec_1658_);
if (v___x_1765_ == 0)
{
lean_object* v___x_1766_; 
v___x_1766_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10);
v___y_1753_ = v___x_1766_;
goto v___jp_1752_;
}
else
{
lean_object* v___x_1767_; 
v___x_1767_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11);
v___y_1753_ = v___x_1767_;
goto v___jp_1752_;
}
v___jp_1752_:
{
lean_object* v___x_1754_; lean_object* v___x_1755_; lean_object* v___x_1757_; 
v___x_1754_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__15));
v___x_1755_ = l_Nat_reprFast(v_i_1748_);
if (v_isShared_1751_ == 0)
{
lean_ctor_set(v___x_1750_, 0, v___x_1755_);
v___x_1757_ = v___x_1750_;
goto v_reusejp_1756_;
}
else
{
lean_object* v_reuseFailAlloc_1763_; 
v_reuseFailAlloc_1763_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v_reuseFailAlloc_1763_, 0, v___x_1755_);
v___x_1757_ = v_reuseFailAlloc_1763_;
goto v_reusejp_1756_;
}
v_reusejp_1756_:
{
lean_object* v___x_1758_; lean_object* v___x_1759_; uint8_t v___x_1760_; lean_object* v___x_1761_; lean_object* v___x_1762_; 
v___x_1758_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1758_, 0, v___x_1754_);
lean_ctor_set(v___x_1758_, 1, v___x_1757_);
lean_inc(v___y_1753_);
v___x_1759_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1759_, 0, v___y_1753_);
lean_ctor_set(v___x_1759_, 1, v___x_1758_);
v___x_1760_ = 0;
v___x_1761_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1761_, 0, v___x_1759_);
lean_ctor_set_uint8(v___x_1761_, sizeof(void*)*1, v___x_1760_);
v___x_1762_ = l_Repr_addAppParen(v___x_1761_, v_prec_1658_);
return v___x_1762_;
}
}
}
}
case 4:
{
lean_object* v___x_1769_; uint8_t v___x_1770_; 
v___x_1769_ = lean_unsigned_to_nat(1024u);
v___x_1770_ = lean_nat_dec_le(v___x_1769_, v_prec_1658_);
if (v___x_1770_ == 0)
{
lean_object* v___x_1771_; 
v___x_1771_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10);
v___y_1660_ = v___x_1771_;
goto v___jp_1659_;
}
else
{
lean_object* v___x_1772_; 
v___x_1772_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11);
v___y_1660_ = v___x_1772_;
goto v___jp_1659_;
}
}
case 5:
{
uint8_t v_heir_1773_; lean_object* v___y_1775_; lean_object* v___x_1784_; uint8_t v___x_1785_; 
v_heir_1773_ = lean_ctor_get_uint8(v_x_1657_, 0);
lean_dec_ref_known(v_x_1657_, 0);
v___x_1784_ = lean_unsigned_to_nat(1024u);
v___x_1785_ = lean_nat_dec_le(v___x_1784_, v_prec_1658_);
if (v___x_1785_ == 0)
{
lean_object* v___x_1786_; 
v___x_1786_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10);
v___y_1775_ = v___x_1786_;
goto v___jp_1774_;
}
else
{
lean_object* v___x_1787_; 
v___x_1787_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11);
v___y_1775_ = v___x_1787_;
goto v___jp_1774_;
}
v___jp_1774_:
{
lean_object* v___x_1776_; lean_object* v___x_1777_; lean_object* v___x_1778_; lean_object* v___x_1779_; lean_object* v___x_1780_; uint8_t v___x_1781_; lean_object* v___x_1782_; lean_object* v___x_1783_; 
v___x_1776_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__18));
v___x_1777_ = lean_unsigned_to_nat(1024u);
v___x_1778_ = l_Legal_USTax_Hunt_Basis_instReprWho_repr(v_heir_1773_, v___x_1777_);
v___x_1779_ = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(v___x_1779_, 0, v___x_1776_);
lean_ctor_set(v___x_1779_, 1, v___x_1778_);
lean_inc(v___y_1775_);
v___x_1780_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1780_, 0, v___y_1775_);
lean_ctor_set(v___x_1780_, 1, v___x_1779_);
v___x_1781_ = 0;
v___x_1782_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1782_, 0, v___x_1780_);
lean_ctor_set_uint8(v___x_1782_, sizeof(void*)*1, v___x_1781_);
v___x_1783_ = l_Repr_addAppParen(v___x_1782_, v_prec_1658_);
return v___x_1783_;
}
}
default: 
{
lean_object* v___x_1788_; uint8_t v___x_1789_; 
v___x_1788_ = lean_unsigned_to_nat(1024u);
v___x_1789_ = lean_nat_dec_le(v___x_1788_, v_prec_1658_);
if (v___x_1789_ == 0)
{
lean_object* v___x_1790_; 
v___x_1790_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__10);
v___y_1667_ = v___x_1790_;
goto v___jp_1666_;
}
else
{
lean_object* v___x_1791_; 
v___x_1791_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11, &l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11_once, _init_l_Legal_USTax_Hunt_Basis_instReprWho_repr___closed__11);
v___y_1667_ = v___x_1791_;
goto v___jp_1666_;
}
}
}
v___jp_1659_:
{
lean_object* v___x_1661_; lean_object* v___x_1662_; uint8_t v___x_1663_; lean_object* v___x_1664_; lean_object* v___x_1665_; 
v___x_1661_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__1));
lean_inc(v___y_1660_);
v___x_1662_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1662_, 0, v___y_1660_);
lean_ctor_set(v___x_1662_, 1, v___x_1661_);
v___x_1663_ = 0;
v___x_1664_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1664_, 0, v___x_1662_);
lean_ctor_set_uint8(v___x_1664_, sizeof(void*)*1, v___x_1663_);
v___x_1665_ = l_Repr_addAppParen(v___x_1664_, v_prec_1658_);
return v___x_1665_;
}
v___jp_1666_:
{
lean_object* v___x_1668_; lean_object* v___x_1669_; uint8_t v___x_1670_; lean_object* v___x_1671_; lean_object* v___x_1672_; 
v___x_1668_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instReprMove_repr___closed__3));
lean_inc(v___y_1667_);
v___x_1669_ = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(v___x_1669_, 0, v___y_1667_);
lean_ctor_set(v___x_1669_, 1, v___x_1668_);
v___x_1670_ = 0;
v___x_1671_ = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(v___x_1671_, 0, v___x_1669_);
lean_ctor_set_uint8(v___x_1671_, sizeof(void*)*1, v___x_1670_);
v___x_1672_ = l_Repr_addAppParen(v___x_1671_, v_prec_1658_);
return v___x_1672_;
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_instReprMove_repr___boxed(lean_object* v_x_1792_, lean_object* v_prec_1793_){
_start:
{
lean_object* v_res_1794_; 
v_res_1794_ = l_Legal_USTax_Hunt_Basis_instReprMove_repr(v_x_1792_, v_prec_1793_);
lean_dec(v_prec_1793_);
return v_res_1794_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_big(void){
_start:
{
lean_object* v___x_1797_; 
v___x_1797_ = lean_cstr_to_nat("1000000000000");
return v___x_1797_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_mfj___closed__6(void){
_start:
{
lean_object* v___x_1816_; lean_object* v___x_1817_; lean_object* v___x_1818_; 
v___x_1816_ = lean_unsigned_to_nat(37u);
v___x_1817_ = lean_cstr_to_nat("1000000000000");
v___x_1818_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_1818_, 0, v___x_1817_);
lean_ctor_set(v___x_1818_, 1, v___x_1816_);
return v___x_1818_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_mfj___closed__7(void){
_start:
{
lean_object* v___x_1819_; lean_object* v___x_1820_; lean_object* v___x_1821_; 
v___x_1819_ = lean_box(0);
v___x_1820_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_mfj___closed__6, &l_Legal_USTax_Hunt_Basis_mfj___closed__6_once, _init_l_Legal_USTax_Hunt_Basis_mfj___closed__6);
v___x_1821_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_1821_, 0, v___x_1820_);
lean_ctor_set(v___x_1821_, 1, v___x_1819_);
return v___x_1821_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_mfj___closed__8(void){
_start:
{
lean_object* v___x_1822_; lean_object* v___x_1823_; lean_object* v___x_1824_; 
v___x_1822_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_mfj___closed__7, &l_Legal_USTax_Hunt_Basis_mfj___closed__7_once, _init_l_Legal_USTax_Hunt_Basis_mfj___closed__7);
v___x_1823_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_mfj___closed__5));
v___x_1824_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_1824_, 0, v___x_1823_);
lean_ctor_set(v___x_1824_, 1, v___x_1822_);
return v___x_1824_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_mfj___closed__9(void){
_start:
{
lean_object* v___x_1825_; lean_object* v___x_1826_; lean_object* v___x_1827_; 
v___x_1825_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_mfj___closed__8, &l_Legal_USTax_Hunt_Basis_mfj___closed__8_once, _init_l_Legal_USTax_Hunt_Basis_mfj___closed__8);
v___x_1826_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_mfj___closed__4));
v___x_1827_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_1827_, 0, v___x_1826_);
lean_ctor_set(v___x_1827_, 1, v___x_1825_);
return v___x_1827_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_mfj___closed__10(void){
_start:
{
lean_object* v___x_1828_; lean_object* v___x_1829_; lean_object* v___x_1830_; 
v___x_1828_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_mfj___closed__9, &l_Legal_USTax_Hunt_Basis_mfj___closed__9_once, _init_l_Legal_USTax_Hunt_Basis_mfj___closed__9);
v___x_1829_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_mfj___closed__3));
v___x_1830_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_1830_, 0, v___x_1829_);
lean_ctor_set(v___x_1830_, 1, v___x_1828_);
return v___x_1830_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_mfj___closed__11(void){
_start:
{
lean_object* v___x_1831_; lean_object* v___x_1832_; lean_object* v___x_1833_; 
v___x_1831_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_mfj___closed__10, &l_Legal_USTax_Hunt_Basis_mfj___closed__10_once, _init_l_Legal_USTax_Hunt_Basis_mfj___closed__10);
v___x_1832_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_mfj___closed__2));
v___x_1833_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_1833_, 0, v___x_1832_);
lean_ctor_set(v___x_1833_, 1, v___x_1831_);
return v___x_1833_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_mfj___closed__12(void){
_start:
{
lean_object* v___x_1834_; lean_object* v___x_1835_; lean_object* v___x_1836_; 
v___x_1834_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_mfj___closed__11, &l_Legal_USTax_Hunt_Basis_mfj___closed__11_once, _init_l_Legal_USTax_Hunt_Basis_mfj___closed__11);
v___x_1835_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_mfj___closed__1));
v___x_1836_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_1836_, 0, v___x_1835_);
lean_ctor_set(v___x_1836_, 1, v___x_1834_);
return v___x_1836_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_mfj___closed__13(void){
_start:
{
lean_object* v___x_1837_; lean_object* v___x_1838_; lean_object* v___x_1839_; 
v___x_1837_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_mfj___closed__12, &l_Legal_USTax_Hunt_Basis_mfj___closed__12_once, _init_l_Legal_USTax_Hunt_Basis_mfj___closed__12);
v___x_1838_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_mfj___closed__0));
v___x_1839_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_1839_, 0, v___x_1838_);
lean_ctor_set(v___x_1839_, 1, v___x_1837_);
return v___x_1839_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_mfj___closed__14(void){
_start:
{
lean_object* v___x_1840_; lean_object* v___x_1841_; lean_object* v___x_1842_; lean_object* v___x_1843_; 
v___x_1840_ = lean_unsigned_to_nat(613700u);
v___x_1841_ = lean_unsigned_to_nat(98900u);
v___x_1842_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_mfj___closed__13, &l_Legal_USTax_Hunt_Basis_mfj___closed__13_once, _init_l_Legal_USTax_Hunt_Basis_mfj___closed__13);
v___x_1843_ = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(v___x_1843_, 0, v___x_1842_);
lean_ctor_set(v___x_1843_, 1, v___x_1841_);
lean_ctor_set(v___x_1843_, 2, v___x_1840_);
return v___x_1843_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_mfj(void){
_start:
{
lean_object* v___x_1844_; 
v___x_1844_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_mfj___closed__14, &l_Legal_USTax_Hunt_Basis_mfj___closed__14_once, _init_l_Legal_USTax_Hunt_Basis_mfj___closed__14);
return v___x_1844_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_single___closed__6(void){
_start:
{
lean_object* v___x_1863_; lean_object* v___x_1864_; lean_object* v___x_1865_; 
v___x_1863_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_mfj___closed__7, &l_Legal_USTax_Hunt_Basis_mfj___closed__7_once, _init_l_Legal_USTax_Hunt_Basis_mfj___closed__7);
v___x_1864_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_single___closed__5));
v___x_1865_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_1865_, 0, v___x_1864_);
lean_ctor_set(v___x_1865_, 1, v___x_1863_);
return v___x_1865_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_single___closed__7(void){
_start:
{
lean_object* v___x_1866_; lean_object* v___x_1867_; lean_object* v___x_1868_; 
v___x_1866_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_single___closed__6, &l_Legal_USTax_Hunt_Basis_single___closed__6_once, _init_l_Legal_USTax_Hunt_Basis_single___closed__6);
v___x_1867_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_single___closed__4));
v___x_1868_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_1868_, 0, v___x_1867_);
lean_ctor_set(v___x_1868_, 1, v___x_1866_);
return v___x_1868_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_single___closed__8(void){
_start:
{
lean_object* v___x_1869_; lean_object* v___x_1870_; lean_object* v___x_1871_; 
v___x_1869_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_single___closed__7, &l_Legal_USTax_Hunt_Basis_single___closed__7_once, _init_l_Legal_USTax_Hunt_Basis_single___closed__7);
v___x_1870_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_single___closed__3));
v___x_1871_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_1871_, 0, v___x_1870_);
lean_ctor_set(v___x_1871_, 1, v___x_1869_);
return v___x_1871_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_single___closed__9(void){
_start:
{
lean_object* v___x_1872_; lean_object* v___x_1873_; lean_object* v___x_1874_; 
v___x_1872_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_single___closed__8, &l_Legal_USTax_Hunt_Basis_single___closed__8_once, _init_l_Legal_USTax_Hunt_Basis_single___closed__8);
v___x_1873_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_single___closed__2));
v___x_1874_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_1874_, 0, v___x_1873_);
lean_ctor_set(v___x_1874_, 1, v___x_1872_);
return v___x_1874_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_single___closed__10(void){
_start:
{
lean_object* v___x_1875_; lean_object* v___x_1876_; lean_object* v___x_1877_; 
v___x_1875_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_single___closed__9, &l_Legal_USTax_Hunt_Basis_single___closed__9_once, _init_l_Legal_USTax_Hunt_Basis_single___closed__9);
v___x_1876_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_single___closed__1));
v___x_1877_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_1877_, 0, v___x_1876_);
lean_ctor_set(v___x_1877_, 1, v___x_1875_);
return v___x_1877_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_single___closed__11(void){
_start:
{
lean_object* v___x_1878_; lean_object* v___x_1879_; lean_object* v___x_1880_; 
v___x_1878_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_single___closed__10, &l_Legal_USTax_Hunt_Basis_single___closed__10_once, _init_l_Legal_USTax_Hunt_Basis_single___closed__10);
v___x_1879_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_single___closed__0));
v___x_1880_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_1880_, 0, v___x_1879_);
lean_ctor_set(v___x_1880_, 1, v___x_1878_);
return v___x_1880_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_single___closed__12(void){
_start:
{
lean_object* v___x_1881_; lean_object* v___x_1882_; lean_object* v___x_1883_; lean_object* v___x_1884_; 
v___x_1881_ = lean_unsigned_to_nat(545500u);
v___x_1882_ = lean_unsigned_to_nat(49450u);
v___x_1883_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_single___closed__11, &l_Legal_USTax_Hunt_Basis_single___closed__11_once, _init_l_Legal_USTax_Hunt_Basis_single___closed__11);
v___x_1884_ = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(v___x_1884_, 0, v___x_1883_);
lean_ctor_set(v___x_1884_, 1, v___x_1882_);
lean_ctor_set(v___x_1884_, 2, v___x_1881_);
return v___x_1884_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_single(void){
_start:
{
lean_object* v___x_1885_; 
v___x_1885_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_single___closed__12, &l_Legal_USTax_Hunt_Basis_single___closed__12_once, _init_l_Legal_USTax_Hunt_Basis_single___closed__12);
return v___x_1885_;
}
}
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_ordTax_spec__0___redArg(lean_object* v_x_1886_, lean_object* v_as_x27_1887_, lean_object* v_b_1888_){
_start:
{
if (lean_obj_tag(v_as_x27_1887_) == 0)
{
return v_b_1888_;
}
else
{
lean_object* v_head_1889_; lean_object* v_tail_1890_; lean_object* v_fst_1891_; lean_object* v_snd_1892_; lean_object* v_t_1894_; lean_object* v_fst_1897_; lean_object* v_snd_1898_; lean_object* v___y_1900_; uint8_t v___x_1906_; 
v_head_1889_ = lean_ctor_get(v_as_x27_1887_, 0);
v_tail_1890_ = lean_ctor_get(v_as_x27_1887_, 1);
v_fst_1891_ = lean_ctor_get(v_head_1889_, 0);
v_snd_1892_ = lean_ctor_get(v_head_1889_, 1);
v_fst_1897_ = lean_ctor_get(v_b_1888_, 0);
lean_inc(v_fst_1897_);
v_snd_1898_ = lean_ctor_get(v_b_1888_, 1);
lean_inc(v_snd_1898_);
lean_dec_ref(v_b_1888_);
v___x_1906_ = lean_nat_dec_lt(v_fst_1897_, v_x_1886_);
if (v___x_1906_ == 0)
{
lean_dec(v_fst_1897_);
v_t_1894_ = v_snd_1898_;
goto v___jp_1893_;
}
else
{
uint8_t v___x_1907_; 
v___x_1907_ = lean_nat_dec_le(v_x_1886_, v_fst_1891_);
if (v___x_1907_ == 0)
{
v___y_1900_ = v_fst_1891_;
goto v___jp_1899_;
}
else
{
v___y_1900_ = v_x_1886_;
goto v___jp_1899_;
}
}
v___jp_1893_:
{
lean_object* v___x_1895_; 
lean_inc(v_fst_1891_);
v___x_1895_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_1895_, 0, v_fst_1891_);
lean_ctor_set(v___x_1895_, 1, v_t_1894_);
v_as_x27_1887_ = v_tail_1890_;
v_b_1888_ = v___x_1895_;
goto _start;
}
v___jp_1899_:
{
lean_object* v___x_1901_; lean_object* v___x_1902_; lean_object* v___x_1903_; lean_object* v___x_1904_; lean_object* v___x_1905_; 
v___x_1901_ = lean_nat_sub(v___y_1900_, v_fst_1897_);
lean_dec(v_fst_1897_);
v___x_1902_ = lean_nat_mul(v___x_1901_, v_snd_1892_);
lean_dec(v___x_1901_);
v___x_1903_ = lean_unsigned_to_nat(100u);
v___x_1904_ = lean_nat_div(v___x_1902_, v___x_1903_);
lean_dec(v___x_1902_);
v___x_1905_ = lean_nat_add(v_snd_1898_, v___x_1904_);
lean_dec(v___x_1904_);
lean_dec(v_snd_1898_);
v_t_1894_ = v___x_1905_;
goto v___jp_1893_;
}
}
}
}
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_ordTax_spec__0___redArg___boxed(lean_object* v_x_1908_, lean_object* v_as_x27_1909_, lean_object* v_b_1910_){
_start:
{
lean_object* v_res_1911_; 
v_res_1911_ = l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_ordTax_spec__0___redArg(v_x_1908_, v_as_x27_1909_, v_b_1910_);
lean_dec(v_as_x27_1909_);
lean_dec(v_x_1908_);
return v_res_1911_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_ordTax(lean_object* v_f_1914_, lean_object* v_x_1915_){
_start:
{
lean_object* v_brk_1916_; lean_object* v___x_1917_; lean_object* v___x_1918_; lean_object* v_snd_1919_; 
v_brk_1916_ = lean_ctor_get(v_f_1914_, 0);
v___x_1917_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_ordTax___closed__0));
v___x_1918_ = l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_ordTax_spec__0___redArg(v_x_1915_, v_brk_1916_, v___x_1917_);
v_snd_1919_ = lean_ctor_get(v___x_1918_, 1);
lean_inc(v_snd_1919_);
lean_dec_ref(v___x_1918_);
return v_snd_1919_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_ordTax___boxed(lean_object* v_f_1920_, lean_object* v_x_1921_){
_start:
{
lean_object* v_res_1922_; 
v_res_1922_ = l_Legal_USTax_Hunt_Basis_ordTax(v_f_1920_, v_x_1921_);
lean_dec(v_x_1921_);
lean_dec_ref(v_f_1920_);
return v_res_1922_;
}
}
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_ordTax_spec__0(lean_object* v_x_1923_, lean_object* v_as_1924_, lean_object* v_as_x27_1925_, lean_object* v_b_1926_, lean_object* v_a_1927_){
_start:
{
lean_object* v___x_1928_; 
v___x_1928_ = l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_ordTax_spec__0___redArg(v_x_1923_, v_as_x27_1925_, v_b_1926_);
return v___x_1928_;
}
}
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_ordTax_spec__0___boxed(lean_object* v_x_1929_, lean_object* v_as_1930_, lean_object* v_as_x27_1931_, lean_object* v_b_1932_, lean_object* v_a_1933_){
_start:
{
lean_object* v_res_1934_; 
v_res_1934_ = l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_ordTax_spec__0(v_x_1929_, v_as_1930_, v_as_x27_1931_, v_b_1932_, v_a_1933_);
lean_dec(v_as_x27_1931_);
lean_dec(v_as_1930_);
lean_dec(v_x_1929_);
return v_res_1934_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_fullTax(lean_object* v_f_1935_, lean_object* v_ord_1936_, lean_object* v_g28_1937_, lean_object* v_lt_1938_){
_start:
{
lean_object* v_t0_1939_; lean_object* v_base_1940_; lean_object* v___x_1941_; lean_object* v___x_1942_; lean_object* v___x_1943_; lean_object* v___x_1944_; lean_object* v___x_1945_; lean_object* v___y_1947_; lean_object* v___y_1948_; lean_object* v___y_1949_; lean_object* v___y_1961_; lean_object* v___y_1962_; lean_object* v___y_1963_; lean_object* v___y_1964_; lean_object* v___y_1968_; lean_object* v___y_1969_; lean_object* v___y_1970_; lean_object* v___y_1971_; lean_object* v___y_1974_; lean_object* v___y_1975_; lean_object* v___y_1976_; lean_object* v___y_1977_; lean_object* v___y_1981_; lean_object* v___y_1982_; lean_object* v___y_1983_; lean_object* v___y_1984_; lean_object* v___y_1988_; lean_object* v___x_1992_; uint8_t v___x_1993_; 
v_t0_1939_ = l_Legal_USTax_Hunt_Basis_ordTax(v_f_1935_, v_ord_1936_);
v_base_1940_ = lean_nat_add(v_ord_1936_, v_g28_1937_);
v___x_1941_ = l_Legal_USTax_Hunt_Basis_ordTax(v_f_1935_, v_base_1940_);
v___x_1942_ = lean_nat_sub(v___x_1941_, v_t0_1939_);
lean_dec(v___x_1941_);
v___x_1943_ = lean_unsigned_to_nat(28u);
v___x_1944_ = lean_nat_mul(v_g28_1937_, v___x_1943_);
v___x_1945_ = lean_unsigned_to_nat(100u);
v___x_1992_ = lean_nat_div(v___x_1944_, v___x_1945_);
lean_dec(v___x_1944_);
v___x_1993_ = lean_nat_dec_le(v___x_1942_, v___x_1992_);
if (v___x_1993_ == 0)
{
lean_dec(v___x_1942_);
v___y_1988_ = v___x_1992_;
goto v___jp_1987_;
}
else
{
lean_dec(v___x_1992_);
v___y_1988_ = v___x_1942_;
goto v___jp_1987_;
}
v___jp_1946_:
{
lean_object* v_at20_1950_; lean_object* v___x_1951_; lean_object* v___x_1952_; lean_object* v___x_1953_; lean_object* v___x_1954_; lean_object* v___x_1955_; lean_object* v___x_1956_; lean_object* v___x_1957_; lean_object* v___x_1958_; lean_object* v___x_1959_; 
v_at20_1950_ = lean_nat_sub(v___y_1947_, v___y_1949_);
lean_dec(v___y_1947_);
v___x_1951_ = lean_nat_add(v_t0_1939_, v___y_1948_);
lean_dec(v___y_1948_);
lean_dec(v_t0_1939_);
v___x_1952_ = lean_unsigned_to_nat(15u);
v___x_1953_ = lean_nat_mul(v___y_1949_, v___x_1952_);
lean_dec(v___y_1949_);
v___x_1954_ = lean_nat_div(v___x_1953_, v___x_1945_);
lean_dec(v___x_1953_);
v___x_1955_ = lean_nat_add(v___x_1951_, v___x_1954_);
lean_dec(v___x_1954_);
lean_dec(v___x_1951_);
v___x_1956_ = lean_unsigned_to_nat(20u);
v___x_1957_ = lean_nat_mul(v_at20_1950_, v___x_1956_);
lean_dec(v_at20_1950_);
v___x_1958_ = lean_nat_div(v___x_1957_, v___x_1945_);
lean_dec(v___x_1957_);
v___x_1959_ = lean_nat_add(v___x_1955_, v___x_1958_);
lean_dec(v___x_1958_);
lean_dec(v___x_1955_);
return v___x_1959_;
}
v___jp_1960_:
{
lean_object* v___x_1965_; uint8_t v___x_1966_; 
v___x_1965_ = lean_nat_sub(v___y_1963_, v___y_1964_);
lean_dec(v___y_1964_);
lean_dec(v___y_1963_);
v___x_1966_ = lean_nat_dec_le(v___y_1961_, v___x_1965_);
if (v___x_1966_ == 0)
{
v___y_1947_ = v___y_1961_;
v___y_1948_ = v___y_1962_;
v___y_1949_ = v___x_1965_;
goto v___jp_1946_;
}
else
{
lean_dec(v___x_1965_);
lean_inc(v___y_1961_);
v___y_1947_ = v___y_1961_;
v___y_1948_ = v___y_1962_;
v___y_1949_ = v___y_1961_;
goto v___jp_1946_;
}
}
v___jp_1967_:
{
uint8_t v___x_1972_; 
v___x_1972_ = lean_nat_dec_le(v___y_1970_, v___y_1971_);
if (v___x_1972_ == 0)
{
v___y_1961_ = v___y_1968_;
v___y_1962_ = v___y_1969_;
v___y_1963_ = v___y_1970_;
v___y_1964_ = v___y_1971_;
goto v___jp_1960_;
}
else
{
lean_dec(v___y_1971_);
lean_inc(v___y_1970_);
v___y_1961_ = v___y_1968_;
v___y_1962_ = v___y_1969_;
v___y_1963_ = v___y_1970_;
v___y_1964_ = v___y_1970_;
goto v___jp_1960_;
}
}
v___jp_1973_:
{
lean_object* v_rem_1978_; uint8_t v___x_1979_; 
v_rem_1978_ = lean_nat_sub(v_lt_1938_, v___y_1977_);
lean_dec(v___y_1977_);
lean_dec(v_lt_1938_);
v___x_1979_ = lean_nat_dec_le(v_base_1940_, v___y_1976_);
if (v___x_1979_ == 0)
{
lean_dec(v___y_1976_);
v___y_1968_ = v_rem_1978_;
v___y_1969_ = v___y_1974_;
v___y_1970_ = v___y_1975_;
v___y_1971_ = v_base_1940_;
goto v___jp_1967_;
}
else
{
lean_dec(v_base_1940_);
v___y_1968_ = v_rem_1978_;
v___y_1969_ = v___y_1974_;
v___y_1970_ = v___y_1975_;
v___y_1971_ = v___y_1976_;
goto v___jp_1967_;
}
}
v___jp_1980_:
{
lean_object* v___x_1985_; uint8_t v___x_1986_; 
v___x_1985_ = lean_nat_sub(v___y_1983_, v___y_1984_);
lean_dec(v___y_1984_);
v___x_1986_ = lean_nat_dec_le(v_lt_1938_, v___x_1985_);
if (v___x_1986_ == 0)
{
v___y_1974_ = v___y_1981_;
v___y_1975_ = v___y_1982_;
v___y_1976_ = v___y_1983_;
v___y_1977_ = v___x_1985_;
goto v___jp_1973_;
}
else
{
lean_dec(v___x_1985_);
lean_inc(v_lt_1938_);
v___y_1974_ = v___y_1981_;
v___y_1975_ = v___y_1982_;
v___y_1976_ = v___y_1983_;
v___y_1977_ = v_lt_1938_;
goto v___jp_1973_;
}
}
v___jp_1987_:
{
lean_object* v_z0_1989_; lean_object* v_z15_1990_; uint8_t v___x_1991_; 
v_z0_1989_ = lean_ctor_get(v_f_1935_, 1);
lean_inc(v_z0_1989_);
v_z15_1990_ = lean_ctor_get(v_f_1935_, 2);
lean_inc(v_z15_1990_);
lean_dec_ref(v_f_1935_);
v___x_1991_ = lean_nat_dec_le(v_z0_1989_, v_base_1940_);
if (v___x_1991_ == 0)
{
lean_inc(v_base_1940_);
v___y_1981_ = v___y_1988_;
v___y_1982_ = v_z15_1990_;
v___y_1983_ = v_z0_1989_;
v___y_1984_ = v_base_1940_;
goto v___jp_1980_;
}
else
{
lean_inc(v_z0_1989_);
v___y_1981_ = v___y_1988_;
v___y_1982_ = v_z15_1990_;
v___y_1983_ = v_z0_1989_;
v___y_1984_ = v_z0_1989_;
goto v___jp_1980_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_fullTax___boxed(lean_object* v_f_1994_, lean_object* v_ord_1995_, lean_object* v_g28_1996_, lean_object* v_lt_1997_){
_start:
{
lean_object* v_res_1998_; 
v_res_1998_ = l_Legal_USTax_Hunt_Basis_fullTax(v_f_1994_, v_ord_1995_, v_g28_1996_, v_lt_1997_);
lean_dec(v_g28_1996_);
lean_dec(v_ord_1995_);
return v_res_1998_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_capNet(lean_object* v_r_1999_){
_start:
{
lean_object* v_st_2000_; lean_object* v_lt_2001_; lean_object* v_g28_2002_; lean_object* v_cfS_2003_; lean_object* v_cfL_2004_; lean_object* v___x_2005_; lean_object* v_s_2006_; lean_object* v___x_2007_; lean_object* v_l_2008_; lean_object* v_g_2009_; lean_object* v___x_2010_; lean_object* v___y_2012_; lean_object* v___y_2013_; lean_object* v___y_2014_; lean_object* v___y_2015_; lean_object* v___y_2016_; lean_object* v___y_2023_; lean_object* v___y_2024_; lean_object* v___y_2025_; lean_object* v___y_2026_; lean_object* v___y_2029_; lean_object* v___y_2030_; lean_object* v___y_2031_; lean_object* v___y_2040_; lean_object* v___y_2041_; lean_object* v___y_2042_; lean_object* v___y_2047_; lean_object* v___y_2048_; lean_object* v___y_2049_; lean_object* v___x_2053_; lean_object* v___y_2055_; lean_object* v___y_2056_; lean_object* v___y_2057_; uint8_t v___y_2058_; lean_object* v___y_2070_; lean_object* v___y_2071_; lean_object* v___y_2072_; uint8_t v___y_2073_; lean_object* v___y_2086_; lean_object* v___y_2087_; lean_object* v___y_2088_; lean_object* v___y_2098_; uint8_t v___x_2104_; 
v_st_2000_ = lean_ctor_get(v_r_1999_, 0);
lean_inc(v_st_2000_);
v_lt_2001_ = lean_ctor_get(v_r_1999_, 1);
lean_inc(v_lt_2001_);
v_g28_2002_ = lean_ctor_get(v_r_1999_, 2);
lean_inc(v_g28_2002_);
v_cfS_2003_ = lean_ctor_get(v_r_1999_, 3);
lean_inc(v_cfS_2003_);
v_cfL_2004_ = lean_ctor_get(v_r_1999_, 4);
lean_inc(v_cfL_2004_);
lean_dec_ref(v_r_1999_);
v___x_2005_ = lean_nat_to_int(v_cfS_2003_);
v_s_2006_ = lean_int_sub(v_st_2000_, v___x_2005_);
lean_dec(v___x_2005_);
lean_dec(v_st_2000_);
v___x_2007_ = lean_nat_to_int(v_cfL_2004_);
v_l_2008_ = lean_int_sub(v_lt_2001_, v___x_2007_);
lean_dec(v___x_2007_);
lean_dec(v_lt_2001_);
v_g_2009_ = lean_nat_to_int(v_g28_2002_);
v___x_2010_ = lean_unsigned_to_nat(0u);
v___x_2053_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0, &l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0);
v___x_2104_ = lean_int_dec_lt(v_s_2006_, v___x_2053_);
if (v___x_2104_ == 0)
{
v___y_2098_ = v___x_2053_;
goto v___jp_2097_;
}
else
{
lean_object* v___x_2105_; uint8_t v___x_2106_; 
v___x_2105_ = lean_int_neg(v_s_2006_);
v___x_2106_ = lean_int_dec_le(v___x_2105_, v_g_2009_);
if (v___x_2106_ == 0)
{
lean_dec(v___x_2105_);
lean_inc(v_g_2009_);
v___y_2098_ = v_g_2009_;
goto v___jp_2097_;
}
else
{
v___y_2098_ = v___x_2105_;
goto v___jp_2097_;
}
}
v___jp_2011_:
{
lean_object* v___x_2017_; lean_object* v___x_2018_; lean_object* v___x_2019_; lean_object* v___x_2020_; lean_object* v___x_2021_; 
v___x_2017_ = l_Int_toNat(v___y_2014_);
lean_dec(v___y_2014_);
v___x_2018_ = lean_nat_sub(v___y_2013_, v___y_2016_);
lean_dec(v___y_2013_);
v___x_2019_ = lean_nat_sub(v___y_2015_, v___y_2016_);
lean_dec(v___y_2016_);
v___x_2020_ = lean_nat_sub(v___y_2012_, v___x_2019_);
lean_dec(v___x_2019_);
lean_dec(v___y_2012_);
v___x_2021_ = lean_alloc_ctor(0, 6, 0);
lean_ctor_set(v___x_2021_, 0, v___x_2010_);
lean_ctor_set(v___x_2021_, 1, v___x_2010_);
lean_ctor_set(v___x_2021_, 2, v___x_2017_);
lean_ctor_set(v___x_2021_, 3, v___y_2015_);
lean_ctor_set(v___x_2021_, 4, v___x_2018_);
lean_ctor_set(v___x_2021_, 5, v___x_2020_);
return v___x_2021_;
}
v___jp_2022_:
{
uint8_t v___x_2027_; 
v___x_2027_ = lean_nat_dec_le(v___y_2026_, v___y_2024_);
if (v___x_2027_ == 0)
{
lean_inc(v___y_2024_);
v___y_2012_ = v___y_2023_;
v___y_2013_ = v___y_2024_;
v___y_2014_ = v___y_2025_;
v___y_2015_ = v___y_2026_;
v___y_2016_ = v___y_2024_;
goto v___jp_2011_;
}
else
{
lean_inc(v___y_2026_);
v___y_2012_ = v___y_2023_;
v___y_2013_ = v___y_2024_;
v___y_2014_ = v___y_2025_;
v___y_2015_ = v___y_2026_;
v___y_2016_ = v___y_2026_;
goto v___jp_2011_;
}
}
v___jp_2028_:
{
lean_object* v___x_2032_; lean_object* v_ls_2033_; lean_object* v___x_2034_; lean_object* v_ll_2035_; lean_object* v___x_2036_; lean_object* v___x_2037_; uint8_t v___x_2038_; 
v___x_2032_ = lean_int_neg(v___y_2029_);
lean_dec(v___y_2029_);
v_ls_2033_ = l_Int_toNat(v___x_2032_);
lean_dec(v___x_2032_);
v___x_2034_ = lean_int_neg(v___y_2030_);
lean_dec(v___y_2030_);
v_ll_2035_ = l_Int_toNat(v___x_2034_);
lean_dec(v___x_2034_);
v___x_2036_ = lean_unsigned_to_nat(3000u);
v___x_2037_ = lean_nat_add(v_ls_2033_, v_ll_2035_);
v___x_2038_ = lean_nat_dec_le(v___x_2036_, v___x_2037_);
if (v___x_2038_ == 0)
{
v___y_2023_ = v_ll_2035_;
v___y_2024_ = v_ls_2033_;
v___y_2025_ = v___y_2031_;
v___y_2026_ = v___x_2037_;
goto v___jp_2022_;
}
else
{
lean_dec(v___x_2037_);
v___y_2023_ = v_ll_2035_;
v___y_2024_ = v_ls_2033_;
v___y_2025_ = v___y_2031_;
v___y_2026_ = v___x_2036_;
goto v___jp_2022_;
}
}
v___jp_2039_:
{
lean_object* v___x_2043_; lean_object* v___x_2044_; lean_object* v___x_2045_; 
v___x_2043_ = l_Int_toNat(v___y_2041_);
lean_dec(v___y_2041_);
v___x_2044_ = lean_nat_sub(v___y_2040_, v___y_2042_);
lean_dec(v___y_2040_);
v___x_2045_ = lean_alloc_ctor(0, 6, 0);
lean_ctor_set(v___x_2045_, 0, v___x_2010_);
lean_ctor_set(v___x_2045_, 1, v___x_2010_);
lean_ctor_set(v___x_2045_, 2, v___x_2043_);
lean_ctor_set(v___x_2045_, 3, v___y_2042_);
lean_ctor_set(v___x_2045_, 4, v___x_2010_);
lean_ctor_set(v___x_2045_, 5, v___x_2044_);
return v___x_2045_;
}
v___jp_2046_:
{
lean_object* v___x_2050_; lean_object* v___x_2051_; lean_object* v___x_2052_; 
v___x_2050_ = l_Int_toNat(v___y_2047_);
lean_dec(v___y_2047_);
v___x_2051_ = lean_nat_sub(v___y_2048_, v___y_2049_);
lean_dec(v___y_2048_);
v___x_2052_ = lean_alloc_ctor(0, 6, 0);
lean_ctor_set(v___x_2052_, 0, v___x_2010_);
lean_ctor_set(v___x_2052_, 1, v___x_2010_);
lean_ctor_set(v___x_2052_, 2, v___x_2050_);
lean_ctor_set(v___x_2052_, 3, v___y_2049_);
lean_ctor_set(v___x_2052_, 4, v___x_2051_);
lean_ctor_set(v___x_2052_, 5, v___x_2010_);
return v___x_2052_;
}
v___jp_2054_:
{
uint8_t v___x_2059_; 
v___x_2059_ = lean_int_dec_lt(v___y_2056_, v___x_2053_);
if (v___x_2059_ == 0)
{
v___y_2029_ = v___y_2055_;
v___y_2030_ = v___y_2056_;
v___y_2031_ = v___y_2057_;
goto v___jp_2028_;
}
else
{
if (v___y_2058_ == 0)
{
v___y_2029_ = v___y_2055_;
v___y_2030_ = v___y_2056_;
v___y_2031_ = v___y_2057_;
goto v___jp_2028_;
}
else
{
lean_object* v___x_2060_; uint8_t v___x_2061_; 
v___x_2060_ = lean_int_add(v___y_2056_, v___y_2055_);
lean_dec(v___y_2055_);
lean_dec(v___y_2056_);
v___x_2061_ = lean_int_dec_le(v___x_2053_, v___x_2060_);
if (v___x_2061_ == 0)
{
lean_object* v___x_2062_; lean_object* v_loss_2063_; lean_object* v___x_2064_; uint8_t v___x_2065_; 
v___x_2062_ = lean_int_neg(v___x_2060_);
lean_dec(v___x_2060_);
v_loss_2063_ = l_Int_toNat(v___x_2062_);
lean_dec(v___x_2062_);
v___x_2064_ = lean_unsigned_to_nat(3000u);
v___x_2065_ = lean_nat_dec_le(v___x_2064_, v_loss_2063_);
if (v___x_2065_ == 0)
{
lean_inc(v_loss_2063_);
v___y_2040_ = v_loss_2063_;
v___y_2041_ = v___y_2057_;
v___y_2042_ = v_loss_2063_;
goto v___jp_2039_;
}
else
{
v___y_2040_ = v_loss_2063_;
v___y_2041_ = v___y_2057_;
v___y_2042_ = v___x_2064_;
goto v___jp_2039_;
}
}
else
{
lean_object* v___x_2066_; lean_object* v___x_2067_; lean_object* v___x_2068_; 
v___x_2066_ = l_Int_toNat(v___x_2060_);
lean_dec(v___x_2060_);
v___x_2067_ = l_Int_toNat(v___y_2057_);
lean_dec(v___y_2057_);
v___x_2068_ = lean_alloc_ctor(0, 6, 0);
lean_ctor_set(v___x_2068_, 0, v___x_2066_);
lean_ctor_set(v___x_2068_, 1, v___x_2010_);
lean_ctor_set(v___x_2068_, 2, v___x_2067_);
lean_ctor_set(v___x_2068_, 3, v___x_2010_);
lean_ctor_set(v___x_2068_, 4, v___x_2010_);
lean_ctor_set(v___x_2068_, 5, v___x_2010_);
return v___x_2068_;
}
}
}
}
v___jp_2069_:
{
uint8_t v___x_2074_; 
v___x_2074_ = lean_int_dec_lt(v___y_2070_, v___x_2053_);
if (v___x_2074_ == 0)
{
v___y_2055_ = v___y_2070_;
v___y_2056_ = v___y_2071_;
v___y_2057_ = v___y_2072_;
v___y_2058_ = v___y_2073_;
goto v___jp_2054_;
}
else
{
uint8_t v___x_2075_; 
v___x_2075_ = lean_int_dec_le(v___x_2053_, v___y_2071_);
if (v___x_2075_ == 0)
{
v___y_2055_ = v___y_2070_;
v___y_2056_ = v___y_2071_;
v___y_2057_ = v___y_2072_;
v___y_2058_ = v___y_2073_;
goto v___jp_2054_;
}
else
{
lean_object* v___x_2076_; uint8_t v___x_2077_; 
v___x_2076_ = lean_int_add(v___y_2071_, v___y_2070_);
lean_dec(v___y_2070_);
lean_dec(v___y_2071_);
v___x_2077_ = lean_int_dec_le(v___x_2053_, v___x_2076_);
if (v___x_2077_ == 0)
{
lean_object* v___x_2078_; lean_object* v_loss_2079_; lean_object* v___x_2080_; uint8_t v___x_2081_; 
v___x_2078_ = lean_int_neg(v___x_2076_);
lean_dec(v___x_2076_);
v_loss_2079_ = l_Int_toNat(v___x_2078_);
lean_dec(v___x_2078_);
v___x_2080_ = lean_unsigned_to_nat(3000u);
v___x_2081_ = lean_nat_dec_le(v___x_2080_, v_loss_2079_);
if (v___x_2081_ == 0)
{
lean_inc(v_loss_2079_);
v___y_2047_ = v___y_2072_;
v___y_2048_ = v_loss_2079_;
v___y_2049_ = v_loss_2079_;
goto v___jp_2046_;
}
else
{
v___y_2047_ = v___y_2072_;
v___y_2048_ = v_loss_2079_;
v___y_2049_ = v___x_2080_;
goto v___jp_2046_;
}
}
else
{
lean_object* v___x_2082_; lean_object* v___x_2083_; lean_object* v___x_2084_; 
v___x_2082_ = l_Int_toNat(v___x_2076_);
lean_dec(v___x_2076_);
v___x_2083_ = l_Int_toNat(v___y_2072_);
lean_dec(v___y_2072_);
v___x_2084_ = lean_alloc_ctor(0, 6, 0);
lean_ctor_set(v___x_2084_, 0, v___x_2010_);
lean_ctor_set(v___x_2084_, 1, v___x_2082_);
lean_ctor_set(v___x_2084_, 2, v___x_2083_);
lean_ctor_set(v___x_2084_, 3, v___x_2010_);
lean_ctor_set(v___x_2084_, 4, v___x_2010_);
lean_ctor_set(v___x_2084_, 5, v___x_2010_);
return v___x_2084_;
}
}
}
}
v___jp_2085_:
{
lean_object* v_l_2089_; lean_object* v_g_2090_; uint8_t v___x_2091_; 
v_l_2089_ = lean_int_add(v_l_2008_, v___y_2088_);
lean_dec(v_l_2008_);
v_g_2090_ = lean_int_sub(v___y_2087_, v___y_2088_);
lean_dec(v___y_2088_);
lean_dec(v___y_2087_);
v___x_2091_ = lean_int_dec_le(v___x_2053_, v___y_2086_);
if (v___x_2091_ == 0)
{
v___y_2070_ = v___y_2086_;
v___y_2071_ = v_l_2089_;
v___y_2072_ = v_g_2090_;
v___y_2073_ = v___x_2091_;
goto v___jp_2069_;
}
else
{
uint8_t v___x_2092_; 
v___x_2092_ = lean_int_dec_le(v___x_2053_, v_l_2089_);
if (v___x_2092_ == 0)
{
v___y_2070_ = v___y_2086_;
v___y_2071_ = v_l_2089_;
v___y_2072_ = v_g_2090_;
v___y_2073_ = v___x_2091_;
goto v___jp_2069_;
}
else
{
lean_object* v___x_2093_; lean_object* v___x_2094_; lean_object* v___x_2095_; lean_object* v___x_2096_; 
v___x_2093_ = l_Int_toNat(v___y_2086_);
lean_dec(v___y_2086_);
v___x_2094_ = l_Int_toNat(v_l_2089_);
lean_dec(v_l_2089_);
v___x_2095_ = l_Int_toNat(v_g_2090_);
lean_dec(v_g_2090_);
v___x_2096_ = lean_alloc_ctor(0, 6, 0);
lean_ctor_set(v___x_2096_, 0, v___x_2093_);
lean_ctor_set(v___x_2096_, 1, v___x_2094_);
lean_ctor_set(v___x_2096_, 2, v___x_2095_);
lean_ctor_set(v___x_2096_, 3, v___x_2010_);
lean_ctor_set(v___x_2096_, 4, v___x_2010_);
lean_ctor_set(v___x_2096_, 5, v___x_2010_);
return v___x_2096_;
}
}
}
v___jp_2097_:
{
lean_object* v_s_2099_; lean_object* v_g_2100_; uint8_t v___x_2101_; 
v_s_2099_ = lean_int_add(v_s_2006_, v___y_2098_);
lean_dec(v_s_2006_);
v_g_2100_ = lean_int_sub(v_g_2009_, v___y_2098_);
lean_dec(v___y_2098_);
lean_dec(v_g_2009_);
v___x_2101_ = lean_int_dec_lt(v_l_2008_, v___x_2053_);
if (v___x_2101_ == 0)
{
v___y_2086_ = v_s_2099_;
v___y_2087_ = v_g_2100_;
v___y_2088_ = v___x_2053_;
goto v___jp_2085_;
}
else
{
lean_object* v___x_2102_; uint8_t v___x_2103_; 
v___x_2102_ = lean_int_neg(v_l_2008_);
v___x_2103_ = lean_int_dec_le(v___x_2102_, v_g_2100_);
if (v___x_2103_ == 0)
{
lean_dec(v___x_2102_);
lean_inc(v_g_2100_);
v___y_2086_ = v_s_2099_;
v___y_2087_ = v_g_2100_;
v___y_2088_ = v_g_2100_;
goto v___jp_2085_;
}
else
{
v___y_2086_ = v_s_2099_;
v___y_2087_ = v_g_2100_;
v___y_2088_ = v___x_2102_;
goto v___jp_2085_;
}
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_tiParts(lean_object* v_wages_2107_, lean_object* v_ded_2108_, lean_object* v_n_2109_){
_start:
{
lean_object* v_sG_2110_; lean_object* v_lG_2111_; lean_object* v_g28_2112_; lean_object* v_lossDed_2113_; lean_object* v___x_2114_; lean_object* v_og_2115_; lean_object* v_ord_2116_; lean_object* v_spare_2117_; lean_object* v_g_2118_; lean_object* v_spare_2119_; lean_object* v___x_2120_; lean_object* v___x_2121_; lean_object* v___x_2122_; 
v_sG_2110_ = lean_ctor_get(v_n_2109_, 0);
v_lG_2111_ = lean_ctor_get(v_n_2109_, 1);
v_g28_2112_ = lean_ctor_get(v_n_2109_, 2);
v_lossDed_2113_ = lean_ctor_get(v_n_2109_, 3);
v___x_2114_ = lean_nat_add(v_wages_2107_, v_sG_2110_);
v_og_2115_ = lean_nat_sub(v___x_2114_, v_lossDed_2113_);
lean_dec(v___x_2114_);
v_ord_2116_ = lean_nat_sub(v_og_2115_, v_ded_2108_);
v_spare_2117_ = lean_nat_sub(v_ded_2108_, v_og_2115_);
lean_dec(v_og_2115_);
v_g_2118_ = lean_nat_sub(v_g28_2112_, v_spare_2117_);
v_spare_2119_ = lean_nat_sub(v_spare_2117_, v_g28_2112_);
lean_dec(v_spare_2117_);
v___x_2120_ = lean_nat_sub(v_lG_2111_, v_spare_2119_);
lean_dec(v_spare_2119_);
v___x_2121_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_2121_, 0, v_g_2118_);
lean_ctor_set(v___x_2121_, 1, v___x_2120_);
v___x_2122_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_2122_, 0, v_ord_2116_);
lean_ctor_set(v___x_2122_, 1, v___x_2121_);
return v___x_2122_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_tiParts___boxed(lean_object* v_wages_2123_, lean_object* v_ded_2124_, lean_object* v_n_2125_){
_start:
{
lean_object* v_res_2126_; 
v_res_2126_ = l_Legal_USTax_Hunt_Basis_tiParts(v_wages_2123_, v_ded_2124_, v_n_2125_);
lean_dec_ref(v_n_2125_);
lean_dec(v_ded_2124_);
lean_dec(v_wages_2123_);
return v_res_2126_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_retTax(lean_object* v_f_2127_, lean_object* v_wages_2128_, lean_object* v_ded_2129_, lean_object* v_n_2130_){
_start:
{
lean_object* v___x_2131_; lean_object* v_snd_2132_; lean_object* v_fst_2133_; lean_object* v_fst_2134_; lean_object* v_snd_2135_; lean_object* v___x_2136_; 
v___x_2131_ = l_Legal_USTax_Hunt_Basis_tiParts(v_wages_2128_, v_ded_2129_, v_n_2130_);
v_snd_2132_ = lean_ctor_get(v___x_2131_, 1);
lean_inc(v_snd_2132_);
v_fst_2133_ = lean_ctor_get(v___x_2131_, 0);
lean_inc(v_fst_2133_);
lean_dec_ref(v___x_2131_);
v_fst_2134_ = lean_ctor_get(v_snd_2132_, 0);
lean_inc(v_fst_2134_);
v_snd_2135_ = lean_ctor_get(v_snd_2132_, 1);
lean_inc(v_snd_2135_);
lean_dec(v_snd_2132_);
v___x_2136_ = l_Legal_USTax_Hunt_Basis_fullTax(v_f_2127_, v_fst_2133_, v_fst_2134_, v_snd_2135_);
lean_dec(v_fst_2134_);
lean_dec(v_fst_2133_);
return v___x_2136_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_retTax___boxed(lean_object* v_f_2137_, lean_object* v_wages_2138_, lean_object* v_ded_2139_, lean_object* v_n_2140_){
_start:
{
lean_object* v_res_2141_; 
v_res_2141_ = l_Legal_USTax_Hunt_Basis_retTax(v_f_2137_, v_wages_2138_, v_ded_2139_, v_n_2140_);
lean_dec_ref(v_n_2140_);
lean_dec(v_ded_2139_);
lean_dec(v_wages_2138_);
return v_res_2141_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_agiOf(lean_object* v_wages_2142_, lean_object* v_n_2143_){
_start:
{
lean_object* v_sG_2144_; lean_object* v_lG_2145_; lean_object* v_g28_2146_; lean_object* v_lossDed_2147_; lean_object* v___x_2148_; lean_object* v___x_2149_; lean_object* v___x_2150_; lean_object* v___x_2151_; 
v_sG_2144_ = lean_ctor_get(v_n_2143_, 0);
v_lG_2145_ = lean_ctor_get(v_n_2143_, 1);
v_g28_2146_ = lean_ctor_get(v_n_2143_, 2);
v_lossDed_2147_ = lean_ctor_get(v_n_2143_, 3);
v___x_2148_ = lean_nat_add(v_wages_2142_, v_sG_2144_);
v___x_2149_ = lean_nat_add(v___x_2148_, v_lG_2145_);
lean_dec(v___x_2148_);
v___x_2150_ = lean_nat_add(v___x_2149_, v_g28_2146_);
lean_dec(v___x_2149_);
v___x_2151_ = lean_nat_sub(v___x_2150_, v_lossDed_2147_);
lean_dec(v___x_2150_);
return v___x_2151_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_agiOf___boxed(lean_object* v_wages_2152_, lean_object* v_n_2153_){
_start:
{
lean_object* v_res_2154_; 
v_res_2154_ = l_Legal_USTax_Hunt_Basis_agiOf(v_wages_2152_, v_n_2153_);
lean_dec_ref(v_n_2153_);
lean_dec(v_wages_2152_);
return v_res_2154_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_stdSingle(void){
_start:
{
lean_object* v___x_2155_; 
v___x_2155_ = lean_unsigned_to_nat(16100u);
return v___x_2155_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_stdAged(void){
_start:
{
lean_object* v___x_2156_; 
v___x_2156_ = lean_unsigned_to_nat(2050u);
return v___x_2156_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_seniorDed(void){
_start:
{
lean_object* v___x_2157_; 
v___x_2157_ = lean_unsigned_to_nat(6000u);
return v___x_2157_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_stdDependent(void){
_start:
{
lean_object* v___x_2158_; 
v___x_2158_ = lean_unsigned_to_nat(1350u);
return v___x_2158_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_giftExcl(void){
_start:
{
lean_object* v___x_2159_; 
v___x_2159_ = lean_unsigned_to_nat(19000u);
return v___x_2159_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_qCap(void){
_start:
{
lean_object* v___x_2160_; 
v___x_2160_ = lean_unsigned_to_nat(15000000u);
return v___x_2160_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_top37(void){
_start:
{
lean_object* v___x_2161_; 
v___x_2161_ = lean_unsigned_to_nat(768700u);
return v___x_2161_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_getRet(lean_object* v_s_2162_, uint8_t v_x_2163_){
_start:
{
switch(v_x_2163_)
{
case 2:
{
lean_object* v_rK_2164_; 
v_rK_2164_ = lean_ctor_get(v_s_2162_, 4);
lean_inc_ref(v_rK_2164_);
return v_rK_2164_;
}
case 3:
{
lean_object* v_rA_2165_; 
v_rA_2165_ = lean_ctor_get(v_s_2162_, 5);
lean_inc_ref(v_rA_2165_);
return v_rA_2165_;
}
case 4:
{
lean_object* v_rP_2166_; 
v_rP_2166_ = lean_ctor_get(v_s_2162_, 6);
lean_inc_ref(v_rP_2166_);
return v_rP_2166_;
}
default: 
{
lean_object* v_rJ_2167_; 
v_rJ_2167_ = lean_ctor_get(v_s_2162_, 3);
lean_inc_ref(v_rJ_2167_);
return v_rJ_2167_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_getRet___boxed(lean_object* v_s_2168_, lean_object* v_x_2169_){
_start:
{
uint8_t v_x_37__boxed_2170_; lean_object* v_res_2171_; 
v_x_37__boxed_2170_ = lean_unbox(v_x_2169_);
v_res_2171_ = l_Legal_USTax_Hunt_Basis_getRet(v_s_2168_, v_x_37__boxed_2170_);
lean_dec_ref(v_s_2168_);
return v_res_2171_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_setRet(lean_object* v_s_2172_, uint8_t v_w_2173_, lean_object* v_r_2174_){
_start:
{
switch(v_w_2173_)
{
case 2:
{
lean_object* v_lots_2175_; lean_object* v_year_2176_; lean_object* v_cur_2177_; uint8_t v_pAlive_2178_; uint8_t v_pFinal_2179_; lean_object* v_rJ_2180_; lean_object* v_rA_2181_; lean_object* v_rP_2182_; lean_object* v_charCash_2183_; lean_object* v_charProp_2184_; lean_object* v_cfChar_2185_; lean_object* v_pledge_2186_; lean_object* v_tax_2187_; lean_object* v___x_2189_; uint8_t v_isShared_2190_; uint8_t v_isSharedCheck_2194_; 
v_lots_2175_ = lean_ctor_get(v_s_2172_, 0);
v_year_2176_ = lean_ctor_get(v_s_2172_, 1);
v_cur_2177_ = lean_ctor_get(v_s_2172_, 2);
v_pAlive_2178_ = lean_ctor_get_uint8(v_s_2172_, sizeof(void*)*12);
v_pFinal_2179_ = lean_ctor_get_uint8(v_s_2172_, sizeof(void*)*12 + 1);
v_rJ_2180_ = lean_ctor_get(v_s_2172_, 3);
v_rA_2181_ = lean_ctor_get(v_s_2172_, 5);
v_rP_2182_ = lean_ctor_get(v_s_2172_, 6);
v_charCash_2183_ = lean_ctor_get(v_s_2172_, 7);
v_charProp_2184_ = lean_ctor_get(v_s_2172_, 8);
v_cfChar_2185_ = lean_ctor_get(v_s_2172_, 9);
v_pledge_2186_ = lean_ctor_get(v_s_2172_, 10);
v_tax_2187_ = lean_ctor_get(v_s_2172_, 11);
v_isSharedCheck_2194_ = !lean_is_exclusive(v_s_2172_);
if (v_isSharedCheck_2194_ == 0)
{
lean_object* v_unused_2195_; 
v_unused_2195_ = lean_ctor_get(v_s_2172_, 4);
lean_dec(v_unused_2195_);
v___x_2189_ = v_s_2172_;
v_isShared_2190_ = v_isSharedCheck_2194_;
goto v_resetjp_2188_;
}
else
{
lean_inc(v_tax_2187_);
lean_inc(v_pledge_2186_);
lean_inc(v_cfChar_2185_);
lean_inc(v_charProp_2184_);
lean_inc(v_charCash_2183_);
lean_inc(v_rP_2182_);
lean_inc(v_rA_2181_);
lean_inc(v_rJ_2180_);
lean_inc(v_cur_2177_);
lean_inc(v_year_2176_);
lean_inc(v_lots_2175_);
lean_dec(v_s_2172_);
v___x_2189_ = lean_box(0);
v_isShared_2190_ = v_isSharedCheck_2194_;
goto v_resetjp_2188_;
}
v_resetjp_2188_:
{
lean_object* v___x_2192_; 
if (v_isShared_2190_ == 0)
{
lean_ctor_set(v___x_2189_, 4, v_r_2174_);
v___x_2192_ = v___x_2189_;
goto v_reusejp_2191_;
}
else
{
lean_object* v_reuseFailAlloc_2193_; 
v_reuseFailAlloc_2193_ = lean_alloc_ctor(0, 12, 2);
lean_ctor_set(v_reuseFailAlloc_2193_, 0, v_lots_2175_);
lean_ctor_set(v_reuseFailAlloc_2193_, 1, v_year_2176_);
lean_ctor_set(v_reuseFailAlloc_2193_, 2, v_cur_2177_);
lean_ctor_set(v_reuseFailAlloc_2193_, 3, v_rJ_2180_);
lean_ctor_set(v_reuseFailAlloc_2193_, 4, v_r_2174_);
lean_ctor_set(v_reuseFailAlloc_2193_, 5, v_rA_2181_);
lean_ctor_set(v_reuseFailAlloc_2193_, 6, v_rP_2182_);
lean_ctor_set(v_reuseFailAlloc_2193_, 7, v_charCash_2183_);
lean_ctor_set(v_reuseFailAlloc_2193_, 8, v_charProp_2184_);
lean_ctor_set(v_reuseFailAlloc_2193_, 9, v_cfChar_2185_);
lean_ctor_set(v_reuseFailAlloc_2193_, 10, v_pledge_2186_);
lean_ctor_set(v_reuseFailAlloc_2193_, 11, v_tax_2187_);
lean_ctor_set_uint8(v_reuseFailAlloc_2193_, sizeof(void*)*12, v_pAlive_2178_);
lean_ctor_set_uint8(v_reuseFailAlloc_2193_, sizeof(void*)*12 + 1, v_pFinal_2179_);
v___x_2192_ = v_reuseFailAlloc_2193_;
goto v_reusejp_2191_;
}
v_reusejp_2191_:
{
return v___x_2192_;
}
}
}
case 3:
{
lean_object* v_lots_2196_; lean_object* v_year_2197_; lean_object* v_cur_2198_; uint8_t v_pAlive_2199_; uint8_t v_pFinal_2200_; lean_object* v_rJ_2201_; lean_object* v_rK_2202_; lean_object* v_rP_2203_; lean_object* v_charCash_2204_; lean_object* v_charProp_2205_; lean_object* v_cfChar_2206_; lean_object* v_pledge_2207_; lean_object* v_tax_2208_; lean_object* v___x_2210_; uint8_t v_isShared_2211_; uint8_t v_isSharedCheck_2215_; 
v_lots_2196_ = lean_ctor_get(v_s_2172_, 0);
v_year_2197_ = lean_ctor_get(v_s_2172_, 1);
v_cur_2198_ = lean_ctor_get(v_s_2172_, 2);
v_pAlive_2199_ = lean_ctor_get_uint8(v_s_2172_, sizeof(void*)*12);
v_pFinal_2200_ = lean_ctor_get_uint8(v_s_2172_, sizeof(void*)*12 + 1);
v_rJ_2201_ = lean_ctor_get(v_s_2172_, 3);
v_rK_2202_ = lean_ctor_get(v_s_2172_, 4);
v_rP_2203_ = lean_ctor_get(v_s_2172_, 6);
v_charCash_2204_ = lean_ctor_get(v_s_2172_, 7);
v_charProp_2205_ = lean_ctor_get(v_s_2172_, 8);
v_cfChar_2206_ = lean_ctor_get(v_s_2172_, 9);
v_pledge_2207_ = lean_ctor_get(v_s_2172_, 10);
v_tax_2208_ = lean_ctor_get(v_s_2172_, 11);
v_isSharedCheck_2215_ = !lean_is_exclusive(v_s_2172_);
if (v_isSharedCheck_2215_ == 0)
{
lean_object* v_unused_2216_; 
v_unused_2216_ = lean_ctor_get(v_s_2172_, 5);
lean_dec(v_unused_2216_);
v___x_2210_ = v_s_2172_;
v_isShared_2211_ = v_isSharedCheck_2215_;
goto v_resetjp_2209_;
}
else
{
lean_inc(v_tax_2208_);
lean_inc(v_pledge_2207_);
lean_inc(v_cfChar_2206_);
lean_inc(v_charProp_2205_);
lean_inc(v_charCash_2204_);
lean_inc(v_rP_2203_);
lean_inc(v_rK_2202_);
lean_inc(v_rJ_2201_);
lean_inc(v_cur_2198_);
lean_inc(v_year_2197_);
lean_inc(v_lots_2196_);
lean_dec(v_s_2172_);
v___x_2210_ = lean_box(0);
v_isShared_2211_ = v_isSharedCheck_2215_;
goto v_resetjp_2209_;
}
v_resetjp_2209_:
{
lean_object* v___x_2213_; 
if (v_isShared_2211_ == 0)
{
lean_ctor_set(v___x_2210_, 5, v_r_2174_);
v___x_2213_ = v___x_2210_;
goto v_reusejp_2212_;
}
else
{
lean_object* v_reuseFailAlloc_2214_; 
v_reuseFailAlloc_2214_ = lean_alloc_ctor(0, 12, 2);
lean_ctor_set(v_reuseFailAlloc_2214_, 0, v_lots_2196_);
lean_ctor_set(v_reuseFailAlloc_2214_, 1, v_year_2197_);
lean_ctor_set(v_reuseFailAlloc_2214_, 2, v_cur_2198_);
lean_ctor_set(v_reuseFailAlloc_2214_, 3, v_rJ_2201_);
lean_ctor_set(v_reuseFailAlloc_2214_, 4, v_rK_2202_);
lean_ctor_set(v_reuseFailAlloc_2214_, 5, v_r_2174_);
lean_ctor_set(v_reuseFailAlloc_2214_, 6, v_rP_2203_);
lean_ctor_set(v_reuseFailAlloc_2214_, 7, v_charCash_2204_);
lean_ctor_set(v_reuseFailAlloc_2214_, 8, v_charProp_2205_);
lean_ctor_set(v_reuseFailAlloc_2214_, 9, v_cfChar_2206_);
lean_ctor_set(v_reuseFailAlloc_2214_, 10, v_pledge_2207_);
lean_ctor_set(v_reuseFailAlloc_2214_, 11, v_tax_2208_);
lean_ctor_set_uint8(v_reuseFailAlloc_2214_, sizeof(void*)*12, v_pAlive_2199_);
lean_ctor_set_uint8(v_reuseFailAlloc_2214_, sizeof(void*)*12 + 1, v_pFinal_2200_);
v___x_2213_ = v_reuseFailAlloc_2214_;
goto v_reusejp_2212_;
}
v_reusejp_2212_:
{
return v___x_2213_;
}
}
}
case 4:
{
lean_object* v_lots_2217_; lean_object* v_year_2218_; lean_object* v_cur_2219_; uint8_t v_pAlive_2220_; uint8_t v_pFinal_2221_; lean_object* v_rJ_2222_; lean_object* v_rK_2223_; lean_object* v_rA_2224_; lean_object* v_charCash_2225_; lean_object* v_charProp_2226_; lean_object* v_cfChar_2227_; lean_object* v_pledge_2228_; lean_object* v_tax_2229_; lean_object* v___x_2231_; uint8_t v_isShared_2232_; uint8_t v_isSharedCheck_2236_; 
v_lots_2217_ = lean_ctor_get(v_s_2172_, 0);
v_year_2218_ = lean_ctor_get(v_s_2172_, 1);
v_cur_2219_ = lean_ctor_get(v_s_2172_, 2);
v_pAlive_2220_ = lean_ctor_get_uint8(v_s_2172_, sizeof(void*)*12);
v_pFinal_2221_ = lean_ctor_get_uint8(v_s_2172_, sizeof(void*)*12 + 1);
v_rJ_2222_ = lean_ctor_get(v_s_2172_, 3);
v_rK_2223_ = lean_ctor_get(v_s_2172_, 4);
v_rA_2224_ = lean_ctor_get(v_s_2172_, 5);
v_charCash_2225_ = lean_ctor_get(v_s_2172_, 7);
v_charProp_2226_ = lean_ctor_get(v_s_2172_, 8);
v_cfChar_2227_ = lean_ctor_get(v_s_2172_, 9);
v_pledge_2228_ = lean_ctor_get(v_s_2172_, 10);
v_tax_2229_ = lean_ctor_get(v_s_2172_, 11);
v_isSharedCheck_2236_ = !lean_is_exclusive(v_s_2172_);
if (v_isSharedCheck_2236_ == 0)
{
lean_object* v_unused_2237_; 
v_unused_2237_ = lean_ctor_get(v_s_2172_, 6);
lean_dec(v_unused_2237_);
v___x_2231_ = v_s_2172_;
v_isShared_2232_ = v_isSharedCheck_2236_;
goto v_resetjp_2230_;
}
else
{
lean_inc(v_tax_2229_);
lean_inc(v_pledge_2228_);
lean_inc(v_cfChar_2227_);
lean_inc(v_charProp_2226_);
lean_inc(v_charCash_2225_);
lean_inc(v_rA_2224_);
lean_inc(v_rK_2223_);
lean_inc(v_rJ_2222_);
lean_inc(v_cur_2219_);
lean_inc(v_year_2218_);
lean_inc(v_lots_2217_);
lean_dec(v_s_2172_);
v___x_2231_ = lean_box(0);
v_isShared_2232_ = v_isSharedCheck_2236_;
goto v_resetjp_2230_;
}
v_resetjp_2230_:
{
lean_object* v___x_2234_; 
if (v_isShared_2232_ == 0)
{
lean_ctor_set(v___x_2231_, 6, v_r_2174_);
v___x_2234_ = v___x_2231_;
goto v_reusejp_2233_;
}
else
{
lean_object* v_reuseFailAlloc_2235_; 
v_reuseFailAlloc_2235_ = lean_alloc_ctor(0, 12, 2);
lean_ctor_set(v_reuseFailAlloc_2235_, 0, v_lots_2217_);
lean_ctor_set(v_reuseFailAlloc_2235_, 1, v_year_2218_);
lean_ctor_set(v_reuseFailAlloc_2235_, 2, v_cur_2219_);
lean_ctor_set(v_reuseFailAlloc_2235_, 3, v_rJ_2222_);
lean_ctor_set(v_reuseFailAlloc_2235_, 4, v_rK_2223_);
lean_ctor_set(v_reuseFailAlloc_2235_, 5, v_rA_2224_);
lean_ctor_set(v_reuseFailAlloc_2235_, 6, v_r_2174_);
lean_ctor_set(v_reuseFailAlloc_2235_, 7, v_charCash_2225_);
lean_ctor_set(v_reuseFailAlloc_2235_, 8, v_charProp_2226_);
lean_ctor_set(v_reuseFailAlloc_2235_, 9, v_cfChar_2227_);
lean_ctor_set(v_reuseFailAlloc_2235_, 10, v_pledge_2228_);
lean_ctor_set(v_reuseFailAlloc_2235_, 11, v_tax_2229_);
lean_ctor_set_uint8(v_reuseFailAlloc_2235_, sizeof(void*)*12, v_pAlive_2220_);
lean_ctor_set_uint8(v_reuseFailAlloc_2235_, sizeof(void*)*12 + 1, v_pFinal_2221_);
v___x_2234_ = v_reuseFailAlloc_2235_;
goto v_reusejp_2233_;
}
v_reusejp_2233_:
{
return v___x_2234_;
}
}
}
default: 
{
lean_object* v_lots_2238_; lean_object* v_year_2239_; lean_object* v_cur_2240_; uint8_t v_pAlive_2241_; uint8_t v_pFinal_2242_; lean_object* v_rK_2243_; lean_object* v_rA_2244_; lean_object* v_rP_2245_; lean_object* v_charCash_2246_; lean_object* v_charProp_2247_; lean_object* v_cfChar_2248_; lean_object* v_pledge_2249_; lean_object* v_tax_2250_; lean_object* v___x_2252_; uint8_t v_isShared_2253_; uint8_t v_isSharedCheck_2257_; 
v_lots_2238_ = lean_ctor_get(v_s_2172_, 0);
v_year_2239_ = lean_ctor_get(v_s_2172_, 1);
v_cur_2240_ = lean_ctor_get(v_s_2172_, 2);
v_pAlive_2241_ = lean_ctor_get_uint8(v_s_2172_, sizeof(void*)*12);
v_pFinal_2242_ = lean_ctor_get_uint8(v_s_2172_, sizeof(void*)*12 + 1);
v_rK_2243_ = lean_ctor_get(v_s_2172_, 4);
v_rA_2244_ = lean_ctor_get(v_s_2172_, 5);
v_rP_2245_ = lean_ctor_get(v_s_2172_, 6);
v_charCash_2246_ = lean_ctor_get(v_s_2172_, 7);
v_charProp_2247_ = lean_ctor_get(v_s_2172_, 8);
v_cfChar_2248_ = lean_ctor_get(v_s_2172_, 9);
v_pledge_2249_ = lean_ctor_get(v_s_2172_, 10);
v_tax_2250_ = lean_ctor_get(v_s_2172_, 11);
v_isSharedCheck_2257_ = !lean_is_exclusive(v_s_2172_);
if (v_isSharedCheck_2257_ == 0)
{
lean_object* v_unused_2258_; 
v_unused_2258_ = lean_ctor_get(v_s_2172_, 3);
lean_dec(v_unused_2258_);
v___x_2252_ = v_s_2172_;
v_isShared_2253_ = v_isSharedCheck_2257_;
goto v_resetjp_2251_;
}
else
{
lean_inc(v_tax_2250_);
lean_inc(v_pledge_2249_);
lean_inc(v_cfChar_2248_);
lean_inc(v_charProp_2247_);
lean_inc(v_charCash_2246_);
lean_inc(v_rP_2245_);
lean_inc(v_rA_2244_);
lean_inc(v_rK_2243_);
lean_inc(v_cur_2240_);
lean_inc(v_year_2239_);
lean_inc(v_lots_2238_);
lean_dec(v_s_2172_);
v___x_2252_ = lean_box(0);
v_isShared_2253_ = v_isSharedCheck_2257_;
goto v_resetjp_2251_;
}
v_resetjp_2251_:
{
lean_object* v___x_2255_; 
if (v_isShared_2253_ == 0)
{
lean_ctor_set(v___x_2252_, 3, v_r_2174_);
v___x_2255_ = v___x_2252_;
goto v_reusejp_2254_;
}
else
{
lean_object* v_reuseFailAlloc_2256_; 
v_reuseFailAlloc_2256_ = lean_alloc_ctor(0, 12, 2);
lean_ctor_set(v_reuseFailAlloc_2256_, 0, v_lots_2238_);
lean_ctor_set(v_reuseFailAlloc_2256_, 1, v_year_2239_);
lean_ctor_set(v_reuseFailAlloc_2256_, 2, v_cur_2240_);
lean_ctor_set(v_reuseFailAlloc_2256_, 3, v_r_2174_);
lean_ctor_set(v_reuseFailAlloc_2256_, 4, v_rK_2243_);
lean_ctor_set(v_reuseFailAlloc_2256_, 5, v_rA_2244_);
lean_ctor_set(v_reuseFailAlloc_2256_, 6, v_rP_2245_);
lean_ctor_set(v_reuseFailAlloc_2256_, 7, v_charCash_2246_);
lean_ctor_set(v_reuseFailAlloc_2256_, 8, v_charProp_2247_);
lean_ctor_set(v_reuseFailAlloc_2256_, 9, v_cfChar_2248_);
lean_ctor_set(v_reuseFailAlloc_2256_, 10, v_pledge_2249_);
lean_ctor_set(v_reuseFailAlloc_2256_, 11, v_tax_2250_);
lean_ctor_set_uint8(v_reuseFailAlloc_2256_, sizeof(void*)*12, v_pAlive_2241_);
lean_ctor_set_uint8(v_reuseFailAlloc_2256_, sizeof(void*)*12 + 1, v_pFinal_2242_);
v___x_2255_ = v_reuseFailAlloc_2256_;
goto v_reusejp_2254_;
}
v_reusejp_2254_:
{
return v___x_2255_;
}
}
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_setRet___boxed(lean_object* v_s_2259_, lean_object* v_w_2260_, lean_object* v_r_2261_){
_start:
{
uint8_t v_w_boxed_2262_; lean_object* v_res_2263_; 
v_w_boxed_2262_ = lean_unbox(v_w_2260_);
v_res_2263_ = l_Legal_USTax_Hunt_Basis_setRet(v_s_2259_, v_w_boxed_2262_, v_r_2261_);
return v_res_2263_;
}
}
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_alive(lean_object* v_s_2264_, uint8_t v_w_2265_){
_start:
{
uint8_t v___x_2266_; uint8_t v___x_2267_; 
v___x_2266_ = 4;
v___x_2267_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_w_2265_, v___x_2266_);
if (v___x_2267_ == 0)
{
uint8_t v___x_2268_; 
v___x_2268_ = 1;
return v___x_2268_;
}
else
{
uint8_t v_pAlive_2269_; 
v_pAlive_2269_ = lean_ctor_get_uint8(v_s_2264_, sizeof(void*)*12);
return v_pAlive_2269_;
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_alive___boxed(lean_object* v_s_2270_, lean_object* v_w_2271_){
_start:
{
uint8_t v_w_boxed_2272_; uint8_t v_res_2273_; lean_object* v_r_2274_; 
v_w_boxed_2272_ = lean_unbox(v_w_2271_);
v_res_2273_ = l_Legal_USTax_Hunt_Basis_alive(v_s_2270_, v_w_boxed_2272_);
lean_dec_ref(v_s_2270_);
v_r_2274_ = lean_box(v_res_2273_);
return v_r_2274_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_addGain(lean_object* v_r_2275_, uint8_t v_long_2276_, lean_object* v_x_2277_){
_start:
{
if (v_long_2276_ == 0)
{
lean_object* v_st_2278_; lean_object* v_lt_2279_; lean_object* v_g28_2280_; lean_object* v_cfS_2281_; lean_object* v_cfL_2282_; lean_object* v_00x121_2283_; lean_object* v_xQ_2284_; lean_object* v___x_2286_; uint8_t v_isShared_2287_; uint8_t v_isSharedCheck_2292_; 
v_st_2278_ = lean_ctor_get(v_r_2275_, 0);
v_lt_2279_ = lean_ctor_get(v_r_2275_, 1);
v_g28_2280_ = lean_ctor_get(v_r_2275_, 2);
v_cfS_2281_ = lean_ctor_get(v_r_2275_, 3);
v_cfL_2282_ = lean_ctor_get(v_r_2275_, 4);
v_00x121_2283_ = lean_ctor_get(v_r_2275_, 5);
v_xQ_2284_ = lean_ctor_get(v_r_2275_, 6);
v_isSharedCheck_2292_ = !lean_is_exclusive(v_r_2275_);
if (v_isSharedCheck_2292_ == 0)
{
v___x_2286_ = v_r_2275_;
v_isShared_2287_ = v_isSharedCheck_2292_;
goto v_resetjp_2285_;
}
else
{
lean_inc(v_xQ_2284_);
lean_inc(v_00x121_2283_);
lean_inc(v_cfL_2282_);
lean_inc(v_cfS_2281_);
lean_inc(v_g28_2280_);
lean_inc(v_lt_2279_);
lean_inc(v_st_2278_);
lean_dec(v_r_2275_);
v___x_2286_ = lean_box(0);
v_isShared_2287_ = v_isSharedCheck_2292_;
goto v_resetjp_2285_;
}
v_resetjp_2285_:
{
lean_object* v___x_2288_; lean_object* v___x_2290_; 
v___x_2288_ = lean_int_add(v_st_2278_, v_x_2277_);
lean_dec(v_st_2278_);
if (v_isShared_2287_ == 0)
{
lean_ctor_set(v___x_2286_, 0, v___x_2288_);
v___x_2290_ = v___x_2286_;
goto v_reusejp_2289_;
}
else
{
lean_object* v_reuseFailAlloc_2291_; 
v_reuseFailAlloc_2291_ = lean_alloc_ctor(0, 7, 0);
lean_ctor_set(v_reuseFailAlloc_2291_, 0, v___x_2288_);
lean_ctor_set(v_reuseFailAlloc_2291_, 1, v_lt_2279_);
lean_ctor_set(v_reuseFailAlloc_2291_, 2, v_g28_2280_);
lean_ctor_set(v_reuseFailAlloc_2291_, 3, v_cfS_2281_);
lean_ctor_set(v_reuseFailAlloc_2291_, 4, v_cfL_2282_);
lean_ctor_set(v_reuseFailAlloc_2291_, 5, v_00x121_2283_);
lean_ctor_set(v_reuseFailAlloc_2291_, 6, v_xQ_2284_);
v___x_2290_ = v_reuseFailAlloc_2291_;
goto v_reusejp_2289_;
}
v_reusejp_2289_:
{
return v___x_2290_;
}
}
}
else
{
lean_object* v_st_2293_; lean_object* v_lt_2294_; lean_object* v_g28_2295_; lean_object* v_cfS_2296_; lean_object* v_cfL_2297_; lean_object* v_00x121_2298_; lean_object* v_xQ_2299_; lean_object* v___x_2301_; uint8_t v_isShared_2302_; uint8_t v_isSharedCheck_2307_; 
v_st_2293_ = lean_ctor_get(v_r_2275_, 0);
v_lt_2294_ = lean_ctor_get(v_r_2275_, 1);
v_g28_2295_ = lean_ctor_get(v_r_2275_, 2);
v_cfS_2296_ = lean_ctor_get(v_r_2275_, 3);
v_cfL_2297_ = lean_ctor_get(v_r_2275_, 4);
v_00x121_2298_ = lean_ctor_get(v_r_2275_, 5);
v_xQ_2299_ = lean_ctor_get(v_r_2275_, 6);
v_isSharedCheck_2307_ = !lean_is_exclusive(v_r_2275_);
if (v_isSharedCheck_2307_ == 0)
{
v___x_2301_ = v_r_2275_;
v_isShared_2302_ = v_isSharedCheck_2307_;
goto v_resetjp_2300_;
}
else
{
lean_inc(v_xQ_2299_);
lean_inc(v_00x121_2298_);
lean_inc(v_cfL_2297_);
lean_inc(v_cfS_2296_);
lean_inc(v_g28_2295_);
lean_inc(v_lt_2294_);
lean_inc(v_st_2293_);
lean_dec(v_r_2275_);
v___x_2301_ = lean_box(0);
v_isShared_2302_ = v_isSharedCheck_2307_;
goto v_resetjp_2300_;
}
v_resetjp_2300_:
{
lean_object* v___x_2303_; lean_object* v___x_2305_; 
v___x_2303_ = lean_int_add(v_lt_2294_, v_x_2277_);
lean_dec(v_lt_2294_);
if (v_isShared_2302_ == 0)
{
lean_ctor_set(v___x_2301_, 1, v___x_2303_);
v___x_2305_ = v___x_2301_;
goto v_reusejp_2304_;
}
else
{
lean_object* v_reuseFailAlloc_2306_; 
v_reuseFailAlloc_2306_ = lean_alloc_ctor(0, 7, 0);
lean_ctor_set(v_reuseFailAlloc_2306_, 0, v_st_2293_);
lean_ctor_set(v_reuseFailAlloc_2306_, 1, v___x_2303_);
lean_ctor_set(v_reuseFailAlloc_2306_, 2, v_g28_2295_);
lean_ctor_set(v_reuseFailAlloc_2306_, 3, v_cfS_2296_);
lean_ctor_set(v_reuseFailAlloc_2306_, 4, v_cfL_2297_);
lean_ctor_set(v_reuseFailAlloc_2306_, 5, v_00x121_2298_);
lean_ctor_set(v_reuseFailAlloc_2306_, 6, v_xQ_2299_);
v___x_2305_ = v_reuseFailAlloc_2306_;
goto v_reusejp_2304_;
}
v_reusejp_2304_:
{
return v___x_2305_;
}
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_addGain___boxed(lean_object* v_r_2308_, lean_object* v_long_2309_, lean_object* v_x_2310_){
_start:
{
uint8_t v_long_boxed_2311_; lean_object* v_res_2312_; 
v_long_boxed_2311_ = lean_unbox(v_long_2309_);
v_res_2312_ = l_Legal_USTax_Hunt_Basis_addGain(v_r_2308_, v_long_boxed_2311_, v_x_2310_);
lean_dec(v_x_2310_);
return v_res_2312_;
}
}
LEAN_EXPORT uint8_t l_List_elem___at___00Legal_USTax_Hunt_Basis_limit121_spec__0(uint8_t v_a_2313_, lean_object* v_x_2314_){
_start:
{
if (lean_obj_tag(v_x_2314_) == 0)
{
uint8_t v___x_2315_; 
v___x_2315_ = 0;
return v___x_2315_;
}
else
{
lean_object* v_head_2316_; lean_object* v_tail_2317_; uint8_t v___x_2318_; uint8_t v___x_2319_; 
v_head_2316_ = lean_ctor_get(v_x_2314_, 0);
v_tail_2317_ = lean_ctor_get(v_x_2314_, 1);
v___x_2318_ = lean_unbox(v_head_2316_);
v___x_2319_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_a_2313_, v___x_2318_);
if (v___x_2319_ == 0)
{
v_x_2314_ = v_tail_2317_;
goto _start;
}
else
{
return v___x_2319_;
}
}
}
}
LEAN_EXPORT lean_object* l_List_elem___at___00Legal_USTax_Hunt_Basis_limit121_spec__0___boxed(lean_object* v_a_2321_, lean_object* v_x_2322_){
_start:
{
uint8_t v_a_boxed_2323_; uint8_t v_res_2324_; lean_object* v_r_2325_; 
v_a_boxed_2323_ = lean_unbox(v_a_2321_);
v_res_2324_ = l_List_elem___at___00Legal_USTax_Hunt_Basis_limit121_spec__0(v_a_boxed_2323_, v_x_2322_);
lean_dec(v_x_2322_);
v_r_2325_ = lean_box(v_res_2324_);
return v_r_2325_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_limit121(lean_object* v_cfg_2326_, lean_object* v_l_2327_){
_start:
{
uint8_t v_owner_2328_; lean_object* v_owned_2329_; lean_object* v___y_2331_; lean_object* v___x_2342_; uint8_t v___x_2343_; 
v_owner_2328_ = lean_ctor_get_uint8(v_l_2327_, sizeof(void*)*8 + 1);
v_owned_2329_ = lean_ctor_get(v_l_2327_, 4);
v___x_2342_ = lean_unsigned_to_nat(2u);
v___x_2343_ = lean_nat_dec_lt(v_owned_2329_, v___x_2342_);
if (v___x_2343_ == 0)
{
switch(v_owner_2328_)
{
case 0:
{
goto v___jp_2335_;
}
case 1:
{
goto v___jp_2335_;
}
default: 
{
lean_object* v_users_2344_; uint8_t v___x_2345_; 
v_users_2344_ = lean_ctor_get(v_cfg_2326_, 5);
v___x_2345_ = l_List_elem___at___00Legal_USTax_Hunt_Basis_limit121_spec__0(v_owner_2328_, v_users_2344_);
if (v___x_2345_ == 0)
{
lean_object* v___x_2346_; 
v___x_2346_ = lean_unsigned_to_nat(0u);
return v___x_2346_;
}
else
{
lean_object* v___x_2347_; 
v___x_2347_ = lean_unsigned_to_nat(250000u);
return v___x_2347_;
}
}
}
}
else
{
lean_object* v___x_2348_; 
v___x_2348_ = lean_unsigned_to_nat(0u);
return v___x_2348_;
}
v___jp_2330_:
{
uint8_t v___x_2332_; 
v___x_2332_ = l_List_elem___at___00Legal_USTax_Hunt_Basis_limit121_spec__0(v_owner_2328_, v___y_2331_);
if (v___x_2332_ == 0)
{
lean_object* v___x_2333_; 
v___x_2333_ = lean_unsigned_to_nat(0u);
return v___x_2333_;
}
else
{
lean_object* v___x_2334_; 
v___x_2334_ = lean_unsigned_to_nat(250000u);
return v___x_2334_;
}
}
v___jp_2335_:
{
lean_object* v_users_2336_; uint8_t v___x_2337_; uint8_t v___x_2338_; 
v_users_2336_ = lean_ctor_get(v_cfg_2326_, 5);
v___x_2337_ = 0;
v___x_2338_ = l_List_elem___at___00Legal_USTax_Hunt_Basis_limit121_spec__0(v___x_2337_, v_users_2336_);
if (v___x_2338_ == 0)
{
v___y_2331_ = v_users_2336_;
goto v___jp_2330_;
}
else
{
uint8_t v___x_2339_; uint8_t v___x_2340_; 
v___x_2339_ = 1;
v___x_2340_ = l_List_elem___at___00Legal_USTax_Hunt_Basis_limit121_spec__0(v___x_2339_, v_users_2336_);
if (v___x_2340_ == 0)
{
v___y_2331_ = v_users_2336_;
goto v___jp_2330_;
}
else
{
lean_object* v___x_2341_; 
v___x_2341_ = lean_unsigned_to_nat(500000u);
return v___x_2341_;
}
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_limit121___boxed(lean_object* v_cfg_2349_, lean_object* v_l_2350_){
_start:
{
lean_object* v_res_2351_; 
v_res_2351_ = l_Legal_USTax_Hunt_Basis_limit121(v_cfg_2349_, v_l_2350_);
lean_dec_ref(v_l_2350_);
lean_dec_ref(v_cfg_2349_);
return v_res_2351_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_recognize(lean_object* v_cfg_2352_, lean_object* v_s_2353_, lean_object* v_l_2354_, uint8_t v_lossAllowed_2355_){
_start:
{
uint8_t v_kind_2356_; uint8_t v_owner_2357_; lean_object* v_fmv_2358_; lean_object* v_basis_2359_; lean_object* v_lossBasis_2360_; lean_object* v_held_2361_; lean_object* v_shield_2362_; uint8_t v_inherited_2363_; lean_object* v___y_2365_; lean_object* v___y_2366_; lean_object* v___y_2367_; lean_object* v___y_2368_; lean_object* v___y_2369_; lean_object* v___y_2370_; lean_object* v___y_2371_; lean_object* v___y_2372_; lean_object* v___y_2373_; lean_object* v___y_2374_; lean_object* v___y_2375_; lean_object* v___y_2389_; lean_object* v___y_2390_; lean_object* v___y_2391_; lean_object* v___y_2392_; lean_object* v___y_2393_; lean_object* v___y_2394_; lean_object* v___y_2395_; lean_object* v___y_2396_; lean_object* v___y_2397_; lean_object* v___y_2398_; lean_object* v___y_2399_; lean_object* v___y_2400_; uint8_t v___y_2404_; lean_object* v___y_2405_; lean_object* v___y_2406_; lean_object* v___y_2407_; lean_object* v___y_2424_; uint8_t v___y_2425_; lean_object* v___y_2426_; lean_object* v___y_2427_; lean_object* v___y_2428_; lean_object* v___y_2429_; lean_object* v___y_2430_; lean_object* v___y_2431_; lean_object* v___y_2432_; lean_object* v___y_2433_; lean_object* v___y_2443_; uint8_t v___y_2444_; lean_object* v___y_2445_; lean_object* v___y_2446_; lean_object* v___y_2447_; lean_object* v___y_2448_; lean_object* v___y_2449_; lean_object* v___y_2450_; lean_object* v___y_2451_; lean_object* v___y_2452_; lean_object* v___y_2453_; lean_object* v___y_2457_; uint8_t v___y_2458_; lean_object* v___y_2459_; lean_object* v___y_2460_; uint8_t v___y_2487_; lean_object* v___x_2507_; uint8_t v___x_2508_; 
v_kind_2356_ = lean_ctor_get_uint8(v_l_2354_, sizeof(void*)*8);
v_owner_2357_ = lean_ctor_get_uint8(v_l_2354_, sizeof(void*)*8 + 1);
v_fmv_2358_ = lean_ctor_get(v_l_2354_, 0);
v_basis_2359_ = lean_ctor_get(v_l_2354_, 1);
v_lossBasis_2360_ = lean_ctor_get(v_l_2354_, 2);
v_held_2361_ = lean_ctor_get(v_l_2354_, 3);
v_shield_2362_ = lean_ctor_get(v_l_2354_, 5);
v_inherited_2363_ = lean_ctor_get_uint8(v_l_2354_, sizeof(void*)*8 + 2);
v___x_2507_ = lean_unsigned_to_nat(1u);
v___x_2508_ = lean_nat_dec_le(v___x_2507_, v_held_2361_);
if (v___x_2508_ == 0)
{
v___y_2487_ = v_inherited_2363_;
goto v___jp_2486_;
}
else
{
v___y_2487_ = v___x_2508_;
goto v___jp_2486_;
}
v___jp_2364_:
{
lean_object* v___x_2376_; lean_object* v___x_2377_; lean_object* v_ex_2378_; lean_object* v___x_2379_; lean_object* v___x_2380_; lean_object* v___x_2381_; lean_object* v___x_2382_; lean_object* v___x_2383_; lean_object* v___x_2384_; lean_object* v_r_2385_; lean_object* v___x_2386_; lean_object* v___x_2387_; 
v___x_2376_ = lean_nat_mul(v___y_2375_, v___y_2371_);
v___x_2377_ = lean_unsigned_to_nat(100u);
v_ex_2378_ = lean_nat_div(v___x_2376_, v___x_2377_);
lean_dec(v___x_2376_);
v___x_2379_ = lean_nat_sub(v___y_2373_, v___y_2375_);
lean_dec(v___y_2373_);
v___x_2380_ = lean_nat_to_int(v___x_2379_);
v___x_2381_ = lean_int_add(v___y_2365_, v___x_2380_);
lean_dec(v___x_2380_);
lean_dec(v___y_2365_);
v___x_2382_ = lean_nat_sub(v___y_2375_, v_ex_2378_);
lean_dec(v_ex_2378_);
v___x_2383_ = lean_nat_add(v___y_2370_, v___x_2382_);
lean_dec(v___x_2382_);
lean_dec(v___y_2370_);
v___x_2384_ = lean_nat_add(v___y_2366_, v___y_2375_);
lean_dec(v___y_2375_);
lean_dec(v___y_2366_);
v_r_2385_ = lean_alloc_ctor(0, 7, 0);
lean_ctor_set(v_r_2385_, 0, v___y_2372_);
lean_ctor_set(v_r_2385_, 1, v___x_2381_);
lean_ctor_set(v_r_2385_, 2, v___x_2383_);
lean_ctor_set(v_r_2385_, 3, v___y_2369_);
lean_ctor_set(v_r_2385_, 4, v___y_2374_);
lean_ctor_set(v_r_2385_, 5, v___y_2368_);
lean_ctor_set(v_r_2385_, 6, v___x_2384_);
v___x_2386_ = l_Legal_USTax_Hunt_Basis_setRet(v_s_2353_, v_owner_2357_, v_r_2385_);
v___x_2387_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_2387_, 0, v___x_2386_);
lean_ctor_set(v___x_2387_, 1, v___y_2367_);
return v___x_2387_;
}
v___jp_2388_:
{
lean_object* v___x_2401_; uint8_t v___x_2402_; 
v___x_2401_ = lean_nat_sub(v___y_2394_, v___y_2400_);
lean_dec(v___y_2400_);
lean_dec(v___y_2394_);
v___x_2402_ = lean_nat_dec_le(v___y_2398_, v___x_2401_);
if (v___x_2402_ == 0)
{
v___y_2365_ = v___y_2389_;
v___y_2366_ = v___y_2390_;
v___y_2367_ = v___y_2391_;
v___y_2368_ = v___y_2393_;
v___y_2369_ = v___y_2392_;
v___y_2370_ = v___y_2395_;
v___y_2371_ = v___y_2396_;
v___y_2372_ = v___y_2397_;
v___y_2373_ = v___y_2398_;
v___y_2374_ = v___y_2399_;
v___y_2375_ = v___x_2401_;
goto v___jp_2364_;
}
else
{
lean_dec(v___x_2401_);
lean_inc(v___y_2398_);
v___y_2365_ = v___y_2389_;
v___y_2366_ = v___y_2390_;
v___y_2367_ = v___y_2391_;
v___y_2368_ = v___y_2393_;
v___y_2369_ = v___y_2392_;
v___y_2370_ = v___y_2395_;
v___y_2371_ = v___y_2396_;
v___y_2372_ = v___y_2397_;
v___y_2373_ = v___y_2398_;
v___y_2374_ = v___y_2399_;
v___y_2375_ = v___y_2398_;
goto v___jp_2364_;
}
}
v___jp_2403_:
{
lean_object* v___x_2408_; uint8_t v___x_2409_; 
v___x_2408_ = lean_unsigned_to_nat(0u);
v___x_2409_ = lean_nat_dec_eq(v___y_2407_, v___x_2408_);
if (v___x_2409_ == 0)
{
lean_object* v_st_2410_; lean_object* v_lt_2411_; lean_object* v_g28_2412_; lean_object* v_cfS_2413_; lean_object* v_cfL_2414_; lean_object* v_00x121_2415_; lean_object* v_xQ_2416_; lean_object* v___x_2417_; uint8_t v___x_2418_; 
v_st_2410_ = lean_ctor_get(v___y_2405_, 0);
lean_inc(v_st_2410_);
v_lt_2411_ = lean_ctor_get(v___y_2405_, 1);
lean_inc(v_lt_2411_);
v_g28_2412_ = lean_ctor_get(v___y_2405_, 2);
lean_inc(v_g28_2412_);
v_cfS_2413_ = lean_ctor_get(v___y_2405_, 3);
lean_inc(v_cfS_2413_);
v_cfL_2414_ = lean_ctor_get(v___y_2405_, 4);
lean_inc(v_cfL_2414_);
v_00x121_2415_ = lean_ctor_get(v___y_2405_, 5);
lean_inc(v_00x121_2415_);
v_xQ_2416_ = lean_ctor_get(v___y_2405_, 6);
lean_inc(v_xQ_2416_);
lean_dec_ref(v___y_2405_);
v___x_2417_ = lean_unsigned_to_nat(15000000u);
v___x_2418_ = lean_nat_dec_le(v___x_2417_, v_xQ_2416_);
if (v___x_2418_ == 0)
{
lean_inc(v_xQ_2416_);
v___y_2389_ = v_lt_2411_;
v___y_2390_ = v_xQ_2416_;
v___y_2391_ = v___x_2408_;
v___y_2392_ = v_cfS_2413_;
v___y_2393_ = v_00x121_2415_;
v___y_2394_ = v___x_2417_;
v___y_2395_ = v_g28_2412_;
v___y_2396_ = v___y_2407_;
v___y_2397_ = v_st_2410_;
v___y_2398_ = v___y_2406_;
v___y_2399_ = v_cfL_2414_;
v___y_2400_ = v_xQ_2416_;
goto v___jp_2388_;
}
else
{
v___y_2389_ = v_lt_2411_;
v___y_2390_ = v_xQ_2416_;
v___y_2391_ = v___x_2408_;
v___y_2392_ = v_cfS_2413_;
v___y_2393_ = v_00x121_2415_;
v___y_2394_ = v___x_2417_;
v___y_2395_ = v_g28_2412_;
v___y_2396_ = v___y_2407_;
v___y_2397_ = v_st_2410_;
v___y_2398_ = v___y_2406_;
v___y_2399_ = v_cfL_2414_;
v___y_2400_ = v___x_2417_;
goto v___jp_2388_;
}
}
else
{
lean_object* v___x_2419_; lean_object* v___x_2420_; lean_object* v___x_2421_; lean_object* v___x_2422_; 
v___x_2419_ = lean_nat_to_int(v___y_2406_);
v___x_2420_ = l_Legal_USTax_Hunt_Basis_addGain(v___y_2405_, v___y_2404_, v___x_2419_);
lean_dec(v___x_2419_);
v___x_2421_ = l_Legal_USTax_Hunt_Basis_setRet(v_s_2353_, v_owner_2357_, v___x_2420_);
v___x_2422_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_2422_, 0, v___x_2421_);
lean_ctor_set(v___x_2422_, 1, v___x_2408_);
return v___x_2422_;
}
}
v___jp_2423_:
{
lean_object* v___x_2434_; lean_object* v___x_2435_; lean_object* v___x_2436_; lean_object* v___x_2437_; lean_object* v___x_2438_; lean_object* v___x_2439_; lean_object* v___x_2440_; lean_object* v___x_2441_; 
v___x_2434_ = lean_nat_add(v___y_2432_, v___y_2433_);
lean_dec(v___y_2432_);
v___x_2435_ = lean_alloc_ctor(0, 7, 0);
lean_ctor_set(v___x_2435_, 0, v___y_2424_);
lean_ctor_set(v___x_2435_, 1, v___y_2427_);
lean_ctor_set(v___x_2435_, 2, v___y_2426_);
lean_ctor_set(v___x_2435_, 3, v___y_2429_);
lean_ctor_set(v___x_2435_, 4, v___y_2428_);
lean_ctor_set(v___x_2435_, 5, v___x_2434_);
lean_ctor_set(v___x_2435_, 6, v___y_2430_);
v___x_2436_ = lean_nat_sub(v___y_2431_, v___y_2433_);
lean_dec(v___y_2433_);
lean_dec(v___y_2431_);
v___x_2437_ = lean_nat_to_int(v___x_2436_);
v___x_2438_ = l_Legal_USTax_Hunt_Basis_addGain(v___x_2435_, v___y_2425_, v___x_2437_);
lean_dec(v___x_2437_);
v___x_2439_ = l_Legal_USTax_Hunt_Basis_setRet(v_s_2353_, v_owner_2357_, v___x_2438_);
v___x_2440_ = lean_unsigned_to_nat(0u);
v___x_2441_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_2441_, 0, v___x_2439_);
lean_ctor_set(v___x_2441_, 1, v___x_2440_);
return v___x_2441_;
}
v___jp_2442_:
{
lean_object* v___x_2454_; uint8_t v___x_2455_; 
v___x_2454_ = lean_nat_sub(v___y_2449_, v___y_2453_);
lean_dec(v___y_2453_);
lean_dec(v___y_2449_);
v___x_2455_ = lean_nat_dec_le(v___y_2452_, v___x_2454_);
if (v___x_2455_ == 0)
{
v___y_2424_ = v___y_2443_;
v___y_2425_ = v___y_2444_;
v___y_2426_ = v___y_2446_;
v___y_2427_ = v___y_2445_;
v___y_2428_ = v___y_2447_;
v___y_2429_ = v___y_2448_;
v___y_2430_ = v___y_2450_;
v___y_2431_ = v___y_2452_;
v___y_2432_ = v___y_2451_;
v___y_2433_ = v___x_2454_;
goto v___jp_2423_;
}
else
{
lean_dec(v___x_2454_);
lean_inc(v___y_2452_);
v___y_2424_ = v___y_2443_;
v___y_2425_ = v___y_2444_;
v___y_2426_ = v___y_2446_;
v___y_2427_ = v___y_2445_;
v___y_2428_ = v___y_2447_;
v___y_2429_ = v___y_2448_;
v___y_2430_ = v___y_2450_;
v___y_2431_ = v___y_2452_;
v___y_2432_ = v___y_2451_;
v___y_2433_ = v___y_2452_;
goto v___jp_2423_;
}
}
v___jp_2456_:
{
lean_object* v_gain_2461_; 
v_gain_2461_ = lean_nat_sub(v___y_2457_, v___y_2460_);
lean_dec(v___y_2460_);
lean_dec(v___y_2457_);
switch(v_kind_2356_)
{
case 0:
{
lean_object* v___x_2462_; lean_object* v___x_2463_; lean_object* v___x_2464_; lean_object* v___x_2465_; lean_object* v___x_2466_; 
lean_dec_ref(v_l_2354_);
v___x_2462_ = lean_nat_to_int(v_gain_2461_);
v___x_2463_ = l_Legal_USTax_Hunt_Basis_addGain(v___y_2459_, v___y_2458_, v___x_2462_);
lean_dec(v___x_2462_);
v___x_2464_ = l_Legal_USTax_Hunt_Basis_setRet(v_s_2353_, v_owner_2357_, v___x_2463_);
v___x_2465_ = lean_unsigned_to_nat(0u);
v___x_2466_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_2466_, 0, v___x_2464_);
lean_ctor_set(v___x_2466_, 1, v___x_2465_);
return v___x_2466_;
}
case 1:
{
lean_object* v___x_2467_; uint8_t v___x_2468_; 
lean_inc(v_held_2361_);
lean_dec_ref(v_l_2354_);
v___x_2467_ = lean_unsigned_to_nat(5u);
v___x_2468_ = lean_nat_dec_le(v___x_2467_, v_held_2361_);
if (v___x_2468_ == 0)
{
lean_object* v___x_2469_; uint8_t v___x_2470_; 
v___x_2469_ = lean_unsigned_to_nat(4u);
v___x_2470_ = lean_nat_dec_eq(v_held_2361_, v___x_2469_);
if (v___x_2470_ == 0)
{
lean_object* v___x_2471_; uint8_t v___x_2472_; 
v___x_2471_ = lean_unsigned_to_nat(3u);
v___x_2472_ = lean_nat_dec_eq(v_held_2361_, v___x_2471_);
lean_dec(v_held_2361_);
if (v___x_2472_ == 0)
{
lean_object* v___x_2473_; 
v___x_2473_ = lean_unsigned_to_nat(0u);
v___y_2404_ = v___y_2458_;
v___y_2405_ = v___y_2459_;
v___y_2406_ = v_gain_2461_;
v___y_2407_ = v___x_2473_;
goto v___jp_2403_;
}
else
{
lean_object* v___x_2474_; 
v___x_2474_ = lean_unsigned_to_nat(50u);
v___y_2404_ = v___y_2458_;
v___y_2405_ = v___y_2459_;
v___y_2406_ = v_gain_2461_;
v___y_2407_ = v___x_2474_;
goto v___jp_2403_;
}
}
else
{
lean_object* v___x_2475_; 
lean_dec(v_held_2361_);
v___x_2475_ = lean_unsigned_to_nat(75u);
v___y_2404_ = v___y_2458_;
v___y_2405_ = v___y_2459_;
v___y_2406_ = v_gain_2461_;
v___y_2407_ = v___x_2475_;
goto v___jp_2403_;
}
}
else
{
lean_object* v___x_2476_; 
lean_dec(v_held_2361_);
v___x_2476_ = lean_unsigned_to_nat(100u);
v___y_2404_ = v___y_2458_;
v___y_2405_ = v___y_2459_;
v___y_2406_ = v_gain_2461_;
v___y_2407_ = v___x_2476_;
goto v___jp_2403_;
}
}
default: 
{
lean_object* v_st_2477_; lean_object* v_lt_2478_; lean_object* v_g28_2479_; lean_object* v_cfS_2480_; lean_object* v_cfL_2481_; lean_object* v_00x121_2482_; lean_object* v_xQ_2483_; lean_object* v_lim_2484_; uint8_t v___x_2485_; 
v_st_2477_ = lean_ctor_get(v___y_2459_, 0);
lean_inc(v_st_2477_);
v_lt_2478_ = lean_ctor_get(v___y_2459_, 1);
lean_inc(v_lt_2478_);
v_g28_2479_ = lean_ctor_get(v___y_2459_, 2);
lean_inc(v_g28_2479_);
v_cfS_2480_ = lean_ctor_get(v___y_2459_, 3);
lean_inc(v_cfS_2480_);
v_cfL_2481_ = lean_ctor_get(v___y_2459_, 4);
lean_inc(v_cfL_2481_);
v_00x121_2482_ = lean_ctor_get(v___y_2459_, 5);
lean_inc(v_00x121_2482_);
v_xQ_2483_ = lean_ctor_get(v___y_2459_, 6);
lean_inc(v_xQ_2483_);
lean_dec_ref(v___y_2459_);
v_lim_2484_ = l_Legal_USTax_Hunt_Basis_limit121(v_cfg_2352_, v_l_2354_);
lean_dec_ref(v_l_2354_);
v___x_2485_ = lean_nat_dec_le(v_lim_2484_, v_00x121_2482_);
if (v___x_2485_ == 0)
{
lean_inc(v_00x121_2482_);
v___y_2443_ = v_st_2477_;
v___y_2444_ = v___y_2458_;
v___y_2445_ = v_lt_2478_;
v___y_2446_ = v_g28_2479_;
v___y_2447_ = v_cfL_2481_;
v___y_2448_ = v_cfS_2480_;
v___y_2449_ = v_lim_2484_;
v___y_2450_ = v_xQ_2483_;
v___y_2451_ = v_00x121_2482_;
v___y_2452_ = v_gain_2461_;
v___y_2453_ = v_00x121_2482_;
goto v___jp_2442_;
}
else
{
lean_inc(v_lim_2484_);
v___y_2443_ = v_st_2477_;
v___y_2444_ = v___y_2458_;
v___y_2445_ = v_lt_2478_;
v___y_2446_ = v_g28_2479_;
v___y_2447_ = v_cfL_2481_;
v___y_2448_ = v_cfS_2480_;
v___y_2449_ = v_lim_2484_;
v___y_2450_ = v_xQ_2483_;
v___y_2451_ = v_00x121_2482_;
v___y_2452_ = v_gain_2461_;
v___y_2453_ = v_lim_2484_;
goto v___jp_2442_;
}
}
}
}
v___jp_2486_:
{
lean_object* v_r_2488_; uint8_t v___x_2489_; 
v_r_2488_ = l_Legal_USTax_Hunt_Basis_getRet(v_s_2353_, v_owner_2357_);
v___x_2489_ = lean_nat_dec_lt(v_basis_2359_, v_fmv_2358_);
if (v___x_2489_ == 0)
{
uint8_t v___x_2490_; 
lean_inc(v_lossBasis_2360_);
lean_inc(v_fmv_2358_);
lean_dec_ref(v_l_2354_);
v___x_2490_ = lean_nat_dec_lt(v_fmv_2358_, v_lossBasis_2360_);
if (v___x_2490_ == 0)
{
lean_object* v___x_2491_; lean_object* v___x_2492_; 
lean_dec_ref(v_r_2488_);
lean_dec(v_lossBasis_2360_);
lean_dec(v_fmv_2358_);
v___x_2491_ = lean_unsigned_to_nat(0u);
v___x_2492_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_2492_, 0, v_s_2353_);
lean_ctor_set(v___x_2492_, 1, v___x_2491_);
return v___x_2492_;
}
else
{
uint8_t v___x_2493_; uint8_t v___x_2494_; 
v___x_2493_ = 2;
v___x_2494_ = l_Legal_USTax_Hunt_Basis_instBEqKind_beq(v_kind_2356_, v___x_2493_);
if (v___x_2494_ == 0)
{
lean_object* v_loss_2495_; 
v_loss_2495_ = lean_nat_sub(v_lossBasis_2360_, v_fmv_2358_);
lean_dec(v_fmv_2358_);
lean_dec(v_lossBasis_2360_);
if (v_lossAllowed_2355_ == 0)
{
lean_object* v___x_2496_; 
lean_dec_ref(v_r_2488_);
v___x_2496_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_2496_, 0, v_s_2353_);
lean_ctor_set(v___x_2496_, 1, v_loss_2495_);
return v___x_2496_;
}
else
{
lean_object* v___x_2497_; lean_object* v___x_2498_; lean_object* v___x_2499_; lean_object* v___x_2500_; lean_object* v___x_2501_; lean_object* v___x_2502_; 
v___x_2497_ = lean_nat_to_int(v_loss_2495_);
v___x_2498_ = lean_int_neg(v___x_2497_);
lean_dec(v___x_2497_);
v___x_2499_ = l_Legal_USTax_Hunt_Basis_addGain(v_r_2488_, v___y_2487_, v___x_2498_);
lean_dec(v___x_2498_);
v___x_2500_ = l_Legal_USTax_Hunt_Basis_setRet(v_s_2353_, v_owner_2357_, v___x_2499_);
v___x_2501_ = lean_unsigned_to_nat(0u);
v___x_2502_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_2502_, 0, v___x_2500_);
lean_ctor_set(v___x_2502_, 1, v___x_2501_);
return v___x_2502_;
}
}
else
{
lean_object* v___x_2503_; lean_object* v___x_2504_; 
lean_dec_ref(v_r_2488_);
lean_dec(v_lossBasis_2360_);
lean_dec(v_fmv_2358_);
v___x_2503_ = lean_unsigned_to_nat(0u);
v___x_2504_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_2504_, 0, v_s_2353_);
lean_ctor_set(v___x_2504_, 1, v___x_2503_);
return v___x_2504_;
}
}
}
else
{
lean_object* v_gain0_2505_; uint8_t v___x_2506_; 
v_gain0_2505_ = lean_nat_sub(v_fmv_2358_, v_basis_2359_);
v___x_2506_ = lean_nat_dec_le(v_gain0_2505_, v_shield_2362_);
if (v___x_2506_ == 0)
{
lean_inc(v_shield_2362_);
v___y_2457_ = v_gain0_2505_;
v___y_2458_ = v___y_2487_;
v___y_2459_ = v_r_2488_;
v___y_2460_ = v_shield_2362_;
goto v___jp_2456_;
}
else
{
lean_inc(v_gain0_2505_);
v___y_2457_ = v_gain0_2505_;
v___y_2458_ = v___y_2487_;
v___y_2459_ = v_r_2488_;
v___y_2460_ = v_gain0_2505_;
goto v___jp_2456_;
}
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_recognize___boxed(lean_object* v_cfg_2509_, lean_object* v_s_2510_, lean_object* v_l_2511_, lean_object* v_lossAllowed_2512_){
_start:
{
uint8_t v_lossAllowed_boxed_2513_; lean_object* v_res_2514_; 
v_lossAllowed_boxed_2513_ = lean_unbox(v_lossAllowed_2512_);
v_res_2514_ = l_Legal_USTax_Hunt_Basis_recognize(v_cfg_2509_, v_s_2510_, v_l_2511_, v_lossAllowed_boxed_2513_);
lean_dec_ref(v_cfg_2509_);
return v_res_2514_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_zeroYear(lean_object* v_r_2515_, lean_object* v_n_2516_){
_start:
{
lean_object* v_cfS_2517_; lean_object* v_cfL_2518_; lean_object* v_00x121_2519_; lean_object* v_xQ_2520_; lean_object* v___x_2522_; uint8_t v_isShared_2523_; uint8_t v_isSharedCheck_2529_; 
v_cfS_2517_ = lean_ctor_get(v_n_2516_, 4);
v_cfL_2518_ = lean_ctor_get(v_n_2516_, 5);
v_00x121_2519_ = lean_ctor_get(v_r_2515_, 5);
v_xQ_2520_ = lean_ctor_get(v_r_2515_, 6);
v_isSharedCheck_2529_ = !lean_is_exclusive(v_r_2515_);
if (v_isSharedCheck_2529_ == 0)
{
lean_object* v_unused_2530_; lean_object* v_unused_2531_; lean_object* v_unused_2532_; lean_object* v_unused_2533_; lean_object* v_unused_2534_; 
v_unused_2530_ = lean_ctor_get(v_r_2515_, 4);
lean_dec(v_unused_2530_);
v_unused_2531_ = lean_ctor_get(v_r_2515_, 3);
lean_dec(v_unused_2531_);
v_unused_2532_ = lean_ctor_get(v_r_2515_, 2);
lean_dec(v_unused_2532_);
v_unused_2533_ = lean_ctor_get(v_r_2515_, 1);
lean_dec(v_unused_2533_);
v_unused_2534_ = lean_ctor_get(v_r_2515_, 0);
lean_dec(v_unused_2534_);
v___x_2522_ = v_r_2515_;
v_isShared_2523_ = v_isSharedCheck_2529_;
goto v_resetjp_2521_;
}
else
{
lean_inc(v_xQ_2520_);
lean_inc(v_00x121_2519_);
lean_dec(v_r_2515_);
v___x_2522_ = lean_box(0);
v_isShared_2523_ = v_isSharedCheck_2529_;
goto v_resetjp_2521_;
}
v_resetjp_2521_:
{
lean_object* v___x_2524_; lean_object* v___x_2525_; lean_object* v___x_2527_; 
v___x_2524_ = lean_unsigned_to_nat(0u);
v___x_2525_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0, &l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0);
lean_inc(v_cfL_2518_);
lean_inc(v_cfS_2517_);
if (v_isShared_2523_ == 0)
{
lean_ctor_set(v___x_2522_, 4, v_cfL_2518_);
lean_ctor_set(v___x_2522_, 3, v_cfS_2517_);
lean_ctor_set(v___x_2522_, 2, v___x_2524_);
lean_ctor_set(v___x_2522_, 1, v___x_2525_);
lean_ctor_set(v___x_2522_, 0, v___x_2525_);
v___x_2527_ = v___x_2522_;
goto v_reusejp_2526_;
}
else
{
lean_object* v_reuseFailAlloc_2528_; 
v_reuseFailAlloc_2528_ = lean_alloc_ctor(0, 7, 0);
lean_ctor_set(v_reuseFailAlloc_2528_, 0, v___x_2525_);
lean_ctor_set(v_reuseFailAlloc_2528_, 1, v___x_2525_);
lean_ctor_set(v_reuseFailAlloc_2528_, 2, v___x_2524_);
lean_ctor_set(v_reuseFailAlloc_2528_, 3, v_cfS_2517_);
lean_ctor_set(v_reuseFailAlloc_2528_, 4, v_cfL_2518_);
lean_ctor_set(v_reuseFailAlloc_2528_, 5, v_00x121_2519_);
lean_ctor_set(v_reuseFailAlloc_2528_, 6, v_xQ_2520_);
v___x_2527_ = v_reuseFailAlloc_2528_;
goto v_reusejp_2526_;
}
v_reusejp_2526_:
{
return v___x_2527_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_zeroYear___boxed(lean_object* v_r_2535_, lean_object* v_n_2536_){
_start:
{
lean_object* v_res_2537_; 
v_res_2537_ = l_Legal_USTax_Hunt_Basis_zeroYear(v_r_2535_, v_n_2536_);
lean_dec_ref(v_n_2536_);
return v_res_2537_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_norm(lean_object* v_cfg_2547_, uint8_t v_pAlive_2548_, lean_object* v_l_2549_){
_start:
{
uint8_t v_kind_2550_; uint8_t v_owner_2551_; lean_object* v_fmv_2552_; lean_object* v_basis_2553_; lean_object* v_lossBasis_2554_; lean_object* v_held_2555_; lean_object* v_owned_2556_; lean_object* v_shield_2557_; lean_object* v_donor_2558_; lean_object* v_giftAge_2559_; uint8_t v_inherited_2560_; uint8_t v_gone_2561_; lean_object* v___x_2563_; uint8_t v_isShared_2564_; uint8_t v_isSharedCheck_2593_; 
v_kind_2550_ = lean_ctor_get_uint8(v_l_2549_, sizeof(void*)*8);
v_owner_2551_ = lean_ctor_get_uint8(v_l_2549_, sizeof(void*)*8 + 1);
v_fmv_2552_ = lean_ctor_get(v_l_2549_, 0);
v_basis_2553_ = lean_ctor_get(v_l_2549_, 1);
v_lossBasis_2554_ = lean_ctor_get(v_l_2549_, 2);
v_held_2555_ = lean_ctor_get(v_l_2549_, 3);
v_owned_2556_ = lean_ctor_get(v_l_2549_, 4);
v_shield_2557_ = lean_ctor_get(v_l_2549_, 5);
v_donor_2558_ = lean_ctor_get(v_l_2549_, 6);
v_giftAge_2559_ = lean_ctor_get(v_l_2549_, 7);
v_inherited_2560_ = lean_ctor_get_uint8(v_l_2549_, sizeof(void*)*8 + 2);
v_gone_2561_ = lean_ctor_get_uint8(v_l_2549_, sizeof(void*)*8 + 3);
v_isSharedCheck_2593_ = !lean_is_exclusive(v_l_2549_);
if (v_isSharedCheck_2593_ == 0)
{
v___x_2563_ = v_l_2549_;
v_isShared_2564_ = v_isSharedCheck_2593_;
goto v_resetjp_2562_;
}
else
{
lean_inc(v_giftAge_2559_);
lean_inc(v_donor_2558_);
lean_inc(v_shield_2557_);
lean_inc(v_owned_2556_);
lean_inc(v_held_2555_);
lean_inc(v_lossBasis_2554_);
lean_inc(v_basis_2553_);
lean_inc(v_fmv_2552_);
lean_dec(v_l_2549_);
v___x_2563_ = lean_box(0);
v_isShared_2564_ = v_isSharedCheck_2593_;
goto v_resetjp_2562_;
}
v_resetjp_2562_:
{
lean_object* v___y_2566_; uint8_t v___y_2567_; lean_object* v___y_2568_; uint8_t v___y_2578_; lean_object* v___y_2579_; uint8_t v___y_2584_; 
if (v_gone_2561_ == 0)
{
uint8_t v___x_2589_; uint8_t v___x_2590_; 
v___x_2589_ = 4;
v___x_2590_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_owner_2551_, v___x_2589_);
if (v___x_2590_ == 0)
{
v___y_2584_ = v_gone_2561_;
goto v___jp_2583_;
}
else
{
if (v_pAlive_2548_ == 0)
{
v___y_2584_ = v_gone_2561_;
goto v___jp_2583_;
}
else
{
lean_object* v_death_2591_; 
v_death_2591_ = lean_ctor_get(v_cfg_2547_, 3);
if (lean_obj_tag(v_death_2591_) == 0)
{
v___y_2584_ = v_gone_2561_;
goto v___jp_2583_;
}
else
{
v___y_2584_ = v_pAlive_2548_;
goto v___jp_2583_;
}
}
}
}
else
{
lean_object* v___x_2592_; 
lean_del_object(v___x_2563_);
lean_dec(v_giftAge_2559_);
lean_dec(v_donor_2558_);
lean_dec(v_shield_2557_);
lean_dec(v_owned_2556_);
lean_dec(v_held_2555_);
lean_dec(v_lossBasis_2554_);
lean_dec(v_basis_2553_);
lean_dec(v_fmv_2552_);
v___x_2592_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_deadLot));
return v___x_2592_;
}
v___jp_2565_:
{
if (v___y_2567_ == 0)
{
lean_object* v___x_2569_; lean_object* v___x_2570_; lean_object* v___x_2572_; 
lean_dec(v_giftAge_2559_);
lean_dec(v_donor_2558_);
v___x_2569_ = lean_box(0);
v___x_2570_ = lean_unsigned_to_nat(1u);
if (v_isShared_2564_ == 0)
{
lean_ctor_set(v___x_2563_, 7, v___x_2570_);
lean_ctor_set(v___x_2563_, 6, v___x_2569_);
lean_ctor_set(v___x_2563_, 4, v___y_2568_);
lean_ctor_set(v___x_2563_, 3, v___y_2566_);
v___x_2572_ = v___x_2563_;
goto v_reusejp_2571_;
}
else
{
lean_object* v_reuseFailAlloc_2573_; 
v_reuseFailAlloc_2573_ = lean_alloc_ctor(0, 8, 4);
lean_ctor_set(v_reuseFailAlloc_2573_, 0, v_fmv_2552_);
lean_ctor_set(v_reuseFailAlloc_2573_, 1, v_basis_2553_);
lean_ctor_set(v_reuseFailAlloc_2573_, 2, v_lossBasis_2554_);
lean_ctor_set(v_reuseFailAlloc_2573_, 3, v___y_2566_);
lean_ctor_set(v_reuseFailAlloc_2573_, 4, v___y_2568_);
lean_ctor_set(v_reuseFailAlloc_2573_, 5, v_shield_2557_);
lean_ctor_set(v_reuseFailAlloc_2573_, 6, v___x_2569_);
lean_ctor_set(v_reuseFailAlloc_2573_, 7, v___x_2570_);
lean_ctor_set_uint8(v_reuseFailAlloc_2573_, sizeof(void*)*8, v_kind_2550_);
lean_ctor_set_uint8(v_reuseFailAlloc_2573_, sizeof(void*)*8 + 1, v_owner_2551_);
lean_ctor_set_uint8(v_reuseFailAlloc_2573_, sizeof(void*)*8 + 2, v_inherited_2560_);
lean_ctor_set_uint8(v_reuseFailAlloc_2573_, sizeof(void*)*8 + 3, v_gone_2561_);
v___x_2572_ = v_reuseFailAlloc_2573_;
goto v_reusejp_2571_;
}
v_reusejp_2571_:
{
return v___x_2572_;
}
}
else
{
lean_object* v___x_2575_; 
if (v_isShared_2564_ == 0)
{
lean_ctor_set(v___x_2563_, 4, v___y_2568_);
lean_ctor_set(v___x_2563_, 3, v___y_2566_);
v___x_2575_ = v___x_2563_;
goto v_reusejp_2574_;
}
else
{
lean_object* v_reuseFailAlloc_2576_; 
v_reuseFailAlloc_2576_ = lean_alloc_ctor(0, 8, 4);
lean_ctor_set(v_reuseFailAlloc_2576_, 0, v_fmv_2552_);
lean_ctor_set(v_reuseFailAlloc_2576_, 1, v_basis_2553_);
lean_ctor_set(v_reuseFailAlloc_2576_, 2, v_lossBasis_2554_);
lean_ctor_set(v_reuseFailAlloc_2576_, 3, v___y_2566_);
lean_ctor_set(v_reuseFailAlloc_2576_, 4, v___y_2568_);
lean_ctor_set(v_reuseFailAlloc_2576_, 5, v_shield_2557_);
lean_ctor_set(v_reuseFailAlloc_2576_, 6, v_donor_2558_);
lean_ctor_set(v_reuseFailAlloc_2576_, 7, v_giftAge_2559_);
lean_ctor_set_uint8(v_reuseFailAlloc_2576_, sizeof(void*)*8, v_kind_2550_);
lean_ctor_set_uint8(v_reuseFailAlloc_2576_, sizeof(void*)*8 + 1, v_owner_2551_);
lean_ctor_set_uint8(v_reuseFailAlloc_2576_, sizeof(void*)*8 + 2, v_inherited_2560_);
lean_ctor_set_uint8(v_reuseFailAlloc_2576_, sizeof(void*)*8 + 3, v_gone_2561_);
v___x_2575_ = v_reuseFailAlloc_2576_;
goto v_reusejp_2574_;
}
v_reusejp_2574_:
{
return v___x_2575_;
}
}
}
v___jp_2577_:
{
uint8_t v___x_2580_; uint8_t v___x_2581_; 
v___x_2580_ = 2;
v___x_2581_ = l_Legal_USTax_Hunt_Basis_instBEqKind_beq(v_kind_2550_, v___x_2580_);
if (v___x_2581_ == 0)
{
lean_object* v___x_2582_; 
lean_dec(v_owned_2556_);
v___x_2582_ = lean_unsigned_to_nat(0u);
v___y_2566_ = v___y_2579_;
v___y_2567_ = v___y_2578_;
v___y_2568_ = v___x_2582_;
goto v___jp_2565_;
}
else
{
v___y_2566_ = v___y_2579_;
v___y_2567_ = v___y_2578_;
v___y_2568_ = v_owned_2556_;
goto v___jp_2565_;
}
}
v___jp_2583_:
{
uint8_t v___x_2585_; uint8_t v___x_2586_; 
v___x_2585_ = 1;
v___x_2586_ = l_Legal_USTax_Hunt_Basis_instBEqKind_beq(v_kind_2550_, v___x_2585_);
if (v___x_2586_ == 0)
{
lean_object* v___x_2587_; uint8_t v___x_2588_; 
v___x_2587_ = lean_unsigned_to_nat(1u);
v___x_2588_ = lean_nat_dec_le(v___x_2587_, v_held_2555_);
if (v___x_2588_ == 0)
{
v___y_2578_ = v___y_2584_;
v___y_2579_ = v_held_2555_;
goto v___jp_2577_;
}
else
{
lean_dec(v_held_2555_);
v___y_2578_ = v___y_2584_;
v___y_2579_ = v___x_2587_;
goto v___jp_2577_;
}
}
else
{
v___y_2578_ = v___y_2584_;
v___y_2579_ = v_held_2555_;
goto v___jp_2577_;
}
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_norm___boxed(lean_object* v_cfg_2594_, lean_object* v_pAlive_2595_, lean_object* v_l_2596_){
_start:
{
uint8_t v_pAlive_boxed_2597_; lean_object* v_res_2598_; 
v_pAlive_boxed_2597_ = lean_unbox(v_pAlive_2595_);
v_res_2598_ = l_Legal_USTax_Hunt_Basis_norm(v_cfg_2594_, v_pAlive_boxed_2597_, v_l_2596_);
lean_dec_ref(v_cfg_2594_);
return v_res_2598_;
}
}
LEAN_EXPORT lean_object* l_List_mapTR_loop___at___00Legal_USTax_Hunt_Basis_closeYear_spec__0(lean_object* v_cfg_2599_, uint8_t v___x_2600_, lean_object* v_a_2601_, lean_object* v_a_2602_){
_start:
{
if (lean_obj_tag(v_a_2601_) == 0)
{
lean_object* v___x_2603_; 
v___x_2603_ = l_List_reverse___redArg(v_a_2602_);
return v___x_2603_;
}
else
{
lean_object* v_head_2604_; lean_object* v_tail_2605_; lean_object* v___x_2607_; uint8_t v_isShared_2608_; uint8_t v_isSharedCheck_2647_; 
v_head_2604_ = lean_ctor_get(v_a_2601_, 0);
v_tail_2605_ = lean_ctor_get(v_a_2601_, 1);
v_isSharedCheck_2647_ = !lean_is_exclusive(v_a_2601_);
if (v_isSharedCheck_2647_ == 0)
{
v___x_2607_ = v_a_2601_;
v_isShared_2608_ = v_isSharedCheck_2647_;
goto v_resetjp_2606_;
}
else
{
lean_inc(v_tail_2605_);
lean_inc(v_head_2604_);
lean_dec(v_a_2601_);
v___x_2607_ = lean_box(0);
v_isShared_2608_ = v_isSharedCheck_2647_;
goto v_resetjp_2606_;
}
v_resetjp_2606_:
{
lean_object* v___y_2610_; uint8_t v_gone_2615_; 
v_gone_2615_ = lean_ctor_get_uint8(v_head_2604_, sizeof(void*)*8 + 3);
if (v_gone_2615_ == 0)
{
uint8_t v_kind_2616_; uint8_t v_owner_2617_; lean_object* v_fmv_2618_; lean_object* v_basis_2619_; lean_object* v_lossBasis_2620_; lean_object* v_held_2621_; lean_object* v_owned_2622_; lean_object* v_shield_2623_; lean_object* v_donor_2624_; uint8_t v_inherited_2625_; lean_object* v___x_2627_; uint8_t v_isShared_2628_; uint8_t v_isSharedCheck_2645_; 
v_kind_2616_ = lean_ctor_get_uint8(v_head_2604_, sizeof(void*)*8);
v_owner_2617_ = lean_ctor_get_uint8(v_head_2604_, sizeof(void*)*8 + 1);
v_fmv_2618_ = lean_ctor_get(v_head_2604_, 0);
v_basis_2619_ = lean_ctor_get(v_head_2604_, 1);
v_lossBasis_2620_ = lean_ctor_get(v_head_2604_, 2);
v_held_2621_ = lean_ctor_get(v_head_2604_, 3);
v_owned_2622_ = lean_ctor_get(v_head_2604_, 4);
v_shield_2623_ = lean_ctor_get(v_head_2604_, 5);
v_donor_2624_ = lean_ctor_get(v_head_2604_, 6);
v_inherited_2625_ = lean_ctor_get_uint8(v_head_2604_, sizeof(void*)*8 + 2);
v_isSharedCheck_2645_ = !lean_is_exclusive(v_head_2604_);
if (v_isSharedCheck_2645_ == 0)
{
lean_object* v_unused_2646_; 
v_unused_2646_ = lean_ctor_get(v_head_2604_, 7);
lean_dec(v_unused_2646_);
v___x_2627_ = v_head_2604_;
v_isShared_2628_ = v_isSharedCheck_2645_;
goto v_resetjp_2626_;
}
else
{
lean_inc(v_donor_2624_);
lean_inc(v_shield_2623_);
lean_inc(v_owned_2622_);
lean_inc(v_held_2621_);
lean_inc(v_lossBasis_2620_);
lean_inc(v_basis_2619_);
lean_inc(v_fmv_2618_);
lean_dec(v_head_2604_);
v___x_2627_ = lean_box(0);
v_isShared_2628_ = v_isSharedCheck_2645_;
goto v_resetjp_2626_;
}
v_resetjp_2626_:
{
lean_object* v___x_2629_; lean_object* v___x_2630_; lean_object* v___x_2631_; lean_object* v___y_2633_; lean_object* v___y_2634_; lean_object* v___y_2640_; lean_object* v___x_2643_; uint8_t v___x_2644_; 
v___x_2629_ = lean_unsigned_to_nat(2u);
v___x_2630_ = lean_unsigned_to_nat(5u);
v___x_2631_ = lean_unsigned_to_nat(1u);
v___x_2643_ = lean_nat_add(v_held_2621_, v___x_2631_);
lean_dec(v_held_2621_);
v___x_2644_ = lean_nat_dec_le(v___x_2630_, v___x_2643_);
if (v___x_2644_ == 0)
{
v___y_2640_ = v___x_2643_;
goto v___jp_2639_;
}
else
{
lean_dec(v___x_2643_);
v___y_2640_ = v___x_2630_;
goto v___jp_2639_;
}
v___jp_2632_:
{
lean_object* v___x_2636_; 
if (v_isShared_2628_ == 0)
{
lean_ctor_set(v___x_2627_, 7, v___x_2631_);
lean_ctor_set(v___x_2627_, 4, v___y_2634_);
lean_ctor_set(v___x_2627_, 3, v___y_2633_);
v___x_2636_ = v___x_2627_;
goto v_reusejp_2635_;
}
else
{
lean_object* v_reuseFailAlloc_2638_; 
v_reuseFailAlloc_2638_ = lean_alloc_ctor(0, 8, 4);
lean_ctor_set(v_reuseFailAlloc_2638_, 0, v_fmv_2618_);
lean_ctor_set(v_reuseFailAlloc_2638_, 1, v_basis_2619_);
lean_ctor_set(v_reuseFailAlloc_2638_, 2, v_lossBasis_2620_);
lean_ctor_set(v_reuseFailAlloc_2638_, 3, v___y_2633_);
lean_ctor_set(v_reuseFailAlloc_2638_, 4, v___y_2634_);
lean_ctor_set(v_reuseFailAlloc_2638_, 5, v_shield_2623_);
lean_ctor_set(v_reuseFailAlloc_2638_, 6, v_donor_2624_);
lean_ctor_set(v_reuseFailAlloc_2638_, 7, v___x_2631_);
lean_ctor_set_uint8(v_reuseFailAlloc_2638_, sizeof(void*)*8, v_kind_2616_);
lean_ctor_set_uint8(v_reuseFailAlloc_2638_, sizeof(void*)*8 + 1, v_owner_2617_);
lean_ctor_set_uint8(v_reuseFailAlloc_2638_, sizeof(void*)*8 + 2, v_inherited_2625_);
lean_ctor_set_uint8(v_reuseFailAlloc_2638_, sizeof(void*)*8 + 3, v_gone_2615_);
v___x_2636_ = v_reuseFailAlloc_2638_;
goto v_reusejp_2635_;
}
v_reusejp_2635_:
{
lean_object* v___x_2637_; 
v___x_2637_ = l_Legal_USTax_Hunt_Basis_norm(v_cfg_2599_, v___x_2600_, v___x_2636_);
v___y_2610_ = v___x_2637_;
goto v___jp_2609_;
}
}
v___jp_2639_:
{
lean_object* v___x_2641_; uint8_t v___x_2642_; 
v___x_2641_ = lean_nat_add(v_owned_2622_, v___x_2631_);
lean_dec(v_owned_2622_);
v___x_2642_ = lean_nat_dec_le(v___x_2629_, v___x_2641_);
if (v___x_2642_ == 0)
{
v___y_2633_ = v___y_2640_;
v___y_2634_ = v___x_2641_;
goto v___jp_2632_;
}
else
{
lean_dec(v___x_2641_);
v___y_2633_ = v___y_2640_;
v___y_2634_ = v___x_2629_;
goto v___jp_2632_;
}
}
}
}
else
{
v___y_2610_ = v_head_2604_;
goto v___jp_2609_;
}
v___jp_2609_:
{
lean_object* v___x_2612_; 
if (v_isShared_2608_ == 0)
{
lean_ctor_set(v___x_2607_, 1, v_a_2602_);
lean_ctor_set(v___x_2607_, 0, v___y_2610_);
v___x_2612_ = v___x_2607_;
goto v_reusejp_2611_;
}
else
{
lean_object* v_reuseFailAlloc_2614_; 
v_reuseFailAlloc_2614_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v_reuseFailAlloc_2614_, 0, v___y_2610_);
lean_ctor_set(v_reuseFailAlloc_2614_, 1, v_a_2602_);
v___x_2612_ = v_reuseFailAlloc_2614_;
goto v_reusejp_2611_;
}
v_reusejp_2611_:
{
v_a_2601_ = v_tail_2605_;
v_a_2602_ = v___x_2612_;
goto _start;
}
}
}
}
}
}
LEAN_EXPORT lean_object* l_List_mapTR_loop___at___00Legal_USTax_Hunt_Basis_closeYear_spec__0___boxed(lean_object* v_cfg_2648_, lean_object* v___x_2649_, lean_object* v_a_2650_, lean_object* v_a_2651_){
_start:
{
uint8_t v___x_818__boxed_2652_; lean_object* v_res_2653_; 
v___x_818__boxed_2652_ = lean_unbox(v___x_2649_);
v_res_2653_ = l_List_mapTR_loop___at___00Legal_USTax_Hunt_Basis_closeYear_spec__0(v_cfg_2648_, v___x_818__boxed_2652_, v_a_2650_, v_a_2651_);
lean_dec_ref(v_cfg_2648_);
return v_res_2653_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_closeYear(lean_object* v_cfg_2654_, lean_object* v_s_2655_){
_start:
{
lean_object* v_lots_2656_; lean_object* v_year_2657_; uint8_t v_pAlive_2658_; uint8_t v_pFinal_2659_; lean_object* v_rJ_2660_; lean_object* v_rK_2661_; lean_object* v_rA_2662_; lean_object* v_rP_2663_; lean_object* v_charCash_2664_; lean_object* v_charProp_2665_; lean_object* v_cfChar_2666_; lean_object* v_pledge_2667_; lean_object* v_tax_2668_; lean_object* v___x_2670_; uint8_t v_isShared_2671_; uint8_t v_isSharedCheck_2889_; 
v_lots_2656_ = lean_ctor_get(v_s_2655_, 0);
v_year_2657_ = lean_ctor_get(v_s_2655_, 1);
v_pAlive_2658_ = lean_ctor_get_uint8(v_s_2655_, sizeof(void*)*12);
v_pFinal_2659_ = lean_ctor_get_uint8(v_s_2655_, sizeof(void*)*12 + 1);
v_rJ_2660_ = lean_ctor_get(v_s_2655_, 3);
v_rK_2661_ = lean_ctor_get(v_s_2655_, 4);
v_rA_2662_ = lean_ctor_get(v_s_2655_, 5);
v_rP_2663_ = lean_ctor_get(v_s_2655_, 6);
v_charCash_2664_ = lean_ctor_get(v_s_2655_, 7);
v_charProp_2665_ = lean_ctor_get(v_s_2655_, 8);
v_cfChar_2666_ = lean_ctor_get(v_s_2655_, 9);
v_pledge_2667_ = lean_ctor_get(v_s_2655_, 10);
v_tax_2668_ = lean_ctor_get(v_s_2655_, 11);
v_isSharedCheck_2889_ = !lean_is_exclusive(v_s_2655_);
if (v_isSharedCheck_2889_ == 0)
{
lean_object* v_unused_2890_; 
v_unused_2890_ = lean_ctor_get(v_s_2655_, 2);
lean_dec(v_unused_2890_);
v___x_2670_ = v_s_2655_;
v_isShared_2671_ = v_isSharedCheck_2889_;
goto v_resetjp_2669_;
}
else
{
lean_inc(v_tax_2668_);
lean_inc(v_pledge_2667_);
lean_inc(v_cfChar_2666_);
lean_inc(v_charProp_2665_);
lean_inc(v_charCash_2664_);
lean_inc(v_rP_2663_);
lean_inc(v_rA_2662_);
lean_inc(v_rK_2661_);
lean_inc(v_rJ_2660_);
lean_inc(v_year_2657_);
lean_inc(v_lots_2656_);
lean_dec(v_s_2655_);
v___x_2670_ = lean_box(0);
v_isShared_2671_ = v_isSharedCheck_2889_;
goto v_resetjp_2669_;
}
v_resetjp_2669_:
{
lean_object* v_wJ_2672_; lean_object* v_wA_2673_; lean_object* v_wP_2674_; lean_object* v_nJ_2675_; lean_object* v___y_2677_; lean_object* v___y_2678_; lean_object* v___y_2679_; lean_object* v___y_2680_; lean_object* v___y_2681_; lean_object* v___y_2682_; lean_object* v___y_2683_; lean_object* v___y_2684_; lean_object* v___y_2685_; lean_object* v___y_2702_; lean_object* v___y_2703_; lean_object* v___y_2704_; lean_object* v___y_2705_; lean_object* v___y_2706_; lean_object* v___y_2707_; lean_object* v___y_2708_; lean_object* v___y_2709_; lean_object* v___y_2710_; lean_object* v___y_2715_; lean_object* v___y_2716_; lean_object* v___y_2717_; lean_object* v___y_2718_; lean_object* v___y_2719_; lean_object* v___y_2720_; lean_object* v___y_2721_; lean_object* v___y_2722_; lean_object* v___y_2723_; lean_object* v___y_2724_; lean_object* v___y_2729_; lean_object* v___y_2730_; lean_object* v___y_2731_; lean_object* v___y_2732_; lean_object* v___y_2733_; lean_object* v___y_2734_; lean_object* v___y_2735_; lean_object* v___y_2736_; lean_object* v___y_2737_; lean_object* v___y_2738_; lean_object* v___y_2739_; lean_object* v_agiJ_2741_; lean_object* v___x_2742_; lean_object* v___x_2743_; lean_object* v___x_2744_; lean_object* v___y_2746_; lean_object* v___y_2747_; lean_object* v___y_2748_; lean_object* v___y_2749_; lean_object* v___y_2750_; lean_object* v___y_2751_; lean_object* v___y_2765_; lean_object* v___y_2766_; lean_object* v___y_2767_; lean_object* v___y_2768_; lean_object* v___y_2769_; lean_object* v___y_2770_; lean_object* v___y_2771_; lean_object* v___y_2772_; lean_object* v___y_2776_; lean_object* v___y_2777_; lean_object* v___y_2778_; lean_object* v___y_2779_; lean_object* v___y_2780_; lean_object* v___y_2781_; lean_object* v___y_2782_; lean_object* v___y_2783_; lean_object* v___y_2784_; lean_object* v___y_2785_; lean_object* v___y_2786_; lean_object* v___y_2787_; lean_object* v___y_2788_; lean_object* v___y_2789_; lean_object* v___y_2809_; lean_object* v___y_2810_; lean_object* v___y_2811_; lean_object* v___y_2812_; lean_object* v___y_2813_; lean_object* v___y_2837_; lean_object* v___y_2838_; lean_object* v___y_2839_; lean_object* v___y_2854_; lean_object* v___y_2855_; lean_object* v___y_2856_; lean_object* v___y_2865_; lean_object* v___y_2866_; lean_object* v___y_2867_; lean_object* v___y_2870_; lean_object* v___y_2871_; lean_object* v___y_2872_; lean_object* v___y_2873_; lean_object* v___y_2874_; lean_object* v___y_2878_; lean_object* v___x_2887_; uint8_t v___x_2888_; 
v_wJ_2672_ = lean_ctor_get(v_cfg_2654_, 0);
v_wA_2673_ = lean_ctor_get(v_cfg_2654_, 1);
v_wP_2674_ = lean_ctor_get(v_cfg_2654_, 2);
lean_inc_ref(v_rJ_2660_);
v_nJ_2675_ = l_Legal_USTax_Hunt_Basis_capNet(v_rJ_2660_);
v_agiJ_2741_ = l_Legal_USTax_Hunt_Basis_agiOf(v_wJ_2672_, v_nJ_2675_);
v___x_2742_ = lean_unsigned_to_nat(60u);
v___x_2743_ = lean_nat_mul(v_agiJ_2741_, v___x_2742_);
v___x_2744_ = lean_unsigned_to_nat(100u);
v___x_2887_ = lean_nat_div(v___x_2743_, v___x_2744_);
lean_dec(v___x_2743_);
v___x_2888_ = lean_nat_dec_le(v_charCash_2664_, v___x_2887_);
if (v___x_2888_ == 0)
{
v___y_2878_ = v___x_2887_;
goto v___jp_2877_;
}
else
{
lean_dec(v___x_2887_);
lean_inc(v_charCash_2664_);
v___y_2878_ = v_charCash_2664_;
goto v___jp_2877_;
}
v___jp_2676_:
{
lean_object* v___x_2686_; lean_object* v___x_2687_; lean_object* v___x_2688_; lean_object* v___x_2689_; uint8_t v___x_2690_; lean_object* v___x_2691_; lean_object* v___x_2692_; lean_object* v___x_2693_; lean_object* v___x_2694_; lean_object* v___x_2695_; lean_object* v___x_2696_; lean_object* v___x_2697_; lean_object* v___x_2699_; 
v___x_2686_ = lean_box(0);
v___x_2687_ = l_List_mapTR_loop___at___00Legal_USTax_Hunt_Basis_closeYear_spec__0(v_cfg_2654_, v_pAlive_2658_, v_lots_2656_, v___x_2686_);
v___x_2688_ = lean_unsigned_to_nat(1u);
v___x_2689_ = lean_nat_add(v_year_2657_, v___x_2688_);
lean_dec(v_year_2657_);
v___x_2690_ = 0;
v___x_2691_ = l_Legal_USTax_Hunt_Basis_zeroYear(v_rJ_2660_, v_nJ_2675_);
lean_dec_ref(v_nJ_2675_);
v___x_2692_ = l_Legal_USTax_Hunt_Basis_zeroYear(v_rK_2661_, v___y_2678_);
lean_dec_ref(v___y_2678_);
v___x_2693_ = l_Legal_USTax_Hunt_Basis_zeroYear(v_rA_2662_, v___y_2681_);
lean_dec_ref(v___y_2681_);
v___x_2694_ = lean_nat_add(v_tax_2668_, v___y_2679_);
lean_dec(v___y_2679_);
lean_dec(v_tax_2668_);
v___x_2695_ = lean_nat_add(v___x_2694_, v___y_2683_);
lean_dec(v___y_2683_);
lean_dec(v___x_2694_);
v___x_2696_ = lean_nat_add(v___x_2695_, v___y_2682_);
lean_dec(v___y_2682_);
lean_dec(v___x_2695_);
v___x_2697_ = lean_nat_add(v___x_2696_, v___y_2684_);
lean_dec(v___y_2684_);
lean_dec(v___x_2696_);
lean_inc_n(v___y_2680_, 2);
if (v_isShared_2671_ == 0)
{
lean_ctor_set(v___x_2670_, 11, v___x_2697_);
lean_ctor_set(v___x_2670_, 9, v___y_2677_);
lean_ctor_set(v___x_2670_, 8, v___y_2680_);
lean_ctor_set(v___x_2670_, 7, v___y_2680_);
lean_ctor_set(v___x_2670_, 6, v___y_2685_);
lean_ctor_set(v___x_2670_, 5, v___x_2693_);
lean_ctor_set(v___x_2670_, 4, v___x_2692_);
lean_ctor_set(v___x_2670_, 3, v___x_2691_);
lean_ctor_set(v___x_2670_, 2, v___y_2680_);
lean_ctor_set(v___x_2670_, 1, v___x_2689_);
lean_ctor_set(v___x_2670_, 0, v___x_2687_);
v___x_2699_ = v___x_2670_;
goto v_reusejp_2698_;
}
else
{
lean_object* v_reuseFailAlloc_2700_; 
v_reuseFailAlloc_2700_ = lean_alloc_ctor(0, 12, 2);
lean_ctor_set(v_reuseFailAlloc_2700_, 0, v___x_2687_);
lean_ctor_set(v_reuseFailAlloc_2700_, 1, v___x_2689_);
lean_ctor_set(v_reuseFailAlloc_2700_, 2, v___y_2680_);
lean_ctor_set(v_reuseFailAlloc_2700_, 3, v___x_2691_);
lean_ctor_set(v_reuseFailAlloc_2700_, 4, v___x_2692_);
lean_ctor_set(v_reuseFailAlloc_2700_, 5, v___x_2693_);
lean_ctor_set(v_reuseFailAlloc_2700_, 6, v___y_2685_);
lean_ctor_set(v_reuseFailAlloc_2700_, 7, v___y_2680_);
lean_ctor_set(v_reuseFailAlloc_2700_, 8, v___y_2680_);
lean_ctor_set(v_reuseFailAlloc_2700_, 9, v___y_2677_);
lean_ctor_set(v_reuseFailAlloc_2700_, 10, v_pledge_2667_);
lean_ctor_set(v_reuseFailAlloc_2700_, 11, v___x_2697_);
lean_ctor_set_uint8(v_reuseFailAlloc_2700_, sizeof(void*)*12, v_pAlive_2658_);
v___x_2699_ = v_reuseFailAlloc_2700_;
goto v_reusejp_2698_;
}
v_reusejp_2698_:
{
lean_ctor_set_uint8(v___x_2699_, sizeof(void*)*12 + 1, v___x_2690_);
return v___x_2699_;
}
}
v___jp_2701_:
{
if (v_pAlive_2658_ == 0)
{
lean_object* v___x_2711_; lean_object* v___x_2712_; 
lean_dec_ref(v___y_2704_);
lean_dec_ref(v_rP_2663_);
lean_inc_n(v___y_2706_, 6);
v___x_2711_ = lean_nat_to_int(v___y_2706_);
lean_inc(v___x_2711_);
v___x_2712_ = lean_alloc_ctor(0, 7, 0);
lean_ctor_set(v___x_2712_, 0, v___x_2711_);
lean_ctor_set(v___x_2712_, 1, v___x_2711_);
lean_ctor_set(v___x_2712_, 2, v___y_2706_);
lean_ctor_set(v___x_2712_, 3, v___y_2706_);
lean_ctor_set(v___x_2712_, 4, v___y_2706_);
lean_ctor_set(v___x_2712_, 5, v___y_2706_);
lean_ctor_set(v___x_2712_, 6, v___y_2706_);
v___y_2677_ = v___y_2702_;
v___y_2678_ = v___y_2703_;
v___y_2679_ = v___y_2705_;
v___y_2680_ = v___y_2706_;
v___y_2681_ = v___y_2707_;
v___y_2682_ = v___y_2708_;
v___y_2683_ = v___y_2709_;
v___y_2684_ = v___y_2710_;
v___y_2685_ = v___x_2712_;
goto v___jp_2676_;
}
else
{
lean_object* v___x_2713_; 
v___x_2713_ = l_Legal_USTax_Hunt_Basis_zeroYear(v_rP_2663_, v___y_2704_);
lean_dec_ref(v___y_2704_);
v___y_2677_ = v___y_2702_;
v___y_2678_ = v___y_2703_;
v___y_2679_ = v___y_2705_;
v___y_2680_ = v___y_2706_;
v___y_2681_ = v___y_2707_;
v___y_2682_ = v___y_2708_;
v___y_2683_ = v___y_2709_;
v___y_2684_ = v___y_2710_;
v___y_2685_ = v___x_2713_;
goto v___jp_2676_;
}
}
v___jp_2714_:
{
lean_object* v___x_2725_; lean_object* v___x_2726_; lean_object* v___x_2727_; 
v___x_2725_ = lean_unsigned_to_nat(18150u);
v___x_2726_ = lean_nat_add(v___x_2725_, v___y_2724_);
lean_dec(v___y_2724_);
v___x_2727_ = l_Legal_USTax_Hunt_Basis_retTax(v___y_2717_, v_wP_2674_, v___x_2726_, v___y_2718_);
lean_dec(v___x_2726_);
v___y_2702_ = v___y_2715_;
v___y_2703_ = v___y_2716_;
v___y_2704_ = v___y_2718_;
v___y_2705_ = v___y_2719_;
v___y_2706_ = v___y_2720_;
v___y_2707_ = v___y_2721_;
v___y_2708_ = v___y_2722_;
v___y_2709_ = v___y_2723_;
v___y_2710_ = v___x_2727_;
goto v___jp_2701_;
}
v___jp_2728_:
{
lean_object* v_sen_2740_; 
v_sen_2740_ = lean_nat_sub(v___y_2736_, v___y_2739_);
lean_dec(v___y_2739_);
lean_dec(v___y_2736_);
if (v_pAlive_2658_ == 0)
{
if (v_pFinal_2659_ == 0)
{
lean_dec(v_sen_2740_);
lean_dec_ref(v___y_2731_);
lean_inc(v___y_2734_);
v___y_2702_ = v___y_2729_;
v___y_2703_ = v___y_2730_;
v___y_2704_ = v___y_2732_;
v___y_2705_ = v___y_2733_;
v___y_2706_ = v___y_2734_;
v___y_2707_ = v___y_2735_;
v___y_2708_ = v___y_2737_;
v___y_2709_ = v___y_2738_;
v___y_2710_ = v___y_2734_;
goto v___jp_2701_;
}
else
{
v___y_2715_ = v___y_2729_;
v___y_2716_ = v___y_2730_;
v___y_2717_ = v___y_2731_;
v___y_2718_ = v___y_2732_;
v___y_2719_ = v___y_2733_;
v___y_2720_ = v___y_2734_;
v___y_2721_ = v___y_2735_;
v___y_2722_ = v___y_2737_;
v___y_2723_ = v___y_2738_;
v___y_2724_ = v_sen_2740_;
goto v___jp_2714_;
}
}
else
{
v___y_2715_ = v___y_2729_;
v___y_2716_ = v___y_2730_;
v___y_2717_ = v___y_2731_;
v___y_2718_ = v___y_2732_;
v___y_2719_ = v___y_2733_;
v___y_2720_ = v___y_2734_;
v___y_2721_ = v___y_2735_;
v___y_2722_ = v___y_2737_;
v___y_2723_ = v___y_2738_;
v___y_2724_ = v_sen_2740_;
goto v___jp_2714_;
}
}
v___jp_2745_:
{
lean_object* v_nA_2752_; lean_object* v___x_2753_; lean_object* v_taxA_2754_; lean_object* v_nP_2755_; lean_object* v_agiP_2756_; lean_object* v___x_2757_; lean_object* v___x_2758_; lean_object* v___x_2759_; lean_object* v___x_2760_; lean_object* v___x_2761_; lean_object* v___x_2762_; uint8_t v___x_2763_; 
lean_inc_ref(v_rA_2662_);
v_nA_2752_ = l_Legal_USTax_Hunt_Basis_capNet(v_rA_2662_);
v___x_2753_ = lean_unsigned_to_nat(16100u);
lean_inc_ref(v___y_2748_);
v_taxA_2754_ = l_Legal_USTax_Hunt_Basis_retTax(v___y_2748_, v_wA_2673_, v___x_2753_, v_nA_2752_);
lean_inc_ref(v_rP_2663_);
v_nP_2755_ = l_Legal_USTax_Hunt_Basis_capNet(v_rP_2663_);
v_agiP_2756_ = l_Legal_USTax_Hunt_Basis_agiOf(v_wP_2674_, v_nP_2755_);
v___x_2757_ = lean_unsigned_to_nat(6000u);
v___x_2758_ = lean_unsigned_to_nat(6u);
v___x_2759_ = lean_unsigned_to_nat(75000u);
v___x_2760_ = lean_nat_sub(v_agiP_2756_, v___x_2759_);
lean_dec(v_agiP_2756_);
v___x_2761_ = lean_nat_mul(v___x_2758_, v___x_2760_);
lean_dec(v___x_2760_);
v___x_2762_ = lean_nat_div(v___x_2761_, v___x_2744_);
lean_dec(v___x_2761_);
v___x_2763_ = lean_nat_dec_le(v___x_2757_, v___x_2762_);
if (v___x_2763_ == 0)
{
v___y_2729_ = v___y_2746_;
v___y_2730_ = v___y_2747_;
v___y_2731_ = v___y_2748_;
v___y_2732_ = v_nP_2755_;
v___y_2733_ = v___y_2749_;
v___y_2734_ = v___y_2750_;
v___y_2735_ = v_nA_2752_;
v___y_2736_ = v___x_2757_;
v___y_2737_ = v_taxA_2754_;
v___y_2738_ = v___y_2751_;
v___y_2739_ = v___x_2762_;
goto v___jp_2728_;
}
else
{
lean_dec(v___x_2762_);
v___y_2729_ = v___y_2746_;
v___y_2730_ = v___y_2747_;
v___y_2731_ = v___y_2748_;
v___y_2732_ = v_nP_2755_;
v___y_2733_ = v___y_2749_;
v___y_2734_ = v___y_2750_;
v___y_2735_ = v_nA_2752_;
v___y_2736_ = v___x_2757_;
v___y_2737_ = v_taxA_2754_;
v___y_2738_ = v___y_2751_;
v___y_2739_ = v___x_2757_;
goto v___jp_2728_;
}
}
v___jp_2764_:
{
lean_object* v___x_2773_; uint8_t v___x_2774_; 
v___x_2773_ = lean_nat_add(v___y_2772_, v___y_2771_);
lean_dec(v___y_2771_);
lean_dec(v___y_2772_);
v___x_2774_ = lean_nat_dec_le(v___y_2769_, v___x_2773_);
if (v___x_2774_ == 0)
{
lean_dec(v___x_2773_);
v___y_2746_ = v___y_2765_;
v___y_2747_ = v___y_2766_;
v___y_2748_ = v___y_2767_;
v___y_2749_ = v___y_2768_;
v___y_2750_ = v___y_2770_;
v___y_2751_ = v___y_2769_;
goto v___jp_2745_;
}
else
{
lean_dec(v___y_2769_);
v___y_2746_ = v___y_2765_;
v___y_2747_ = v___y_2766_;
v___y_2748_ = v___y_2767_;
v___y_2749_ = v___y_2768_;
v___y_2750_ = v___y_2770_;
v___y_2751_ = v___x_2773_;
goto v___jp_2745_;
}
}
v___jp_2775_:
{
lean_object* v___x_2790_; lean_object* v_regK_2791_; uint8_t v___x_2792_; 
v___x_2790_ = l_Legal_USTax_Hunt_Basis_single;
v_regK_2791_ = l_Legal_USTax_Hunt_Basis_retTax(v___x_2790_, v___y_2782_, v___y_2785_, v___y_2780_);
v___x_2792_ = lean_nat_dec_eq(v___y_2789_, v___y_2782_);
if (v___x_2792_ == 0)
{
lean_object* v___x_2793_; lean_object* v_aS_2794_; lean_object* v___x_2795_; lean_object* v_aG_2796_; lean_object* v___x_2797_; lean_object* v_aL_2798_; lean_object* v___x_2799_; lean_object* v___x_2800_; lean_object* v___x_2801_; lean_object* v___x_2802_; lean_object* v_par_2803_; lean_object* v_rest_2804_; uint8_t v___x_2805_; 
v___x_2793_ = lean_nat_mul(v___y_2789_, v___y_2777_);
v_aS_2794_ = lean_nat_div(v___x_2793_, v___y_2787_);
lean_dec(v___x_2793_);
v___x_2795_ = lean_nat_mul(v___y_2789_, v___y_2784_);
lean_dec(v___y_2784_);
v_aG_2796_ = lean_nat_div(v___x_2795_, v___y_2787_);
lean_dec(v___y_2787_);
lean_dec(v___x_2795_);
v___x_2797_ = lean_nat_sub(v___y_2789_, v_aS_2794_);
v_aL_2798_ = lean_nat_sub(v___x_2797_, v_aG_2796_);
lean_dec(v___x_2797_);
v___x_2799_ = lean_nat_add(v___y_2788_, v_aS_2794_);
lean_dec(v_aS_2794_);
lean_dec(v___y_2788_);
v___x_2800_ = lean_nat_add(v___y_2778_, v_aG_2796_);
lean_dec(v_aG_2796_);
lean_dec(v___y_2778_);
v___x_2801_ = lean_nat_add(v___y_2779_, v_aL_2798_);
lean_dec(v_aL_2798_);
lean_dec(v___y_2779_);
v___x_2802_ = l_Legal_USTax_Hunt_Basis_fullTax(v___y_2783_, v___x_2799_, v___x_2800_, v___x_2801_);
lean_dec(v___x_2800_);
lean_dec(v___x_2799_);
v_par_2803_ = lean_nat_sub(v___x_2802_, v___y_2786_);
lean_dec(v___x_2802_);
v_rest_2804_ = lean_nat_sub(v___y_2781_, v___y_2789_);
lean_dec(v___y_2789_);
lean_dec(v___y_2781_);
v___x_2805_ = lean_nat_dec_lt(v___y_2782_, v___y_2777_);
lean_dec(v___y_2777_);
if (v___x_2805_ == 0)
{
lean_object* v___x_2806_; 
v___x_2806_ = l_Legal_USTax_Hunt_Basis_fullTax(v___x_2790_, v___y_2782_, v___y_2782_, v_rest_2804_);
v___y_2765_ = v___y_2776_;
v___y_2766_ = v___y_2780_;
v___y_2767_ = v___x_2790_;
v___y_2768_ = v___y_2786_;
v___y_2769_ = v_regK_2791_;
v___y_2770_ = v___y_2782_;
v___y_2771_ = v_par_2803_;
v___y_2772_ = v___x_2806_;
goto v___jp_2764_;
}
else
{
lean_object* v___x_2807_; 
lean_inc(v___y_2782_);
v___x_2807_ = l_Legal_USTax_Hunt_Basis_fullTax(v___x_2790_, v_rest_2804_, v___y_2782_, v___y_2782_);
lean_dec(v_rest_2804_);
v___y_2765_ = v___y_2776_;
v___y_2766_ = v___y_2780_;
v___y_2767_ = v___x_2790_;
v___y_2768_ = v___y_2786_;
v___y_2769_ = v_regK_2791_;
v___y_2770_ = v___y_2782_;
v___y_2771_ = v_par_2803_;
v___y_2772_ = v___x_2807_;
goto v___jp_2764_;
}
}
else
{
lean_dec(v___y_2789_);
lean_dec(v___y_2788_);
lean_dec(v___y_2787_);
lean_dec(v___y_2784_);
lean_dec_ref(v___y_2783_);
lean_dec(v___y_2781_);
lean_dec(v___y_2779_);
lean_dec(v___y_2778_);
lean_dec(v___y_2777_);
v___y_2746_ = v___y_2776_;
v___y_2747_ = v___y_2780_;
v___y_2748_ = v___x_2790_;
v___y_2749_ = v___y_2786_;
v___y_2750_ = v___y_2782_;
v___y_2751_ = v_regK_2791_;
goto v___jp_2745_;
}
}
v___jp_2808_:
{
lean_object* v___x_2814_; lean_object* v___x_2815_; lean_object* v___x_2816_; lean_object* v_ded_2817_; lean_object* v___x_2818_; lean_object* v_snd_2819_; lean_object* v_fst_2820_; lean_object* v_fst_2821_; lean_object* v_snd_2822_; lean_object* v_nK_2823_; lean_object* v_sG_2824_; lean_object* v_lG_2825_; lean_object* v_g28_2826_; lean_object* v___x_2827_; lean_object* v_taxJ_2828_; lean_object* v___x_2829_; lean_object* v_u_2830_; lean_object* v___x_2831_; lean_object* v_tiK_2832_; lean_object* v___x_2833_; lean_object* v___x_2834_; uint8_t v___x_2835_; 
v___x_2814_ = lean_nat_mul(v___y_2811_, v___y_2813_);
lean_dec(v___y_2813_);
v___x_2815_ = lean_unsigned_to_nat(37u);
v___x_2816_ = lean_nat_div(v___x_2814_, v___x_2815_);
lean_dec(v___x_2814_);
v_ded_2817_ = lean_nat_sub(v___y_2810_, v___x_2816_);
lean_dec(v___x_2816_);
lean_dec(v___y_2810_);
v___x_2818_ = l_Legal_USTax_Hunt_Basis_tiParts(v_wJ_2672_, v_ded_2817_, v_nJ_2675_);
lean_dec(v_ded_2817_);
v_snd_2819_ = lean_ctor_get(v___x_2818_, 1);
lean_inc(v_snd_2819_);
v_fst_2820_ = lean_ctor_get(v___x_2818_, 0);
lean_inc(v_fst_2820_);
lean_dec_ref(v___x_2818_);
v_fst_2821_ = lean_ctor_get(v_snd_2819_, 0);
lean_inc(v_fst_2821_);
v_snd_2822_ = lean_ctor_get(v_snd_2819_, 1);
lean_inc_n(v_snd_2822_, 2);
lean_dec(v_snd_2819_);
lean_inc_ref(v_rK_2661_);
v_nK_2823_ = l_Legal_USTax_Hunt_Basis_capNet(v_rK_2661_);
v_sG_2824_ = lean_ctor_get(v_nK_2823_, 0);
lean_inc(v_sG_2824_);
v_lG_2825_ = lean_ctor_get(v_nK_2823_, 1);
lean_inc(v_lG_2825_);
v_g28_2826_ = lean_ctor_get(v_nK_2823_, 2);
lean_inc(v_g28_2826_);
v___x_2827_ = l_Legal_USTax_Hunt_Basis_mfj;
v_taxJ_2828_ = l_Legal_USTax_Hunt_Basis_fullTax(v___x_2827_, v_fst_2820_, v_fst_2821_, v_snd_2822_);
v___x_2829_ = lean_nat_add(v_sG_2824_, v_lG_2825_);
lean_dec(v_lG_2825_);
v_u_2830_ = lean_nat_add(v___x_2829_, v_g28_2826_);
lean_dec(v___x_2829_);
v___x_2831_ = lean_unsigned_to_nat(1350u);
v_tiK_2832_ = lean_nat_sub(v_u_2830_, v___x_2831_);
v___x_2833_ = lean_unsigned_to_nat(2700u);
v___x_2834_ = lean_nat_sub(v_u_2830_, v___x_2833_);
v___x_2835_ = lean_nat_dec_le(v_tiK_2832_, v___x_2834_);
if (v___x_2835_ == 0)
{
v___y_2776_ = v___y_2809_;
v___y_2777_ = v_sG_2824_;
v___y_2778_ = v_fst_2821_;
v___y_2779_ = v_snd_2822_;
v___y_2780_ = v_nK_2823_;
v___y_2781_ = v_tiK_2832_;
v___y_2782_ = v___y_2812_;
v___y_2783_ = v___x_2827_;
v___y_2784_ = v_g28_2826_;
v___y_2785_ = v___x_2831_;
v___y_2786_ = v_taxJ_2828_;
v___y_2787_ = v_u_2830_;
v___y_2788_ = v_fst_2820_;
v___y_2789_ = v___x_2834_;
goto v___jp_2775_;
}
else
{
lean_dec(v___x_2834_);
lean_inc(v_tiK_2832_);
v___y_2776_ = v___y_2809_;
v___y_2777_ = v_sG_2824_;
v___y_2778_ = v_fst_2821_;
v___y_2779_ = v_snd_2822_;
v___y_2780_ = v_nK_2823_;
v___y_2781_ = v_tiK_2832_;
v___y_2782_ = v___y_2812_;
v___y_2783_ = v___x_2827_;
v___y_2784_ = v_g28_2826_;
v___y_2785_ = v___x_2831_;
v___y_2786_ = v_taxJ_2828_;
v___y_2787_ = v_u_2830_;
v___y_2788_ = v_fst_2820_;
v___y_2789_ = v_tiK_2832_;
goto v___jp_2775_;
}
}
v___jp_2836_:
{
lean_object* v___x_2840_; lean_object* v_tiNo_2841_; lean_object* v_snd_2842_; lean_object* v_fst_2843_; lean_object* v_fst_2844_; lean_object* v_snd_2845_; lean_object* v_ded0_2846_; lean_object* v___x_2847_; lean_object* v_tiNoSum_2848_; lean_object* v___x_2849_; lean_object* v___x_2850_; lean_object* v___x_2851_; uint8_t v___x_2852_; 
v___x_2840_ = lean_unsigned_to_nat(0u);
v_tiNo_2841_ = l_Legal_USTax_Hunt_Basis_tiParts(v_wJ_2672_, v___x_2840_, v_nJ_2675_);
v_snd_2842_ = lean_ctor_get(v_tiNo_2841_, 1);
lean_inc(v_snd_2842_);
v_fst_2843_ = lean_ctor_get(v_tiNo_2841_, 0);
lean_inc(v_fst_2843_);
lean_dec_ref(v_tiNo_2841_);
v_fst_2844_ = lean_ctor_get(v_snd_2842_, 0);
lean_inc(v_fst_2844_);
v_snd_2845_ = lean_ctor_get(v_snd_2842_, 1);
lean_inc(v_snd_2845_);
lean_dec(v_snd_2842_);
v_ded0_2846_ = lean_nat_sub(v___y_2838_, v___y_2839_);
lean_dec(v___y_2839_);
lean_dec(v___y_2838_);
v___x_2847_ = lean_nat_add(v_fst_2843_, v_fst_2844_);
lean_dec(v_fst_2844_);
lean_dec(v_fst_2843_);
v_tiNoSum_2848_ = lean_nat_add(v___x_2847_, v_snd_2845_);
lean_dec(v_snd_2845_);
lean_dec(v___x_2847_);
v___x_2849_ = lean_unsigned_to_nat(2u);
v___x_2850_ = lean_unsigned_to_nat(768700u);
v___x_2851_ = lean_nat_sub(v_tiNoSum_2848_, v___x_2850_);
lean_dec(v_tiNoSum_2848_);
v___x_2852_ = lean_nat_dec_le(v_ded0_2846_, v___x_2851_);
if (v___x_2852_ == 0)
{
v___y_2809_ = v___y_2837_;
v___y_2810_ = v_ded0_2846_;
v___y_2811_ = v___x_2849_;
v___y_2812_ = v___x_2840_;
v___y_2813_ = v___x_2851_;
goto v___jp_2808_;
}
else
{
lean_dec(v___x_2851_);
lean_inc(v_ded0_2846_);
v___y_2809_ = v___y_2837_;
v___y_2810_ = v_ded0_2846_;
v___y_2811_ = v___x_2849_;
v___y_2812_ = v___x_2840_;
v___y_2813_ = v_ded0_2846_;
goto v___jp_2808_;
}
}
v___jp_2853_:
{
lean_object* v___x_2857_; lean_object* v___x_2858_; lean_object* v_cf_2859_; lean_object* v_total_2860_; lean_object* v___x_2861_; lean_object* v___x_2862_; uint8_t v___x_2863_; 
v___x_2857_ = lean_nat_sub(v___y_2854_, v___y_2856_);
lean_dec(v___y_2854_);
v___x_2858_ = lean_nat_sub(v_charCash_2664_, v___y_2855_);
lean_dec(v_charCash_2664_);
v_cf_2859_ = lean_nat_add(v___x_2857_, v___x_2858_);
lean_dec(v___x_2858_);
lean_dec(v___x_2857_);
v_total_2860_ = lean_nat_add(v___y_2855_, v___y_2856_);
lean_dec(v___y_2856_);
lean_dec(v___y_2855_);
v___x_2861_ = lean_unsigned_to_nat(200u);
v___x_2862_ = lean_nat_div(v_agiJ_2741_, v___x_2861_);
lean_dec(v_agiJ_2741_);
v___x_2863_ = lean_nat_dec_le(v_total_2860_, v___x_2862_);
if (v___x_2863_ == 0)
{
v___y_2837_ = v_cf_2859_;
v___y_2838_ = v_total_2860_;
v___y_2839_ = v___x_2862_;
goto v___jp_2836_;
}
else
{
lean_dec(v___x_2862_);
lean_inc(v_total_2860_);
v___y_2837_ = v_cf_2859_;
v___y_2838_ = v_total_2860_;
v___y_2839_ = v_total_2860_;
goto v___jp_2836_;
}
}
v___jp_2864_:
{
uint8_t v___x_2868_; 
v___x_2868_ = lean_nat_dec_le(v___y_2865_, v___y_2867_);
if (v___x_2868_ == 0)
{
v___y_2854_ = v___y_2865_;
v___y_2855_ = v___y_2866_;
v___y_2856_ = v___y_2867_;
goto v___jp_2853_;
}
else
{
lean_dec(v___y_2867_);
lean_inc(v___y_2865_);
v___y_2854_ = v___y_2865_;
v___y_2855_ = v___y_2866_;
v___y_2856_ = v___y_2865_;
goto v___jp_2853_;
}
}
v___jp_2869_:
{
lean_object* v___x_2875_; uint8_t v___x_2876_; 
v___x_2875_ = lean_nat_sub(v___y_2872_, v___y_2874_);
lean_dec(v___y_2874_);
lean_dec(v___y_2872_);
v___x_2876_ = lean_nat_dec_le(v___y_2873_, v___x_2875_);
if (v___x_2876_ == 0)
{
lean_dec(v___y_2873_);
v___y_2865_ = v___y_2870_;
v___y_2866_ = v___y_2871_;
v___y_2867_ = v___x_2875_;
goto v___jp_2864_;
}
else
{
lean_dec(v___x_2875_);
v___y_2865_ = v___y_2870_;
v___y_2866_ = v___y_2871_;
v___y_2867_ = v___y_2873_;
goto v___jp_2864_;
}
}
v___jp_2877_:
{
lean_object* v_availP_2879_; lean_object* v___x_2880_; lean_object* v___x_2881_; lean_object* v___x_2882_; lean_object* v___x_2883_; lean_object* v___x_2884_; lean_object* v___x_2885_; uint8_t v___x_2886_; 
v_availP_2879_ = lean_nat_add(v_charProp_2665_, v_cfChar_2666_);
lean_dec(v_cfChar_2666_);
lean_dec(v_charProp_2665_);
v___x_2880_ = lean_unsigned_to_nat(30u);
v___x_2881_ = lean_nat_mul(v_agiJ_2741_, v___x_2880_);
v___x_2882_ = lean_nat_div(v___x_2881_, v___x_2744_);
lean_dec(v___x_2881_);
v___x_2883_ = lean_unsigned_to_nat(50u);
v___x_2884_ = lean_nat_mul(v_agiJ_2741_, v___x_2883_);
v___x_2885_ = lean_nat_div(v___x_2884_, v___x_2744_);
lean_dec(v___x_2884_);
v___x_2886_ = lean_nat_dec_le(v___x_2885_, v___y_2878_);
if (v___x_2886_ == 0)
{
lean_inc(v___y_2878_);
v___y_2870_ = v_availP_2879_;
v___y_2871_ = v___y_2878_;
v___y_2872_ = v___x_2885_;
v___y_2873_ = v___x_2882_;
v___y_2874_ = v___y_2878_;
goto v___jp_2869_;
}
else
{
lean_inc(v___x_2885_);
v___y_2870_ = v_availP_2879_;
v___y_2871_ = v___y_2878_;
v___y_2872_ = v___x_2885_;
v___y_2873_ = v___x_2882_;
v___y_2874_ = v___x_2885_;
goto v___jp_2869_;
}
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_closeYear___boxed(lean_object* v_cfg_2891_, lean_object* v_s_2892_){
_start:
{
lean_object* v_res_2893_; 
v_res_2893_ = l_Legal_USTax_Hunt_Basis_closeYear(v_cfg_2891_, v_s_2892_);
lean_dec_ref(v_cfg_2891_);
return v_res_2893_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_touch(lean_object* v_cfg_2896_, lean_object* v_s_2897_, lean_object* v_i_2898_, lean_object* v_l_2899_){
_start:
{
lean_object* v_lots_2900_; lean_object* v_year_2901_; uint8_t v_pAlive_2902_; uint8_t v_pFinal_2903_; lean_object* v_rJ_2904_; lean_object* v_rK_2905_; lean_object* v_rA_2906_; lean_object* v_rP_2907_; lean_object* v_charCash_2908_; lean_object* v_charProp_2909_; lean_object* v_cfChar_2910_; lean_object* v_pledge_2911_; lean_object* v_tax_2912_; lean_object* v___x_2914_; uint8_t v_isShared_2915_; uint8_t v_isSharedCheck_2922_; 
v_lots_2900_ = lean_ctor_get(v_s_2897_, 0);
v_year_2901_ = lean_ctor_get(v_s_2897_, 1);
v_pAlive_2902_ = lean_ctor_get_uint8(v_s_2897_, sizeof(void*)*12);
v_pFinal_2903_ = lean_ctor_get_uint8(v_s_2897_, sizeof(void*)*12 + 1);
v_rJ_2904_ = lean_ctor_get(v_s_2897_, 3);
v_rK_2905_ = lean_ctor_get(v_s_2897_, 4);
v_rA_2906_ = lean_ctor_get(v_s_2897_, 5);
v_rP_2907_ = lean_ctor_get(v_s_2897_, 6);
v_charCash_2908_ = lean_ctor_get(v_s_2897_, 7);
v_charProp_2909_ = lean_ctor_get(v_s_2897_, 8);
v_cfChar_2910_ = lean_ctor_get(v_s_2897_, 9);
v_pledge_2911_ = lean_ctor_get(v_s_2897_, 10);
v_tax_2912_ = lean_ctor_get(v_s_2897_, 11);
v_isSharedCheck_2922_ = !lean_is_exclusive(v_s_2897_);
if (v_isSharedCheck_2922_ == 0)
{
lean_object* v_unused_2923_; 
v_unused_2923_ = lean_ctor_get(v_s_2897_, 2);
lean_dec(v_unused_2923_);
v___x_2914_ = v_s_2897_;
v_isShared_2915_ = v_isSharedCheck_2922_;
goto v_resetjp_2913_;
}
else
{
lean_inc(v_tax_2912_);
lean_inc(v_pledge_2911_);
lean_inc(v_cfChar_2910_);
lean_inc(v_charProp_2909_);
lean_inc(v_charCash_2908_);
lean_inc(v_rP_2907_);
lean_inc(v_rA_2906_);
lean_inc(v_rK_2905_);
lean_inc(v_rJ_2904_);
lean_inc(v_year_2901_);
lean_inc(v_lots_2900_);
lean_dec(v_s_2897_);
v___x_2914_ = lean_box(0);
v_isShared_2915_ = v_isSharedCheck_2922_;
goto v_resetjp_2913_;
}
v_resetjp_2913_:
{
lean_object* v___x_2916_; lean_object* v___x_2917_; lean_object* v___x_2918_; lean_object* v___x_2920_; 
v___x_2916_ = l_Legal_USTax_Hunt_Basis_norm(v_cfg_2896_, v_pAlive_2902_, v_l_2899_);
v___x_2917_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_touch___closed__0));
lean_inc(v_i_2898_);
lean_inc(v_lots_2900_);
v___x_2918_ = l___private_Init_Data_List_Impl_0__List_setTR_go___redArg(v_lots_2900_, v___x_2916_, v_lots_2900_, v_i_2898_, v___x_2917_);
lean_dec(v_lots_2900_);
if (v_isShared_2915_ == 0)
{
lean_ctor_set(v___x_2914_, 2, v_i_2898_);
lean_ctor_set(v___x_2914_, 0, v___x_2918_);
v___x_2920_ = v___x_2914_;
goto v_reusejp_2919_;
}
else
{
lean_object* v_reuseFailAlloc_2921_; 
v_reuseFailAlloc_2921_ = lean_alloc_ctor(0, 12, 2);
lean_ctor_set(v_reuseFailAlloc_2921_, 0, v___x_2918_);
lean_ctor_set(v_reuseFailAlloc_2921_, 1, v_year_2901_);
lean_ctor_set(v_reuseFailAlloc_2921_, 2, v_i_2898_);
lean_ctor_set(v_reuseFailAlloc_2921_, 3, v_rJ_2904_);
lean_ctor_set(v_reuseFailAlloc_2921_, 4, v_rK_2905_);
lean_ctor_set(v_reuseFailAlloc_2921_, 5, v_rA_2906_);
lean_ctor_set(v_reuseFailAlloc_2921_, 6, v_rP_2907_);
lean_ctor_set(v_reuseFailAlloc_2921_, 7, v_charCash_2908_);
lean_ctor_set(v_reuseFailAlloc_2921_, 8, v_charProp_2909_);
lean_ctor_set(v_reuseFailAlloc_2921_, 9, v_cfChar_2910_);
lean_ctor_set(v_reuseFailAlloc_2921_, 10, v_pledge_2911_);
lean_ctor_set(v_reuseFailAlloc_2921_, 11, v_tax_2912_);
lean_ctor_set_uint8(v_reuseFailAlloc_2921_, sizeof(void*)*12, v_pAlive_2902_);
lean_ctor_set_uint8(v_reuseFailAlloc_2921_, sizeof(void*)*12 + 1, v_pFinal_2903_);
v___x_2920_ = v_reuseFailAlloc_2921_;
goto v_reusejp_2919_;
}
v_reusejp_2919_:
{
return v___x_2920_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_touch___boxed(lean_object* v_cfg_2924_, lean_object* v_s_2925_, lean_object* v_i_2926_, lean_object* v_l_2927_){
_start:
{
lean_object* v_res_2928_; 
v_res_2928_ = l_Legal_USTax_Hunt_Basis_touch(v_cfg_2924_, v_s_2925_, v_i_2926_, v_l_2927_);
lean_dec_ref(v_cfg_2924_);
return v_res_2928_;
}
}
LEAN_EXPORT uint8_t l_Option_instBEq_beq___at___00Legal_USTax_Hunt_Basis_step_spec__0(lean_object* v_x_2929_, lean_object* v_x_2930_){
_start:
{
if (lean_obj_tag(v_x_2929_) == 0)
{
if (lean_obj_tag(v_x_2930_) == 0)
{
uint8_t v___x_2931_; 
v___x_2931_ = 1;
return v___x_2931_;
}
else
{
uint8_t v___x_2932_; 
v___x_2932_ = 0;
return v___x_2932_;
}
}
else
{
if (lean_obj_tag(v_x_2930_) == 0)
{
uint8_t v___x_2933_; 
v___x_2933_ = 0;
return v___x_2933_;
}
else
{
lean_object* v_val_2934_; lean_object* v_val_2935_; uint8_t v___x_2936_; 
v_val_2934_ = lean_ctor_get(v_x_2929_, 0);
v_val_2935_ = lean_ctor_get(v_x_2930_, 0);
v___x_2936_ = lean_nat_dec_eq(v_val_2934_, v_val_2935_);
return v___x_2936_;
}
}
}
}
LEAN_EXPORT lean_object* l_Option_instBEq_beq___at___00Legal_USTax_Hunt_Basis_step_spec__0___boxed(lean_object* v_x_2937_, lean_object* v_x_2938_){
_start:
{
uint8_t v_res_2939_; lean_object* v_r_2940_; 
v_res_2939_ = l_Option_instBEq_beq___at___00Legal_USTax_Hunt_Basis_step_spec__0(v_x_2937_, v_x_2938_);
lean_dec(v_x_2938_);
lean_dec(v_x_2937_);
v_r_2940_ = lean_box(v_res_2939_);
return v_r_2940_;
}
}
LEAN_EXPORT lean_object* l_List_mapTR_loop___at___00Legal_USTax_Hunt_Basis_step_spec__1(uint8_t v_heir_2941_, uint8_t v___x_2942_, lean_object* v_a_2943_, lean_object* v_a_2944_){
_start:
{
if (lean_obj_tag(v_a_2943_) == 0)
{
lean_object* v___x_2945_; 
v___x_2945_ = l_List_reverse___redArg(v_a_2944_);
return v___x_2945_;
}
else
{
lean_object* v_head_2946_; lean_object* v_tail_2947_; lean_object* v___x_2949_; uint8_t v_isShared_2950_; uint8_t v_isSharedCheck_2986_; 
v_head_2946_ = lean_ctor_get(v_a_2943_, 0);
v_tail_2947_ = lean_ctor_get(v_a_2943_, 1);
v_isSharedCheck_2986_ = !lean_is_exclusive(v_a_2943_);
if (v_isSharedCheck_2986_ == 0)
{
v___x_2949_ = v_a_2943_;
v_isShared_2950_ = v_isSharedCheck_2986_;
goto v_resetjp_2948_;
}
else
{
lean_inc(v_tail_2947_);
lean_inc(v_head_2946_);
lean_dec(v_a_2943_);
v___x_2949_ = lean_box(0);
v_isShared_2950_ = v_isSharedCheck_2986_;
goto v_resetjp_2948_;
}
v_resetjp_2948_:
{
lean_object* v___y_2952_; uint8_t v_kind_2957_; uint8_t v_owner_2958_; lean_object* v_fmv_2959_; lean_object* v_basis_2960_; lean_object* v_lossBasis_2961_; lean_object* v_held_2962_; lean_object* v_donor_2963_; lean_object* v_giftAge_2964_; uint8_t v_inherited_2965_; uint8_t v_gone_2966_; uint8_t v___y_2972_; 
v_kind_2957_ = lean_ctor_get_uint8(v_head_2946_, sizeof(void*)*8);
v_owner_2958_ = lean_ctor_get_uint8(v_head_2946_, sizeof(void*)*8 + 1);
v_fmv_2959_ = lean_ctor_get(v_head_2946_, 0);
v_basis_2960_ = lean_ctor_get(v_head_2946_, 1);
v_lossBasis_2961_ = lean_ctor_get(v_head_2946_, 2);
v_held_2962_ = lean_ctor_get(v_head_2946_, 3);
v_donor_2963_ = lean_ctor_get(v_head_2946_, 6);
v_giftAge_2964_ = lean_ctor_get(v_head_2946_, 7);
v_inherited_2965_ = lean_ctor_get_uint8(v_head_2946_, sizeof(void*)*8 + 2);
v_gone_2966_ = lean_ctor_get_uint8(v_head_2946_, sizeof(void*)*8 + 3);
if (v_gone_2966_ == 0)
{
uint8_t v___x_2976_; uint8_t v___x_2977_; 
v___x_2976_ = 4;
v___x_2977_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_owner_2958_, v___x_2976_);
if (v___x_2977_ == 0)
{
v___y_2952_ = v_head_2946_;
goto v___jp_2951_;
}
else
{
lean_inc(v_giftAge_2964_);
lean_inc(v_donor_2963_);
lean_inc(v_held_2962_);
lean_inc(v_lossBasis_2961_);
lean_inc(v_basis_2960_);
lean_inc(v_fmv_2959_);
lean_dec(v_head_2946_);
if (lean_obj_tag(v_donor_2963_) == 0)
{
lean_dec(v_lossBasis_2961_);
lean_dec(v_basis_2960_);
goto v___jp_2967_;
}
else
{
lean_object* v_val_2978_; lean_object* v___x_2979_; uint8_t v___x_2980_; 
v_val_2978_ = lean_ctor_get(v_donor_2963_, 0);
lean_inc(v_val_2978_);
lean_dec_ref_known(v_donor_2963_, 1);
v___x_2979_ = lean_unsigned_to_nat(0u);
v___x_2980_ = lean_nat_dec_eq(v_giftAge_2964_, v___x_2979_);
if (v___x_2980_ == 0)
{
lean_dec(v_val_2978_);
lean_dec(v_lossBasis_2961_);
lean_dec(v_basis_2960_);
goto v___jp_2967_;
}
else
{
uint8_t v___x_2981_; 
v___x_2981_ = lean_nat_dec_lt(v_basis_2960_, v_fmv_2959_);
if (v___x_2981_ == 0)
{
lean_dec(v_val_2978_);
lean_dec(v_lossBasis_2961_);
lean_dec(v_basis_2960_);
goto v___jp_2967_;
}
else
{
uint8_t v___x_2982_; uint8_t v___x_2983_; 
v___x_2982_ = lean_unbox(v_val_2978_);
v___x_2983_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v___x_2982_, v_heir_2941_);
if (v___x_2983_ == 0)
{
uint8_t v___x_2984_; uint8_t v___x_2985_; 
v___x_2984_ = lean_unbox(v_val_2978_);
lean_dec(v_val_2978_);
v___x_2985_ = l_Legal_USTax_Hunt_Basis_spouses(v___x_2984_, v_heir_2941_);
v___y_2972_ = v___x_2985_;
goto v___jp_2971_;
}
else
{
lean_dec(v_val_2978_);
v___y_2972_ = v___x_2983_;
goto v___jp_2971_;
}
}
}
}
}
}
else
{
v___y_2952_ = v_head_2946_;
goto v___jp_2951_;
}
v___jp_2951_:
{
lean_object* v___x_2954_; 
if (v_isShared_2950_ == 0)
{
lean_ctor_set(v___x_2949_, 1, v_a_2944_);
lean_ctor_set(v___x_2949_, 0, v___y_2952_);
v___x_2954_ = v___x_2949_;
goto v_reusejp_2953_;
}
else
{
lean_object* v_reuseFailAlloc_2956_; 
v_reuseFailAlloc_2956_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v_reuseFailAlloc_2956_, 0, v___y_2952_);
lean_ctor_set(v_reuseFailAlloc_2956_, 1, v_a_2944_);
v___x_2954_ = v_reuseFailAlloc_2956_;
goto v_reusejp_2953_;
}
v_reusejp_2953_:
{
v_a_2943_ = v_tail_2947_;
v_a_2944_ = v___x_2954_;
goto _start;
}
}
v___jp_2967_:
{
lean_object* v___x_2968_; lean_object* v___x_2969_; lean_object* v___x_2970_; 
v___x_2968_ = lean_unsigned_to_nat(0u);
v___x_2969_ = lean_box(0);
lean_inc_n(v_fmv_2959_, 2);
v___x_2970_ = lean_alloc_ctor(0, 8, 4);
lean_ctor_set(v___x_2970_, 0, v_fmv_2959_);
lean_ctor_set(v___x_2970_, 1, v_fmv_2959_);
lean_ctor_set(v___x_2970_, 2, v_fmv_2959_);
lean_ctor_set(v___x_2970_, 3, v_held_2962_);
lean_ctor_set(v___x_2970_, 4, v___x_2968_);
lean_ctor_set(v___x_2970_, 5, v___x_2968_);
lean_ctor_set(v___x_2970_, 6, v___x_2969_);
lean_ctor_set(v___x_2970_, 7, v_giftAge_2964_);
lean_ctor_set_uint8(v___x_2970_, sizeof(void*)*8, v_kind_2957_);
lean_ctor_set_uint8(v___x_2970_, sizeof(void*)*8 + 1, v_heir_2941_);
lean_ctor_set_uint8(v___x_2970_, sizeof(void*)*8 + 2, v___x_2942_);
lean_ctor_set_uint8(v___x_2970_, sizeof(void*)*8 + 3, v_gone_2966_);
v___y_2952_ = v___x_2970_;
goto v___jp_2951_;
}
v___jp_2971_:
{
if (v___y_2972_ == 0)
{
lean_dec(v_lossBasis_2961_);
lean_dec(v_basis_2960_);
goto v___jp_2967_;
}
else
{
lean_object* v___x_2973_; lean_object* v___x_2974_; lean_object* v___x_2975_; 
v___x_2973_ = lean_unsigned_to_nat(0u);
v___x_2974_ = lean_box(0);
v___x_2975_ = lean_alloc_ctor(0, 8, 4);
lean_ctor_set(v___x_2975_, 0, v_fmv_2959_);
lean_ctor_set(v___x_2975_, 1, v_basis_2960_);
lean_ctor_set(v___x_2975_, 2, v_lossBasis_2961_);
lean_ctor_set(v___x_2975_, 3, v_held_2962_);
lean_ctor_set(v___x_2975_, 4, v___x_2973_);
lean_ctor_set(v___x_2975_, 5, v___x_2973_);
lean_ctor_set(v___x_2975_, 6, v___x_2974_);
lean_ctor_set(v___x_2975_, 7, v_giftAge_2964_);
lean_ctor_set_uint8(v___x_2975_, sizeof(void*)*8, v_kind_2957_);
lean_ctor_set_uint8(v___x_2975_, sizeof(void*)*8 + 1, v_heir_2941_);
lean_ctor_set_uint8(v___x_2975_, sizeof(void*)*8 + 2, v_inherited_2965_);
lean_ctor_set_uint8(v___x_2975_, sizeof(void*)*8 + 3, v_gone_2966_);
v___y_2952_ = v___x_2975_;
goto v___jp_2951_;
}
}
}
}
}
}
LEAN_EXPORT lean_object* l_List_mapTR_loop___at___00Legal_USTax_Hunt_Basis_step_spec__1___boxed(lean_object* v_heir_2987_, lean_object* v___x_2988_, lean_object* v_a_2989_, lean_object* v_a_2990_){
_start:
{
uint8_t v_heir_4550__boxed_2991_; uint8_t v___x_4551__boxed_2992_; lean_object* v_res_2993_; 
v_heir_4550__boxed_2991_ = lean_unbox(v_heir_2987_);
v___x_4551__boxed_2992_ = lean_unbox(v___x_2988_);
v_res_2993_ = l_List_mapTR_loop___at___00Legal_USTax_Hunt_Basis_step_spec__1(v_heir_4550__boxed_2991_, v___x_4551__boxed_2992_, v_a_2989_, v_a_2990_);
return v_res_2993_;
}
}
LEAN_EXPORT lean_object* l_List_mapTR_loop___at___00Legal_USTax_Hunt_Basis_step_spec__2(lean_object* v_cfg_2994_, uint8_t v___x_2995_, lean_object* v_a_2996_, lean_object* v_a_2997_){
_start:
{
if (lean_obj_tag(v_a_2996_) == 0)
{
lean_object* v___x_2998_; 
v___x_2998_ = l_List_reverse___redArg(v_a_2997_);
return v___x_2998_;
}
else
{
lean_object* v_head_2999_; lean_object* v_tail_3000_; lean_object* v___x_3002_; uint8_t v_isShared_3003_; uint8_t v_isSharedCheck_3009_; 
v_head_2999_ = lean_ctor_get(v_a_2996_, 0);
v_tail_3000_ = lean_ctor_get(v_a_2996_, 1);
v_isSharedCheck_3009_ = !lean_is_exclusive(v_a_2996_);
if (v_isSharedCheck_3009_ == 0)
{
v___x_3002_ = v_a_2996_;
v_isShared_3003_ = v_isSharedCheck_3009_;
goto v_resetjp_3001_;
}
else
{
lean_inc(v_tail_3000_);
lean_inc(v_head_2999_);
lean_dec(v_a_2996_);
v___x_3002_ = lean_box(0);
v_isShared_3003_ = v_isSharedCheck_3009_;
goto v_resetjp_3001_;
}
v_resetjp_3001_:
{
lean_object* v___x_3004_; lean_object* v___x_3006_; 
v___x_3004_ = l_Legal_USTax_Hunt_Basis_norm(v_cfg_2994_, v___x_2995_, v_head_2999_);
if (v_isShared_3003_ == 0)
{
lean_ctor_set(v___x_3002_, 1, v_a_2997_);
lean_ctor_set(v___x_3002_, 0, v___x_3004_);
v___x_3006_ = v___x_3002_;
goto v_reusejp_3005_;
}
else
{
lean_object* v_reuseFailAlloc_3008_; 
v_reuseFailAlloc_3008_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v_reuseFailAlloc_3008_, 0, v___x_3004_);
lean_ctor_set(v_reuseFailAlloc_3008_, 1, v_a_2997_);
v___x_3006_ = v_reuseFailAlloc_3008_;
goto v_reusejp_3005_;
}
v_reusejp_3005_:
{
v_a_2996_ = v_tail_3000_;
v_a_2997_ = v___x_3006_;
goto _start;
}
}
}
}
}
LEAN_EXPORT lean_object* l_List_mapTR_loop___at___00Legal_USTax_Hunt_Basis_step_spec__2___boxed(lean_object* v_cfg_3010_, lean_object* v___x_3011_, lean_object* v_a_3012_, lean_object* v_a_3013_){
_start:
{
uint8_t v___x_4626__boxed_3014_; lean_object* v_res_3015_; 
v___x_4626__boxed_3014_ = lean_unbox(v___x_3011_);
v_res_3015_ = l_List_mapTR_loop___at___00Legal_USTax_Hunt_Basis_step_spec__2(v_cfg_3010_, v___x_4626__boxed_3014_, v_a_3012_, v_a_3013_);
lean_dec_ref(v_cfg_3010_);
return v_res_3015_;
}
}
LEAN_EXPORT uint8_t l_List_any___at___00Legal_USTax_Hunt_Basis_step_spec__3(lean_object* v___x_3016_, lean_object* v___x_3017_, uint8_t v___y_3018_, lean_object* v_x_3019_){
_start:
{
if (lean_obj_tag(v_x_3019_) == 0)
{
uint8_t v___x_3020_; 
v___x_3020_ = 0;
return v___x_3020_;
}
else
{
lean_object* v_head_3021_; lean_object* v_tail_3022_; uint8_t v___y_3024_; uint8_t v_gone_3026_; 
v_head_3021_ = lean_ctor_get(v_x_3019_, 0);
v_tail_3022_ = lean_ctor_get(v_x_3019_, 1);
v_gone_3026_ = lean_ctor_get_uint8(v_head_3021_, sizeof(void*)*8 + 3);
if (v_gone_3026_ == 0)
{
uint8_t v___x_3027_; 
v___x_3027_ = lean_nat_dec_eq(v___x_3016_, v___x_3017_);
v___y_3024_ = v___x_3027_;
goto v___jp_3023_;
}
else
{
v___y_3024_ = v___y_3018_;
goto v___jp_3023_;
}
v___jp_3023_:
{
if (v___y_3024_ == 0)
{
v_x_3019_ = v_tail_3022_;
goto _start;
}
else
{
return v___y_3024_;
}
}
}
}
}
LEAN_EXPORT lean_object* l_List_any___at___00Legal_USTax_Hunt_Basis_step_spec__3___boxed(lean_object* v___x_3028_, lean_object* v___x_3029_, lean_object* v___y_3030_, lean_object* v_x_3031_){
_start:
{
uint8_t v___y_4661__boxed_3032_; uint8_t v_res_3033_; lean_object* v_r_3034_; 
v___y_4661__boxed_3032_ = lean_unbox(v___y_3030_);
v_res_3033_ = l_List_any___at___00Legal_USTax_Hunt_Basis_step_spec__3(v___x_3028_, v___x_3029_, v___y_4661__boxed_3032_, v_x_3031_);
lean_dec(v_x_3031_);
lean_dec(v___x_3029_);
lean_dec(v___x_3028_);
v_r_3034_ = lean_box(v_res_3033_);
return v_r_3034_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_step(lean_object* v_cfg_3035_, lean_object* v_s_3036_, lean_object* v_x_3037_){
_start:
{
switch(lean_obj_tag(v_x_3037_))
{
case 0:
{
lean_object* v_i_3038_; lean_object* v_lots_3039_; lean_object* v_year_3040_; lean_object* v_cur_3041_; lean_object* v___x_3042_; 
v_i_3038_ = lean_ctor_get(v_x_3037_, 0);
lean_inc_n(v_i_3038_, 2);
lean_dec_ref_known(v_x_3037_, 1);
v_lots_3039_ = lean_ctor_get(v_s_3036_, 0);
v_year_3040_ = lean_ctor_get(v_s_3036_, 1);
v_cur_3041_ = lean_ctor_get(v_s_3036_, 2);
v___x_3042_ = l_List_get_x3fInternal___redArg(v_lots_3039_, v_i_3038_);
if (lean_obj_tag(v___x_3042_) == 0)
{
lean_object* v___x_3043_; 
lean_dec(v_i_3038_);
lean_dec_ref(v_s_3036_);
v___x_3043_ = lean_box(0);
return v___x_3043_;
}
else
{
lean_object* v_val_3044_; lean_object* v___x_3046_; uint8_t v_isShared_3047_; uint8_t v_isSharedCheck_3079_; 
v_val_3044_ = lean_ctor_get(v___x_3042_, 0);
v_isSharedCheck_3079_ = !lean_is_exclusive(v___x_3042_);
if (v_isSharedCheck_3079_ == 0)
{
v___x_3046_ = v___x_3042_;
v_isShared_3047_ = v_isSharedCheck_3079_;
goto v_resetjp_3045_;
}
else
{
lean_inc(v_val_3044_);
lean_dec(v___x_3042_);
v___x_3046_ = lean_box(0);
v_isShared_3047_ = v_isSharedCheck_3079_;
goto v_resetjp_3045_;
}
v_resetjp_3045_:
{
uint8_t v_gone_3048_; 
v_gone_3048_ = lean_ctor_get_uint8(v_val_3044_, sizeof(void*)*8 + 3);
if (v_gone_3048_ == 0)
{
uint8_t v_kind_3049_; uint8_t v_owner_3050_; lean_object* v_fmv_3051_; lean_object* v_basis_3052_; lean_object* v_lossBasis_3053_; lean_object* v_held_3054_; lean_object* v_owned_3055_; lean_object* v_shield_3056_; lean_object* v_donor_3057_; lean_object* v_giftAge_3058_; uint8_t v_inherited_3059_; uint8_t v___x_3060_; 
v_kind_3049_ = lean_ctor_get_uint8(v_val_3044_, sizeof(void*)*8);
v_owner_3050_ = lean_ctor_get_uint8(v_val_3044_, sizeof(void*)*8 + 1);
v_fmv_3051_ = lean_ctor_get(v_val_3044_, 0);
lean_inc(v_fmv_3051_);
v_basis_3052_ = lean_ctor_get(v_val_3044_, 1);
lean_inc(v_basis_3052_);
v_lossBasis_3053_ = lean_ctor_get(v_val_3044_, 2);
lean_inc(v_lossBasis_3053_);
v_held_3054_ = lean_ctor_get(v_val_3044_, 3);
lean_inc(v_held_3054_);
v_owned_3055_ = lean_ctor_get(v_val_3044_, 4);
lean_inc(v_owned_3055_);
v_shield_3056_ = lean_ctor_get(v_val_3044_, 5);
lean_inc(v_shield_3056_);
v_donor_3057_ = lean_ctor_get(v_val_3044_, 6);
lean_inc(v_donor_3057_);
v_giftAge_3058_ = lean_ctor_get(v_val_3044_, 7);
lean_inc(v_giftAge_3058_);
v_inherited_3059_ = lean_ctor_get_uint8(v_val_3044_, sizeof(void*)*8 + 2);
v___x_3060_ = lean_nat_dec_lt(v_i_3038_, v_cur_3041_);
if (v___x_3060_ == 0)
{
uint8_t v___x_3061_; 
v___x_3061_ = l_Legal_USTax_Hunt_Basis_alive(v_s_3036_, v_owner_3050_);
if (v___x_3061_ == 0)
{
lean_object* v___x_3070_; 
lean_dec(v_giftAge_3058_);
lean_dec(v_donor_3057_);
lean_dec(v_shield_3056_);
lean_dec(v_owned_3055_);
lean_dec(v_held_3054_);
lean_dec(v_lossBasis_3053_);
lean_dec(v_basis_3052_);
lean_dec(v_fmv_3051_);
lean_del_object(v___x_3046_);
lean_dec(v_val_3044_);
lean_dec(v_i_3038_);
lean_dec_ref(v_s_3036_);
v___x_3070_ = lean_box(0);
return v___x_3070_;
}
else
{
uint8_t v_hold_3071_; 
v_hold_3071_ = lean_ctor_get_uint8(v_cfg_3035_, sizeof(void*)*6);
if (v_hold_3071_ == 0)
{
goto v___jp_3062_;
}
else
{
lean_object* v_horizon_3072_; lean_object* v___x_3073_; lean_object* v___x_3074_; uint8_t v___x_3075_; 
v_horizon_3072_ = lean_ctor_get(v_cfg_3035_, 4);
v___x_3073_ = lean_unsigned_to_nat(1u);
v___x_3074_ = lean_nat_add(v_year_3040_, v___x_3073_);
v___x_3075_ = lean_nat_dec_eq(v___x_3074_, v_horizon_3072_);
lean_dec(v___x_3074_);
if (v___x_3075_ == 0)
{
lean_object* v___x_3076_; 
lean_dec(v_giftAge_3058_);
lean_dec(v_donor_3057_);
lean_dec(v_shield_3056_);
lean_dec(v_owned_3055_);
lean_dec(v_held_3054_);
lean_dec(v_lossBasis_3053_);
lean_dec(v_basis_3052_);
lean_dec(v_fmv_3051_);
lean_del_object(v___x_3046_);
lean_dec(v_val_3044_);
lean_dec(v_i_3038_);
lean_dec_ref(v_s_3036_);
v___x_3076_ = lean_box(0);
return v___x_3076_;
}
else
{
goto v___jp_3062_;
}
}
}
v___jp_3062_:
{
lean_object* v___x_3063_; lean_object* v_fst_3064_; lean_object* v___x_3065_; lean_object* v___x_3066_; lean_object* v___x_3068_; 
v___x_3063_ = l_Legal_USTax_Hunt_Basis_recognize(v_cfg_3035_, v_s_3036_, v_val_3044_, v___x_3061_);
v_fst_3064_ = lean_ctor_get(v___x_3063_, 0);
lean_inc(v_fst_3064_);
lean_dec_ref(v___x_3063_);
v___x_3065_ = lean_alloc_ctor(0, 8, 4);
lean_ctor_set(v___x_3065_, 0, v_fmv_3051_);
lean_ctor_set(v___x_3065_, 1, v_basis_3052_);
lean_ctor_set(v___x_3065_, 2, v_lossBasis_3053_);
lean_ctor_set(v___x_3065_, 3, v_held_3054_);
lean_ctor_set(v___x_3065_, 4, v_owned_3055_);
lean_ctor_set(v___x_3065_, 5, v_shield_3056_);
lean_ctor_set(v___x_3065_, 6, v_donor_3057_);
lean_ctor_set(v___x_3065_, 7, v_giftAge_3058_);
lean_ctor_set_uint8(v___x_3065_, sizeof(void*)*8, v_kind_3049_);
lean_ctor_set_uint8(v___x_3065_, sizeof(void*)*8 + 1, v_owner_3050_);
lean_ctor_set_uint8(v___x_3065_, sizeof(void*)*8 + 2, v_inherited_3059_);
lean_ctor_set_uint8(v___x_3065_, sizeof(void*)*8 + 3, v___x_3061_);
v___x_3066_ = l_Legal_USTax_Hunt_Basis_touch(v_cfg_3035_, v_fst_3064_, v_i_3038_, v___x_3065_);
if (v_isShared_3047_ == 0)
{
lean_ctor_set(v___x_3046_, 0, v___x_3066_);
v___x_3068_ = v___x_3046_;
goto v_reusejp_3067_;
}
else
{
lean_object* v_reuseFailAlloc_3069_; 
v_reuseFailAlloc_3069_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v_reuseFailAlloc_3069_, 0, v___x_3066_);
v___x_3068_ = v_reuseFailAlloc_3069_;
goto v_reusejp_3067_;
}
v_reusejp_3067_:
{
return v___x_3068_;
}
}
}
else
{
lean_object* v___x_3077_; 
lean_dec(v_giftAge_3058_);
lean_dec(v_donor_3057_);
lean_dec(v_shield_3056_);
lean_dec(v_owned_3055_);
lean_dec(v_held_3054_);
lean_dec(v_lossBasis_3053_);
lean_dec(v_basis_3052_);
lean_dec(v_fmv_3051_);
lean_del_object(v___x_3046_);
lean_dec(v_val_3044_);
lean_dec(v_i_3038_);
lean_dec_ref(v_s_3036_);
v___x_3077_ = lean_box(0);
return v___x_3077_;
}
}
else
{
lean_object* v___x_3078_; 
lean_del_object(v___x_3046_);
lean_dec(v_val_3044_);
lean_dec(v_i_3038_);
lean_dec_ref(v_s_3036_);
v___x_3078_ = lean_box(0);
return v___x_3078_;
}
}
}
}
case 1:
{
lean_object* v_i_3080_; uint8_t v_to_3081_; lean_object* v_lots_3082_; lean_object* v_cur_3083_; lean_object* v___x_3084_; 
v_i_3080_ = lean_ctor_get(v_x_3037_, 0);
lean_inc_n(v_i_3080_, 2);
v_to_3081_ = lean_ctor_get_uint8(v_x_3037_, sizeof(void*)*1);
lean_dec_ref_known(v_x_3037_, 1);
v_lots_3082_ = lean_ctor_get(v_s_3036_, 0);
v_cur_3083_ = lean_ctor_get(v_s_3036_, 2);
v___x_3084_ = l_List_get_x3fInternal___redArg(v_lots_3082_, v_i_3080_);
if (lean_obj_tag(v___x_3084_) == 0)
{
lean_object* v___x_3085_; 
lean_dec(v_i_3080_);
lean_dec_ref(v_s_3036_);
v___x_3085_ = lean_box(0);
return v___x_3085_;
}
else
{
lean_object* v_val_3086_; lean_object* v___x_3088_; uint8_t v_isShared_3089_; uint8_t v_isSharedCheck_3138_; 
v_val_3086_ = lean_ctor_get(v___x_3084_, 0);
v_isSharedCheck_3138_ = !lean_is_exclusive(v___x_3084_);
if (v_isSharedCheck_3138_ == 0)
{
v___x_3088_ = v___x_3084_;
v_isShared_3089_ = v_isSharedCheck_3138_;
goto v_resetjp_3087_;
}
else
{
lean_inc(v_val_3086_);
lean_dec(v___x_3084_);
v___x_3088_ = lean_box(0);
v_isShared_3089_ = v_isSharedCheck_3138_;
goto v_resetjp_3087_;
}
v_resetjp_3087_:
{
uint8_t v_kind_3090_; uint8_t v_owner_3091_; lean_object* v_fmv_3092_; lean_object* v_basis_3093_; lean_object* v_lossBasis_3094_; lean_object* v_held_3095_; lean_object* v_owned_3096_; uint8_t v_inherited_3097_; uint8_t v_gone_3098_; lean_object* v___x_3100_; uint8_t v_isShared_3101_; uint8_t v_isSharedCheck_3134_; 
v_kind_3090_ = lean_ctor_get_uint8(v_val_3086_, sizeof(void*)*8);
v_owner_3091_ = lean_ctor_get_uint8(v_val_3086_, sizeof(void*)*8 + 1);
v_fmv_3092_ = lean_ctor_get(v_val_3086_, 0);
v_basis_3093_ = lean_ctor_get(v_val_3086_, 1);
v_lossBasis_3094_ = lean_ctor_get(v_val_3086_, 2);
v_held_3095_ = lean_ctor_get(v_val_3086_, 3);
v_owned_3096_ = lean_ctor_get(v_val_3086_, 4);
v_inherited_3097_ = lean_ctor_get_uint8(v_val_3086_, sizeof(void*)*8 + 2);
v_gone_3098_ = lean_ctor_get_uint8(v_val_3086_, sizeof(void*)*8 + 3);
v_isSharedCheck_3134_ = !lean_is_exclusive(v_val_3086_);
if (v_isSharedCheck_3134_ == 0)
{
lean_object* v_unused_3135_; lean_object* v_unused_3136_; lean_object* v_unused_3137_; 
v_unused_3135_ = lean_ctor_get(v_val_3086_, 7);
lean_dec(v_unused_3135_);
v_unused_3136_ = lean_ctor_get(v_val_3086_, 6);
lean_dec(v_unused_3136_);
v_unused_3137_ = lean_ctor_get(v_val_3086_, 5);
lean_dec(v_unused_3137_);
v___x_3100_ = v_val_3086_;
v_isShared_3101_ = v_isSharedCheck_3134_;
goto v_resetjp_3099_;
}
else
{
lean_inc(v_owned_3096_);
lean_inc(v_held_3095_);
lean_inc(v_lossBasis_3094_);
lean_inc(v_basis_3093_);
lean_inc(v_fmv_3092_);
lean_dec(v_val_3086_);
v___x_3100_ = lean_box(0);
v_isShared_3101_ = v_isSharedCheck_3134_;
goto v_resetjp_3099_;
}
v_resetjp_3099_:
{
lean_object* v___y_3103_; 
if (v_gone_3098_ == 0)
{
uint8_t v___x_3114_; 
v___x_3114_ = lean_nat_dec_lt(v_i_3080_, v_cur_3083_);
if (v___x_3114_ == 0)
{
uint8_t v___x_3115_; 
v___x_3115_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_owner_3091_, v_to_3081_);
if (v___x_3115_ == 0)
{
uint8_t v___x_3116_; uint8_t v___x_3117_; 
v___x_3116_ = 2;
v___x_3117_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_owner_3091_, v___x_3116_);
if (v___x_3117_ == 0)
{
uint8_t v___x_3118_; 
v___x_3118_ = l_Legal_USTax_Hunt_Basis_alive(v_s_3036_, v_owner_3091_);
if (v___x_3118_ == 0)
{
lean_object* v___x_3119_; 
lean_del_object(v___x_3100_);
lean_dec(v_owned_3096_);
lean_dec(v_held_3095_);
lean_dec(v_lossBasis_3094_);
lean_dec(v_basis_3093_);
lean_dec(v_fmv_3092_);
lean_del_object(v___x_3088_);
lean_dec(v_i_3080_);
lean_dec_ref(v_s_3036_);
v___x_3119_ = lean_box(0);
return v___x_3119_;
}
else
{
uint8_t v___x_3120_; 
v___x_3120_ = l_Legal_USTax_Hunt_Basis_alive(v_s_3036_, v_to_3081_);
if (v___x_3120_ == 0)
{
lean_object* v___x_3121_; 
lean_del_object(v___x_3100_);
lean_dec(v_owned_3096_);
lean_dec(v_held_3095_);
lean_dec(v_lossBasis_3094_);
lean_dec(v_basis_3093_);
lean_dec(v_fmv_3092_);
lean_del_object(v___x_3088_);
lean_dec(v_i_3080_);
lean_dec_ref(v_s_3036_);
v___x_3121_ = lean_box(0);
return v___x_3121_;
}
else
{
uint8_t v___x_3122_; 
v___x_3122_ = l_Legal_USTax_Hunt_Basis_spouses(v_owner_3091_, v_to_3081_);
if (v___x_3122_ == 0)
{
uint8_t v___x_3123_; 
lean_dec(v_owned_3096_);
v___x_3123_ = lean_nat_dec_le(v_lossBasis_3094_, v_fmv_3092_);
if (v___x_3123_ == 0)
{
lean_dec(v_lossBasis_3094_);
lean_inc(v_fmv_3092_);
v___y_3103_ = v_fmv_3092_;
goto v___jp_3102_;
}
else
{
v___y_3103_ = v_lossBasis_3094_;
goto v___jp_3102_;
}
}
else
{
lean_object* v___x_3124_; lean_object* v___x_3125_; lean_object* v___x_3126_; lean_object* v___x_3127_; lean_object* v___x_3128_; lean_object* v___x_3129_; 
lean_del_object(v___x_3100_);
lean_del_object(v___x_3088_);
v___x_3124_ = lean_unsigned_to_nat(0u);
v___x_3125_ = lean_box(v_owner_3091_);
v___x_3126_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v___x_3126_, 0, v___x_3125_);
v___x_3127_ = lean_alloc_ctor(0, 8, 4);
lean_ctor_set(v___x_3127_, 0, v_fmv_3092_);
lean_ctor_set(v___x_3127_, 1, v_basis_3093_);
lean_ctor_set(v___x_3127_, 2, v_lossBasis_3094_);
lean_ctor_set(v___x_3127_, 3, v_held_3095_);
lean_ctor_set(v___x_3127_, 4, v_owned_3096_);
lean_ctor_set(v___x_3127_, 5, v___x_3124_);
lean_ctor_set(v___x_3127_, 6, v___x_3126_);
lean_ctor_set(v___x_3127_, 7, v___x_3124_);
lean_ctor_set_uint8(v___x_3127_, sizeof(void*)*8, v_kind_3090_);
lean_ctor_set_uint8(v___x_3127_, sizeof(void*)*8 + 1, v_to_3081_);
lean_ctor_set_uint8(v___x_3127_, sizeof(void*)*8 + 2, v_inherited_3097_);
lean_ctor_set_uint8(v___x_3127_, sizeof(void*)*8 + 3, v_gone_3098_);
v___x_3128_ = l_Legal_USTax_Hunt_Basis_touch(v_cfg_3035_, v_s_3036_, v_i_3080_, v___x_3127_);
v___x_3129_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v___x_3129_, 0, v___x_3128_);
return v___x_3129_;
}
}
}
}
else
{
lean_object* v___x_3130_; 
lean_del_object(v___x_3100_);
lean_dec(v_owned_3096_);
lean_dec(v_held_3095_);
lean_dec(v_lossBasis_3094_);
lean_dec(v_basis_3093_);
lean_dec(v_fmv_3092_);
lean_del_object(v___x_3088_);
lean_dec(v_i_3080_);
lean_dec_ref(v_s_3036_);
v___x_3130_ = lean_box(0);
return v___x_3130_;
}
}
else
{
lean_object* v___x_3131_; 
lean_del_object(v___x_3100_);
lean_dec(v_owned_3096_);
lean_dec(v_held_3095_);
lean_dec(v_lossBasis_3094_);
lean_dec(v_basis_3093_);
lean_dec(v_fmv_3092_);
lean_del_object(v___x_3088_);
lean_dec(v_i_3080_);
lean_dec_ref(v_s_3036_);
v___x_3131_ = lean_box(0);
return v___x_3131_;
}
}
else
{
lean_object* v___x_3132_; 
lean_del_object(v___x_3100_);
lean_dec(v_owned_3096_);
lean_dec(v_held_3095_);
lean_dec(v_lossBasis_3094_);
lean_dec(v_basis_3093_);
lean_dec(v_fmv_3092_);
lean_del_object(v___x_3088_);
lean_dec(v_i_3080_);
lean_dec_ref(v_s_3036_);
v___x_3132_ = lean_box(0);
return v___x_3132_;
}
}
else
{
lean_object* v___x_3133_; 
lean_del_object(v___x_3100_);
lean_dec(v_owned_3096_);
lean_dec(v_held_3095_);
lean_dec(v_lossBasis_3094_);
lean_dec(v_basis_3093_);
lean_dec(v_fmv_3092_);
lean_del_object(v___x_3088_);
lean_dec(v_i_3080_);
lean_dec_ref(v_s_3036_);
v___x_3133_ = lean_box(0);
return v___x_3133_;
}
v___jp_3102_:
{
lean_object* v___x_3104_; lean_object* v___x_3105_; lean_object* v___x_3107_; 
v___x_3104_ = lean_unsigned_to_nat(0u);
v___x_3105_ = lean_box(v_owner_3091_);
if (v_isShared_3089_ == 0)
{
lean_ctor_set(v___x_3088_, 0, v___x_3105_);
v___x_3107_ = v___x_3088_;
goto v_reusejp_3106_;
}
else
{
lean_object* v_reuseFailAlloc_3113_; 
v_reuseFailAlloc_3113_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v_reuseFailAlloc_3113_, 0, v___x_3105_);
v___x_3107_ = v_reuseFailAlloc_3113_;
goto v_reusejp_3106_;
}
v_reusejp_3106_:
{
lean_object* v___x_3109_; 
if (v_isShared_3101_ == 0)
{
lean_ctor_set(v___x_3100_, 7, v___x_3104_);
lean_ctor_set(v___x_3100_, 6, v___x_3107_);
lean_ctor_set(v___x_3100_, 5, v___x_3104_);
lean_ctor_set(v___x_3100_, 4, v___x_3104_);
lean_ctor_set(v___x_3100_, 2, v___y_3103_);
v___x_3109_ = v___x_3100_;
goto v_reusejp_3108_;
}
else
{
lean_object* v_reuseFailAlloc_3112_; 
v_reuseFailAlloc_3112_ = lean_alloc_ctor(0, 8, 4);
lean_ctor_set(v_reuseFailAlloc_3112_, 0, v_fmv_3092_);
lean_ctor_set(v_reuseFailAlloc_3112_, 1, v_basis_3093_);
lean_ctor_set(v_reuseFailAlloc_3112_, 2, v___y_3103_);
lean_ctor_set(v_reuseFailAlloc_3112_, 3, v_held_3095_);
lean_ctor_set(v_reuseFailAlloc_3112_, 4, v___x_3104_);
lean_ctor_set(v_reuseFailAlloc_3112_, 5, v___x_3104_);
lean_ctor_set(v_reuseFailAlloc_3112_, 6, v___x_3107_);
lean_ctor_set(v_reuseFailAlloc_3112_, 7, v___x_3104_);
lean_ctor_set_uint8(v_reuseFailAlloc_3112_, sizeof(void*)*8, v_kind_3090_);
lean_ctor_set_uint8(v_reuseFailAlloc_3112_, sizeof(void*)*8 + 2, v_inherited_3097_);
lean_ctor_set_uint8(v_reuseFailAlloc_3112_, sizeof(void*)*8 + 3, v_gone_3098_);
v___x_3109_ = v_reuseFailAlloc_3112_;
goto v_reusejp_3108_;
}
v_reusejp_3108_:
{
lean_object* v___x_3110_; lean_object* v___x_3111_; 
lean_ctor_set_uint8(v___x_3109_, sizeof(void*)*8 + 1, v_to_3081_);
v___x_3110_ = l_Legal_USTax_Hunt_Basis_touch(v_cfg_3035_, v_s_3036_, v_i_3080_, v___x_3109_);
v___x_3111_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v___x_3111_, 0, v___x_3110_);
return v___x_3111_;
}
}
}
}
}
}
}
case 2:
{
lean_object* v_i_3139_; uint8_t v_to_3140_; lean_object* v_lots_3141_; lean_object* v_cur_3142_; lean_object* v___x_3143_; 
v_i_3139_ = lean_ctor_get(v_x_3037_, 0);
lean_inc_n(v_i_3139_, 2);
v_to_3140_ = lean_ctor_get_uint8(v_x_3037_, sizeof(void*)*1);
lean_dec_ref_known(v_x_3037_, 1);
v_lots_3141_ = lean_ctor_get(v_s_3036_, 0);
v_cur_3142_ = lean_ctor_get(v_s_3036_, 2);
v___x_3143_ = l_List_get_x3fInternal___redArg(v_lots_3141_, v_i_3139_);
if (lean_obj_tag(v___x_3143_) == 0)
{
lean_object* v___x_3144_; 
lean_dec(v_i_3139_);
lean_dec_ref(v_s_3036_);
v___x_3144_ = lean_box(0);
return v___x_3144_;
}
else
{
lean_object* v_val_3145_; lean_object* v___x_3147_; uint8_t v_isShared_3148_; uint8_t v_isSharedCheck_3184_; 
v_val_3145_ = lean_ctor_get(v___x_3143_, 0);
v_isSharedCheck_3184_ = !lean_is_exclusive(v___x_3143_);
if (v_isSharedCheck_3184_ == 0)
{
v___x_3147_ = v___x_3143_;
v_isShared_3148_ = v_isSharedCheck_3184_;
goto v_resetjp_3146_;
}
else
{
lean_inc(v_val_3145_);
lean_dec(v___x_3143_);
v___x_3147_ = lean_box(0);
v_isShared_3148_ = v_isSharedCheck_3184_;
goto v_resetjp_3146_;
}
v_resetjp_3146_:
{
uint8_t v_kind_3149_; uint8_t v_owner_3150_; lean_object* v_fmv_3151_; lean_object* v_lossBasis_3152_; uint8_t v_gone_3153_; uint8_t v___y_3155_; uint8_t v___y_3156_; 
v_kind_3149_ = lean_ctor_get_uint8(v_val_3145_, sizeof(void*)*8);
v_owner_3150_ = lean_ctor_get_uint8(v_val_3145_, sizeof(void*)*8 + 1);
v_fmv_3151_ = lean_ctor_get(v_val_3145_, 0);
lean_inc(v_fmv_3151_);
v_lossBasis_3152_ = lean_ctor_get(v_val_3145_, 2);
v_gone_3153_ = lean_ctor_get_uint8(v_val_3145_, sizeof(void*)*8 + 3);
if (v_gone_3153_ == 0)
{
uint8_t v___x_3167_; 
v___x_3167_ = lean_nat_dec_lt(v_i_3139_, v_cur_3142_);
if (v___x_3167_ == 0)
{
uint8_t v___x_3168_; 
v___x_3168_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_owner_3150_, v_to_3140_);
if (v___x_3168_ == 0)
{
uint8_t v___x_3169_; 
v___x_3169_ = l_Legal_USTax_Hunt_Basis_spouses(v_owner_3150_, v_to_3140_);
if (v___x_3169_ == 0)
{
uint8_t v___x_3170_; 
v___x_3170_ = l_Legal_USTax_Hunt_Basis_alive(v_s_3036_, v_owner_3150_);
if (v___x_3170_ == 0)
{
lean_object* v___x_3171_; 
lean_dec(v_fmv_3151_);
lean_del_object(v___x_3147_);
lean_dec(v_val_3145_);
lean_dec(v_i_3139_);
lean_dec_ref(v_s_3036_);
v___x_3171_ = lean_box(0);
return v___x_3171_;
}
else
{
uint8_t v___x_3172_; uint8_t v___y_3174_; 
v___x_3172_ = l_Legal_USTax_Hunt_Basis_alive(v_s_3036_, v_to_3140_);
if (v___x_3172_ == 0)
{
lean_object* v___x_3176_; 
lean_dec(v_fmv_3151_);
lean_del_object(v___x_3147_);
lean_dec(v_val_3145_);
lean_dec(v_i_3139_);
lean_dec_ref(v_s_3036_);
v___x_3176_ = lean_box(0);
return v___x_3176_;
}
else
{
uint8_t v___x_3177_; 
v___x_3177_ = lean_nat_dec_lt(v_fmv_3151_, v_lossBasis_3152_);
if (v___x_3177_ == 0)
{
uint8_t v_hold_3178_; 
v_hold_3178_ = lean_ctor_get_uint8(v_cfg_3035_, sizeof(void*)*6);
if (v_hold_3178_ == 0)
{
lean_object* v___x_3179_; 
lean_dec(v_fmv_3151_);
lean_del_object(v___x_3147_);
lean_dec(v_val_3145_);
lean_dec(v_i_3139_);
lean_dec_ref(v_s_3036_);
v___x_3179_ = lean_box(0);
return v___x_3179_;
}
else
{
v___y_3174_ = v___x_3169_;
goto v___jp_3173_;
}
}
else
{
v___y_3174_ = v___x_3169_;
goto v___jp_3173_;
}
}
v___jp_3173_:
{
uint8_t v___x_3175_; 
v___x_3175_ = l_Legal_USTax_Hunt_Basis_related267(v_owner_3150_, v_to_3140_);
if (v___x_3175_ == 0)
{
v___y_3155_ = v___y_3174_;
v___y_3156_ = v___x_3172_;
goto v___jp_3154_;
}
else
{
v___y_3155_ = v___y_3174_;
v___y_3156_ = v___y_3174_;
goto v___jp_3154_;
}
}
}
}
else
{
lean_object* v___x_3180_; 
lean_dec(v_fmv_3151_);
lean_del_object(v___x_3147_);
lean_dec(v_val_3145_);
lean_dec(v_i_3139_);
lean_dec_ref(v_s_3036_);
v___x_3180_ = lean_box(0);
return v___x_3180_;
}
}
else
{
lean_object* v___x_3181_; 
lean_dec(v_fmv_3151_);
lean_del_object(v___x_3147_);
lean_dec(v_val_3145_);
lean_dec(v_i_3139_);
lean_dec_ref(v_s_3036_);
v___x_3181_ = lean_box(0);
return v___x_3181_;
}
}
else
{
lean_object* v___x_3182_; 
lean_dec(v_fmv_3151_);
lean_del_object(v___x_3147_);
lean_dec(v_val_3145_);
lean_dec(v_i_3139_);
lean_dec_ref(v_s_3036_);
v___x_3182_ = lean_box(0);
return v___x_3182_;
}
}
else
{
lean_object* v___x_3183_; 
lean_dec(v_fmv_3151_);
lean_del_object(v___x_3147_);
lean_dec(v_val_3145_);
lean_dec(v_i_3139_);
lean_dec_ref(v_s_3036_);
v___x_3183_ = lean_box(0);
return v___x_3183_;
}
v___jp_3154_:
{
lean_object* v___x_3157_; lean_object* v_fst_3158_; lean_object* v_snd_3159_; lean_object* v___x_3160_; lean_object* v___x_3161_; lean_object* v___x_3162_; lean_object* v___x_3163_; lean_object* v___x_3165_; 
v___x_3157_ = l_Legal_USTax_Hunt_Basis_recognize(v_cfg_3035_, v_s_3036_, v_val_3145_, v___y_3156_);
v_fst_3158_ = lean_ctor_get(v___x_3157_, 0);
lean_inc(v_fst_3158_);
v_snd_3159_ = lean_ctor_get(v___x_3157_, 1);
lean_inc(v_snd_3159_);
lean_dec_ref(v___x_3157_);
v___x_3160_ = lean_unsigned_to_nat(0u);
v___x_3161_ = lean_box(0);
lean_inc_n(v_fmv_3151_, 2);
v___x_3162_ = lean_alloc_ctor(0, 8, 4);
lean_ctor_set(v___x_3162_, 0, v_fmv_3151_);
lean_ctor_set(v___x_3162_, 1, v_fmv_3151_);
lean_ctor_set(v___x_3162_, 2, v_fmv_3151_);
lean_ctor_set(v___x_3162_, 3, v___x_3160_);
lean_ctor_set(v___x_3162_, 4, v___x_3160_);
lean_ctor_set(v___x_3162_, 5, v_snd_3159_);
lean_ctor_set(v___x_3162_, 6, v___x_3161_);
lean_ctor_set(v___x_3162_, 7, v___x_3160_);
lean_ctor_set_uint8(v___x_3162_, sizeof(void*)*8, v_kind_3149_);
lean_ctor_set_uint8(v___x_3162_, sizeof(void*)*8 + 1, v_to_3140_);
lean_ctor_set_uint8(v___x_3162_, sizeof(void*)*8 + 2, v___y_3155_);
lean_ctor_set_uint8(v___x_3162_, sizeof(void*)*8 + 3, v_gone_3153_);
v___x_3163_ = l_Legal_USTax_Hunt_Basis_touch(v_cfg_3035_, v_fst_3158_, v_i_3139_, v___x_3162_);
if (v_isShared_3148_ == 0)
{
lean_ctor_set(v___x_3147_, 0, v___x_3163_);
v___x_3165_ = v___x_3147_;
goto v_reusejp_3164_;
}
else
{
lean_object* v_reuseFailAlloc_3166_; 
v_reuseFailAlloc_3166_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v_reuseFailAlloc_3166_, 0, v___x_3163_);
v___x_3165_ = v_reuseFailAlloc_3166_;
goto v_reusejp_3164_;
}
v_reusejp_3164_:
{
return v___x_3165_;
}
}
}
}
}
case 3:
{
lean_object* v_i_3185_; lean_object* v___x_3187_; uint8_t v_isShared_3188_; uint8_t v_isSharedCheck_3286_; 
v_i_3185_ = lean_ctor_get(v_x_3037_, 0);
v_isSharedCheck_3286_ = !lean_is_exclusive(v_x_3037_);
if (v_isSharedCheck_3286_ == 0)
{
v___x_3187_ = v_x_3037_;
v_isShared_3188_ = v_isSharedCheck_3286_;
goto v_resetjp_3186_;
}
else
{
lean_inc(v_i_3185_);
lean_dec(v_x_3037_);
v___x_3187_ = lean_box(0);
v_isShared_3188_ = v_isSharedCheck_3286_;
goto v_resetjp_3186_;
}
v_resetjp_3186_:
{
lean_object* v___y_3190_; lean_object* v___y_3191_; uint8_t v___y_3192_; lean_object* v___y_3193_; lean_object* v___y_3194_; uint8_t v___y_3195_; uint8_t v___y_3196_; lean_object* v___y_3197_; uint8_t v___y_3198_; lean_object* v___y_3199_; lean_object* v___y_3200_; lean_object* v___y_3201_; lean_object* v___y_3202_; lean_object* v_lots_3208_; lean_object* v_year_3209_; lean_object* v_cur_3210_; uint8_t v_pAlive_3211_; uint8_t v_pFinal_3212_; lean_object* v_rJ_3213_; lean_object* v_rK_3214_; lean_object* v_rA_3215_; lean_object* v_rP_3216_; lean_object* v_charCash_3217_; lean_object* v_charProp_3218_; lean_object* v_cfChar_3219_; lean_object* v_pledge_3220_; lean_object* v_tax_3221_; lean_object* v___x_3223_; uint8_t v_isShared_3224_; uint8_t v_isSharedCheck_3285_; 
v_lots_3208_ = lean_ctor_get(v_s_3036_, 0);
v_year_3209_ = lean_ctor_get(v_s_3036_, 1);
v_cur_3210_ = lean_ctor_get(v_s_3036_, 2);
v_pAlive_3211_ = lean_ctor_get_uint8(v_s_3036_, sizeof(void*)*12);
v_pFinal_3212_ = lean_ctor_get_uint8(v_s_3036_, sizeof(void*)*12 + 1);
v_rJ_3213_ = lean_ctor_get(v_s_3036_, 3);
v_rK_3214_ = lean_ctor_get(v_s_3036_, 4);
v_rA_3215_ = lean_ctor_get(v_s_3036_, 5);
v_rP_3216_ = lean_ctor_get(v_s_3036_, 6);
v_charCash_3217_ = lean_ctor_get(v_s_3036_, 7);
v_charProp_3218_ = lean_ctor_get(v_s_3036_, 8);
v_cfChar_3219_ = lean_ctor_get(v_s_3036_, 9);
v_pledge_3220_ = lean_ctor_get(v_s_3036_, 10);
v_tax_3221_ = lean_ctor_get(v_s_3036_, 11);
v_isSharedCheck_3285_ = !lean_is_exclusive(v_s_3036_);
if (v_isSharedCheck_3285_ == 0)
{
v___x_3223_ = v_s_3036_;
v_isShared_3224_ = v_isSharedCheck_3285_;
goto v_resetjp_3222_;
}
else
{
lean_inc(v_tax_3221_);
lean_inc(v_pledge_3220_);
lean_inc(v_cfChar_3219_);
lean_inc(v_charProp_3218_);
lean_inc(v_charCash_3217_);
lean_inc(v_rP_3216_);
lean_inc(v_rA_3215_);
lean_inc(v_rK_3214_);
lean_inc(v_rJ_3213_);
lean_inc(v_cur_3210_);
lean_inc(v_year_3209_);
lean_inc(v_lots_3208_);
lean_dec(v_s_3036_);
v___x_3223_ = lean_box(0);
v_isShared_3224_ = v_isSharedCheck_3285_;
goto v_resetjp_3222_;
}
v___jp_3189_:
{
lean_object* v___x_3203_; lean_object* v___x_3204_; lean_object* v___x_3206_; 
v___x_3203_ = lean_alloc_ctor(0, 8, 4);
lean_ctor_set(v___x_3203_, 0, v___y_3194_);
lean_ctor_set(v___x_3203_, 1, v___y_3201_);
lean_ctor_set(v___x_3203_, 2, v___y_3199_);
lean_ctor_set(v___x_3203_, 3, v___y_3193_);
lean_ctor_set(v___x_3203_, 4, v___y_3191_);
lean_ctor_set(v___x_3203_, 5, v___y_3200_);
lean_ctor_set(v___x_3203_, 6, v___y_3197_);
lean_ctor_set(v___x_3203_, 7, v___y_3190_);
lean_ctor_set_uint8(v___x_3203_, sizeof(void*)*8, v___y_3196_);
lean_ctor_set_uint8(v___x_3203_, sizeof(void*)*8 + 1, v___y_3195_);
lean_ctor_set_uint8(v___x_3203_, sizeof(void*)*8 + 2, v___y_3192_);
lean_ctor_set_uint8(v___x_3203_, sizeof(void*)*8 + 3, v___y_3198_);
v___x_3204_ = l_Legal_USTax_Hunt_Basis_touch(v_cfg_3035_, v___y_3202_, v_i_3185_, v___x_3203_);
if (v_isShared_3188_ == 0)
{
lean_ctor_set_tag(v___x_3187_, 1);
lean_ctor_set(v___x_3187_, 0, v___x_3204_);
v___x_3206_ = v___x_3187_;
goto v_reusejp_3205_;
}
else
{
lean_object* v_reuseFailAlloc_3207_; 
v_reuseFailAlloc_3207_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v_reuseFailAlloc_3207_, 0, v___x_3204_);
v___x_3206_ = v_reuseFailAlloc_3207_;
goto v_reusejp_3205_;
}
v_reusejp_3205_:
{
return v___x_3206_;
}
}
v_resetjp_3222_:
{
lean_object* v___y_3226_; lean_object* v___y_3227_; uint8_t v___y_3228_; lean_object* v___y_3229_; uint8_t v___y_3230_; lean_object* v___y_3231_; uint8_t v___y_3232_; lean_object* v___y_3233_; uint8_t v___y_3234_; lean_object* v___y_3235_; lean_object* v___y_3236_; lean_object* v___y_3237_; uint8_t v___y_3238_; lean_object* v___x_3253_; 
lean_inc(v_i_3185_);
v___x_3253_ = l_List_get_x3fInternal___redArg(v_lots_3208_, v_i_3185_);
if (lean_obj_tag(v___x_3253_) == 0)
{
lean_object* v___x_3254_; 
lean_del_object(v___x_3223_);
lean_dec(v_tax_3221_);
lean_dec(v_pledge_3220_);
lean_dec(v_cfChar_3219_);
lean_dec(v_charProp_3218_);
lean_dec(v_charCash_3217_);
lean_dec_ref(v_rP_3216_);
lean_dec_ref(v_rA_3215_);
lean_dec_ref(v_rK_3214_);
lean_dec_ref(v_rJ_3213_);
lean_dec(v_cur_3210_);
lean_dec(v_year_3209_);
lean_dec(v_lots_3208_);
lean_del_object(v___x_3187_);
lean_dec(v_i_3185_);
v___x_3254_ = lean_box(0);
return v___x_3254_;
}
else
{
lean_object* v_val_3255_; uint8_t v_kind_3256_; uint8_t v_owner_3257_; lean_object* v_fmv_3258_; lean_object* v_basis_3259_; lean_object* v_lossBasis_3260_; lean_object* v_held_3261_; lean_object* v_owned_3262_; lean_object* v_shield_3263_; lean_object* v_donor_3264_; lean_object* v_giftAge_3265_; uint8_t v_inherited_3266_; uint8_t v_gone_3267_; uint8_t v___y_3269_; 
v_val_3255_ = lean_ctor_get(v___x_3253_, 0);
lean_inc(v_val_3255_);
lean_dec_ref_known(v___x_3253_, 1);
v_kind_3256_ = lean_ctor_get_uint8(v_val_3255_, sizeof(void*)*8);
v_owner_3257_ = lean_ctor_get_uint8(v_val_3255_, sizeof(void*)*8 + 1);
v_fmv_3258_ = lean_ctor_get(v_val_3255_, 0);
lean_inc(v_fmv_3258_);
v_basis_3259_ = lean_ctor_get(v_val_3255_, 1);
lean_inc(v_basis_3259_);
v_lossBasis_3260_ = lean_ctor_get(v_val_3255_, 2);
lean_inc(v_lossBasis_3260_);
v_held_3261_ = lean_ctor_get(v_val_3255_, 3);
lean_inc(v_held_3261_);
v_owned_3262_ = lean_ctor_get(v_val_3255_, 4);
lean_inc(v_owned_3262_);
v_shield_3263_ = lean_ctor_get(v_val_3255_, 5);
lean_inc(v_shield_3263_);
v_donor_3264_ = lean_ctor_get(v_val_3255_, 6);
lean_inc(v_donor_3264_);
v_giftAge_3265_ = lean_ctor_get(v_val_3255_, 7);
lean_inc(v_giftAge_3265_);
v_inherited_3266_ = lean_ctor_get_uint8(v_val_3255_, sizeof(void*)*8 + 2);
v_gone_3267_ = lean_ctor_get_uint8(v_val_3255_, sizeof(void*)*8 + 3);
lean_dec(v_val_3255_);
if (v_gone_3267_ == 0)
{
uint8_t v___x_3278_; 
v___x_3278_ = lean_nat_dec_lt(v_i_3185_, v_cur_3210_);
if (v___x_3278_ == 0)
{
uint8_t v___x_3279_; uint8_t v___x_3280_; 
v___x_3279_ = 0;
v___x_3280_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_owner_3257_, v___x_3279_);
if (v___x_3280_ == 0)
{
uint8_t v___x_3281_; uint8_t v___x_3282_; 
v___x_3281_ = 1;
v___x_3282_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_owner_3257_, v___x_3281_);
v___y_3269_ = v___x_3282_;
goto v___jp_3268_;
}
else
{
v___y_3269_ = v___x_3280_;
goto v___jp_3268_;
}
}
else
{
lean_object* v___x_3283_; 
lean_dec(v_giftAge_3265_);
lean_dec(v_donor_3264_);
lean_dec(v_shield_3263_);
lean_dec(v_owned_3262_);
lean_dec(v_held_3261_);
lean_dec(v_lossBasis_3260_);
lean_dec(v_basis_3259_);
lean_dec(v_fmv_3258_);
lean_del_object(v___x_3223_);
lean_dec(v_tax_3221_);
lean_dec(v_pledge_3220_);
lean_dec(v_cfChar_3219_);
lean_dec(v_charProp_3218_);
lean_dec(v_charCash_3217_);
lean_dec_ref(v_rP_3216_);
lean_dec_ref(v_rA_3215_);
lean_dec_ref(v_rK_3214_);
lean_dec_ref(v_rJ_3213_);
lean_dec(v_cur_3210_);
lean_dec(v_year_3209_);
lean_dec(v_lots_3208_);
lean_del_object(v___x_3187_);
lean_dec(v_i_3185_);
v___x_3283_ = lean_box(0);
return v___x_3283_;
}
}
else
{
lean_object* v___x_3284_; 
lean_dec(v_giftAge_3265_);
lean_dec(v_donor_3264_);
lean_dec(v_shield_3263_);
lean_dec(v_owned_3262_);
lean_dec(v_held_3261_);
lean_dec(v_lossBasis_3260_);
lean_dec(v_basis_3259_);
lean_dec(v_fmv_3258_);
lean_del_object(v___x_3223_);
lean_dec(v_tax_3221_);
lean_dec(v_pledge_3220_);
lean_dec(v_cfChar_3219_);
lean_dec(v_charProp_3218_);
lean_dec(v_charCash_3217_);
lean_dec_ref(v_rP_3216_);
lean_dec_ref(v_rA_3215_);
lean_dec_ref(v_rK_3214_);
lean_dec_ref(v_rJ_3213_);
lean_dec(v_cur_3210_);
lean_dec(v_year_3209_);
lean_dec(v_lots_3208_);
lean_del_object(v___x_3187_);
lean_dec(v_i_3185_);
v___x_3284_ = lean_box(0);
return v___x_3284_;
}
v___jp_3268_:
{
if (v___y_3269_ == 0)
{
lean_object* v___x_3270_; 
lean_dec(v_giftAge_3265_);
lean_dec(v_donor_3264_);
lean_dec(v_shield_3263_);
lean_dec(v_owned_3262_);
lean_dec(v_held_3261_);
lean_dec(v_lossBasis_3260_);
lean_dec(v_basis_3259_);
lean_dec(v_fmv_3258_);
lean_del_object(v___x_3223_);
lean_dec(v_tax_3221_);
lean_dec(v_pledge_3220_);
lean_dec(v_cfChar_3219_);
lean_dec(v_charProp_3218_);
lean_dec(v_charCash_3217_);
lean_dec_ref(v_rP_3216_);
lean_dec_ref(v_rA_3215_);
lean_dec_ref(v_rK_3214_);
lean_dec_ref(v_rJ_3213_);
lean_dec(v_cur_3210_);
lean_dec(v_year_3209_);
lean_dec(v_lots_3208_);
lean_del_object(v___x_3187_);
lean_dec(v_i_3185_);
v___x_3270_ = lean_box(0);
return v___x_3270_;
}
else
{
uint8_t v___x_3271_; uint8_t v___x_3272_; 
v___x_3271_ = 0;
v___x_3272_ = l_Legal_USTax_Hunt_Basis_instBEqKind_beq(v_kind_3256_, v___x_3271_);
if (v___x_3272_ == 0)
{
lean_object* v___x_3273_; 
lean_dec(v_giftAge_3265_);
lean_dec(v_donor_3264_);
lean_dec(v_shield_3263_);
lean_dec(v_owned_3262_);
lean_dec(v_held_3261_);
lean_dec(v_lossBasis_3260_);
lean_dec(v_basis_3259_);
lean_dec(v_fmv_3258_);
lean_del_object(v___x_3223_);
lean_dec(v_tax_3221_);
lean_dec(v_pledge_3220_);
lean_dec(v_cfChar_3219_);
lean_dec(v_charProp_3218_);
lean_dec(v_charCash_3217_);
lean_dec_ref(v_rP_3216_);
lean_dec_ref(v_rA_3215_);
lean_dec_ref(v_rK_3214_);
lean_dec_ref(v_rJ_3213_);
lean_dec(v_cur_3210_);
lean_dec(v_year_3209_);
lean_dec(v_lots_3208_);
lean_del_object(v___x_3187_);
lean_dec(v_i_3185_);
v___x_3273_ = lean_box(0);
return v___x_3273_;
}
else
{
uint8_t v___x_3274_; 
v___x_3274_ = lean_nat_dec_lt(v_pledge_3220_, v_fmv_3258_);
if (v___x_3274_ == 0)
{
lean_object* v___x_3275_; uint8_t v___x_3276_; 
v___x_3275_ = lean_unsigned_to_nat(1u);
v___x_3276_ = lean_nat_dec_le(v___x_3275_, v_held_3261_);
if (v___x_3276_ == 0)
{
v___y_3226_ = v_giftAge_3265_;
v___y_3227_ = v_owned_3262_;
v___y_3228_ = v_owner_3257_;
v___y_3229_ = v_held_3261_;
v___y_3230_ = v_inherited_3266_;
v___y_3231_ = v_fmv_3258_;
v___y_3232_ = v_kind_3256_;
v___y_3233_ = v_donor_3264_;
v___y_3234_ = v___x_3272_;
v___y_3235_ = v_lossBasis_3260_;
v___y_3236_ = v_basis_3259_;
v___y_3237_ = v_shield_3263_;
v___y_3238_ = v_inherited_3266_;
goto v___jp_3225_;
}
else
{
v___y_3226_ = v_giftAge_3265_;
v___y_3227_ = v_owned_3262_;
v___y_3228_ = v_owner_3257_;
v___y_3229_ = v_held_3261_;
v___y_3230_ = v_inherited_3266_;
v___y_3231_ = v_fmv_3258_;
v___y_3232_ = v_kind_3256_;
v___y_3233_ = v_donor_3264_;
v___y_3234_ = v___x_3272_;
v___y_3235_ = v_lossBasis_3260_;
v___y_3236_ = v_basis_3259_;
v___y_3237_ = v_shield_3263_;
v___y_3238_ = v___x_3276_;
goto v___jp_3225_;
}
}
else
{
lean_object* v___x_3277_; 
lean_dec(v_giftAge_3265_);
lean_dec(v_donor_3264_);
lean_dec(v_shield_3263_);
lean_dec(v_owned_3262_);
lean_dec(v_held_3261_);
lean_dec(v_lossBasis_3260_);
lean_dec(v_basis_3259_);
lean_dec(v_fmv_3258_);
lean_del_object(v___x_3223_);
lean_dec(v_tax_3221_);
lean_dec(v_pledge_3220_);
lean_dec(v_cfChar_3219_);
lean_dec(v_charProp_3218_);
lean_dec(v_charCash_3217_);
lean_dec_ref(v_rP_3216_);
lean_dec_ref(v_rA_3215_);
lean_dec_ref(v_rK_3214_);
lean_dec_ref(v_rJ_3213_);
lean_dec(v_cur_3210_);
lean_dec(v_year_3209_);
lean_dec(v_lots_3208_);
lean_del_object(v___x_3187_);
lean_dec(v_i_3185_);
v___x_3277_ = lean_box(0);
return v___x_3277_;
}
}
}
}
}
v___jp_3225_:
{
lean_object* v___x_3239_; uint8_t v___x_3240_; 
v___x_3239_ = lean_nat_sub(v_pledge_3220_, v___y_3231_);
lean_dec(v_pledge_3220_);
v___x_3240_ = lean_nat_dec_lt(v___y_3236_, v___y_3231_);
if (v___x_3240_ == 0)
{
lean_object* v___x_3241_; lean_object* v___x_3243_; 
v___x_3241_ = lean_nat_add(v_charCash_3217_, v___y_3231_);
lean_dec(v_charCash_3217_);
if (v_isShared_3224_ == 0)
{
lean_ctor_set(v___x_3223_, 10, v___x_3239_);
lean_ctor_set(v___x_3223_, 7, v___x_3241_);
v___x_3243_ = v___x_3223_;
goto v_reusejp_3242_;
}
else
{
lean_object* v_reuseFailAlloc_3244_; 
v_reuseFailAlloc_3244_ = lean_alloc_ctor(0, 12, 2);
lean_ctor_set(v_reuseFailAlloc_3244_, 0, v_lots_3208_);
lean_ctor_set(v_reuseFailAlloc_3244_, 1, v_year_3209_);
lean_ctor_set(v_reuseFailAlloc_3244_, 2, v_cur_3210_);
lean_ctor_set(v_reuseFailAlloc_3244_, 3, v_rJ_3213_);
lean_ctor_set(v_reuseFailAlloc_3244_, 4, v_rK_3214_);
lean_ctor_set(v_reuseFailAlloc_3244_, 5, v_rA_3215_);
lean_ctor_set(v_reuseFailAlloc_3244_, 6, v_rP_3216_);
lean_ctor_set(v_reuseFailAlloc_3244_, 7, v___x_3241_);
lean_ctor_set(v_reuseFailAlloc_3244_, 8, v_charProp_3218_);
lean_ctor_set(v_reuseFailAlloc_3244_, 9, v_cfChar_3219_);
lean_ctor_set(v_reuseFailAlloc_3244_, 10, v___x_3239_);
lean_ctor_set(v_reuseFailAlloc_3244_, 11, v_tax_3221_);
lean_ctor_set_uint8(v_reuseFailAlloc_3244_, sizeof(void*)*12, v_pAlive_3211_);
lean_ctor_set_uint8(v_reuseFailAlloc_3244_, sizeof(void*)*12 + 1, v_pFinal_3212_);
v___x_3243_ = v_reuseFailAlloc_3244_;
goto v_reusejp_3242_;
}
v_reusejp_3242_:
{
v___y_3190_ = v___y_3226_;
v___y_3191_ = v___y_3227_;
v___y_3192_ = v___y_3230_;
v___y_3193_ = v___y_3229_;
v___y_3194_ = v___y_3231_;
v___y_3195_ = v___y_3228_;
v___y_3196_ = v___y_3232_;
v___y_3197_ = v___y_3233_;
v___y_3198_ = v___y_3234_;
v___y_3199_ = v___y_3235_;
v___y_3200_ = v___y_3237_;
v___y_3201_ = v___y_3236_;
v___y_3202_ = v___x_3243_;
goto v___jp_3189_;
}
}
else
{
if (v___y_3238_ == 0)
{
lean_object* v___x_3245_; lean_object* v___x_3247_; 
v___x_3245_ = lean_nat_add(v_charCash_3217_, v___y_3236_);
lean_dec(v_charCash_3217_);
if (v_isShared_3224_ == 0)
{
lean_ctor_set(v___x_3223_, 10, v___x_3239_);
lean_ctor_set(v___x_3223_, 7, v___x_3245_);
v___x_3247_ = v___x_3223_;
goto v_reusejp_3246_;
}
else
{
lean_object* v_reuseFailAlloc_3248_; 
v_reuseFailAlloc_3248_ = lean_alloc_ctor(0, 12, 2);
lean_ctor_set(v_reuseFailAlloc_3248_, 0, v_lots_3208_);
lean_ctor_set(v_reuseFailAlloc_3248_, 1, v_year_3209_);
lean_ctor_set(v_reuseFailAlloc_3248_, 2, v_cur_3210_);
lean_ctor_set(v_reuseFailAlloc_3248_, 3, v_rJ_3213_);
lean_ctor_set(v_reuseFailAlloc_3248_, 4, v_rK_3214_);
lean_ctor_set(v_reuseFailAlloc_3248_, 5, v_rA_3215_);
lean_ctor_set(v_reuseFailAlloc_3248_, 6, v_rP_3216_);
lean_ctor_set(v_reuseFailAlloc_3248_, 7, v___x_3245_);
lean_ctor_set(v_reuseFailAlloc_3248_, 8, v_charProp_3218_);
lean_ctor_set(v_reuseFailAlloc_3248_, 9, v_cfChar_3219_);
lean_ctor_set(v_reuseFailAlloc_3248_, 10, v___x_3239_);
lean_ctor_set(v_reuseFailAlloc_3248_, 11, v_tax_3221_);
lean_ctor_set_uint8(v_reuseFailAlloc_3248_, sizeof(void*)*12, v_pAlive_3211_);
lean_ctor_set_uint8(v_reuseFailAlloc_3248_, sizeof(void*)*12 + 1, v_pFinal_3212_);
v___x_3247_ = v_reuseFailAlloc_3248_;
goto v_reusejp_3246_;
}
v_reusejp_3246_:
{
v___y_3190_ = v___y_3226_;
v___y_3191_ = v___y_3227_;
v___y_3192_ = v___y_3230_;
v___y_3193_ = v___y_3229_;
v___y_3194_ = v___y_3231_;
v___y_3195_ = v___y_3228_;
v___y_3196_ = v___y_3232_;
v___y_3197_ = v___y_3233_;
v___y_3198_ = v___y_3234_;
v___y_3199_ = v___y_3235_;
v___y_3200_ = v___y_3237_;
v___y_3201_ = v___y_3236_;
v___y_3202_ = v___x_3247_;
goto v___jp_3189_;
}
}
else
{
lean_object* v___x_3249_; lean_object* v___x_3251_; 
v___x_3249_ = lean_nat_add(v_charProp_3218_, v___y_3231_);
lean_dec(v_charProp_3218_);
if (v_isShared_3224_ == 0)
{
lean_ctor_set(v___x_3223_, 10, v___x_3239_);
lean_ctor_set(v___x_3223_, 8, v___x_3249_);
v___x_3251_ = v___x_3223_;
goto v_reusejp_3250_;
}
else
{
lean_object* v_reuseFailAlloc_3252_; 
v_reuseFailAlloc_3252_ = lean_alloc_ctor(0, 12, 2);
lean_ctor_set(v_reuseFailAlloc_3252_, 0, v_lots_3208_);
lean_ctor_set(v_reuseFailAlloc_3252_, 1, v_year_3209_);
lean_ctor_set(v_reuseFailAlloc_3252_, 2, v_cur_3210_);
lean_ctor_set(v_reuseFailAlloc_3252_, 3, v_rJ_3213_);
lean_ctor_set(v_reuseFailAlloc_3252_, 4, v_rK_3214_);
lean_ctor_set(v_reuseFailAlloc_3252_, 5, v_rA_3215_);
lean_ctor_set(v_reuseFailAlloc_3252_, 6, v_rP_3216_);
lean_ctor_set(v_reuseFailAlloc_3252_, 7, v_charCash_3217_);
lean_ctor_set(v_reuseFailAlloc_3252_, 8, v___x_3249_);
lean_ctor_set(v_reuseFailAlloc_3252_, 9, v_cfChar_3219_);
lean_ctor_set(v_reuseFailAlloc_3252_, 10, v___x_3239_);
lean_ctor_set(v_reuseFailAlloc_3252_, 11, v_tax_3221_);
lean_ctor_set_uint8(v_reuseFailAlloc_3252_, sizeof(void*)*12, v_pAlive_3211_);
lean_ctor_set_uint8(v_reuseFailAlloc_3252_, sizeof(void*)*12 + 1, v_pFinal_3212_);
v___x_3251_ = v_reuseFailAlloc_3252_;
goto v_reusejp_3250_;
}
v_reusejp_3250_:
{
v___y_3190_ = v___y_3226_;
v___y_3191_ = v___y_3227_;
v___y_3192_ = v___y_3230_;
v___y_3193_ = v___y_3229_;
v___y_3194_ = v___y_3231_;
v___y_3195_ = v___y_3228_;
v___y_3196_ = v___y_3232_;
v___y_3197_ = v___y_3233_;
v___y_3198_ = v___y_3234_;
v___y_3199_ = v___y_3235_;
v___y_3200_ = v___y_3237_;
v___y_3201_ = v___y_3236_;
v___y_3202_ = v___x_3251_;
goto v___jp_3189_;
}
}
}
}
}
}
}
case 4:
{
lean_object* v_lots_3287_; lean_object* v_year_3288_; lean_object* v_cur_3289_; uint8_t v_pAlive_3290_; uint8_t v_pFinal_3291_; lean_object* v_rJ_3292_; lean_object* v_rK_3293_; lean_object* v_rA_3294_; lean_object* v_rP_3295_; lean_object* v_charCash_3296_; lean_object* v_charProp_3297_; lean_object* v_cfChar_3298_; lean_object* v_pledge_3299_; lean_object* v_tax_3300_; lean_object* v___x_3302_; uint8_t v_isShared_3303_; uint8_t v_isSharedCheck_3312_; 
v_lots_3287_ = lean_ctor_get(v_s_3036_, 0);
v_year_3288_ = lean_ctor_get(v_s_3036_, 1);
v_cur_3289_ = lean_ctor_get(v_s_3036_, 2);
v_pAlive_3290_ = lean_ctor_get_uint8(v_s_3036_, sizeof(void*)*12);
v_pFinal_3291_ = lean_ctor_get_uint8(v_s_3036_, sizeof(void*)*12 + 1);
v_rJ_3292_ = lean_ctor_get(v_s_3036_, 3);
v_rK_3293_ = lean_ctor_get(v_s_3036_, 4);
v_rA_3294_ = lean_ctor_get(v_s_3036_, 5);
v_rP_3295_ = lean_ctor_get(v_s_3036_, 6);
v_charCash_3296_ = lean_ctor_get(v_s_3036_, 7);
v_charProp_3297_ = lean_ctor_get(v_s_3036_, 8);
v_cfChar_3298_ = lean_ctor_get(v_s_3036_, 9);
v_pledge_3299_ = lean_ctor_get(v_s_3036_, 10);
v_tax_3300_ = lean_ctor_get(v_s_3036_, 11);
v_isSharedCheck_3312_ = !lean_is_exclusive(v_s_3036_);
if (v_isSharedCheck_3312_ == 0)
{
v___x_3302_ = v_s_3036_;
v_isShared_3303_ = v_isSharedCheck_3312_;
goto v_resetjp_3301_;
}
else
{
lean_inc(v_tax_3300_);
lean_inc(v_pledge_3299_);
lean_inc(v_cfChar_3298_);
lean_inc(v_charProp_3297_);
lean_inc(v_charCash_3296_);
lean_inc(v_rP_3295_);
lean_inc(v_rA_3294_);
lean_inc(v_rK_3293_);
lean_inc(v_rJ_3292_);
lean_inc(v_cur_3289_);
lean_inc(v_year_3288_);
lean_inc(v_lots_3287_);
lean_dec(v_s_3036_);
v___x_3302_ = lean_box(0);
v_isShared_3303_ = v_isSharedCheck_3312_;
goto v_resetjp_3301_;
}
v_resetjp_3301_:
{
lean_object* v___x_3304_; uint8_t v___x_3305_; 
v___x_3304_ = lean_unsigned_to_nat(0u);
v___x_3305_ = lean_nat_dec_eq(v_pledge_3299_, v___x_3304_);
if (v___x_3305_ == 0)
{
lean_object* v___x_3306_; lean_object* v___x_3308_; 
v___x_3306_ = lean_nat_add(v_charCash_3296_, v_pledge_3299_);
lean_dec(v_pledge_3299_);
lean_dec(v_charCash_3296_);
if (v_isShared_3303_ == 0)
{
lean_ctor_set(v___x_3302_, 10, v___x_3304_);
lean_ctor_set(v___x_3302_, 7, v___x_3306_);
v___x_3308_ = v___x_3302_;
goto v_reusejp_3307_;
}
else
{
lean_object* v_reuseFailAlloc_3310_; 
v_reuseFailAlloc_3310_ = lean_alloc_ctor(0, 12, 2);
lean_ctor_set(v_reuseFailAlloc_3310_, 0, v_lots_3287_);
lean_ctor_set(v_reuseFailAlloc_3310_, 1, v_year_3288_);
lean_ctor_set(v_reuseFailAlloc_3310_, 2, v_cur_3289_);
lean_ctor_set(v_reuseFailAlloc_3310_, 3, v_rJ_3292_);
lean_ctor_set(v_reuseFailAlloc_3310_, 4, v_rK_3293_);
lean_ctor_set(v_reuseFailAlloc_3310_, 5, v_rA_3294_);
lean_ctor_set(v_reuseFailAlloc_3310_, 6, v_rP_3295_);
lean_ctor_set(v_reuseFailAlloc_3310_, 7, v___x_3306_);
lean_ctor_set(v_reuseFailAlloc_3310_, 8, v_charProp_3297_);
lean_ctor_set(v_reuseFailAlloc_3310_, 9, v_cfChar_3298_);
lean_ctor_set(v_reuseFailAlloc_3310_, 10, v___x_3304_);
lean_ctor_set(v_reuseFailAlloc_3310_, 11, v_tax_3300_);
lean_ctor_set_uint8(v_reuseFailAlloc_3310_, sizeof(void*)*12, v_pAlive_3290_);
lean_ctor_set_uint8(v_reuseFailAlloc_3310_, sizeof(void*)*12 + 1, v_pFinal_3291_);
v___x_3308_ = v_reuseFailAlloc_3310_;
goto v_reusejp_3307_;
}
v_reusejp_3307_:
{
lean_object* v___x_3309_; 
v___x_3309_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v___x_3309_, 0, v___x_3308_);
return v___x_3309_;
}
}
else
{
lean_object* v___x_3311_; 
lean_del_object(v___x_3302_);
lean_dec(v_tax_3300_);
lean_dec(v_pledge_3299_);
lean_dec(v_cfChar_3298_);
lean_dec(v_charProp_3297_);
lean_dec(v_charCash_3296_);
lean_dec_ref(v_rP_3295_);
lean_dec_ref(v_rA_3294_);
lean_dec_ref(v_rK_3293_);
lean_dec_ref(v_rJ_3292_);
lean_dec(v_cur_3289_);
lean_dec(v_year_3288_);
lean_dec(v_lots_3287_);
v___x_3311_ = lean_box(0);
return v___x_3311_;
}
}
}
case 5:
{
uint8_t v_pAlive_3313_; 
v_pAlive_3313_ = lean_ctor_get_uint8(v_s_3036_, sizeof(void*)*12);
if (v_pAlive_3313_ == 0)
{
lean_object* v___x_3314_; 
lean_dec_ref_known(v_x_3037_, 0);
lean_dec_ref(v_s_3036_);
v___x_3314_ = lean_box(0);
return v___x_3314_;
}
else
{
uint8_t v_heir_3315_; lean_object* v_lots_3316_; lean_object* v_year_3317_; lean_object* v_rJ_3318_; lean_object* v_rK_3319_; lean_object* v_rA_3320_; lean_object* v_rP_3321_; lean_object* v_charCash_3322_; lean_object* v_charProp_3323_; lean_object* v_cfChar_3324_; lean_object* v_pledge_3325_; lean_object* v_tax_3326_; lean_object* v___x_3328_; uint8_t v_isShared_3329_; uint8_t v_isSharedCheck_3348_; 
v_heir_3315_ = lean_ctor_get_uint8(v_x_3037_, 0);
lean_dec_ref_known(v_x_3037_, 0);
v_lots_3316_ = lean_ctor_get(v_s_3036_, 0);
v_year_3317_ = lean_ctor_get(v_s_3036_, 1);
v_rJ_3318_ = lean_ctor_get(v_s_3036_, 3);
v_rK_3319_ = lean_ctor_get(v_s_3036_, 4);
v_rA_3320_ = lean_ctor_get(v_s_3036_, 5);
v_rP_3321_ = lean_ctor_get(v_s_3036_, 6);
v_charCash_3322_ = lean_ctor_get(v_s_3036_, 7);
v_charProp_3323_ = lean_ctor_get(v_s_3036_, 8);
v_cfChar_3324_ = lean_ctor_get(v_s_3036_, 9);
v_pledge_3325_ = lean_ctor_get(v_s_3036_, 10);
v_tax_3326_ = lean_ctor_get(v_s_3036_, 11);
v_isSharedCheck_3348_ = !lean_is_exclusive(v_s_3036_);
if (v_isSharedCheck_3348_ == 0)
{
lean_object* v_unused_3349_; 
v_unused_3349_ = lean_ctor_get(v_s_3036_, 2);
lean_dec(v_unused_3349_);
v___x_3328_ = v_s_3036_;
v_isShared_3329_ = v_isSharedCheck_3348_;
goto v_resetjp_3327_;
}
else
{
lean_inc(v_tax_3326_);
lean_inc(v_pledge_3325_);
lean_inc(v_cfChar_3324_);
lean_inc(v_charProp_3323_);
lean_inc(v_charCash_3322_);
lean_inc(v_rP_3321_);
lean_inc(v_rA_3320_);
lean_inc(v_rK_3319_);
lean_inc(v_rJ_3318_);
lean_inc(v_year_3317_);
lean_inc(v_lots_3316_);
lean_dec(v_s_3036_);
v___x_3328_ = lean_box(0);
v_isShared_3329_ = v_isSharedCheck_3348_;
goto v_resetjp_3327_;
}
v_resetjp_3327_:
{
lean_object* v_death_3330_; lean_object* v___x_3331_; uint8_t v___x_3332_; 
v_death_3330_ = lean_ctor_get(v_cfg_3035_, 3);
lean_inc(v_year_3317_);
v___x_3331_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v___x_3331_, 0, v_year_3317_);
v___x_3332_ = l_Option_instBEq_beq___at___00Legal_USTax_Hunt_Basis_step_spec__0(v_death_3330_, v___x_3331_);
lean_dec_ref_known(v___x_3331_, 1);
if (v___x_3332_ == 0)
{
lean_object* v___x_3333_; 
lean_del_object(v___x_3328_);
lean_dec(v_tax_3326_);
lean_dec(v_pledge_3325_);
lean_dec(v_cfChar_3324_);
lean_dec(v_charProp_3323_);
lean_dec(v_charCash_3322_);
lean_dec_ref(v_rP_3321_);
lean_dec_ref(v_rA_3320_);
lean_dec_ref(v_rK_3319_);
lean_dec_ref(v_rJ_3318_);
lean_dec(v_year_3317_);
lean_dec(v_lots_3316_);
v___x_3333_ = lean_box(0);
return v___x_3333_;
}
else
{
uint8_t v___x_3334_; uint8_t v___x_3335_; 
v___x_3334_ = 4;
v___x_3335_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_heir_3315_, v___x_3334_);
if (v___x_3335_ == 0)
{
uint8_t v___x_3336_; uint8_t v___x_3337_; 
v___x_3336_ = 1;
v___x_3337_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_heir_3315_, v___x_3336_);
if (v___x_3337_ == 0)
{
lean_object* v___x_3338_; lean_object* v_lots_3339_; lean_object* v___x_3340_; lean_object* v___x_3341_; lean_object* v___x_3343_; 
v___x_3338_ = lean_box(0);
v_lots_3339_ = l_List_mapTR_loop___at___00Legal_USTax_Hunt_Basis_step_spec__1(v_heir_3315_, v___x_3332_, v_lots_3316_, v___x_3338_);
v___x_3340_ = l_List_mapTR_loop___at___00Legal_USTax_Hunt_Basis_step_spec__2(v_cfg_3035_, v___x_3337_, v_lots_3339_, v___x_3338_);
v___x_3341_ = lean_unsigned_to_nat(0u);
if (v_isShared_3329_ == 0)
{
lean_ctor_set(v___x_3328_, 2, v___x_3341_);
lean_ctor_set(v___x_3328_, 0, v___x_3340_);
v___x_3343_ = v___x_3328_;
goto v_reusejp_3342_;
}
else
{
lean_object* v_reuseFailAlloc_3345_; 
v_reuseFailAlloc_3345_ = lean_alloc_ctor(0, 12, 2);
lean_ctor_set(v_reuseFailAlloc_3345_, 0, v___x_3340_);
lean_ctor_set(v_reuseFailAlloc_3345_, 1, v_year_3317_);
lean_ctor_set(v_reuseFailAlloc_3345_, 2, v___x_3341_);
lean_ctor_set(v_reuseFailAlloc_3345_, 3, v_rJ_3318_);
lean_ctor_set(v_reuseFailAlloc_3345_, 4, v_rK_3319_);
lean_ctor_set(v_reuseFailAlloc_3345_, 5, v_rA_3320_);
lean_ctor_set(v_reuseFailAlloc_3345_, 6, v_rP_3321_);
lean_ctor_set(v_reuseFailAlloc_3345_, 7, v_charCash_3322_);
lean_ctor_set(v_reuseFailAlloc_3345_, 8, v_charProp_3323_);
lean_ctor_set(v_reuseFailAlloc_3345_, 9, v_cfChar_3324_);
lean_ctor_set(v_reuseFailAlloc_3345_, 10, v_pledge_3325_);
lean_ctor_set(v_reuseFailAlloc_3345_, 11, v_tax_3326_);
v___x_3343_ = v_reuseFailAlloc_3345_;
goto v_reusejp_3342_;
}
v_reusejp_3342_:
{
lean_object* v___x_3344_; 
lean_ctor_set_uint8(v___x_3343_, sizeof(void*)*12, v___x_3337_);
lean_ctor_set_uint8(v___x_3343_, sizeof(void*)*12 + 1, v___x_3332_);
v___x_3344_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v___x_3344_, 0, v___x_3343_);
return v___x_3344_;
}
}
else
{
lean_object* v___x_3346_; 
lean_del_object(v___x_3328_);
lean_dec(v_tax_3326_);
lean_dec(v_pledge_3325_);
lean_dec(v_cfChar_3324_);
lean_dec(v_charProp_3323_);
lean_dec(v_charCash_3322_);
lean_dec_ref(v_rP_3321_);
lean_dec_ref(v_rA_3320_);
lean_dec_ref(v_rK_3319_);
lean_dec_ref(v_rJ_3318_);
lean_dec(v_year_3317_);
lean_dec(v_lots_3316_);
v___x_3346_ = lean_box(0);
return v___x_3346_;
}
}
else
{
lean_object* v___x_3347_; 
lean_del_object(v___x_3328_);
lean_dec(v_tax_3326_);
lean_dec(v_pledge_3325_);
lean_dec(v_cfChar_3324_);
lean_dec(v_charProp_3323_);
lean_dec(v_charCash_3322_);
lean_dec_ref(v_rP_3321_);
lean_dec_ref(v_rA_3320_);
lean_dec_ref(v_rK_3319_);
lean_dec_ref(v_rJ_3318_);
lean_dec(v_year_3317_);
lean_dec(v_lots_3316_);
v___x_3347_ = lean_box(0);
return v___x_3347_;
}
}
}
}
}
default: 
{
lean_object* v_death_3350_; lean_object* v_horizon_3351_; lean_object* v_lots_3352_; lean_object* v_year_3353_; uint8_t v_pAlive_3354_; lean_object* v_pledge_3355_; uint8_t v___y_3362_; lean_object* v___x_3372_; uint8_t v___x_3373_; 
v_death_3350_ = lean_ctor_get(v_cfg_3035_, 3);
v_horizon_3351_ = lean_ctor_get(v_cfg_3035_, 4);
v_lots_3352_ = lean_ctor_get(v_s_3036_, 0);
v_year_3353_ = lean_ctor_get(v_s_3036_, 1);
v_pAlive_3354_ = lean_ctor_get_uint8(v_s_3036_, sizeof(void*)*12);
v_pledge_3355_ = lean_ctor_get(v_s_3036_, 10);
lean_inc(v_year_3353_);
v___x_3372_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v___x_3372_, 0, v_year_3353_);
v___x_3373_ = l_Option_instBEq_beq___at___00Legal_USTax_Hunt_Basis_step_spec__0(v_death_3350_, v___x_3372_);
lean_dec_ref_known(v___x_3372_, 1);
if (v___x_3373_ == 0)
{
v___y_3362_ = v___x_3373_;
goto v___jp_3361_;
}
else
{
v___y_3362_ = v_pAlive_3354_;
goto v___jp_3361_;
}
v___jp_3356_:
{
uint8_t v___x_3357_; 
v___x_3357_ = lean_nat_dec_le(v_horizon_3351_, v_year_3353_);
if (v___x_3357_ == 0)
{
lean_object* v___x_3358_; lean_object* v___x_3359_; 
v___x_3358_ = l_Legal_USTax_Hunt_Basis_closeYear(v_cfg_3035_, v_s_3036_);
v___x_3359_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v___x_3359_, 0, v___x_3358_);
return v___x_3359_;
}
else
{
lean_object* v___x_3360_; 
lean_dec_ref(v_s_3036_);
v___x_3360_ = lean_box(0);
return v___x_3360_;
}
}
v___jp_3361_:
{
if (v___y_3362_ == 0)
{
lean_object* v___x_3363_; lean_object* v___x_3364_; uint8_t v___x_3365_; 
v___x_3363_ = lean_unsigned_to_nat(1u);
v___x_3364_ = lean_nat_add(v_year_3353_, v___x_3363_);
v___x_3365_ = lean_nat_dec_eq(v___x_3364_, v_horizon_3351_);
if (v___x_3365_ == 0)
{
lean_dec(v___x_3364_);
goto v___jp_3356_;
}
else
{
lean_object* v___x_3366_; uint8_t v___x_3367_; 
v___x_3366_ = lean_unsigned_to_nat(0u);
v___x_3367_ = lean_nat_dec_eq(v_pledge_3355_, v___x_3366_);
if (v___x_3367_ == 0)
{
lean_object* v___x_3368_; 
lean_dec(v___x_3364_);
lean_dec_ref(v_s_3036_);
v___x_3368_ = lean_box(0);
return v___x_3368_;
}
else
{
uint8_t v___x_3369_; 
v___x_3369_ = l_List_any___at___00Legal_USTax_Hunt_Basis_step_spec__3(v___x_3364_, v_horizon_3351_, v___y_3362_, v_lots_3352_);
lean_dec(v___x_3364_);
if (v___x_3369_ == 0)
{
goto v___jp_3356_;
}
else
{
lean_object* v___x_3370_; 
lean_dec_ref(v_s_3036_);
v___x_3370_ = lean_box(0);
return v___x_3370_;
}
}
}
}
else
{
lean_object* v___x_3371_; 
lean_dec_ref(v_s_3036_);
v___x_3371_ = lean_box(0);
return v___x_3371_;
}
}
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_step___boxed(lean_object* v_cfg_3374_, lean_object* v_s_3375_, lean_object* v_x_3376_){
_start:
{
lean_object* v_res_3377_; 
v_res_3377_ = l_Legal_USTax_Hunt_Basis_step(v_cfg_3374_, v_s_3375_, v_x_3376_);
lean_dec_ref(v_cfg_3374_);
return v_res_3377_;
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_List_Impl_0__List_flatMapTR_go___at___00Legal_USTax_Hunt_Basis_moves_spec__0(lean_object* v_i_3399_, lean_object* v_a_3400_, lean_object* v_a_3401_){
_start:
{
if (lean_obj_tag(v_a_3400_) == 0)
{
lean_object* v___x_3402_; 
lean_dec(v_i_3399_);
v___x_3402_ = lean_array_to_list(v_a_3401_);
return v___x_3402_;
}
else
{
lean_object* v_head_3403_; lean_object* v_tail_3404_; lean_object* v___x_3406_; uint8_t v_isShared_3407_; uint8_t v_isSharedCheck_3419_; 
v_head_3403_ = lean_ctor_get(v_a_3400_, 0);
v_tail_3404_ = lean_ctor_get(v_a_3400_, 1);
v_isSharedCheck_3419_ = !lean_is_exclusive(v_a_3400_);
if (v_isSharedCheck_3419_ == 0)
{
v___x_3406_ = v_a_3400_;
v_isShared_3407_ = v_isSharedCheck_3419_;
goto v_resetjp_3405_;
}
else
{
lean_inc(v_tail_3404_);
lean_inc(v_head_3403_);
lean_dec(v_a_3400_);
v___x_3406_ = lean_box(0);
v_isShared_3407_ = v_isSharedCheck_3419_;
goto v_resetjp_3405_;
}
v_resetjp_3405_:
{
lean_object* v___x_3408_; lean_object* v___x_3409_; uint8_t v___x_3410_; lean_object* v___x_3411_; uint8_t v___x_3412_; lean_object* v___x_3414_; 
v___x_3408_ = lean_box(0);
lean_inc_n(v_i_3399_, 2);
v___x_3409_ = lean_alloc_ctor(1, 1, 1);
lean_ctor_set(v___x_3409_, 0, v_i_3399_);
v___x_3410_ = lean_unbox(v_head_3403_);
lean_ctor_set_uint8(v___x_3409_, sizeof(void*)*1, v___x_3410_);
v___x_3411_ = lean_alloc_ctor(2, 1, 1);
lean_ctor_set(v___x_3411_, 0, v_i_3399_);
v___x_3412_ = lean_unbox(v_head_3403_);
lean_dec(v_head_3403_);
lean_ctor_set_uint8(v___x_3411_, sizeof(void*)*1, v___x_3412_);
if (v_isShared_3407_ == 0)
{
lean_ctor_set(v___x_3406_, 1, v___x_3408_);
lean_ctor_set(v___x_3406_, 0, v___x_3411_);
v___x_3414_ = v___x_3406_;
goto v_reusejp_3413_;
}
else
{
lean_object* v_reuseFailAlloc_3418_; 
v_reuseFailAlloc_3418_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v_reuseFailAlloc_3418_, 0, v___x_3411_);
lean_ctor_set(v_reuseFailAlloc_3418_, 1, v___x_3408_);
v___x_3414_ = v_reuseFailAlloc_3418_;
goto v_reusejp_3413_;
}
v_reusejp_3413_:
{
lean_object* v___x_3415_; lean_object* v___x_3416_; 
v___x_3415_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_3415_, 0, v___x_3409_);
lean_ctor_set(v___x_3415_, 1, v___x_3414_);
v___x_3416_ = l_List_foldl___at___00Array_appendList_spec__0___redArg(v_a_3401_, v___x_3415_);
v_a_3400_ = v_tail_3404_;
v_a_3401_ = v___x_3416_;
goto _start;
}
}
}
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_List_Impl_0__List_flatMapTR_go___at___00Legal_USTax_Hunt_Basis_moves_spec__1(lean_object* v_a_3422_, lean_object* v_a_3423_){
_start:
{
if (lean_obj_tag(v_a_3422_) == 0)
{
lean_object* v___x_3424_; 
v___x_3424_ = lean_array_to_list(v_a_3423_);
return v___x_3424_;
}
else
{
lean_object* v_head_3425_; lean_object* v_tail_3426_; lean_object* v___x_3428_; uint8_t v_isShared_3429_; uint8_t v_isSharedCheck_3443_; 
v_head_3425_ = lean_ctor_get(v_a_3422_, 0);
v_tail_3426_ = lean_ctor_get(v_a_3422_, 1);
v_isSharedCheck_3443_ = !lean_is_exclusive(v_a_3422_);
if (v_isSharedCheck_3443_ == 0)
{
v___x_3428_ = v_a_3422_;
v_isShared_3429_ = v_isSharedCheck_3443_;
goto v_resetjp_3427_;
}
else
{
lean_inc(v_tail_3426_);
lean_inc(v_head_3425_);
lean_dec(v_a_3422_);
v___x_3428_ = lean_box(0);
v_isShared_3429_ = v_isSharedCheck_3443_;
goto v_resetjp_3427_;
}
v_resetjp_3427_:
{
lean_object* v___x_3430_; lean_object* v___x_3431_; lean_object* v___x_3432_; lean_object* v___x_3434_; 
lean_inc_n(v_head_3425_, 2);
v___x_3430_ = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(v___x_3430_, 0, v_head_3425_);
v___x_3431_ = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(v___x_3431_, 0, v_head_3425_);
v___x_3432_ = lean_box(0);
if (v_isShared_3429_ == 0)
{
lean_ctor_set(v___x_3428_, 1, v___x_3432_);
lean_ctor_set(v___x_3428_, 0, v___x_3431_);
v___x_3434_ = v___x_3428_;
goto v_reusejp_3433_;
}
else
{
lean_object* v_reuseFailAlloc_3442_; 
v_reuseFailAlloc_3442_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v_reuseFailAlloc_3442_, 0, v___x_3431_);
lean_ctor_set(v_reuseFailAlloc_3442_, 1, v___x_3432_);
v___x_3434_ = v_reuseFailAlloc_3442_;
goto v_reusejp_3433_;
}
v_reusejp_3433_:
{
lean_object* v___x_3435_; lean_object* v___x_3436_; lean_object* v___x_3437_; lean_object* v___x_3438_; lean_object* v___x_3439_; lean_object* v___x_3440_; 
v___x_3435_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_3435_, 0, v___x_3430_);
lean_ctor_set(v___x_3435_, 1, v___x_3434_);
v___x_3436_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_people));
v___x_3437_ = ((lean_object*)(l___private_Init_Data_List_Impl_0__List_flatMapTR_go___at___00Legal_USTax_Hunt_Basis_moves_spec__1___closed__0));
v___x_3438_ = l___private_Init_Data_List_Impl_0__List_flatMapTR_go___at___00Legal_USTax_Hunt_Basis_moves_spec__0(v_head_3425_, v___x_3436_, v___x_3437_);
v___x_3439_ = l_List_appendTR___redArg(v___x_3435_, v___x_3438_);
v___x_3440_ = l_List_foldl___at___00Array_appendList_spec__0___redArg(v_a_3423_, v___x_3439_);
v_a_3422_ = v_tail_3426_;
v_a_3423_ = v___x_3440_;
goto _start;
}
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_moves(lean_object* v_s_3465_){
_start:
{
lean_object* v_lots_3466_; lean_object* v_n_3467_; lean_object* v___x_3468_; lean_object* v___x_3469_; lean_object* v_per_3470_; lean_object* v___x_3471_; lean_object* v___x_3472_; 
v_lots_3466_ = lean_ctor_get(v_s_3465_, 0);
v_n_3467_ = l_List_lengthTR___redArg(v_lots_3466_);
v___x_3468_ = l_List_range(v_n_3467_);
v___x_3469_ = ((lean_object*)(l___private_Init_Data_List_Impl_0__List_flatMapTR_go___at___00Legal_USTax_Hunt_Basis_moves_spec__1___closed__0));
v_per_3470_ = l___private_Init_Data_List_Impl_0__List_flatMapTR_go___at___00Legal_USTax_Hunt_Basis_moves_spec__1(v___x_3468_, v___x_3469_);
v___x_3471_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_moves___closed__7));
v___x_3472_ = l_List_appendTR___redArg(v_per_3470_, v___x_3471_);
return v___x_3472_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_moves___boxed(lean_object* v_s_3473_){
_start:
{
lean_object* v_res_3474_; 
v_res_3474_ = l_Legal_USTax_Hunt_Basis_moves(v_s_3473_);
lean_dec_ref(v_s_3473_);
return v_res_3474_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_kindName(uint8_t v_x_3478_){
_start:
{
switch(v_x_3478_)
{
case 0:
{
lean_object* v___x_3479_; 
v___x_3479_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_kindName___closed__0));
return v___x_3479_;
}
case 1:
{
lean_object* v___x_3480_; 
v___x_3480_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_kindName___closed__1));
return v___x_3480_;
}
default: 
{
lean_object* v___x_3481_; 
v___x_3481_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_kindName___closed__2));
return v___x_3481_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_kindName___boxed(lean_object* v_x_3482_){
_start:
{
uint8_t v_x_31__boxed_3483_; lean_object* v_res_3484_; 
v_x_31__boxed_3483_ = lean_unbox(v_x_3482_);
v_res_3484_ = l_Legal_USTax_Hunt_Basis_kindName(v_x_31__boxed_3483_);
return v_res_3484_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_describe(lean_object* v_s_3503_, lean_object* v_x_3504_){
_start:
{
lean_object* v___x_3505_; 
v___x_3505_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instInhabitedLot_default));
switch(lean_obj_tag(v_x_3504_))
{
case 0:
{
lean_object* v_i_3506_; lean_object* v_lots_3507_; lean_object* v_year_3508_; lean_object* v_l_3509_; uint8_t v_owner_3510_; lean_object* v___x_3511_; lean_object* v___x_3512_; lean_object* v___x_3513_; lean_object* v___x_3514_; lean_object* v___x_3515_; lean_object* v___x_3516_; lean_object* v___x_3517_; lean_object* v___x_3518_; lean_object* v___x_3519_; lean_object* v___x_3520_; lean_object* v___x_3521_; lean_object* v___x_3522_; lean_object* v___x_3523_; lean_object* v___x_3524_; 
v_i_3506_ = lean_ctor_get(v_x_3504_, 0);
lean_inc_n(v_i_3506_, 2);
lean_dec_ref_known(v_x_3504_, 1);
v_lots_3507_ = lean_ctor_get(v_s_3503_, 0);
lean_inc(v_lots_3507_);
v_year_3508_ = lean_ctor_get(v_s_3503_, 1);
lean_inc(v_year_3508_);
lean_dec_ref(v_s_3503_);
v_l_3509_ = l_List_get_x21Internal___redArg(v___x_3505_, v_lots_3507_, v_i_3506_);
lean_dec(v_lots_3507_);
v_owner_3510_ = lean_ctor_get_uint8(v_l_3509_, sizeof(void*)*8 + 1);
lean_dec(v_l_3509_);
v___x_3511_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__0));
v___x_3512_ = l_Nat_reprFast(v_year_3508_);
v___x_3513_ = lean_string_append(v___x_3511_, v___x_3512_);
lean_dec_ref(v___x_3512_);
v___x_3514_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__1));
v___x_3515_ = lean_string_append(v___x_3513_, v___x_3514_);
v___x_3516_ = l_Legal_USTax_Hunt_Basis_Who_name(v_owner_3510_);
v___x_3517_ = lean_string_append(v___x_3515_, v___x_3516_);
v___x_3518_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__2));
v___x_3519_ = lean_string_append(v___x_3517_, v___x_3518_);
v___x_3520_ = l_Nat_reprFast(v_i_3506_);
v___x_3521_ = lean_string_append(v___x_3519_, v___x_3520_);
lean_dec_ref(v___x_3520_);
v___x_3522_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__3));
v___x_3523_ = lean_string_append(v___x_3516_, v___x_3522_);
v___x_3524_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_3524_, 0, v___x_3521_);
lean_ctor_set(v___x_3524_, 1, v___x_3523_);
return v___x_3524_;
}
case 1:
{
lean_object* v_i_3525_; uint8_t v_to_3526_; lean_object* v_lots_3527_; lean_object* v_year_3528_; lean_object* v_l_3529_; uint8_t v_owner_3530_; lean_object* v___x_3531_; lean_object* v___x_3532_; lean_object* v___x_3533_; lean_object* v___x_3534_; lean_object* v___x_3535_; lean_object* v___x_3536_; lean_object* v___x_3537_; lean_object* v___x_3538_; lean_object* v___x_3539_; lean_object* v___x_3540_; lean_object* v___x_3541_; lean_object* v___x_3542_; lean_object* v___x_3543_; lean_object* v___x_3544_; lean_object* v___x_3545_; lean_object* v___x_3546_; lean_object* v___x_3547_; lean_object* v___x_3548_; lean_object* v___x_3549_; lean_object* v___x_3550_; lean_object* v___x_3551_; 
v_i_3525_ = lean_ctor_get(v_x_3504_, 0);
lean_inc_n(v_i_3525_, 2);
v_to_3526_ = lean_ctor_get_uint8(v_x_3504_, sizeof(void*)*1);
lean_dec_ref_known(v_x_3504_, 1);
v_lots_3527_ = lean_ctor_get(v_s_3503_, 0);
lean_inc(v_lots_3527_);
v_year_3528_ = lean_ctor_get(v_s_3503_, 1);
lean_inc(v_year_3528_);
lean_dec_ref(v_s_3503_);
v_l_3529_ = l_List_get_x21Internal___redArg(v___x_3505_, v_lots_3527_, v_i_3525_);
lean_dec(v_lots_3527_);
v_owner_3530_ = lean_ctor_get_uint8(v_l_3529_, sizeof(void*)*8 + 1);
lean_dec(v_l_3529_);
v___x_3531_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__0));
v___x_3532_ = l_Nat_reprFast(v_year_3528_);
v___x_3533_ = lean_string_append(v___x_3531_, v___x_3532_);
lean_dec_ref(v___x_3532_);
v___x_3534_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__1));
v___x_3535_ = lean_string_append(v___x_3533_, v___x_3534_);
v___x_3536_ = l_Legal_USTax_Hunt_Basis_Who_name(v_owner_3530_);
v___x_3537_ = lean_string_append(v___x_3535_, v___x_3536_);
v___x_3538_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__4));
v___x_3539_ = lean_string_append(v___x_3537_, v___x_3538_);
v___x_3540_ = l_Nat_reprFast(v_i_3525_);
v___x_3541_ = lean_string_append(v___x_3539_, v___x_3540_);
lean_dec_ref(v___x_3540_);
v___x_3542_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__5));
v___x_3543_ = lean_string_append(v___x_3541_, v___x_3542_);
v___x_3544_ = l_Legal_USTax_Hunt_Basis_Who_name(v_to_3526_);
v___x_3545_ = lean_string_append(v___x_3543_, v___x_3544_);
v___x_3546_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__6));
v___x_3547_ = lean_string_append(v___x_3536_, v___x_3546_);
v___x_3548_ = lean_string_append(v___x_3547_, v___x_3544_);
lean_dec_ref(v___x_3544_);
v___x_3549_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__7));
v___x_3550_ = lean_string_append(v___x_3548_, v___x_3549_);
v___x_3551_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_3551_, 0, v___x_3545_);
lean_ctor_set(v___x_3551_, 1, v___x_3550_);
return v___x_3551_;
}
case 2:
{
lean_object* v_i_3552_; uint8_t v_to_3553_; lean_object* v_lots_3554_; lean_object* v_year_3555_; lean_object* v_l_3556_; uint8_t v_owner_3557_; lean_object* v___x_3558_; lean_object* v___x_3559_; lean_object* v___x_3560_; lean_object* v___x_3561_; lean_object* v___x_3562_; lean_object* v___x_3563_; lean_object* v___x_3564_; lean_object* v___x_3565_; lean_object* v___x_3566_; lean_object* v___x_3567_; lean_object* v___x_3568_; lean_object* v___x_3569_; lean_object* v___x_3570_; lean_object* v___x_3571_; lean_object* v___x_3572_; lean_object* v___x_3573_; lean_object* v___x_3574_; lean_object* v___x_3575_; lean_object* v___x_3576_; lean_object* v___x_3577_; lean_object* v___x_3578_; 
v_i_3552_ = lean_ctor_get(v_x_3504_, 0);
lean_inc_n(v_i_3552_, 2);
v_to_3553_ = lean_ctor_get_uint8(v_x_3504_, sizeof(void*)*1);
lean_dec_ref_known(v_x_3504_, 1);
v_lots_3554_ = lean_ctor_get(v_s_3503_, 0);
lean_inc(v_lots_3554_);
v_year_3555_ = lean_ctor_get(v_s_3503_, 1);
lean_inc(v_year_3555_);
lean_dec_ref(v_s_3503_);
v_l_3556_ = l_List_get_x21Internal___redArg(v___x_3505_, v_lots_3554_, v_i_3552_);
lean_dec(v_lots_3554_);
v_owner_3557_ = lean_ctor_get_uint8(v_l_3556_, sizeof(void*)*8 + 1);
lean_dec(v_l_3556_);
v___x_3558_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__0));
v___x_3559_ = l_Nat_reprFast(v_year_3555_);
v___x_3560_ = lean_string_append(v___x_3558_, v___x_3559_);
lean_dec_ref(v___x_3559_);
v___x_3561_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__1));
v___x_3562_ = lean_string_append(v___x_3560_, v___x_3561_);
v___x_3563_ = l_Legal_USTax_Hunt_Basis_Who_name(v_owner_3557_);
v___x_3564_ = lean_string_append(v___x_3562_, v___x_3563_);
v___x_3565_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__2));
v___x_3566_ = lean_string_append(v___x_3564_, v___x_3565_);
v___x_3567_ = l_Nat_reprFast(v_i_3552_);
v___x_3568_ = lean_string_append(v___x_3566_, v___x_3567_);
lean_dec_ref(v___x_3567_);
v___x_3569_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__5));
v___x_3570_ = lean_string_append(v___x_3568_, v___x_3569_);
v___x_3571_ = l_Legal_USTax_Hunt_Basis_Who_name(v_to_3553_);
v___x_3572_ = lean_string_append(v___x_3570_, v___x_3571_);
v___x_3573_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__6));
v___x_3574_ = lean_string_append(v___x_3563_, v___x_3573_);
v___x_3575_ = lean_string_append(v___x_3574_, v___x_3571_);
lean_dec_ref(v___x_3571_);
v___x_3576_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__8));
v___x_3577_ = lean_string_append(v___x_3575_, v___x_3576_);
v___x_3578_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_3578_, 0, v___x_3572_);
lean_ctor_set(v___x_3578_, 1, v___x_3577_);
return v___x_3578_;
}
case 3:
{
lean_object* v_i_3579_; lean_object* v_year_3580_; lean_object* v___x_3581_; lean_object* v___x_3582_; lean_object* v___x_3583_; lean_object* v___x_3584_; lean_object* v___x_3585_; lean_object* v___x_3586_; lean_object* v___x_3587_; lean_object* v___x_3588_; lean_object* v___x_3589_; 
v_i_3579_ = lean_ctor_get(v_x_3504_, 0);
lean_inc(v_i_3579_);
lean_dec_ref_known(v_x_3504_, 1);
v_year_3580_ = lean_ctor_get(v_s_3503_, 1);
lean_inc(v_year_3580_);
lean_dec_ref(v_s_3503_);
v___x_3581_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__0));
v___x_3582_ = l_Nat_reprFast(v_year_3580_);
v___x_3583_ = lean_string_append(v___x_3581_, v___x_3582_);
lean_dec_ref(v___x_3582_);
v___x_3584_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__9));
v___x_3585_ = lean_string_append(v___x_3583_, v___x_3584_);
v___x_3586_ = l_Nat_reprFast(v_i_3579_);
v___x_3587_ = lean_string_append(v___x_3585_, v___x_3586_);
lean_dec_ref(v___x_3586_);
v___x_3588_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__10));
v___x_3589_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_3589_, 0, v___x_3587_);
lean_ctor_set(v___x_3589_, 1, v___x_3588_);
return v___x_3589_;
}
case 4:
{
lean_object* v_year_3590_; lean_object* v___x_3591_; lean_object* v___x_3592_; lean_object* v___x_3593_; lean_object* v___x_3594_; lean_object* v___x_3595_; lean_object* v___x_3596_; lean_object* v___x_3597_; 
v_year_3590_ = lean_ctor_get(v_s_3503_, 1);
lean_inc(v_year_3590_);
lean_dec_ref(v_s_3503_);
v___x_3591_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__0));
v___x_3592_ = l_Nat_reprFast(v_year_3590_);
v___x_3593_ = lean_string_append(v___x_3591_, v___x_3592_);
lean_dec_ref(v___x_3592_);
v___x_3594_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__11));
v___x_3595_ = lean_string_append(v___x_3593_, v___x_3594_);
v___x_3596_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__12));
v___x_3597_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_3597_, 0, v___x_3595_);
lean_ctor_set(v___x_3597_, 1, v___x_3596_);
return v___x_3597_;
}
case 5:
{
uint8_t v_heir_3598_; lean_object* v_year_3599_; lean_object* v___x_3600_; lean_object* v___x_3601_; lean_object* v___x_3602_; lean_object* v___x_3603_; lean_object* v___x_3604_; lean_object* v___x_3605_; lean_object* v___x_3606_; lean_object* v___x_3607_; lean_object* v___x_3608_; lean_object* v___x_3609_; 
v_heir_3598_ = lean_ctor_get_uint8(v_x_3504_, 0);
lean_dec_ref_known(v_x_3504_, 0);
v_year_3599_ = lean_ctor_get(v_s_3503_, 1);
lean_inc(v_year_3599_);
lean_dec_ref(v_s_3503_);
v___x_3600_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__0));
v___x_3601_ = l_Nat_reprFast(v_year_3599_);
v___x_3602_ = lean_string_append(v___x_3600_, v___x_3601_);
lean_dec_ref(v___x_3601_);
v___x_3603_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__13));
v___x_3604_ = lean_string_append(v___x_3602_, v___x_3603_);
v___x_3605_ = l_Legal_USTax_Hunt_Basis_Who_name(v_heir_3598_);
v___x_3606_ = lean_string_append(v___x_3604_, v___x_3605_);
v___x_3607_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__14));
v___x_3608_ = lean_string_append(v___x_3607_, v___x_3605_);
lean_dec_ref(v___x_3605_);
v___x_3609_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_3609_, 0, v___x_3606_);
lean_ctor_set(v___x_3609_, 1, v___x_3608_);
return v___x_3609_;
}
default: 
{
lean_object* v___x_3610_; 
lean_dec_ref(v_s_3503_);
v___x_3610_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__16));
return v___x_3610_;
}
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_giftOver(lean_object* v_s_3611_, lean_object* v_x_3612_){
_start:
{
if (lean_obj_tag(v_x_3612_) == 1)
{
lean_object* v_i_3613_; uint8_t v_to_3614_; lean_object* v_lots_3615_; lean_object* v___x_3616_; lean_object* v_l_3617_; uint8_t v_owner_3618_; lean_object* v_fmv_3619_; uint8_t v___x_3623_; 
v_i_3613_ = lean_ctor_get(v_x_3612_, 0);
lean_inc(v_i_3613_);
v_to_3614_ = lean_ctor_get_uint8(v_x_3612_, sizeof(void*)*1);
lean_dec_ref_known(v_x_3612_, 1);
v_lots_3615_ = lean_ctor_get(v_s_3611_, 0);
v___x_3616_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_instInhabitedLot_default));
v_l_3617_ = l_List_get_x21Internal___redArg(v___x_3616_, v_lots_3615_, v_i_3613_);
v_owner_3618_ = lean_ctor_get_uint8(v_l_3617_, sizeof(void*)*8 + 1);
v_fmv_3619_ = lean_ctor_get(v_l_3617_, 0);
lean_inc(v_fmv_3619_);
lean_dec(v_l_3617_);
v___x_3623_ = l_Legal_USTax_Hunt_Basis_spouses(v_owner_3618_, v_to_3614_);
if (v___x_3623_ == 0)
{
uint8_t v___x_3624_; uint8_t v___x_3625_; 
v___x_3624_ = 0;
v___x_3625_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_owner_3618_, v___x_3624_);
if (v___x_3625_ == 0)
{
uint8_t v___x_3626_; uint8_t v___x_3627_; 
v___x_3626_ = 1;
v___x_3627_ = l_Legal_USTax_Hunt_Basis_instBEqWho_beq(v_owner_3618_, v___x_3626_);
if (v___x_3627_ == 0)
{
lean_object* v___x_3628_; lean_object* v___x_3629_; 
v___x_3628_ = lean_unsigned_to_nat(19000u);
v___x_3629_ = lean_nat_sub(v_fmv_3619_, v___x_3628_);
lean_dec(v_fmv_3619_);
return v___x_3629_;
}
else
{
goto v___jp_3620_;
}
}
else
{
goto v___jp_3620_;
}
}
else
{
lean_object* v___x_3630_; 
lean_dec(v_fmv_3619_);
v___x_3630_ = lean_unsigned_to_nat(0u);
return v___x_3630_;
}
v___jp_3620_:
{
lean_object* v___x_3621_; lean_object* v___x_3622_; 
v___x_3621_ = lean_unsigned_to_nat(38000u);
v___x_3622_ = lean_nat_sub(v_fmv_3619_, v___x_3621_);
lean_dec(v_fmv_3619_);
return v___x_3622_;
}
}
else
{
lean_object* v___x_3631_; 
lean_dec(v_x_3612_);
v___x_3631_ = lean_unsigned_to_nat(0u);
return v___x_3631_;
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_giftOver___boxed(lean_object* v_s_3632_, lean_object* v_x_3633_){
_start:
{
lean_object* v_res_3634_; 
v_res_3634_ = l_Legal_USTax_Hunt_Basis_giftOver(v_s_3632_, v_x_3633_);
lean_dec_ref(v_s_3632_);
return v_res_3634_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_insertSorted(lean_object* v_x_3635_, lean_object* v_x_3636_){
_start:
{
if (lean_obj_tag(v_x_3636_) == 0)
{
lean_object* v___x_3637_; 
v___x_3637_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_3637_, 0, v_x_3635_);
lean_ctor_set(v___x_3637_, 1, v_x_3636_);
return v___x_3637_;
}
else
{
lean_object* v_head_3638_; lean_object* v_tail_3639_; uint8_t v___x_3640_; 
v_head_3638_ = lean_ctor_get(v_x_3636_, 0);
v_tail_3639_ = lean_ctor_get(v_x_3636_, 1);
v___x_3640_ = lean_string_dec_eq(v_x_3635_, v_head_3638_);
if (v___x_3640_ == 0)
{
uint8_t v___x_3641_; 
v___x_3641_ = lean_string_dec_lt(v_x_3635_, v_head_3638_);
if (v___x_3641_ == 0)
{
lean_object* v___x_3643_; uint8_t v_isShared_3644_; uint8_t v_isSharedCheck_3649_; 
lean_inc(v_tail_3639_);
lean_inc(v_head_3638_);
v_isSharedCheck_3649_ = !lean_is_exclusive(v_x_3636_);
if (v_isSharedCheck_3649_ == 0)
{
lean_object* v_unused_3650_; lean_object* v_unused_3651_; 
v_unused_3650_ = lean_ctor_get(v_x_3636_, 1);
lean_dec(v_unused_3650_);
v_unused_3651_ = lean_ctor_get(v_x_3636_, 0);
lean_dec(v_unused_3651_);
v___x_3643_ = v_x_3636_;
v_isShared_3644_ = v_isSharedCheck_3649_;
goto v_resetjp_3642_;
}
else
{
lean_dec(v_x_3636_);
v___x_3643_ = lean_box(0);
v_isShared_3644_ = v_isSharedCheck_3649_;
goto v_resetjp_3642_;
}
v_resetjp_3642_:
{
lean_object* v___x_3645_; lean_object* v___x_3647_; 
v___x_3645_ = l_Legal_USTax_Hunt_Basis_insertSorted(v_x_3635_, v_tail_3639_);
if (v_isShared_3644_ == 0)
{
lean_ctor_set(v___x_3643_, 1, v___x_3645_);
v___x_3647_ = v___x_3643_;
goto v_reusejp_3646_;
}
else
{
lean_object* v_reuseFailAlloc_3648_; 
v_reuseFailAlloc_3648_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v_reuseFailAlloc_3648_, 0, v_head_3638_);
lean_ctor_set(v_reuseFailAlloc_3648_, 1, v___x_3645_);
v___x_3647_ = v_reuseFailAlloc_3648_;
goto v_reusejp_3646_;
}
v_reusejp_3646_:
{
return v___x_3647_;
}
}
}
else
{
lean_object* v___x_3652_; 
v___x_3652_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_3652_, 0, v_x_3635_);
lean_ctor_set(v___x_3652_, 1, v_x_3636_);
return v___x_3652_;
}
}
else
{
lean_dec_ref(v_x_3635_);
return v_x_3636_;
}
}
}
}
LEAN_EXPORT lean_object* l_List_foldlM___at___00Legal_USTax_Hunt_Basis_runPath_spec__0(lean_object* v_cfg_3653_, lean_object* v_x_3654_, lean_object* v_x_3655_){
_start:
{
if (lean_obj_tag(v_x_3655_) == 0)
{
lean_object* v___x_3656_; 
v___x_3656_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v___x_3656_, 0, v_x_3654_);
return v___x_3656_;
}
else
{
lean_object* v_head_3657_; lean_object* v_tail_3658_; lean_object* v___x_3659_; 
v_head_3657_ = lean_ctor_get(v_x_3655_, 0);
lean_inc(v_head_3657_);
v_tail_3658_ = lean_ctor_get(v_x_3655_, 1);
lean_inc(v_tail_3658_);
lean_dec_ref_known(v_x_3655_, 2);
v___x_3659_ = l_Legal_USTax_Hunt_Basis_step(v_cfg_3653_, v_x_3654_, v_head_3657_);
if (lean_obj_tag(v___x_3659_) == 0)
{
lean_dec(v_tail_3658_);
return v___x_3659_;
}
else
{
lean_object* v_val_3660_; 
v_val_3660_ = lean_ctor_get(v___x_3659_, 0);
lean_inc(v_val_3660_);
lean_dec_ref_known(v___x_3659_, 1);
v_x_3654_ = v_val_3660_;
v_x_3655_ = v_tail_3658_;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* l_List_foldlM___at___00Legal_USTax_Hunt_Basis_runPath_spec__0___boxed(lean_object* v_cfg_3662_, lean_object* v_x_3663_, lean_object* v_x_3664_){
_start:
{
lean_object* v_res_3665_; 
v_res_3665_ = l_List_foldlM___at___00Legal_USTax_Hunt_Basis_runPath_spec__0(v_cfg_3662_, v_x_3663_, v_x_3664_);
lean_dec_ref(v_cfg_3662_);
return v_res_3665_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_runPath(lean_object* v_cfg_3666_, lean_object* v_s_3667_, lean_object* v_ms_3668_){
_start:
{
lean_object* v___x_3669_; 
v___x_3669_ = l_List_foldlM___at___00Legal_USTax_Hunt_Basis_runPath_spec__0(v_cfg_3666_, v_s_3667_, v_ms_3668_);
return v___x_3669_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_runPath___boxed(lean_object* v_cfg_3670_, lean_object* v_s_3671_, lean_object* v_ms_3672_){
_start:
{
lean_object* v_res_3673_; 
v_res_3673_ = l_Legal_USTax_Hunt_Basis_runPath(v_cfg_3670_, v_s_3671_, v_ms_3672_);
lean_dec_ref(v_cfg_3670_);
return v_res_3673_;
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__0___redArg(lean_object* v_cfg_3674_, lean_object* v_range_3675_, lean_object* v_b_3676_, lean_object* v_i_3677_){
_start:
{
lean_object* v_stop_3678_; lean_object* v_step_3679_; lean_object* v_a_3681_; uint8_t v___x_3684_; 
v_stop_3678_ = lean_ctor_get(v_range_3675_, 1);
v_step_3679_ = lean_ctor_get(v_range_3675_, 2);
v___x_3684_ = lean_nat_dec_lt(v_i_3677_, v_stop_3678_);
if (v___x_3684_ == 0)
{
lean_dec(v_i_3677_);
return v_b_3676_;
}
else
{
lean_object* v___x_3685_; lean_object* v___x_3686_; 
lean_inc(v_i_3677_);
v___x_3685_ = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(v___x_3685_, 0, v_i_3677_);
lean_inc_ref(v_b_3676_);
v___x_3686_ = l_Legal_USTax_Hunt_Basis_step(v_cfg_3674_, v_b_3676_, v___x_3685_);
if (lean_obj_tag(v___x_3686_) == 0)
{
v_a_3681_ = v_b_3676_;
goto v___jp_3680_;
}
else
{
lean_object* v_val_3687_; 
lean_dec_ref(v_b_3676_);
v_val_3687_ = lean_ctor_get(v___x_3686_, 0);
lean_inc(v_val_3687_);
lean_dec_ref_known(v___x_3686_, 1);
v_a_3681_ = v_val_3687_;
goto v___jp_3680_;
}
}
v___jp_3680_:
{
lean_object* v___x_3682_; 
v___x_3682_ = lean_nat_add(v_i_3677_, v_step_3679_);
lean_dec(v_i_3677_);
v_b_3676_ = v_a_3681_;
v_i_3677_ = v___x_3682_;
goto _start;
}
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__0___redArg___boxed(lean_object* v_cfg_3688_, lean_object* v_range_3689_, lean_object* v_b_3690_, lean_object* v_i_3691_){
_start:
{
lean_object* v_res_3692_; 
v_res_3692_ = l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__0___redArg(v_cfg_3688_, v_range_3689_, v_b_3690_, v_i_3691_);
lean_dec_ref(v_range_3689_);
lean_dec_ref(v_cfg_3688_);
return v_res_3692_;
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__1___redArg(lean_object* v_cfg_3693_, lean_object* v___x_3694_, lean_object* v_range_3695_, lean_object* v_b_3696_, lean_object* v_i_3697_){
_start:
{
lean_object* v_stop_3698_; lean_object* v_step_3699_; uint8_t v___x_3700_; 
v_stop_3698_ = lean_ctor_get(v_range_3695_, 1);
v_step_3699_ = lean_ctor_get(v_range_3695_, 2);
v___x_3700_ = lean_nat_dec_lt(v_i_3697_, v_stop_3698_);
if (v___x_3700_ == 0)
{
lean_dec(v_i_3697_);
return v_b_3696_;
}
else
{
lean_object* v_snd_3701_; lean_object* v___x_3703_; uint8_t v_isShared_3704_; uint8_t v_isSharedCheck_3746_; 
v_snd_3701_ = lean_ctor_get(v_b_3696_, 1);
v_isSharedCheck_3746_ = !lean_is_exclusive(v_b_3696_);
if (v_isSharedCheck_3746_ == 0)
{
lean_object* v_unused_3747_; 
v_unused_3747_ = lean_ctor_get(v_b_3696_, 0);
lean_dec(v_unused_3747_);
v___x_3703_ = v_b_3696_;
v_isShared_3704_ = v_isSharedCheck_3746_;
goto v_resetjp_3702_;
}
else
{
lean_inc(v_snd_3701_);
lean_dec(v_b_3696_);
v___x_3703_ = lean_box(0);
v_isShared_3704_ = v_isSharedCheck_3746_;
goto v_resetjp_3702_;
}
v_resetjp_3702_:
{
uint8_t v_hold_3705_; lean_object* v___x_3706_; lean_object* v_s_3708_; lean_object* v___x_3721_; lean_object* v___x_3722_; lean_object* v_s_3724_; lean_object* v_s_3732_; 
v_hold_3705_ = lean_ctor_get_uint8(v_cfg_3693_, sizeof(void*)*6);
v___x_3706_ = lean_box(0);
v___x_3721_ = lean_unsigned_to_nat(1u);
v___x_3722_ = lean_unsigned_to_nat(0u);
if (v_hold_3705_ == 0)
{
goto v___jp_3736_;
}
else
{
lean_object* v___x_3744_; uint8_t v___x_3745_; 
v___x_3744_ = lean_nat_add(v_i_3697_, v___x_3721_);
v___x_3745_ = lean_nat_dec_eq(v___x_3744_, v___x_3694_);
lean_dec(v___x_3744_);
if (v___x_3745_ == 0)
{
v_s_3732_ = v_snd_3701_;
goto v___jp_3731_;
}
else
{
goto v___jp_3736_;
}
}
v___jp_3707_:
{
lean_object* v___x_3709_; lean_object* v___x_3710_; 
v___x_3709_ = lean_box(6);
lean_inc_ref(v_s_3708_);
v___x_3710_ = l_Legal_USTax_Hunt_Basis_step(v_cfg_3693_, v_s_3708_, v___x_3709_);
if (lean_obj_tag(v___x_3710_) == 0)
{
lean_object* v___x_3711_; lean_object* v___x_3713_; 
lean_dec(v_i_3697_);
v___x_3711_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v___x_3711_, 0, v___x_3710_);
if (v_isShared_3704_ == 0)
{
lean_ctor_set(v___x_3703_, 1, v_s_3708_);
lean_ctor_set(v___x_3703_, 0, v___x_3711_);
v___x_3713_ = v___x_3703_;
goto v_reusejp_3712_;
}
else
{
lean_object* v_reuseFailAlloc_3714_; 
v_reuseFailAlloc_3714_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_3714_, 0, v___x_3711_);
lean_ctor_set(v_reuseFailAlloc_3714_, 1, v_s_3708_);
v___x_3713_ = v_reuseFailAlloc_3714_;
goto v_reusejp_3712_;
}
v_reusejp_3712_:
{
return v___x_3713_;
}
}
else
{
lean_object* v_val_3715_; lean_object* v___x_3717_; 
lean_dec_ref(v_s_3708_);
v_val_3715_ = lean_ctor_get(v___x_3710_, 0);
lean_inc(v_val_3715_);
lean_dec_ref_known(v___x_3710_, 1);
if (v_isShared_3704_ == 0)
{
lean_ctor_set(v___x_3703_, 1, v_val_3715_);
lean_ctor_set(v___x_3703_, 0, v___x_3706_);
v___x_3717_ = v___x_3703_;
goto v_reusejp_3716_;
}
else
{
lean_object* v_reuseFailAlloc_3720_; 
v_reuseFailAlloc_3720_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_3720_, 0, v___x_3706_);
lean_ctor_set(v_reuseFailAlloc_3720_, 1, v_val_3715_);
v___x_3717_ = v_reuseFailAlloc_3720_;
goto v_reusejp_3716_;
}
v_reusejp_3716_:
{
lean_object* v___x_3718_; 
v___x_3718_ = lean_nat_add(v_i_3697_, v_step_3699_);
lean_dec(v_i_3697_);
v_b_3696_ = v___x_3717_;
v_i_3697_ = v___x_3718_;
goto _start;
}
}
}
v___jp_3723_:
{
lean_object* v___x_3725_; uint8_t v___x_3726_; 
v___x_3725_ = lean_nat_add(v_i_3697_, v___x_3721_);
v___x_3726_ = lean_nat_dec_eq(v___x_3725_, v___x_3694_);
lean_dec(v___x_3725_);
if (v___x_3726_ == 0)
{
v_s_3708_ = v_s_3724_;
goto v___jp_3707_;
}
else
{
lean_object* v_lots_3727_; lean_object* v___x_3728_; lean_object* v___x_3729_; lean_object* v___x_3730_; 
v_lots_3727_ = lean_ctor_get(v_s_3724_, 0);
v___x_3728_ = l_List_lengthTR___redArg(v_lots_3727_);
v___x_3729_ = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(v___x_3729_, 0, v___x_3722_);
lean_ctor_set(v___x_3729_, 1, v___x_3728_);
lean_ctor_set(v___x_3729_, 2, v___x_3721_);
v___x_3730_ = l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__0___redArg(v_cfg_3693_, v___x_3729_, v_s_3724_, v___x_3722_);
lean_dec_ref_known(v___x_3729_, 3);
v_s_3708_ = v___x_3730_;
goto v___jp_3707_;
}
}
v___jp_3731_:
{
lean_object* v___x_3733_; lean_object* v___x_3734_; 
v___x_3733_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_moves___closed__0));
lean_inc_ref(v_s_3732_);
v___x_3734_ = l_Legal_USTax_Hunt_Basis_step(v_cfg_3693_, v_s_3732_, v___x_3733_);
if (lean_obj_tag(v___x_3734_) == 0)
{
v_s_3724_ = v_s_3732_;
goto v___jp_3723_;
}
else
{
lean_object* v_val_3735_; 
lean_dec_ref(v_s_3732_);
v_val_3735_ = lean_ctor_get(v___x_3734_, 0);
lean_inc(v_val_3735_);
lean_dec_ref_known(v___x_3734_, 1);
v_s_3724_ = v_val_3735_;
goto v___jp_3723_;
}
}
v___jp_3736_:
{
lean_object* v_lots_3737_; lean_object* v___x_3738_; lean_object* v___x_3739_; lean_object* v___x_3740_; lean_object* v___x_3741_; lean_object* v___x_3742_; 
v_lots_3737_ = lean_ctor_get(v_snd_3701_, 0);
v___x_3738_ = l_List_lengthTR___redArg(v_lots_3737_);
v___x_3739_ = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(v___x_3739_, 0, v___x_3722_);
lean_ctor_set(v___x_3739_, 1, v___x_3738_);
lean_ctor_set(v___x_3739_, 2, v___x_3721_);
v___x_3740_ = l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__0___redArg(v_cfg_3693_, v___x_3739_, v_snd_3701_, v___x_3722_);
lean_dec_ref_known(v___x_3739_, 3);
v___x_3741_ = lean_box(4);
lean_inc_ref(v___x_3740_);
v___x_3742_ = l_Legal_USTax_Hunt_Basis_step(v_cfg_3693_, v___x_3740_, v___x_3741_);
if (lean_obj_tag(v___x_3742_) == 0)
{
v_s_3732_ = v___x_3740_;
goto v___jp_3731_;
}
else
{
lean_object* v_val_3743_; 
lean_dec_ref(v___x_3740_);
v_val_3743_ = lean_ctor_get(v___x_3742_, 0);
lean_inc(v_val_3743_);
lean_dec_ref_known(v___x_3742_, 1);
v_s_3732_ = v_val_3743_;
goto v___jp_3731_;
}
}
}
}
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__1___redArg___boxed(lean_object* v_cfg_3748_, lean_object* v___x_3749_, lean_object* v_range_3750_, lean_object* v_b_3751_, lean_object* v_i_3752_){
_start:
{
lean_object* v_res_3753_; 
v_res_3753_ = l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__1___redArg(v_cfg_3748_, v___x_3749_, v_range_3750_, v_b_3751_, v_i_3752_);
lean_dec_ref(v_range_3750_);
lean_dec(v___x_3749_);
lean_dec_ref(v_cfg_3748_);
return v_res_3753_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_baseline(lean_object* v_cfg_3754_, lean_object* v_s0_3755_){
_start:
{
lean_object* v_horizon_3756_; lean_object* v___x_3757_; lean_object* v___x_3758_; lean_object* v___x_3759_; lean_object* v___x_3760_; lean_object* v___x_3761_; lean_object* v___x_3762_; lean_object* v_fst_3763_; 
v_horizon_3756_ = lean_ctor_get(v_cfg_3754_, 4);
v___x_3757_ = lean_unsigned_to_nat(0u);
v___x_3758_ = lean_unsigned_to_nat(1u);
lean_inc(v_horizon_3756_);
v___x_3759_ = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(v___x_3759_, 0, v___x_3757_);
lean_ctor_set(v___x_3759_, 1, v_horizon_3756_);
lean_ctor_set(v___x_3759_, 2, v___x_3758_);
v___x_3760_ = lean_box(0);
v___x_3761_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_3761_, 0, v___x_3760_);
lean_ctor_set(v___x_3761_, 1, v_s0_3755_);
v___x_3762_ = l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__1___redArg(v_cfg_3754_, v_horizon_3756_, v___x_3759_, v___x_3761_, v___x_3757_);
lean_dec_ref_known(v___x_3759_, 3);
v_fst_3763_ = lean_ctor_get(v___x_3762_, 0);
lean_inc(v_fst_3763_);
if (lean_obj_tag(v_fst_3763_) == 0)
{
lean_object* v_snd_3764_; lean_object* v___x_3765_; 
v_snd_3764_ = lean_ctor_get(v___x_3762_, 1);
lean_inc(v_snd_3764_);
lean_dec_ref(v___x_3762_);
v___x_3765_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v___x_3765_, 0, v_snd_3764_);
return v___x_3765_;
}
else
{
lean_object* v_val_3766_; 
lean_dec_ref(v___x_3762_);
v_val_3766_ = lean_ctor_get(v_fst_3763_, 0);
lean_inc(v_val_3766_);
lean_dec_ref_known(v_fst_3763_, 1);
return v_val_3766_;
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_baseline___boxed(lean_object* v_cfg_3767_, lean_object* v_s0_3768_){
_start:
{
lean_object* v_res_3769_; 
v_res_3769_ = l_Legal_USTax_Hunt_Basis_baseline(v_cfg_3767_, v_s0_3768_);
lean_dec_ref(v_cfg_3767_);
return v_res_3769_;
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__0(lean_object* v_cfg_3770_, lean_object* v_range_3771_, lean_object* v_b_3772_, lean_object* v_i_3773_, lean_object* v_hs_3774_, lean_object* v_hl_3775_){
_start:
{
lean_object* v___x_3776_; 
v___x_3776_ = l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__0___redArg(v_cfg_3770_, v_range_3771_, v_b_3772_, v_i_3773_);
return v___x_3776_;
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__0___boxed(lean_object* v_cfg_3777_, lean_object* v_range_3778_, lean_object* v_b_3779_, lean_object* v_i_3780_, lean_object* v_hs_3781_, lean_object* v_hl_3782_){
_start:
{
lean_object* v_res_3783_; 
v_res_3783_ = l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__0(v_cfg_3777_, v_range_3778_, v_b_3779_, v_i_3780_, v_hs_3781_, v_hl_3782_);
lean_dec_ref(v_range_3778_);
lean_dec_ref(v_cfg_3777_);
return v_res_3783_;
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__1(lean_object* v_cfg_3784_, lean_object* v___x_3785_, lean_object* v_range_3786_, lean_object* v_b_3787_, lean_object* v_i_3788_, lean_object* v_hs_3789_, lean_object* v_hl_3790_){
_start:
{
lean_object* v___x_3791_; 
v___x_3791_ = l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__1___redArg(v_cfg_3784_, v___x_3785_, v_range_3786_, v_b_3787_, v_i_3788_);
return v___x_3791_;
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__1___boxed(lean_object* v_cfg_3792_, lean_object* v___x_3793_, lean_object* v_range_3794_, lean_object* v_b_3795_, lean_object* v_i_3796_, lean_object* v_hs_3797_, lean_object* v_hl_3798_){
_start:
{
lean_object* v_res_3799_; 
v_res_3799_ = l___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_baseline_spec__1(v_cfg_3792_, v___x_3793_, v_range_3794_, v_b_3795_, v_i_3796_, v_hs_3797_, v_hl_3798_);
lean_dec_ref(v_range_3794_);
lean_dec(v___x_3793_);
lean_dec_ref(v_cfg_3792_);
return v_res_3799_;
}
}
LEAN_EXPORT uint8_t l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11___redArg___lam__0(lean_object* v_a_3800_, lean_object* v_b_3801_){
_start:
{
lean_object* v_snd_3802_; lean_object* v_snd_3803_; lean_object* v_fst_3804_; lean_object* v_tax_3805_; lean_object* v_fst_3806_; lean_object* v_tax_3807_; uint8_t v___x_3808_; 
v_snd_3802_ = lean_ctor_get(v_a_3800_, 1);
v_snd_3803_ = lean_ctor_get(v_b_3801_, 1);
v_fst_3804_ = lean_ctor_get(v_a_3800_, 0);
v_tax_3805_ = lean_ctor_get(v_snd_3802_, 0);
v_fst_3806_ = lean_ctor_get(v_b_3801_, 0);
v_tax_3807_ = lean_ctor_get(v_snd_3803_, 0);
v___x_3808_ = lean_nat_dec_lt(v_tax_3805_, v_tax_3807_);
if (v___x_3808_ == 0)
{
uint8_t v___x_3809_; 
v___x_3809_ = lean_nat_dec_eq(v_tax_3805_, v_tax_3807_);
if (v___x_3809_ == 0)
{
return v___x_3809_;
}
else
{
lean_object* v___x_3810_; lean_object* v___x_3811_; uint8_t v___x_3812_; 
v___x_3810_ = lean_string_length(v_fst_3804_);
v___x_3811_ = lean_string_length(v_fst_3806_);
v___x_3812_ = lean_nat_dec_lt(v___x_3810_, v___x_3811_);
return v___x_3812_;
}
}
else
{
return v___x_3808_;
}
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11___redArg___lam__0___boxed(lean_object* v_a_3813_, lean_object* v_b_3814_){
_start:
{
uint8_t v_res_3815_; lean_object* v_r_3816_; 
v_res_3815_ = l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11___redArg___lam__0(v_a_3813_, v_b_3814_);
lean_dec_ref(v_b_3814_);
lean_dec_ref(v_a_3813_);
v_r_3816_ = lean_box(v_res_3815_);
return v_r_3816_;
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Array_QSort_Basic_0__Array_qpartition_loop___at___00__private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11_spec__19___redArg(lean_object* v_hi_3817_, lean_object* v_pivot_3818_, lean_object* v_as_3819_, lean_object* v_i_3820_, lean_object* v_k_3821_){
_start:
{
uint8_t v___x_3832_; 
v___x_3832_ = lean_nat_dec_lt(v_k_3821_, v_hi_3817_);
if (v___x_3832_ == 0)
{
lean_object* v___x_3833_; lean_object* v___x_3834_; 
lean_dec(v_k_3821_);
v___x_3833_ = lean_array_fswap(v_as_3819_, v_i_3820_, v_hi_3817_);
v___x_3834_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_3834_, 0, v_i_3820_);
lean_ctor_set(v___x_3834_, 1, v___x_3833_);
return v___x_3834_;
}
else
{
lean_object* v___x_3835_; lean_object* v_snd_3836_; lean_object* v_snd_3837_; lean_object* v_fst_3838_; lean_object* v_tax_3839_; lean_object* v_fst_3840_; lean_object* v_tax_3841_; uint8_t v___x_3842_; 
v___x_3835_ = lean_array_fget_borrowed(v_as_3819_, v_k_3821_);
v_snd_3836_ = lean_ctor_get(v___x_3835_, 1);
v_snd_3837_ = lean_ctor_get(v_pivot_3818_, 1);
v_fst_3838_ = lean_ctor_get(v___x_3835_, 0);
v_tax_3839_ = lean_ctor_get(v_snd_3836_, 0);
v_fst_3840_ = lean_ctor_get(v_pivot_3818_, 0);
v_tax_3841_ = lean_ctor_get(v_snd_3837_, 0);
v___x_3842_ = lean_nat_dec_lt(v_tax_3839_, v_tax_3841_);
if (v___x_3842_ == 0)
{
uint8_t v___x_3843_; 
v___x_3843_ = lean_nat_dec_eq(v_tax_3839_, v_tax_3841_);
if (v___x_3843_ == 0)
{
goto v___jp_3828_;
}
else
{
lean_object* v___x_3844_; lean_object* v___x_3845_; uint8_t v___x_3846_; 
v___x_3844_ = lean_string_length(v_fst_3838_);
v___x_3845_ = lean_string_length(v_fst_3840_);
v___x_3846_ = lean_nat_dec_lt(v___x_3844_, v___x_3845_);
if (v___x_3846_ == 0)
{
goto v___jp_3828_;
}
else
{
goto v___jp_3822_;
}
}
}
else
{
goto v___jp_3822_;
}
}
v___jp_3822_:
{
lean_object* v___x_3823_; lean_object* v___x_3824_; lean_object* v___x_3825_; lean_object* v___x_3826_; 
v___x_3823_ = lean_array_fswap(v_as_3819_, v_i_3820_, v_k_3821_);
v___x_3824_ = lean_unsigned_to_nat(1u);
v___x_3825_ = lean_nat_add(v_i_3820_, v___x_3824_);
lean_dec(v_i_3820_);
v___x_3826_ = lean_nat_add(v_k_3821_, v___x_3824_);
lean_dec(v_k_3821_);
v_as_3819_ = v___x_3823_;
v_i_3820_ = v___x_3825_;
v_k_3821_ = v___x_3826_;
goto _start;
}
v___jp_3828_:
{
lean_object* v___x_3829_; lean_object* v___x_3830_; 
v___x_3829_ = lean_unsigned_to_nat(1u);
v___x_3830_ = lean_nat_add(v_k_3821_, v___x_3829_);
lean_dec(v_k_3821_);
v_k_3821_ = v___x_3830_;
goto _start;
}
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Array_QSort_Basic_0__Array_qpartition_loop___at___00__private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11_spec__19___redArg___boxed(lean_object* v_hi_3847_, lean_object* v_pivot_3848_, lean_object* v_as_3849_, lean_object* v_i_3850_, lean_object* v_k_3851_){
_start:
{
lean_object* v_res_3852_; 
v_res_3852_ = l___private_Init_Data_Array_QSort_Basic_0__Array_qpartition_loop___at___00__private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11_spec__19___redArg(v_hi_3847_, v_pivot_3848_, v_as_3849_, v_i_3850_, v_k_3851_);
lean_dec_ref(v_pivot_3848_);
lean_dec(v_hi_3847_);
return v_res_3852_;
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11___redArg(lean_object* v_n_3853_, lean_object* v_as_3854_, lean_object* v_lo_3855_, lean_object* v_hi_3856_){
_start:
{
lean_object* v___y_3858_; uint8_t v___x_3868_; 
v___x_3868_ = lean_nat_dec_lt(v_lo_3855_, v_hi_3856_);
if (v___x_3868_ == 0)
{
lean_dec(v_lo_3855_);
return v_as_3854_;
}
else
{
lean_object* v___x_3869_; lean_object* v___x_3870_; lean_object* v_mid_3871_; lean_object* v___y_3873_; lean_object* v___y_3879_; lean_object* v___x_3884_; lean_object* v___x_3885_; uint8_t v___x_3886_; 
v___x_3869_ = lean_nat_add(v_lo_3855_, v_hi_3856_);
v___x_3870_ = lean_unsigned_to_nat(1u);
v_mid_3871_ = lean_nat_shiftr(v___x_3869_, v___x_3870_);
lean_dec(v___x_3869_);
v___x_3884_ = lean_array_fget_borrowed(v_as_3854_, v_mid_3871_);
v___x_3885_ = lean_array_fget_borrowed(v_as_3854_, v_lo_3855_);
v___x_3886_ = l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11___redArg___lam__0(v___x_3884_, v___x_3885_);
if (v___x_3886_ == 0)
{
v___y_3879_ = v_as_3854_;
goto v___jp_3878_;
}
else
{
lean_object* v___x_3887_; 
v___x_3887_ = lean_array_fswap(v_as_3854_, v_lo_3855_, v_mid_3871_);
v___y_3879_ = v___x_3887_;
goto v___jp_3878_;
}
v___jp_3872_:
{
lean_object* v___x_3874_; lean_object* v___x_3875_; uint8_t v___x_3876_; 
v___x_3874_ = lean_array_fget_borrowed(v___y_3873_, v_mid_3871_);
v___x_3875_ = lean_array_fget_borrowed(v___y_3873_, v_hi_3856_);
v___x_3876_ = l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11___redArg___lam__0(v___x_3874_, v___x_3875_);
if (v___x_3876_ == 0)
{
lean_dec(v_mid_3871_);
v___y_3858_ = v___y_3873_;
goto v___jp_3857_;
}
else
{
lean_object* v___x_3877_; 
v___x_3877_ = lean_array_fswap(v___y_3873_, v_mid_3871_, v_hi_3856_);
lean_dec(v_mid_3871_);
v___y_3858_ = v___x_3877_;
goto v___jp_3857_;
}
}
v___jp_3878_:
{
lean_object* v___x_3880_; lean_object* v___x_3881_; uint8_t v___x_3882_; 
v___x_3880_ = lean_array_fget_borrowed(v___y_3879_, v_hi_3856_);
v___x_3881_ = lean_array_fget_borrowed(v___y_3879_, v_lo_3855_);
v___x_3882_ = l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11___redArg___lam__0(v___x_3880_, v___x_3881_);
if (v___x_3882_ == 0)
{
v___y_3873_ = v___y_3879_;
goto v___jp_3872_;
}
else
{
lean_object* v___x_3883_; 
v___x_3883_ = lean_array_fswap(v___y_3879_, v_lo_3855_, v_hi_3856_);
v___y_3873_ = v___x_3883_;
goto v___jp_3872_;
}
}
}
v___jp_3857_:
{
lean_object* v_pivot_3859_; lean_object* v___x_3860_; lean_object* v_fst_3861_; lean_object* v_snd_3862_; uint8_t v___x_3863_; 
v_pivot_3859_ = lean_array_fget(v___y_3858_, v_hi_3856_);
lean_inc_n(v_lo_3855_, 2);
v___x_3860_ = l___private_Init_Data_Array_QSort_Basic_0__Array_qpartition_loop___at___00__private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11_spec__19___redArg(v_hi_3856_, v_pivot_3859_, v___y_3858_, v_lo_3855_, v_lo_3855_);
lean_dec(v_pivot_3859_);
v_fst_3861_ = lean_ctor_get(v___x_3860_, 0);
lean_inc(v_fst_3861_);
v_snd_3862_ = lean_ctor_get(v___x_3860_, 1);
lean_inc(v_snd_3862_);
lean_dec_ref(v___x_3860_);
v___x_3863_ = lean_nat_dec_le(v_hi_3856_, v_fst_3861_);
if (v___x_3863_ == 0)
{
lean_object* v___x_3864_; lean_object* v___x_3865_; lean_object* v___x_3866_; 
v___x_3864_ = l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11___redArg(v_n_3853_, v_snd_3862_, v_lo_3855_, v_fst_3861_);
v___x_3865_ = lean_unsigned_to_nat(1u);
v___x_3866_ = lean_nat_add(v_fst_3861_, v___x_3865_);
lean_dec(v_fst_3861_);
v_as_3854_ = v___x_3864_;
v_lo_3855_ = v___x_3866_;
goto _start;
}
else
{
lean_dec(v_fst_3861_);
lean_dec(v_lo_3855_);
return v_snd_3862_;
}
}
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11___redArg___boxed(lean_object* v_n_3888_, lean_object* v_as_3889_, lean_object* v_lo_3890_, lean_object* v_hi_3891_){
_start:
{
lean_object* v_res_3892_; 
v_res_3892_ = l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11___redArg(v_n_3888_, v_as_3889_, v_lo_3890_, v_hi_3891_);
lean_dec(v_hi_3891_);
lean_dec(v_n_3888_);
return v_res_3892_;
}
}
LEAN_EXPORT uint8_t l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2_spec__3___redArg(lean_object* v_a_3893_, lean_object* v_x_3894_){
_start:
{
if (lean_obj_tag(v_x_3894_) == 0)
{
uint8_t v___x_3895_; 
v___x_3895_ = 0;
return v___x_3895_;
}
else
{
lean_object* v_key_3896_; lean_object* v_tail_3897_; uint8_t v___x_3898_; 
v_key_3896_ = lean_ctor_get(v_x_3894_, 0);
v_tail_3897_ = lean_ctor_get(v_x_3894_, 2);
v___x_3898_ = l_Legal_USTax_Hunt_Basis_instBEqSt_beq(v_key_3896_, v_a_3893_);
if (v___x_3898_ == 0)
{
v_x_3894_ = v_tail_3897_;
goto _start;
}
else
{
return v___x_3898_;
}
}
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2_spec__3___redArg___boxed(lean_object* v_a_3900_, lean_object* v_x_3901_){
_start:
{
uint8_t v_res_3902_; lean_object* v_r_3903_; 
v_res_3902_ = l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2_spec__3___redArg(v_a_3900_, v_x_3901_);
lean_dec(v_x_3901_);
lean_dec_ref(v_a_3900_);
v_r_3903_ = lean_box(v_res_3902_);
return v_r_3903_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_foldlM___at___00__private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3_spec__5_spec__6_spec__17___redArg(lean_object* v_x_3904_, lean_object* v_x_3905_){
_start:
{
if (lean_obj_tag(v_x_3905_) == 0)
{
return v_x_3904_;
}
else
{
lean_object* v_key_3906_; lean_object* v_value_3907_; lean_object* v_tail_3908_; lean_object* v___x_3910_; uint8_t v_isShared_3911_; uint8_t v_isSharedCheck_3931_; 
v_key_3906_ = lean_ctor_get(v_x_3905_, 0);
v_value_3907_ = lean_ctor_get(v_x_3905_, 1);
v_tail_3908_ = lean_ctor_get(v_x_3905_, 2);
v_isSharedCheck_3931_ = !lean_is_exclusive(v_x_3905_);
if (v_isSharedCheck_3931_ == 0)
{
v___x_3910_ = v_x_3905_;
v_isShared_3911_ = v_isSharedCheck_3931_;
goto v_resetjp_3909_;
}
else
{
lean_inc(v_tail_3908_);
lean_inc(v_value_3907_);
lean_inc(v_key_3906_);
lean_dec(v_x_3905_);
v___x_3910_ = lean_box(0);
v_isShared_3911_ = v_isSharedCheck_3931_;
goto v_resetjp_3909_;
}
v_resetjp_3909_:
{
lean_object* v___x_3912_; uint64_t v___x_3913_; uint64_t v___x_3914_; uint64_t v___x_3915_; uint64_t v_fold_3916_; uint64_t v___x_3917_; uint64_t v___x_3918_; uint64_t v___x_3919_; size_t v___x_3920_; size_t v___x_3921_; size_t v___x_3922_; size_t v___x_3923_; size_t v___x_3924_; lean_object* v___x_3925_; lean_object* v___x_3927_; 
v___x_3912_ = lean_array_get_size(v_x_3904_);
v___x_3913_ = l_Legal_USTax_Hunt_Basis_instHashableSt_hash(v_key_3906_);
v___x_3914_ = 32ULL;
v___x_3915_ = lean_uint64_shift_right(v___x_3913_, v___x_3914_);
v_fold_3916_ = lean_uint64_xor(v___x_3913_, v___x_3915_);
v___x_3917_ = 16ULL;
v___x_3918_ = lean_uint64_shift_right(v_fold_3916_, v___x_3917_);
v___x_3919_ = lean_uint64_xor(v_fold_3916_, v___x_3918_);
v___x_3920_ = lean_uint64_to_usize(v___x_3919_);
v___x_3921_ = lean_usize_of_nat(v___x_3912_);
v___x_3922_ = ((size_t)1ULL);
v___x_3923_ = lean_usize_sub(v___x_3921_, v___x_3922_);
v___x_3924_ = lean_usize_land(v___x_3920_, v___x_3923_);
v___x_3925_ = lean_array_uget_borrowed(v_x_3904_, v___x_3924_);
lean_inc(v___x_3925_);
if (v_isShared_3911_ == 0)
{
lean_ctor_set(v___x_3910_, 2, v___x_3925_);
v___x_3927_ = v___x_3910_;
goto v_reusejp_3926_;
}
else
{
lean_object* v_reuseFailAlloc_3930_; 
v_reuseFailAlloc_3930_ = lean_alloc_ctor(1, 3, 0);
lean_ctor_set(v_reuseFailAlloc_3930_, 0, v_key_3906_);
lean_ctor_set(v_reuseFailAlloc_3930_, 1, v_value_3907_);
lean_ctor_set(v_reuseFailAlloc_3930_, 2, v___x_3925_);
v___x_3927_ = v_reuseFailAlloc_3930_;
goto v_reusejp_3926_;
}
v_reusejp_3926_:
{
lean_object* v___x_3928_; 
v___x_3928_ = lean_array_uset(v_x_3904_, v___x_3924_, v___x_3927_);
v_x_3904_ = v___x_3928_;
v_x_3905_ = v_tail_3908_;
goto _start;
}
}
}
}
}
LEAN_EXPORT lean_object* l___private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3_spec__5_spec__6___redArg(lean_object* v_i_3932_, lean_object* v_source_3933_, lean_object* v_target_3934_){
_start:
{
lean_object* v___x_3935_; uint8_t v___x_3936_; 
v___x_3935_ = lean_array_get_size(v_source_3933_);
v___x_3936_ = lean_nat_dec_lt(v_i_3932_, v___x_3935_);
if (v___x_3936_ == 0)
{
lean_dec_ref(v_source_3933_);
lean_dec(v_i_3932_);
return v_target_3934_;
}
else
{
lean_object* v_es_3937_; lean_object* v___x_3938_; lean_object* v_source_3939_; lean_object* v_target_3940_; lean_object* v___x_3941_; lean_object* v___x_3942_; 
v_es_3937_ = lean_array_fget(v_source_3933_, v_i_3932_);
v___x_3938_ = lean_box(0);
v_source_3939_ = lean_array_fset(v_source_3933_, v_i_3932_, v___x_3938_);
v_target_3940_ = l_Std_DHashMap_Internal_AssocList_foldlM___at___00__private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3_spec__5_spec__6_spec__17___redArg(v_target_3934_, v_es_3937_);
v___x_3941_ = lean_unsigned_to_nat(1u);
v___x_3942_ = lean_nat_add(v_i_3932_, v___x_3941_);
lean_dec(v_i_3932_);
v_i_3932_ = v___x_3942_;
v_source_3933_ = v_source_3939_;
v_target_3934_ = v_target_3940_;
goto _start;
}
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3_spec__5___redArg(lean_object* v_data_3944_){
_start:
{
lean_object* v___x_3945_; lean_object* v___x_3946_; lean_object* v_nbuckets_3947_; lean_object* v___x_3948_; lean_object* v___x_3949_; lean_object* v___x_3950_; lean_object* v___x_3951_; lean_object* v___x_3952_; 
v___x_3945_ = lean_array_get_size(v_data_3944_);
v___x_3946_ = lean_unsigned_to_nat(2u);
v_nbuckets_3947_ = lean_nat_mul(v___x_3945_, v___x_3946_);
v___x_3948_ = lean_unsigned_to_nat(0u);
v___x_3949_ = lean_box(0);
v___x_3950_ = lean_mk_array(v_nbuckets_3947_, v___x_3949_);
v___x_3951_ = lean_array_propagate_mark(v_data_3944_, v___x_3950_);
v___x_3952_ = l___private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3_spec__5_spec__6___redArg(v___x_3948_, v_data_3944_, v___x_3951_);
return v___x_3952_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3___redArg(lean_object* v_m_3953_, lean_object* v_a_3954_, lean_object* v_b_3955_){
_start:
{
lean_object* v_size_3956_; lean_object* v_buckets_3957_; lean_object* v___x_3958_; uint64_t v___x_3959_; uint64_t v___x_3960_; uint64_t v___x_3961_; uint64_t v_fold_3962_; uint64_t v___x_3963_; uint64_t v___x_3964_; uint64_t v___x_3965_; size_t v___x_3966_; size_t v___x_3967_; size_t v___x_3968_; size_t v___x_3969_; size_t v___x_3970_; lean_object* v_bkt_3971_; uint8_t v___x_3972_; 
v_size_3956_ = lean_ctor_get(v_m_3953_, 0);
v_buckets_3957_ = lean_ctor_get(v_m_3953_, 1);
v___x_3958_ = lean_array_get_size(v_buckets_3957_);
v___x_3959_ = l_Legal_USTax_Hunt_Basis_instHashableSt_hash(v_a_3954_);
v___x_3960_ = 32ULL;
v___x_3961_ = lean_uint64_shift_right(v___x_3959_, v___x_3960_);
v_fold_3962_ = lean_uint64_xor(v___x_3959_, v___x_3961_);
v___x_3963_ = 16ULL;
v___x_3964_ = lean_uint64_shift_right(v_fold_3962_, v___x_3963_);
v___x_3965_ = lean_uint64_xor(v_fold_3962_, v___x_3964_);
v___x_3966_ = lean_uint64_to_usize(v___x_3965_);
v___x_3967_ = lean_usize_of_nat(v___x_3958_);
v___x_3968_ = ((size_t)1ULL);
v___x_3969_ = lean_usize_sub(v___x_3967_, v___x_3968_);
v___x_3970_ = lean_usize_land(v___x_3966_, v___x_3969_);
v_bkt_3971_ = lean_array_uget_borrowed(v_buckets_3957_, v___x_3970_);
v___x_3972_ = l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2_spec__3___redArg(v_a_3954_, v_bkt_3971_);
if (v___x_3972_ == 0)
{
lean_object* v___x_3974_; uint8_t v_isShared_3975_; uint8_t v_isSharedCheck_3993_; 
lean_inc_ref(v_buckets_3957_);
lean_inc(v_size_3956_);
v_isSharedCheck_3993_ = !lean_is_exclusive(v_m_3953_);
if (v_isSharedCheck_3993_ == 0)
{
lean_object* v_unused_3994_; lean_object* v_unused_3995_; 
v_unused_3994_ = lean_ctor_get(v_m_3953_, 1);
lean_dec(v_unused_3994_);
v_unused_3995_ = lean_ctor_get(v_m_3953_, 0);
lean_dec(v_unused_3995_);
v___x_3974_ = v_m_3953_;
v_isShared_3975_ = v_isSharedCheck_3993_;
goto v_resetjp_3973_;
}
else
{
lean_dec(v_m_3953_);
v___x_3974_ = lean_box(0);
v_isShared_3975_ = v_isSharedCheck_3993_;
goto v_resetjp_3973_;
}
v_resetjp_3973_:
{
lean_object* v___x_3976_; lean_object* v_size_x27_3977_; lean_object* v___x_3978_; lean_object* v_buckets_x27_3979_; lean_object* v___x_3980_; lean_object* v___x_3981_; lean_object* v___x_3982_; lean_object* v___x_3983_; lean_object* v___x_3984_; uint8_t v___x_3985_; 
v___x_3976_ = lean_unsigned_to_nat(1u);
v_size_x27_3977_ = lean_nat_add(v_size_3956_, v___x_3976_);
lean_dec(v_size_3956_);
lean_inc(v_bkt_3971_);
v___x_3978_ = lean_alloc_ctor(1, 3, 0);
lean_ctor_set(v___x_3978_, 0, v_a_3954_);
lean_ctor_set(v___x_3978_, 1, v_b_3955_);
lean_ctor_set(v___x_3978_, 2, v_bkt_3971_);
v_buckets_x27_3979_ = lean_array_uset(v_buckets_3957_, v___x_3970_, v___x_3978_);
v___x_3980_ = lean_unsigned_to_nat(4u);
v___x_3981_ = lean_nat_mul(v_size_x27_3977_, v___x_3980_);
v___x_3982_ = lean_unsigned_to_nat(3u);
v___x_3983_ = lean_nat_div(v___x_3981_, v___x_3982_);
lean_dec(v___x_3981_);
v___x_3984_ = lean_array_get_size(v_buckets_x27_3979_);
v___x_3985_ = lean_nat_dec_le(v___x_3983_, v___x_3984_);
lean_dec(v___x_3983_);
if (v___x_3985_ == 0)
{
lean_object* v_val_3986_; lean_object* v___x_3988_; 
v_val_3986_ = l_Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3_spec__5___redArg(v_buckets_x27_3979_);
if (v_isShared_3975_ == 0)
{
lean_ctor_set(v___x_3974_, 1, v_val_3986_);
lean_ctor_set(v___x_3974_, 0, v_size_x27_3977_);
v___x_3988_ = v___x_3974_;
goto v_reusejp_3987_;
}
else
{
lean_object* v_reuseFailAlloc_3989_; 
v_reuseFailAlloc_3989_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_3989_, 0, v_size_x27_3977_);
lean_ctor_set(v_reuseFailAlloc_3989_, 1, v_val_3986_);
v___x_3988_ = v_reuseFailAlloc_3989_;
goto v_reusejp_3987_;
}
v_reusejp_3987_:
{
return v___x_3988_;
}
}
else
{
lean_object* v___x_3991_; 
if (v_isShared_3975_ == 0)
{
lean_ctor_set(v___x_3974_, 1, v_buckets_x27_3979_);
lean_ctor_set(v___x_3974_, 0, v_size_x27_3977_);
v___x_3991_ = v___x_3974_;
goto v_reusejp_3990_;
}
else
{
lean_object* v_reuseFailAlloc_3992_; 
v_reuseFailAlloc_3992_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_3992_, 0, v_size_x27_3977_);
lean_ctor_set(v_reuseFailAlloc_3992_, 1, v_buckets_x27_3979_);
v___x_3991_ = v_reuseFailAlloc_3992_;
goto v_reusejp_3990_;
}
v_reusejp_3990_:
{
return v___x_3991_;
}
}
}
}
else
{
lean_dec(v_b_3955_);
lean_dec_ref(v_a_3954_);
return v_m_3953_;
}
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_replace___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__9___redArg(lean_object* v_a_3996_, lean_object* v_b_3997_, lean_object* v_x_3998_){
_start:
{
if (lean_obj_tag(v_x_3998_) == 0)
{
lean_dec(v_b_3997_);
lean_dec_ref(v_a_3996_);
return v_x_3998_;
}
else
{
lean_object* v_key_3999_; lean_object* v_value_4000_; lean_object* v_tail_4001_; lean_object* v___x_4003_; uint8_t v_isShared_4004_; uint8_t v_isSharedCheck_4013_; 
v_key_3999_ = lean_ctor_get(v_x_3998_, 0);
v_value_4000_ = lean_ctor_get(v_x_3998_, 1);
v_tail_4001_ = lean_ctor_get(v_x_3998_, 2);
v_isSharedCheck_4013_ = !lean_is_exclusive(v_x_3998_);
if (v_isSharedCheck_4013_ == 0)
{
v___x_4003_ = v_x_3998_;
v_isShared_4004_ = v_isSharedCheck_4013_;
goto v_resetjp_4002_;
}
else
{
lean_inc(v_tail_4001_);
lean_inc(v_value_4000_);
lean_inc(v_key_3999_);
lean_dec(v_x_3998_);
v___x_4003_ = lean_box(0);
v_isShared_4004_ = v_isSharedCheck_4013_;
goto v_resetjp_4002_;
}
v_resetjp_4002_:
{
uint8_t v___x_4005_; 
v___x_4005_ = lean_string_dec_eq(v_key_3999_, v_a_3996_);
if (v___x_4005_ == 0)
{
lean_object* v___x_4006_; lean_object* v___x_4008_; 
v___x_4006_ = l_Std_DHashMap_Internal_AssocList_replace___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__9___redArg(v_a_3996_, v_b_3997_, v_tail_4001_);
if (v_isShared_4004_ == 0)
{
lean_ctor_set(v___x_4003_, 2, v___x_4006_);
v___x_4008_ = v___x_4003_;
goto v_reusejp_4007_;
}
else
{
lean_object* v_reuseFailAlloc_4009_; 
v_reuseFailAlloc_4009_ = lean_alloc_ctor(1, 3, 0);
lean_ctor_set(v_reuseFailAlloc_4009_, 0, v_key_3999_);
lean_ctor_set(v_reuseFailAlloc_4009_, 1, v_value_4000_);
lean_ctor_set(v_reuseFailAlloc_4009_, 2, v___x_4006_);
v___x_4008_ = v_reuseFailAlloc_4009_;
goto v_reusejp_4007_;
}
v_reusejp_4007_:
{
return v___x_4008_;
}
}
else
{
lean_object* v___x_4011_; 
lean_dec(v_value_4000_);
lean_dec(v_key_3999_);
if (v_isShared_4004_ == 0)
{
lean_ctor_set(v___x_4003_, 1, v_b_3997_);
lean_ctor_set(v___x_4003_, 0, v_a_3996_);
v___x_4011_ = v___x_4003_;
goto v_reusejp_4010_;
}
else
{
lean_object* v_reuseFailAlloc_4012_; 
v_reuseFailAlloc_4012_ = lean_alloc_ctor(1, 3, 0);
lean_ctor_set(v_reuseFailAlloc_4012_, 0, v_a_3996_);
lean_ctor_set(v_reuseFailAlloc_4012_, 1, v_b_3997_);
lean_ctor_set(v_reuseFailAlloc_4012_, 2, v_tail_4001_);
v___x_4011_ = v_reuseFailAlloc_4012_;
goto v_reusejp_4010_;
}
v_reusejp_4010_:
{
return v___x_4011_;
}
}
}
}
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_foldlM___at___00__private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__8_spec__10_spec__21___redArg(lean_object* v_x_4014_, lean_object* v_x_4015_){
_start:
{
if (lean_obj_tag(v_x_4015_) == 0)
{
return v_x_4014_;
}
else
{
lean_object* v_key_4016_; lean_object* v_value_4017_; lean_object* v_tail_4018_; lean_object* v___x_4020_; uint8_t v_isShared_4021_; uint8_t v_isSharedCheck_4041_; 
v_key_4016_ = lean_ctor_get(v_x_4015_, 0);
v_value_4017_ = lean_ctor_get(v_x_4015_, 1);
v_tail_4018_ = lean_ctor_get(v_x_4015_, 2);
v_isSharedCheck_4041_ = !lean_is_exclusive(v_x_4015_);
if (v_isSharedCheck_4041_ == 0)
{
v___x_4020_ = v_x_4015_;
v_isShared_4021_ = v_isSharedCheck_4041_;
goto v_resetjp_4019_;
}
else
{
lean_inc(v_tail_4018_);
lean_inc(v_value_4017_);
lean_inc(v_key_4016_);
lean_dec(v_x_4015_);
v___x_4020_ = lean_box(0);
v_isShared_4021_ = v_isSharedCheck_4041_;
goto v_resetjp_4019_;
}
v_resetjp_4019_:
{
lean_object* v___x_4022_; uint64_t v___x_4023_; uint64_t v___x_4024_; uint64_t v___x_4025_; uint64_t v_fold_4026_; uint64_t v___x_4027_; uint64_t v___x_4028_; uint64_t v___x_4029_; size_t v___x_4030_; size_t v___x_4031_; size_t v___x_4032_; size_t v___x_4033_; size_t v___x_4034_; lean_object* v___x_4035_; lean_object* v___x_4037_; 
v___x_4022_ = lean_array_get_size(v_x_4014_);
v___x_4023_ = lean_string_hash(v_key_4016_);
v___x_4024_ = 32ULL;
v___x_4025_ = lean_uint64_shift_right(v___x_4023_, v___x_4024_);
v_fold_4026_ = lean_uint64_xor(v___x_4023_, v___x_4025_);
v___x_4027_ = 16ULL;
v___x_4028_ = lean_uint64_shift_right(v_fold_4026_, v___x_4027_);
v___x_4029_ = lean_uint64_xor(v_fold_4026_, v___x_4028_);
v___x_4030_ = lean_uint64_to_usize(v___x_4029_);
v___x_4031_ = lean_usize_of_nat(v___x_4022_);
v___x_4032_ = ((size_t)1ULL);
v___x_4033_ = lean_usize_sub(v___x_4031_, v___x_4032_);
v___x_4034_ = lean_usize_land(v___x_4030_, v___x_4033_);
v___x_4035_ = lean_array_uget_borrowed(v_x_4014_, v___x_4034_);
lean_inc(v___x_4035_);
if (v_isShared_4021_ == 0)
{
lean_ctor_set(v___x_4020_, 2, v___x_4035_);
v___x_4037_ = v___x_4020_;
goto v_reusejp_4036_;
}
else
{
lean_object* v_reuseFailAlloc_4040_; 
v_reuseFailAlloc_4040_ = lean_alloc_ctor(1, 3, 0);
lean_ctor_set(v_reuseFailAlloc_4040_, 0, v_key_4016_);
lean_ctor_set(v_reuseFailAlloc_4040_, 1, v_value_4017_);
lean_ctor_set(v_reuseFailAlloc_4040_, 2, v___x_4035_);
v___x_4037_ = v_reuseFailAlloc_4040_;
goto v_reusejp_4036_;
}
v_reusejp_4036_:
{
lean_object* v___x_4038_; 
v___x_4038_ = lean_array_uset(v_x_4014_, v___x_4034_, v___x_4037_);
v_x_4014_ = v___x_4038_;
v_x_4015_ = v_tail_4018_;
goto _start;
}
}
}
}
}
LEAN_EXPORT lean_object* l___private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__8_spec__10___redArg(lean_object* v_i_4042_, lean_object* v_source_4043_, lean_object* v_target_4044_){
_start:
{
lean_object* v___x_4045_; uint8_t v___x_4046_; 
v___x_4045_ = lean_array_get_size(v_source_4043_);
v___x_4046_ = lean_nat_dec_lt(v_i_4042_, v___x_4045_);
if (v___x_4046_ == 0)
{
lean_dec_ref(v_source_4043_);
lean_dec(v_i_4042_);
return v_target_4044_;
}
else
{
lean_object* v_es_4047_; lean_object* v___x_4048_; lean_object* v_source_4049_; lean_object* v_target_4050_; lean_object* v___x_4051_; lean_object* v___x_4052_; 
v_es_4047_ = lean_array_fget(v_source_4043_, v_i_4042_);
v___x_4048_ = lean_box(0);
v_source_4049_ = lean_array_fset(v_source_4043_, v_i_4042_, v___x_4048_);
v_target_4050_ = l_Std_DHashMap_Internal_AssocList_foldlM___at___00__private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__8_spec__10_spec__21___redArg(v_target_4044_, v_es_4047_);
v___x_4051_ = lean_unsigned_to_nat(1u);
v___x_4052_ = lean_nat_add(v_i_4042_, v___x_4051_);
lean_dec(v_i_4042_);
v_i_4042_ = v___x_4052_;
v_source_4043_ = v_source_4049_;
v_target_4044_ = v_target_4050_;
goto _start;
}
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__8___redArg(lean_object* v_data_4054_){
_start:
{
lean_object* v___x_4055_; lean_object* v___x_4056_; lean_object* v_nbuckets_4057_; lean_object* v___x_4058_; lean_object* v___x_4059_; lean_object* v___x_4060_; lean_object* v___x_4061_; lean_object* v___x_4062_; 
v___x_4055_ = lean_array_get_size(v_data_4054_);
v___x_4056_ = lean_unsigned_to_nat(2u);
v_nbuckets_4057_ = lean_nat_mul(v___x_4055_, v___x_4056_);
v___x_4058_ = lean_unsigned_to_nat(0u);
v___x_4059_ = lean_box(0);
v___x_4060_ = lean_mk_array(v_nbuckets_4057_, v___x_4059_);
v___x_4061_ = lean_array_propagate_mark(v_data_4054_, v___x_4060_);
v___x_4062_ = l___private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__8_spec__10___redArg(v___x_4058_, v_data_4054_, v___x_4061_);
return v___x_4062_;
}
}
LEAN_EXPORT uint8_t l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__7___redArg(lean_object* v_a_4063_, lean_object* v_x_4064_){
_start:
{
if (lean_obj_tag(v_x_4064_) == 0)
{
uint8_t v___x_4065_; 
v___x_4065_ = 0;
return v___x_4065_;
}
else
{
lean_object* v_key_4066_; lean_object* v_tail_4067_; uint8_t v___x_4068_; 
v_key_4066_ = lean_ctor_get(v_x_4064_, 0);
v_tail_4067_ = lean_ctor_get(v_x_4064_, 2);
v___x_4068_ = lean_string_dec_eq(v_key_4066_, v_a_4063_);
if (v___x_4068_ == 0)
{
v_x_4064_ = v_tail_4067_;
goto _start;
}
else
{
return v___x_4068_;
}
}
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__7___redArg___boxed(lean_object* v_a_4070_, lean_object* v_x_4071_){
_start:
{
uint8_t v_res_4072_; lean_object* v_r_4073_; 
v_res_4072_ = l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__7___redArg(v_a_4070_, v_x_4071_);
lean_dec(v_x_4071_);
lean_dec_ref(v_a_4070_);
v_r_4073_ = lean_box(v_res_4072_);
return v_r_4073_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4___redArg(lean_object* v_m_4074_, lean_object* v_a_4075_, lean_object* v_b_4076_){
_start:
{
lean_object* v_size_4077_; lean_object* v_buckets_4078_; lean_object* v___x_4080_; uint8_t v_isShared_4081_; uint8_t v_isSharedCheck_4121_; 
v_size_4077_ = lean_ctor_get(v_m_4074_, 0);
v_buckets_4078_ = lean_ctor_get(v_m_4074_, 1);
v_isSharedCheck_4121_ = !lean_is_exclusive(v_m_4074_);
if (v_isSharedCheck_4121_ == 0)
{
v___x_4080_ = v_m_4074_;
v_isShared_4081_ = v_isSharedCheck_4121_;
goto v_resetjp_4079_;
}
else
{
lean_inc(v_buckets_4078_);
lean_inc(v_size_4077_);
lean_dec(v_m_4074_);
v___x_4080_ = lean_box(0);
v_isShared_4081_ = v_isSharedCheck_4121_;
goto v_resetjp_4079_;
}
v_resetjp_4079_:
{
lean_object* v___x_4082_; uint64_t v___x_4083_; uint64_t v___x_4084_; uint64_t v___x_4085_; uint64_t v_fold_4086_; uint64_t v___x_4087_; uint64_t v___x_4088_; uint64_t v___x_4089_; size_t v___x_4090_; size_t v___x_4091_; size_t v___x_4092_; size_t v___x_4093_; size_t v___x_4094_; lean_object* v_bkt_4095_; uint8_t v___x_4096_; 
v___x_4082_ = lean_array_get_size(v_buckets_4078_);
v___x_4083_ = lean_string_hash(v_a_4075_);
v___x_4084_ = 32ULL;
v___x_4085_ = lean_uint64_shift_right(v___x_4083_, v___x_4084_);
v_fold_4086_ = lean_uint64_xor(v___x_4083_, v___x_4085_);
v___x_4087_ = 16ULL;
v___x_4088_ = lean_uint64_shift_right(v_fold_4086_, v___x_4087_);
v___x_4089_ = lean_uint64_xor(v_fold_4086_, v___x_4088_);
v___x_4090_ = lean_uint64_to_usize(v___x_4089_);
v___x_4091_ = lean_usize_of_nat(v___x_4082_);
v___x_4092_ = ((size_t)1ULL);
v___x_4093_ = lean_usize_sub(v___x_4091_, v___x_4092_);
v___x_4094_ = lean_usize_land(v___x_4090_, v___x_4093_);
v_bkt_4095_ = lean_array_uget_borrowed(v_buckets_4078_, v___x_4094_);
v___x_4096_ = l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__7___redArg(v_a_4075_, v_bkt_4095_);
if (v___x_4096_ == 0)
{
lean_object* v___x_4097_; lean_object* v_size_x27_4098_; lean_object* v___x_4099_; lean_object* v_buckets_x27_4100_; lean_object* v___x_4101_; lean_object* v___x_4102_; lean_object* v___x_4103_; lean_object* v___x_4104_; lean_object* v___x_4105_; uint8_t v___x_4106_; 
v___x_4097_ = lean_unsigned_to_nat(1u);
v_size_x27_4098_ = lean_nat_add(v_size_4077_, v___x_4097_);
lean_dec(v_size_4077_);
lean_inc(v_bkt_4095_);
v___x_4099_ = lean_alloc_ctor(1, 3, 0);
lean_ctor_set(v___x_4099_, 0, v_a_4075_);
lean_ctor_set(v___x_4099_, 1, v_b_4076_);
lean_ctor_set(v___x_4099_, 2, v_bkt_4095_);
v_buckets_x27_4100_ = lean_array_uset(v_buckets_4078_, v___x_4094_, v___x_4099_);
v___x_4101_ = lean_unsigned_to_nat(4u);
v___x_4102_ = lean_nat_mul(v_size_x27_4098_, v___x_4101_);
v___x_4103_ = lean_unsigned_to_nat(3u);
v___x_4104_ = lean_nat_div(v___x_4102_, v___x_4103_);
lean_dec(v___x_4102_);
v___x_4105_ = lean_array_get_size(v_buckets_x27_4100_);
v___x_4106_ = lean_nat_dec_le(v___x_4104_, v___x_4105_);
lean_dec(v___x_4104_);
if (v___x_4106_ == 0)
{
lean_object* v_val_4107_; lean_object* v___x_4109_; 
v_val_4107_ = l_Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__8___redArg(v_buckets_x27_4100_);
if (v_isShared_4081_ == 0)
{
lean_ctor_set(v___x_4080_, 1, v_val_4107_);
lean_ctor_set(v___x_4080_, 0, v_size_x27_4098_);
v___x_4109_ = v___x_4080_;
goto v_reusejp_4108_;
}
else
{
lean_object* v_reuseFailAlloc_4110_; 
v_reuseFailAlloc_4110_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4110_, 0, v_size_x27_4098_);
lean_ctor_set(v_reuseFailAlloc_4110_, 1, v_val_4107_);
v___x_4109_ = v_reuseFailAlloc_4110_;
goto v_reusejp_4108_;
}
v_reusejp_4108_:
{
return v___x_4109_;
}
}
else
{
lean_object* v___x_4112_; 
if (v_isShared_4081_ == 0)
{
lean_ctor_set(v___x_4080_, 1, v_buckets_x27_4100_);
lean_ctor_set(v___x_4080_, 0, v_size_x27_4098_);
v___x_4112_ = v___x_4080_;
goto v_reusejp_4111_;
}
else
{
lean_object* v_reuseFailAlloc_4113_; 
v_reuseFailAlloc_4113_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4113_, 0, v_size_x27_4098_);
lean_ctor_set(v_reuseFailAlloc_4113_, 1, v_buckets_x27_4100_);
v___x_4112_ = v_reuseFailAlloc_4113_;
goto v_reusejp_4111_;
}
v_reusejp_4111_:
{
return v___x_4112_;
}
}
}
else
{
lean_object* v___x_4114_; lean_object* v_buckets_x27_4115_; lean_object* v___x_4116_; lean_object* v___x_4117_; lean_object* v___x_4119_; 
lean_inc(v_bkt_4095_);
v___x_4114_ = lean_box(0);
v_buckets_x27_4115_ = lean_array_uset(v_buckets_4078_, v___x_4094_, v___x_4114_);
v___x_4116_ = l_Std_DHashMap_Internal_AssocList_replace___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__9___redArg(v_a_4075_, v_b_4076_, v_bkt_4095_);
v___x_4117_ = lean_array_uset(v_buckets_x27_4115_, v___x_4094_, v___x_4116_);
if (v_isShared_4081_ == 0)
{
lean_ctor_set(v___x_4080_, 1, v___x_4117_);
v___x_4119_ = v___x_4080_;
goto v_reusejp_4118_;
}
else
{
lean_object* v_reuseFailAlloc_4120_; 
v_reuseFailAlloc_4120_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4120_, 0, v_size_4077_);
lean_ctor_set(v_reuseFailAlloc_4120_, 1, v___x_4117_);
v___x_4119_ = v_reuseFailAlloc_4120_;
goto v_reusejp_4118_;
}
v_reusejp_4118_:
{
return v___x_4119_;
}
}
}
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_get_x3f___at___00Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5_spec__11___redArg(lean_object* v_a_4122_, lean_object* v_x_4123_){
_start:
{
if (lean_obj_tag(v_x_4123_) == 0)
{
lean_object* v___x_4124_; 
v___x_4124_ = lean_box(0);
return v___x_4124_;
}
else
{
lean_object* v_key_4125_; lean_object* v_value_4126_; lean_object* v_tail_4127_; uint8_t v___x_4128_; 
v_key_4125_ = lean_ctor_get(v_x_4123_, 0);
v_value_4126_ = lean_ctor_get(v_x_4123_, 1);
v_tail_4127_ = lean_ctor_get(v_x_4123_, 2);
v___x_4128_ = lean_string_dec_eq(v_key_4125_, v_a_4122_);
if (v___x_4128_ == 0)
{
v_x_4123_ = v_tail_4127_;
goto _start;
}
else
{
lean_object* v___x_4130_; 
lean_inc(v_value_4126_);
v___x_4130_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v___x_4130_, 0, v_value_4126_);
return v___x_4130_;
}
}
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_get_x3f___at___00Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5_spec__11___redArg___boxed(lean_object* v_a_4131_, lean_object* v_x_4132_){
_start:
{
lean_object* v_res_4133_; 
v_res_4133_ = l_Std_DHashMap_Internal_AssocList_get_x3f___at___00Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5_spec__11___redArg(v_a_4131_, v_x_4132_);
lean_dec(v_x_4132_);
lean_dec_ref(v_a_4131_);
return v_res_4133_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5___redArg(lean_object* v_m_4134_, lean_object* v_a_4135_){
_start:
{
lean_object* v_buckets_4136_; lean_object* v___x_4137_; uint64_t v___x_4138_; uint64_t v___x_4139_; uint64_t v___x_4140_; uint64_t v_fold_4141_; uint64_t v___x_4142_; uint64_t v___x_4143_; uint64_t v___x_4144_; size_t v___x_4145_; size_t v___x_4146_; size_t v___x_4147_; size_t v___x_4148_; size_t v___x_4149_; lean_object* v___x_4150_; lean_object* v___x_4151_; 
v_buckets_4136_ = lean_ctor_get(v_m_4134_, 1);
v___x_4137_ = lean_array_get_size(v_buckets_4136_);
v___x_4138_ = lean_string_hash(v_a_4135_);
v___x_4139_ = 32ULL;
v___x_4140_ = lean_uint64_shift_right(v___x_4138_, v___x_4139_);
v_fold_4141_ = lean_uint64_xor(v___x_4138_, v___x_4140_);
v___x_4142_ = 16ULL;
v___x_4143_ = lean_uint64_shift_right(v_fold_4141_, v___x_4142_);
v___x_4144_ = lean_uint64_xor(v_fold_4141_, v___x_4143_);
v___x_4145_ = lean_uint64_to_usize(v___x_4144_);
v___x_4146_ = lean_usize_of_nat(v___x_4137_);
v___x_4147_ = ((size_t)1ULL);
v___x_4148_ = lean_usize_sub(v___x_4146_, v___x_4147_);
v___x_4149_ = lean_usize_land(v___x_4145_, v___x_4148_);
v___x_4150_ = lean_array_uget_borrowed(v_buckets_4136_, v___x_4149_);
v___x_4151_ = l_Std_DHashMap_Internal_AssocList_get_x3f___at___00Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5_spec__11___redArg(v_a_4135_, v___x_4150_);
return v___x_4151_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5___redArg___boxed(lean_object* v_m_4152_, lean_object* v_a_4153_){
_start:
{
lean_object* v_res_4154_; 
v_res_4154_ = l_Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5___redArg(v_m_4152_, v_a_4153_);
lean_dec_ref(v_a_4153_);
lean_dec_ref(v_m_4152_);
return v_res_4154_;
}
}
LEAN_EXPORT uint8_t l_Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2___redArg(lean_object* v_m_4155_, lean_object* v_a_4156_){
_start:
{
lean_object* v_buckets_4157_; lean_object* v___x_4158_; uint64_t v___x_4159_; uint64_t v___x_4160_; uint64_t v___x_4161_; uint64_t v_fold_4162_; uint64_t v___x_4163_; uint64_t v___x_4164_; uint64_t v___x_4165_; size_t v___x_4166_; size_t v___x_4167_; size_t v___x_4168_; size_t v___x_4169_; size_t v___x_4170_; lean_object* v___x_4171_; uint8_t v___x_4172_; 
v_buckets_4157_ = lean_ctor_get(v_m_4155_, 1);
v___x_4158_ = lean_array_get_size(v_buckets_4157_);
v___x_4159_ = l_Legal_USTax_Hunt_Basis_instHashableSt_hash(v_a_4156_);
v___x_4160_ = 32ULL;
v___x_4161_ = lean_uint64_shift_right(v___x_4159_, v___x_4160_);
v_fold_4162_ = lean_uint64_xor(v___x_4159_, v___x_4161_);
v___x_4163_ = 16ULL;
v___x_4164_ = lean_uint64_shift_right(v_fold_4162_, v___x_4163_);
v___x_4165_ = lean_uint64_xor(v_fold_4162_, v___x_4164_);
v___x_4166_ = lean_uint64_to_usize(v___x_4165_);
v___x_4167_ = lean_usize_of_nat(v___x_4158_);
v___x_4168_ = ((size_t)1ULL);
v___x_4169_ = lean_usize_sub(v___x_4167_, v___x_4168_);
v___x_4170_ = lean_usize_land(v___x_4166_, v___x_4169_);
v___x_4171_ = lean_array_uget_borrowed(v_buckets_4157_, v___x_4170_);
v___x_4172_ = l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2_spec__3___redArg(v_a_4156_, v___x_4171_);
return v___x_4172_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2___redArg___boxed(lean_object* v_m_4173_, lean_object* v_a_4174_){
_start:
{
uint8_t v_res_4175_; lean_object* v_r_4176_; 
v_res_4175_ = l_Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2___redArg(v_m_4173_, v_a_4174_);
lean_dec_ref(v_a_4174_);
lean_dec_ref(v_m_4173_);
v_r_4176_ = lean_box(v_res_4175_);
return v_r_4176_;
}
}
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__6___redArg(lean_object* v_allowed_4178_, lean_object* v_cfg_4179_, lean_object* v_fst_4180_, lean_object* v_snd_4181_, lean_object* v_fst_4182_, lean_object* v_fst_4183_, lean_object* v_as_x27_4184_, lean_object* v_b_4185_){
_start:
{
if (lean_obj_tag(v_as_x27_4184_) == 0)
{
lean_object* v___x_4187_; 
lean_dec(v_fst_4183_);
lean_dec(v_fst_4182_);
lean_dec_ref(v_fst_4180_);
lean_dec_ref(v_allowed_4178_);
v___x_4187_ = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(v___x_4187_, 0, v_b_4185_);
return v___x_4187_;
}
else
{
lean_object* v_snd_4188_; lean_object* v_snd_4189_; lean_object* v_head_4190_; lean_object* v_tail_4191_; lean_object* v_fst_4192_; lean_object* v___x_4194_; uint8_t v_isShared_4195_; uint8_t v_isSharedCheck_4299_; 
v_snd_4188_ = lean_ctor_get(v_b_4185_, 1);
lean_inc(v_snd_4188_);
v_snd_4189_ = lean_ctor_get(v_snd_4188_, 1);
lean_inc(v_snd_4189_);
v_head_4190_ = lean_ctor_get(v_as_x27_4184_, 0);
v_tail_4191_ = lean_ctor_get(v_as_x27_4184_, 1);
v_fst_4192_ = lean_ctor_get(v_b_4185_, 0);
v_isSharedCheck_4299_ = !lean_is_exclusive(v_b_4185_);
if (v_isSharedCheck_4299_ == 0)
{
lean_object* v_unused_4300_; 
v_unused_4300_ = lean_ctor_get(v_b_4185_, 1);
lean_dec(v_unused_4300_);
v___x_4194_ = v_b_4185_;
v_isShared_4195_ = v_isSharedCheck_4299_;
goto v_resetjp_4193_;
}
else
{
lean_inc(v_fst_4192_);
lean_dec(v_b_4185_);
v___x_4194_ = lean_box(0);
v_isShared_4195_ = v_isSharedCheck_4299_;
goto v_resetjp_4193_;
}
v_resetjp_4193_:
{
lean_object* v_fst_4196_; lean_object* v___x_4198_; uint8_t v_isShared_4199_; uint8_t v_isSharedCheck_4297_; 
v_fst_4196_ = lean_ctor_get(v_snd_4188_, 0);
v_isSharedCheck_4297_ = !lean_is_exclusive(v_snd_4188_);
if (v_isSharedCheck_4297_ == 0)
{
lean_object* v_unused_4298_; 
v_unused_4298_ = lean_ctor_get(v_snd_4188_, 1);
lean_dec(v_unused_4298_);
v___x_4198_ = v_snd_4188_;
v_isShared_4199_ = v_isSharedCheck_4297_;
goto v_resetjp_4197_;
}
else
{
lean_inc(v_fst_4196_);
lean_dec(v_snd_4188_);
v___x_4198_ = lean_box(0);
v_isShared_4199_ = v_isSharedCheck_4297_;
goto v_resetjp_4197_;
}
v_resetjp_4197_:
{
lean_object* v_fst_4200_; lean_object* v_snd_4201_; lean_object* v___x_4203_; uint8_t v_isShared_4204_; uint8_t v_isSharedCheck_4296_; 
v_fst_4200_ = lean_ctor_get(v_snd_4189_, 0);
v_snd_4201_ = lean_ctor_get(v_snd_4189_, 1);
v_isSharedCheck_4296_ = !lean_is_exclusive(v_snd_4189_);
if (v_isSharedCheck_4296_ == 0)
{
v___x_4203_ = v_snd_4189_;
v_isShared_4204_ = v_isSharedCheck_4296_;
goto v_resetjp_4202_;
}
else
{
lean_inc(v_snd_4201_);
lean_inc(v_fst_4200_);
lean_dec(v_snd_4189_);
v___x_4203_ = lean_box(0);
v_isShared_4204_ = v_isSharedCheck_4296_;
goto v_resetjp_4202_;
}
v_resetjp_4202_:
{
lean_object* v___y_4206_; lean_object* v___x_4217_; uint8_t v___x_4218_; 
lean_inc_ref(v_allowed_4178_);
lean_inc(v_head_4190_);
v___x_4217_ = lean_apply_1(v_allowed_4178_, v_head_4190_);
v___x_4218_ = lean_unbox(v___x_4217_);
if (v___x_4218_ == 0)
{
lean_object* v___x_4219_; lean_object* v___x_4220_; lean_object* v___x_4221_; 
lean_del_object(v___x_4203_);
lean_del_object(v___x_4198_);
lean_del_object(v___x_4194_);
v___x_4219_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4219_, 0, v_fst_4200_);
lean_ctor_set(v___x_4219_, 1, v_snd_4201_);
v___x_4220_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4220_, 0, v_fst_4196_);
lean_ctor_set(v___x_4220_, 1, v___x_4219_);
v___x_4221_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4221_, 0, v_fst_4192_);
lean_ctor_set(v___x_4221_, 1, v___x_4220_);
v_as_x27_4184_ = v_tail_4191_;
v_b_4185_ = v___x_4221_;
goto _start;
}
else
{
lean_object* v___x_4223_; 
lean_inc(v_head_4190_);
lean_inc_ref(v_fst_4180_);
v___x_4223_ = l_Legal_USTax_Hunt_Basis_step(v_cfg_4179_, v_fst_4180_, v_head_4190_);
if (lean_obj_tag(v___x_4223_) == 0)
{
lean_object* v___x_4224_; lean_object* v___x_4225_; lean_object* v___x_4226_; 
lean_del_object(v___x_4203_);
lean_del_object(v___x_4198_);
lean_del_object(v___x_4194_);
v___x_4224_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4224_, 0, v_fst_4200_);
lean_ctor_set(v___x_4224_, 1, v_snd_4201_);
v___x_4225_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4225_, 0, v_fst_4196_);
lean_ctor_set(v___x_4225_, 1, v___x_4224_);
v___x_4226_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4226_, 0, v_fst_4192_);
lean_ctor_set(v___x_4226_, 1, v___x_4225_);
v_as_x27_4184_ = v_tail_4191_;
v_b_4185_ = v___x_4226_;
goto _start;
}
else
{
lean_object* v_val_4228_; lean_object* v___x_4229_; lean_object* v_fst_4230_; lean_object* v_snd_4231_; lean_object* v___x_4233_; uint8_t v_isShared_4234_; uint8_t v_isSharedCheck_4295_; 
v_val_4228_ = lean_ctor_get(v___x_4223_, 0);
lean_inc(v_val_4228_);
lean_dec_ref_known(v___x_4223_, 1);
lean_inc(v_head_4190_);
lean_inc_ref(v_fst_4180_);
v___x_4229_ = l_Legal_USTax_Hunt_Basis_describe(v_fst_4180_, v_head_4190_);
v_fst_4230_ = lean_ctor_get(v___x_4229_, 0);
v_snd_4231_ = lean_ctor_get(v___x_4229_, 1);
v_isSharedCheck_4295_ = !lean_is_exclusive(v___x_4229_);
if (v_isSharedCheck_4295_ == 0)
{
v___x_4233_ = v___x_4229_;
v_isShared_4234_ = v_isSharedCheck_4295_;
goto v_resetjp_4232_;
}
else
{
lean_inc(v_snd_4231_);
lean_inc(v_fst_4230_);
lean_dec(v___x_4229_);
v___x_4233_ = lean_box(0);
v_isShared_4234_ = v_isSharedCheck_4295_;
goto v_resetjp_4232_;
}
v_resetjp_4232_:
{
lean_object* v___x_4235_; lean_object* v___x_4236_; lean_object* v___x_4237_; lean_object* v___y_4239_; lean_object* v___y_4240_; lean_object* v___y_4241_; lean_object* v___y_4242_; lean_object* v___y_4243_; lean_object* v___y_4256_; lean_object* v___y_4257_; lean_object* v___x_4288_; lean_object* v___y_4290_; uint8_t v___x_4293_; 
v___x_4235_ = lean_unsigned_to_nat(1u);
lean_inc(v_head_4190_);
v___x_4236_ = l_Legal_USTax_Hunt_Basis_giftOver(v_fst_4180_, v_head_4190_);
v___x_4237_ = lean_nat_add(v_snd_4181_, v___x_4236_);
lean_dec(v___x_4236_);
v___x_4288_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__15));
v___x_4293_ = lean_string_dec_eq(v_fst_4230_, v___x_4288_);
if (v___x_4293_ == 0)
{
lean_object* v___x_4294_; 
lean_inc(v_fst_4183_);
v___x_4294_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_4294_, 0, v_fst_4230_);
lean_ctor_set(v___x_4294_, 1, v_fst_4183_);
v___y_4290_ = v___x_4294_;
goto v___jp_4289_;
}
else
{
lean_dec(v_fst_4230_);
lean_inc(v_fst_4183_);
v___y_4290_ = v_fst_4183_;
goto v___jp_4289_;
}
v___jp_4238_:
{
lean_object* v_cfS_4244_; lean_object* v_cfL_4245_; lean_object* v___x_4246_; lean_object* v___x_4247_; lean_object* v___x_4248_; lean_object* v___x_4250_; 
v_cfS_4244_ = lean_ctor_get(v___y_4239_, 3);
lean_inc(v_cfS_4244_);
v_cfL_4245_ = lean_ctor_get(v___y_4239_, 4);
lean_inc(v_cfL_4245_);
lean_dec_ref(v___y_4239_);
v___x_4246_ = lean_nat_add(v_cfS_4244_, v_cfL_4245_);
lean_dec(v_cfL_4245_);
lean_dec(v_cfS_4244_);
v___x_4247_ = lean_alloc_ctor(0, 4, 0);
lean_ctor_set(v___x_4247_, 0, v___y_4241_);
lean_ctor_set(v___x_4247_, 1, v___x_4237_);
lean_ctor_set(v___x_4247_, 2, v___x_4246_);
lean_ctor_set(v___x_4247_, 3, v___y_4242_);
v___x_4248_ = l_Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4___redArg(v_fst_4196_, v___y_4243_, v___x_4247_);
if (v_isShared_4234_ == 0)
{
lean_ctor_set(v___x_4233_, 1, v_snd_4201_);
lean_ctor_set(v___x_4233_, 0, v___y_4240_);
v___x_4250_ = v___x_4233_;
goto v_reusejp_4249_;
}
else
{
lean_object* v_reuseFailAlloc_4254_; 
v_reuseFailAlloc_4254_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4254_, 0, v___y_4240_);
lean_ctor_set(v_reuseFailAlloc_4254_, 1, v_snd_4201_);
v___x_4250_ = v_reuseFailAlloc_4254_;
goto v_reusejp_4249_;
}
v_reusejp_4249_:
{
lean_object* v___x_4251_; lean_object* v___x_4252_; 
v___x_4251_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4251_, 0, v___x_4248_);
lean_ctor_set(v___x_4251_, 1, v___x_4250_);
v___x_4252_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4252_, 0, v_fst_4192_);
lean_ctor_set(v___x_4252_, 1, v___x_4251_);
v_as_x27_4184_ = v_tail_4191_;
v_b_4185_ = v___x_4252_;
goto _start;
}
}
v___jp_4255_:
{
lean_object* v_year_4258_; lean_object* v_rJ_4259_; lean_object* v_tax_4260_; lean_object* v_horizon_4261_; uint8_t v___x_4262_; 
v_year_4258_ = lean_ctor_get(v_val_4228_, 1);
v_rJ_4259_ = lean_ctor_get(v_val_4228_, 3);
v_tax_4260_ = lean_ctor_get(v_val_4228_, 11);
v_horizon_4261_ = lean_ctor_get(v_cfg_4179_, 4);
v___x_4262_ = lean_nat_dec_eq(v_year_4258_, v_horizon_4261_);
if (v___x_4262_ == 0)
{
uint8_t v___x_4263_; 
lean_del_object(v___x_4233_);
lean_del_object(v___x_4203_);
lean_del_object(v___x_4198_);
lean_del_object(v___x_4194_);
v___x_4263_ = l_Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2___redArg(v_fst_4192_, v_val_4228_);
if (v___x_4263_ == 0)
{
lean_object* v___x_4264_; lean_object* v___x_4265_; lean_object* v___x_4266_; lean_object* v___x_4267_; lean_object* v___x_4268_; lean_object* v___x_4269_; lean_object* v___x_4270_; lean_object* v___x_4271_; lean_object* v___x_4272_; 
v___x_4264_ = lean_box(0);
lean_inc(v_val_4228_);
v___x_4265_ = l_Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3___redArg(v_fst_4192_, v_val_4228_, v___x_4264_);
v___x_4266_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4266_, 0, v___y_4257_);
lean_ctor_set(v___x_4266_, 1, v___x_4237_);
v___x_4267_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4267_, 0, v___y_4256_);
lean_ctor_set(v___x_4267_, 1, v___x_4266_);
v___x_4268_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4268_, 0, v_val_4228_);
lean_ctor_set(v___x_4268_, 1, v___x_4267_);
v___x_4269_ = lean_array_push(v_snd_4201_, v___x_4268_);
v___x_4270_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4270_, 0, v_fst_4200_);
lean_ctor_set(v___x_4270_, 1, v___x_4269_);
v___x_4271_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4271_, 0, v_fst_4196_);
lean_ctor_set(v___x_4271_, 1, v___x_4270_);
v___x_4272_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4272_, 0, v___x_4265_);
lean_ctor_set(v___x_4272_, 1, v___x_4271_);
v_as_x27_4184_ = v_tail_4191_;
v_b_4185_ = v___x_4272_;
goto _start;
}
else
{
lean_object* v___x_4274_; lean_object* v___x_4275_; lean_object* v___x_4276_; 
lean_dec(v___y_4257_);
lean_dec(v___y_4256_);
lean_dec(v___x_4237_);
lean_dec(v_val_4228_);
v___x_4274_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4274_, 0, v_fst_4200_);
lean_ctor_set(v___x_4274_, 1, v_snd_4201_);
v___x_4275_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4275_, 0, v_fst_4196_);
lean_ctor_set(v___x_4275_, 1, v___x_4274_);
v___x_4276_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4276_, 0, v_fst_4192_);
lean_ctor_set(v___x_4276_, 1, v___x_4275_);
v_as_x27_4184_ = v_tail_4191_;
v_b_4185_ = v___x_4276_;
goto _start;
}
}
else
{
lean_object* v___x_4278_; lean_object* v___x_4279_; lean_object* v___x_4280_; lean_object* v___x_4281_; 
lean_inc(v_tax_4260_);
lean_inc_ref(v_rJ_4259_);
lean_dec(v_val_4228_);
v___x_4278_ = lean_nat_add(v_fst_4200_, v___x_4235_);
lean_dec(v_fst_4200_);
v___x_4279_ = ((lean_object*)(l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__6___redArg___closed__0));
v___x_4280_ = l_String_intercalate(v___x_4279_, v___y_4257_);
v___x_4281_ = l_Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5___redArg(v_fst_4196_, v___x_4280_);
if (lean_obj_tag(v___x_4281_) == 0)
{
lean_del_object(v___x_4203_);
lean_del_object(v___x_4198_);
lean_del_object(v___x_4194_);
v___y_4239_ = v_rJ_4259_;
v___y_4240_ = v___x_4278_;
v___y_4241_ = v_tax_4260_;
v___y_4242_ = v___y_4256_;
v___y_4243_ = v___x_4280_;
goto v___jp_4238_;
}
else
{
lean_object* v_val_4282_; lean_object* v_tax_4283_; lean_object* v_gifts_4284_; uint8_t v___x_4285_; 
v_val_4282_ = lean_ctor_get(v___x_4281_, 0);
lean_inc(v_val_4282_);
lean_dec_ref_known(v___x_4281_, 1);
v_tax_4283_ = lean_ctor_get(v_val_4282_, 0);
lean_inc(v_tax_4283_);
v_gifts_4284_ = lean_ctor_get(v_val_4282_, 1);
lean_inc(v_gifts_4284_);
lean_dec(v_val_4282_);
v___x_4285_ = lean_nat_dec_lt(v_tax_4260_, v_tax_4283_);
if (v___x_4285_ == 0)
{
uint8_t v___x_4286_; 
v___x_4286_ = lean_nat_dec_eq(v_tax_4260_, v_tax_4283_);
lean_dec(v_tax_4283_);
if (v___x_4286_ == 0)
{
lean_dec(v_gifts_4284_);
lean_dec_ref(v___x_4280_);
lean_dec(v_tax_4260_);
lean_dec_ref(v_rJ_4259_);
lean_dec(v___y_4256_);
lean_dec(v___x_4237_);
lean_del_object(v___x_4233_);
v___y_4206_ = v___x_4278_;
goto v___jp_4205_;
}
else
{
uint8_t v___x_4287_; 
v___x_4287_ = lean_nat_dec_lt(v___x_4237_, v_gifts_4284_);
lean_dec(v_gifts_4284_);
if (v___x_4287_ == 0)
{
lean_dec_ref(v___x_4280_);
lean_dec(v_tax_4260_);
lean_dec_ref(v_rJ_4259_);
lean_dec(v___y_4256_);
lean_dec(v___x_4237_);
lean_del_object(v___x_4233_);
v___y_4206_ = v___x_4278_;
goto v___jp_4205_;
}
else
{
lean_del_object(v___x_4203_);
lean_del_object(v___x_4198_);
lean_del_object(v___x_4194_);
v___y_4239_ = v_rJ_4259_;
v___y_4240_ = v___x_4278_;
v___y_4241_ = v_tax_4260_;
v___y_4242_ = v___y_4256_;
v___y_4243_ = v___x_4280_;
goto v___jp_4238_;
}
}
}
else
{
lean_dec(v_gifts_4284_);
lean_dec(v_tax_4283_);
lean_del_object(v___x_4203_);
lean_del_object(v___x_4198_);
lean_del_object(v___x_4194_);
v___y_4239_ = v_rJ_4259_;
v___y_4240_ = v___x_4278_;
v___y_4241_ = v_tax_4260_;
v___y_4242_ = v___y_4256_;
v___y_4243_ = v___x_4280_;
goto v___jp_4238_;
}
}
}
}
v___jp_4289_:
{
uint8_t v___x_4291_; 
v___x_4291_ = lean_string_dec_eq(v_snd_4231_, v___x_4288_);
if (v___x_4291_ == 0)
{
lean_object* v___x_4292_; 
lean_inc(v_fst_4182_);
v___x_4292_ = l_Legal_USTax_Hunt_Basis_insertSorted(v_snd_4231_, v_fst_4182_);
v___y_4256_ = v___y_4290_;
v___y_4257_ = v___x_4292_;
goto v___jp_4255_;
}
else
{
lean_dec(v_snd_4231_);
lean_inc(v_fst_4182_);
v___y_4256_ = v___y_4290_;
v___y_4257_ = v_fst_4182_;
goto v___jp_4255_;
}
}
}
}
}
v___jp_4205_:
{
lean_object* v___x_4208_; 
if (v_isShared_4204_ == 0)
{
lean_ctor_set(v___x_4203_, 0, v___y_4206_);
v___x_4208_ = v___x_4203_;
goto v_reusejp_4207_;
}
else
{
lean_object* v_reuseFailAlloc_4216_; 
v_reuseFailAlloc_4216_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4216_, 0, v___y_4206_);
lean_ctor_set(v_reuseFailAlloc_4216_, 1, v_snd_4201_);
v___x_4208_ = v_reuseFailAlloc_4216_;
goto v_reusejp_4207_;
}
v_reusejp_4207_:
{
lean_object* v___x_4210_; 
if (v_isShared_4199_ == 0)
{
lean_ctor_set(v___x_4198_, 1, v___x_4208_);
v___x_4210_ = v___x_4198_;
goto v_reusejp_4209_;
}
else
{
lean_object* v_reuseFailAlloc_4215_; 
v_reuseFailAlloc_4215_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4215_, 0, v_fst_4196_);
lean_ctor_set(v_reuseFailAlloc_4215_, 1, v___x_4208_);
v___x_4210_ = v_reuseFailAlloc_4215_;
goto v_reusejp_4209_;
}
v_reusejp_4209_:
{
lean_object* v___x_4212_; 
if (v_isShared_4195_ == 0)
{
lean_ctor_set(v___x_4194_, 1, v___x_4210_);
v___x_4212_ = v___x_4194_;
goto v_reusejp_4211_;
}
else
{
lean_object* v_reuseFailAlloc_4214_; 
v_reuseFailAlloc_4214_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4214_, 0, v_fst_4192_);
lean_ctor_set(v_reuseFailAlloc_4214_, 1, v___x_4210_);
v___x_4212_ = v_reuseFailAlloc_4214_;
goto v_reusejp_4211_;
}
v_reusejp_4211_:
{
v_as_x27_4184_ = v_tail_4191_;
v_b_4185_ = v___x_4212_;
goto _start;
}
}
}
}
}
}
}
}
}
}
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__6___redArg___boxed(lean_object* v_allowed_4301_, lean_object* v_cfg_4302_, lean_object* v_fst_4303_, lean_object* v_snd_4304_, lean_object* v_fst_4305_, lean_object* v_fst_4306_, lean_object* v_as_x27_4307_, lean_object* v_b_4308_, lean_object* v___y_4309_){
_start:
{
lean_object* v_res_4310_; 
v_res_4310_ = l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__6___redArg(v_allowed_4301_, v_cfg_4302_, v_fst_4303_, v_snd_4304_, v_fst_4305_, v_fst_4306_, v_as_x27_4307_, v_b_4308_);
lean_dec(v_as_x27_4307_);
lean_dec(v_snd_4304_);
lean_dec_ref(v_cfg_4302_);
return v_res_4310_;
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__7(lean_object* v_allowed_4311_, lean_object* v_cfg_4312_, lean_object* v_as_4313_, size_t v_sz_4314_, size_t v_i_4315_, lean_object* v_b_4316_){
_start:
{
uint8_t v___x_4318_; 
v___x_4318_ = lean_usize_dec_lt(v_i_4315_, v_sz_4314_);
if (v___x_4318_ == 0)
{
lean_object* v___x_4319_; 
lean_dec_ref(v_allowed_4311_);
v___x_4319_ = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(v___x_4319_, 0, v_b_4316_);
return v___x_4319_;
}
else
{
lean_object* v_a_4320_; lean_object* v_snd_4321_; lean_object* v_snd_4322_; lean_object* v_snd_4323_; lean_object* v_snd_4324_; lean_object* v_fst_4325_; lean_object* v_fst_4326_; lean_object* v_fst_4327_; lean_object* v_snd_4328_; lean_object* v_fst_4329_; lean_object* v___x_4331_; uint8_t v_isShared_4332_; uint8_t v_isSharedCheck_4389_; 
v_a_4320_ = lean_array_uget_borrowed(v_as_4313_, v_i_4315_);
v_snd_4321_ = lean_ctor_get(v_a_4320_, 1);
v_snd_4322_ = lean_ctor_get(v_snd_4321_, 1);
v_snd_4323_ = lean_ctor_get(v_b_4316_, 1);
lean_inc(v_snd_4323_);
v_snd_4324_ = lean_ctor_get(v_snd_4323_, 1);
lean_inc(v_snd_4324_);
v_fst_4325_ = lean_ctor_get(v_a_4320_, 0);
v_fst_4326_ = lean_ctor_get(v_snd_4321_, 0);
v_fst_4327_ = lean_ctor_get(v_snd_4322_, 0);
v_snd_4328_ = lean_ctor_get(v_snd_4322_, 1);
v_fst_4329_ = lean_ctor_get(v_b_4316_, 0);
v_isSharedCheck_4389_ = !lean_is_exclusive(v_b_4316_);
if (v_isSharedCheck_4389_ == 0)
{
lean_object* v_unused_4390_; 
v_unused_4390_ = lean_ctor_get(v_b_4316_, 1);
lean_dec(v_unused_4390_);
v___x_4331_ = v_b_4316_;
v_isShared_4332_ = v_isSharedCheck_4389_;
goto v_resetjp_4330_;
}
else
{
lean_inc(v_fst_4329_);
lean_dec(v_b_4316_);
v___x_4331_ = lean_box(0);
v_isShared_4332_ = v_isSharedCheck_4389_;
goto v_resetjp_4330_;
}
v_resetjp_4330_:
{
lean_object* v_fst_4333_; lean_object* v___x_4335_; uint8_t v_isShared_4336_; uint8_t v_isSharedCheck_4387_; 
v_fst_4333_ = lean_ctor_get(v_snd_4323_, 0);
v_isSharedCheck_4387_ = !lean_is_exclusive(v_snd_4323_);
if (v_isSharedCheck_4387_ == 0)
{
lean_object* v_unused_4388_; 
v_unused_4388_ = lean_ctor_get(v_snd_4323_, 1);
lean_dec(v_unused_4388_);
v___x_4335_ = v_snd_4323_;
v_isShared_4336_ = v_isSharedCheck_4387_;
goto v_resetjp_4334_;
}
else
{
lean_inc(v_fst_4333_);
lean_dec(v_snd_4323_);
v___x_4335_ = lean_box(0);
v_isShared_4336_ = v_isSharedCheck_4387_;
goto v_resetjp_4334_;
}
v_resetjp_4334_:
{
lean_object* v_fst_4337_; lean_object* v_snd_4338_; lean_object* v___x_4340_; uint8_t v_isShared_4341_; uint8_t v_isSharedCheck_4386_; 
v_fst_4337_ = lean_ctor_get(v_snd_4324_, 0);
v_snd_4338_ = lean_ctor_get(v_snd_4324_, 1);
v_isSharedCheck_4386_ = !lean_is_exclusive(v_snd_4324_);
if (v_isSharedCheck_4386_ == 0)
{
v___x_4340_ = v_snd_4324_;
v_isShared_4341_ = v_isSharedCheck_4386_;
goto v_resetjp_4339_;
}
else
{
lean_inc(v_snd_4338_);
lean_inc(v_fst_4337_);
lean_dec(v_snd_4324_);
v___x_4340_ = lean_box(0);
v_isShared_4341_ = v_isSharedCheck_4386_;
goto v_resetjp_4339_;
}
v_resetjp_4339_:
{
lean_object* v___x_4342_; lean_object* v___x_4344_; 
v___x_4342_ = l_Legal_USTax_Hunt_Basis_moves(v_fst_4325_);
if (v_isShared_4341_ == 0)
{
v___x_4344_ = v___x_4340_;
goto v_reusejp_4343_;
}
else
{
lean_object* v_reuseFailAlloc_4385_; 
v_reuseFailAlloc_4385_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4385_, 0, v_fst_4337_);
lean_ctor_set(v_reuseFailAlloc_4385_, 1, v_snd_4338_);
v___x_4344_ = v_reuseFailAlloc_4385_;
goto v_reusejp_4343_;
}
v_reusejp_4343_:
{
lean_object* v___x_4346_; 
if (v_isShared_4336_ == 0)
{
lean_ctor_set(v___x_4335_, 1, v___x_4344_);
v___x_4346_ = v___x_4335_;
goto v_reusejp_4345_;
}
else
{
lean_object* v_reuseFailAlloc_4384_; 
v_reuseFailAlloc_4384_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4384_, 0, v_fst_4333_);
lean_ctor_set(v_reuseFailAlloc_4384_, 1, v___x_4344_);
v___x_4346_ = v_reuseFailAlloc_4384_;
goto v_reusejp_4345_;
}
v_reusejp_4345_:
{
lean_object* v___x_4348_; 
if (v_isShared_4332_ == 0)
{
lean_ctor_set(v___x_4331_, 1, v___x_4346_);
v___x_4348_ = v___x_4331_;
goto v_reusejp_4347_;
}
else
{
lean_object* v_reuseFailAlloc_4383_; 
v_reuseFailAlloc_4383_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4383_, 0, v_fst_4329_);
lean_ctor_set(v_reuseFailAlloc_4383_, 1, v___x_4346_);
v___x_4348_ = v_reuseFailAlloc_4383_;
goto v_reusejp_4347_;
}
v_reusejp_4347_:
{
lean_object* v___x_4349_; 
lean_inc(v_fst_4326_);
lean_inc(v_fst_4327_);
lean_inc(v_fst_4325_);
lean_inc_ref(v_allowed_4311_);
v___x_4349_ = l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__6___redArg(v_allowed_4311_, v_cfg_4312_, v_fst_4325_, v_snd_4328_, v_fst_4327_, v_fst_4326_, v___x_4342_, v___x_4348_);
lean_dec(v___x_4342_);
if (lean_obj_tag(v___x_4349_) == 0)
{
lean_object* v_a_4350_; lean_object* v_snd_4351_; lean_object* v_snd_4352_; lean_object* v_fst_4353_; lean_object* v___x_4355_; uint8_t v_isShared_4356_; uint8_t v_isSharedCheck_4381_; 
v_a_4350_ = lean_ctor_get(v___x_4349_, 0);
lean_inc(v_a_4350_);
lean_dec_ref_known(v___x_4349_, 1);
v_snd_4351_ = lean_ctor_get(v_a_4350_, 1);
lean_inc(v_snd_4351_);
v_snd_4352_ = lean_ctor_get(v_snd_4351_, 1);
lean_inc(v_snd_4352_);
v_fst_4353_ = lean_ctor_get(v_a_4350_, 0);
v_isSharedCheck_4381_ = !lean_is_exclusive(v_a_4350_);
if (v_isSharedCheck_4381_ == 0)
{
lean_object* v_unused_4382_; 
v_unused_4382_ = lean_ctor_get(v_a_4350_, 1);
lean_dec(v_unused_4382_);
v___x_4355_ = v_a_4350_;
v_isShared_4356_ = v_isSharedCheck_4381_;
goto v_resetjp_4354_;
}
else
{
lean_inc(v_fst_4353_);
lean_dec(v_a_4350_);
v___x_4355_ = lean_box(0);
v_isShared_4356_ = v_isSharedCheck_4381_;
goto v_resetjp_4354_;
}
v_resetjp_4354_:
{
lean_object* v_fst_4357_; lean_object* v___x_4359_; uint8_t v_isShared_4360_; uint8_t v_isSharedCheck_4379_; 
v_fst_4357_ = lean_ctor_get(v_snd_4351_, 0);
v_isSharedCheck_4379_ = !lean_is_exclusive(v_snd_4351_);
if (v_isSharedCheck_4379_ == 0)
{
lean_object* v_unused_4380_; 
v_unused_4380_ = lean_ctor_get(v_snd_4351_, 1);
lean_dec(v_unused_4380_);
v___x_4359_ = v_snd_4351_;
v_isShared_4360_ = v_isSharedCheck_4379_;
goto v_resetjp_4358_;
}
else
{
lean_inc(v_fst_4357_);
lean_dec(v_snd_4351_);
v___x_4359_ = lean_box(0);
v_isShared_4360_ = v_isSharedCheck_4379_;
goto v_resetjp_4358_;
}
v_resetjp_4358_:
{
lean_object* v_fst_4361_; lean_object* v_snd_4362_; lean_object* v___x_4364_; uint8_t v_isShared_4365_; uint8_t v_isSharedCheck_4378_; 
v_fst_4361_ = lean_ctor_get(v_snd_4352_, 0);
v_snd_4362_ = lean_ctor_get(v_snd_4352_, 1);
v_isSharedCheck_4378_ = !lean_is_exclusive(v_snd_4352_);
if (v_isSharedCheck_4378_ == 0)
{
v___x_4364_ = v_snd_4352_;
v_isShared_4365_ = v_isSharedCheck_4378_;
goto v_resetjp_4363_;
}
else
{
lean_inc(v_snd_4362_);
lean_inc(v_fst_4361_);
lean_dec(v_snd_4352_);
v___x_4364_ = lean_box(0);
v_isShared_4365_ = v_isSharedCheck_4378_;
goto v_resetjp_4363_;
}
v_resetjp_4363_:
{
lean_object* v___x_4367_; 
if (v_isShared_4365_ == 0)
{
v___x_4367_ = v___x_4364_;
goto v_reusejp_4366_;
}
else
{
lean_object* v_reuseFailAlloc_4377_; 
v_reuseFailAlloc_4377_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4377_, 0, v_fst_4361_);
lean_ctor_set(v_reuseFailAlloc_4377_, 1, v_snd_4362_);
v___x_4367_ = v_reuseFailAlloc_4377_;
goto v_reusejp_4366_;
}
v_reusejp_4366_:
{
lean_object* v___x_4369_; 
if (v_isShared_4360_ == 0)
{
lean_ctor_set(v___x_4359_, 1, v___x_4367_);
v___x_4369_ = v___x_4359_;
goto v_reusejp_4368_;
}
else
{
lean_object* v_reuseFailAlloc_4376_; 
v_reuseFailAlloc_4376_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4376_, 0, v_fst_4357_);
lean_ctor_set(v_reuseFailAlloc_4376_, 1, v___x_4367_);
v___x_4369_ = v_reuseFailAlloc_4376_;
goto v_reusejp_4368_;
}
v_reusejp_4368_:
{
lean_object* v___x_4371_; 
if (v_isShared_4356_ == 0)
{
lean_ctor_set(v___x_4355_, 1, v___x_4369_);
v___x_4371_ = v___x_4355_;
goto v_reusejp_4370_;
}
else
{
lean_object* v_reuseFailAlloc_4375_; 
v_reuseFailAlloc_4375_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4375_, 0, v_fst_4353_);
lean_ctor_set(v_reuseFailAlloc_4375_, 1, v___x_4369_);
v___x_4371_ = v_reuseFailAlloc_4375_;
goto v_reusejp_4370_;
}
v_reusejp_4370_:
{
size_t v___x_4372_; size_t v___x_4373_; 
v___x_4372_ = ((size_t)1ULL);
v___x_4373_ = lean_usize_add(v_i_4315_, v___x_4372_);
v_i_4315_ = v___x_4373_;
v_b_4316_ = v___x_4371_;
goto _start;
}
}
}
}
}
}
}
else
{
lean_dec_ref(v_allowed_4311_);
return v___x_4349_;
}
}
}
}
}
}
}
}
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__7___boxed(lean_object* v_allowed_4391_, lean_object* v_cfg_4392_, lean_object* v_as_4393_, lean_object* v_sz_4394_, lean_object* v_i_4395_, lean_object* v_b_4396_, lean_object* v___y_4397_){
_start:
{
size_t v_sz_boxed_4398_; size_t v_i_boxed_4399_; lean_object* v_res_4400_; 
v_sz_boxed_4398_ = lean_unbox_usize(v_sz_4394_);
lean_dec(v_sz_4394_);
v_i_boxed_4399_ = lean_unbox_usize(v_i_4395_);
lean_dec(v_i_4395_);
v_res_4400_ = l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__7(v_allowed_4391_, v_cfg_4392_, v_as_4393_, v_sz_boxed_4398_, v_i_boxed_4399_, v_b_4396_);
lean_dec_ref(v_as_4393_);
lean_dec_ref(v_cfg_4392_);
return v_res_4400_;
}
}
LEAN_EXPORT lean_object* l___private_Init_While_0__repeatM_erased___at___00Legal_USTax_Hunt_Basis_search_spec__8___redArg(lean_object* v_allowed_4403_, lean_object* v_cfg_4404_, lean_object* v_a_4405_){
_start:
{
lean_object* v_snd_4407_; lean_object* v_snd_4408_; lean_object* v_snd_4409_; lean_object* v_fst_4410_; lean_object* v___x_4412_; uint8_t v_isShared_4413_; uint8_t v_isSharedCheck_4505_; 
v_snd_4407_ = lean_ctor_get(v_a_4405_, 1);
lean_inc(v_snd_4407_);
v_snd_4408_ = lean_ctor_get(v_snd_4407_, 1);
lean_inc(v_snd_4408_);
v_snd_4409_ = lean_ctor_get(v_snd_4408_, 1);
lean_inc(v_snd_4409_);
v_fst_4410_ = lean_ctor_get(v_a_4405_, 0);
v_isSharedCheck_4505_ = !lean_is_exclusive(v_a_4405_);
if (v_isSharedCheck_4505_ == 0)
{
lean_object* v_unused_4506_; 
v_unused_4506_ = lean_ctor_get(v_a_4405_, 1);
lean_dec(v_unused_4506_);
v___x_4412_ = v_a_4405_;
v_isShared_4413_ = v_isSharedCheck_4505_;
goto v_resetjp_4411_;
}
else
{
lean_inc(v_fst_4410_);
lean_dec(v_a_4405_);
v___x_4412_ = lean_box(0);
v_isShared_4413_ = v_isSharedCheck_4505_;
goto v_resetjp_4411_;
}
v_resetjp_4411_:
{
lean_object* v_fst_4414_; lean_object* v___x_4416_; uint8_t v_isShared_4417_; uint8_t v_isSharedCheck_4503_; 
v_fst_4414_ = lean_ctor_get(v_snd_4407_, 0);
v_isSharedCheck_4503_ = !lean_is_exclusive(v_snd_4407_);
if (v_isSharedCheck_4503_ == 0)
{
lean_object* v_unused_4504_; 
v_unused_4504_ = lean_ctor_get(v_snd_4407_, 1);
lean_dec(v_unused_4504_);
v___x_4416_ = v_snd_4407_;
v_isShared_4417_ = v_isSharedCheck_4503_;
goto v_resetjp_4415_;
}
else
{
lean_inc(v_fst_4414_);
lean_dec(v_snd_4407_);
v___x_4416_ = lean_box(0);
v_isShared_4417_ = v_isSharedCheck_4503_;
goto v_resetjp_4415_;
}
v_resetjp_4415_:
{
lean_object* v_fst_4418_; lean_object* v___x_4420_; uint8_t v_isShared_4421_; uint8_t v_isSharedCheck_4501_; 
v_fst_4418_ = lean_ctor_get(v_snd_4408_, 0);
v_isSharedCheck_4501_ = !lean_is_exclusive(v_snd_4408_);
if (v_isSharedCheck_4501_ == 0)
{
lean_object* v_unused_4502_; 
v_unused_4502_ = lean_ctor_get(v_snd_4408_, 1);
lean_dec(v_unused_4502_);
v___x_4420_ = v_snd_4408_;
v_isShared_4421_ = v_isSharedCheck_4501_;
goto v_resetjp_4419_;
}
else
{
lean_inc(v_fst_4418_);
lean_dec(v_snd_4408_);
v___x_4420_ = lean_box(0);
v_isShared_4421_ = v_isSharedCheck_4501_;
goto v_resetjp_4419_;
}
v_resetjp_4419_:
{
lean_object* v_fst_4422_; lean_object* v_snd_4423_; lean_object* v___x_4425_; uint8_t v_isShared_4426_; uint8_t v_isSharedCheck_4500_; 
v_fst_4422_ = lean_ctor_get(v_snd_4409_, 0);
v_snd_4423_ = lean_ctor_get(v_snd_4409_, 1);
v_isSharedCheck_4500_ = !lean_is_exclusive(v_snd_4409_);
if (v_isSharedCheck_4500_ == 0)
{
v___x_4425_ = v_snd_4409_;
v_isShared_4426_ = v_isSharedCheck_4500_;
goto v_resetjp_4424_;
}
else
{
lean_inc(v_snd_4423_);
lean_inc(v_fst_4422_);
lean_dec(v_snd_4409_);
v___x_4425_ = lean_box(0);
v_isShared_4426_ = v_isSharedCheck_4500_;
goto v_resetjp_4424_;
}
v_resetjp_4424_:
{
lean_object* v___x_4427_; lean_object* v___x_4428_; uint8_t v___x_4429_; 
v___x_4427_ = lean_unsigned_to_nat(0u);
v___x_4428_ = lean_array_get_size(v_fst_4410_);
v___x_4429_ = lean_nat_dec_lt(v___x_4427_, v___x_4428_);
if (v___x_4429_ == 0)
{
lean_object* v___x_4431_; 
lean_dec_ref(v_allowed_4403_);
if (v_isShared_4426_ == 0)
{
v___x_4431_ = v___x_4425_;
goto v_reusejp_4430_;
}
else
{
lean_object* v_reuseFailAlloc_4442_; 
v_reuseFailAlloc_4442_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4442_, 0, v_fst_4422_);
lean_ctor_set(v_reuseFailAlloc_4442_, 1, v_snd_4423_);
v___x_4431_ = v_reuseFailAlloc_4442_;
goto v_reusejp_4430_;
}
v_reusejp_4430_:
{
lean_object* v___x_4433_; 
if (v_isShared_4421_ == 0)
{
lean_ctor_set(v___x_4420_, 1, v___x_4431_);
v___x_4433_ = v___x_4420_;
goto v_reusejp_4432_;
}
else
{
lean_object* v_reuseFailAlloc_4441_; 
v_reuseFailAlloc_4441_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4441_, 0, v_fst_4418_);
lean_ctor_set(v_reuseFailAlloc_4441_, 1, v___x_4431_);
v___x_4433_ = v_reuseFailAlloc_4441_;
goto v_reusejp_4432_;
}
v_reusejp_4432_:
{
lean_object* v___x_4435_; 
if (v_isShared_4417_ == 0)
{
lean_ctor_set(v___x_4416_, 1, v___x_4433_);
v___x_4435_ = v___x_4416_;
goto v_reusejp_4434_;
}
else
{
lean_object* v_reuseFailAlloc_4440_; 
v_reuseFailAlloc_4440_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4440_, 0, v_fst_4414_);
lean_ctor_set(v_reuseFailAlloc_4440_, 1, v___x_4433_);
v___x_4435_ = v_reuseFailAlloc_4440_;
goto v_reusejp_4434_;
}
v_reusejp_4434_:
{
lean_object* v___x_4437_; 
if (v_isShared_4413_ == 0)
{
lean_ctor_set(v___x_4412_, 1, v___x_4435_);
v___x_4437_ = v___x_4412_;
goto v_reusejp_4436_;
}
else
{
lean_object* v_reuseFailAlloc_4439_; 
v_reuseFailAlloc_4439_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4439_, 0, v_fst_4410_);
lean_ctor_set(v_reuseFailAlloc_4439_, 1, v___x_4435_);
v___x_4437_ = v_reuseFailAlloc_4439_;
goto v_reusejp_4436_;
}
v_reusejp_4436_:
{
lean_object* v___x_4438_; 
v___x_4438_ = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(v___x_4438_, 0, v___x_4437_);
return v___x_4438_;
}
}
}
}
}
else
{
lean_object* v___x_4443_; lean_object* v___x_4444_; lean_object* v___x_4445_; lean_object* v___x_4447_; 
v___x_4443_ = lean_unsigned_to_nat(1u);
v___x_4444_ = lean_nat_add(v_snd_4423_, v___x_4443_);
lean_dec(v_snd_4423_);
v___x_4445_ = ((lean_object*)(l___private_Init_While_0__repeatM_erased___at___00Legal_USTax_Hunt_Basis_search_spec__8___redArg___closed__0));
if (v_isShared_4426_ == 0)
{
lean_ctor_set(v___x_4425_, 1, v___x_4445_);
v___x_4447_ = v___x_4425_;
goto v_reusejp_4446_;
}
else
{
lean_object* v_reuseFailAlloc_4499_; 
v_reuseFailAlloc_4499_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4499_, 0, v_fst_4422_);
lean_ctor_set(v_reuseFailAlloc_4499_, 1, v___x_4445_);
v___x_4447_ = v_reuseFailAlloc_4499_;
goto v_reusejp_4446_;
}
v_reusejp_4446_:
{
lean_object* v___x_4449_; 
if (v_isShared_4421_ == 0)
{
lean_ctor_set(v___x_4420_, 1, v___x_4447_);
v___x_4449_ = v___x_4420_;
goto v_reusejp_4448_;
}
else
{
lean_object* v_reuseFailAlloc_4498_; 
v_reuseFailAlloc_4498_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4498_, 0, v_fst_4418_);
lean_ctor_set(v_reuseFailAlloc_4498_, 1, v___x_4447_);
v___x_4449_ = v_reuseFailAlloc_4498_;
goto v_reusejp_4448_;
}
v_reusejp_4448_:
{
lean_object* v___x_4451_; 
if (v_isShared_4417_ == 0)
{
lean_ctor_set(v___x_4416_, 1, v___x_4449_);
v___x_4451_ = v___x_4416_;
goto v_reusejp_4450_;
}
else
{
lean_object* v_reuseFailAlloc_4497_; 
v_reuseFailAlloc_4497_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4497_, 0, v_fst_4414_);
lean_ctor_set(v_reuseFailAlloc_4497_, 1, v___x_4449_);
v___x_4451_ = v_reuseFailAlloc_4497_;
goto v_reusejp_4450_;
}
v_reusejp_4450_:
{
size_t v_sz_4452_; size_t v___x_4453_; lean_object* v___x_4454_; 
v_sz_4452_ = lean_array_size(v_fst_4410_);
v___x_4453_ = ((size_t)0ULL);
lean_inc_ref(v_allowed_4403_);
v___x_4454_ = l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__7(v_allowed_4403_, v_cfg_4404_, v_fst_4410_, v_sz_4452_, v___x_4453_, v___x_4451_);
lean_dec(v_fst_4410_);
if (lean_obj_tag(v___x_4454_) == 0)
{
lean_object* v_a_4455_; lean_object* v_snd_4456_; lean_object* v_snd_4457_; lean_object* v_fst_4458_; lean_object* v___x_4460_; uint8_t v_isShared_4461_; uint8_t v_isSharedCheck_4487_; 
v_a_4455_ = lean_ctor_get(v___x_4454_, 0);
lean_inc(v_a_4455_);
lean_dec_ref_known(v___x_4454_, 1);
v_snd_4456_ = lean_ctor_get(v_a_4455_, 1);
lean_inc(v_snd_4456_);
v_snd_4457_ = lean_ctor_get(v_snd_4456_, 1);
lean_inc(v_snd_4457_);
v_fst_4458_ = lean_ctor_get(v_a_4455_, 0);
v_isSharedCheck_4487_ = !lean_is_exclusive(v_a_4455_);
if (v_isSharedCheck_4487_ == 0)
{
lean_object* v_unused_4488_; 
v_unused_4488_ = lean_ctor_get(v_a_4455_, 1);
lean_dec(v_unused_4488_);
v___x_4460_ = v_a_4455_;
v_isShared_4461_ = v_isSharedCheck_4487_;
goto v_resetjp_4459_;
}
else
{
lean_inc(v_fst_4458_);
lean_dec(v_a_4455_);
v___x_4460_ = lean_box(0);
v_isShared_4461_ = v_isSharedCheck_4487_;
goto v_resetjp_4459_;
}
v_resetjp_4459_:
{
lean_object* v_fst_4462_; lean_object* v___x_4464_; uint8_t v_isShared_4465_; uint8_t v_isSharedCheck_4485_; 
v_fst_4462_ = lean_ctor_get(v_snd_4456_, 0);
v_isSharedCheck_4485_ = !lean_is_exclusive(v_snd_4456_);
if (v_isSharedCheck_4485_ == 0)
{
lean_object* v_unused_4486_; 
v_unused_4486_ = lean_ctor_get(v_snd_4456_, 1);
lean_dec(v_unused_4486_);
v___x_4464_ = v_snd_4456_;
v_isShared_4465_ = v_isSharedCheck_4485_;
goto v_resetjp_4463_;
}
else
{
lean_inc(v_fst_4462_);
lean_dec(v_snd_4456_);
v___x_4464_ = lean_box(0);
v_isShared_4465_ = v_isSharedCheck_4485_;
goto v_resetjp_4463_;
}
v_resetjp_4463_:
{
lean_object* v_fst_4466_; lean_object* v_snd_4467_; lean_object* v___x_4469_; uint8_t v_isShared_4470_; uint8_t v_isSharedCheck_4484_; 
v_fst_4466_ = lean_ctor_get(v_snd_4457_, 0);
v_snd_4467_ = lean_ctor_get(v_snd_4457_, 1);
v_isSharedCheck_4484_ = !lean_is_exclusive(v_snd_4457_);
if (v_isSharedCheck_4484_ == 0)
{
v___x_4469_ = v_snd_4457_;
v_isShared_4470_ = v_isSharedCheck_4484_;
goto v_resetjp_4468_;
}
else
{
lean_inc(v_snd_4467_);
lean_inc(v_fst_4466_);
lean_dec(v_snd_4457_);
v___x_4469_ = lean_box(0);
v_isShared_4470_ = v_isSharedCheck_4484_;
goto v_resetjp_4468_;
}
v_resetjp_4468_:
{
lean_object* v___x_4472_; 
if (v_isShared_4470_ == 0)
{
lean_ctor_set(v___x_4469_, 1, v___x_4444_);
v___x_4472_ = v___x_4469_;
goto v_reusejp_4471_;
}
else
{
lean_object* v_reuseFailAlloc_4483_; 
v_reuseFailAlloc_4483_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4483_, 0, v_fst_4466_);
lean_ctor_set(v_reuseFailAlloc_4483_, 1, v___x_4444_);
v___x_4472_ = v_reuseFailAlloc_4483_;
goto v_reusejp_4471_;
}
v_reusejp_4471_:
{
lean_object* v___x_4474_; 
if (v_isShared_4465_ == 0)
{
lean_ctor_set(v___x_4464_, 1, v___x_4472_);
v___x_4474_ = v___x_4464_;
goto v_reusejp_4473_;
}
else
{
lean_object* v_reuseFailAlloc_4482_; 
v_reuseFailAlloc_4482_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4482_, 0, v_fst_4462_);
lean_ctor_set(v_reuseFailAlloc_4482_, 1, v___x_4472_);
v___x_4474_ = v_reuseFailAlloc_4482_;
goto v_reusejp_4473_;
}
v_reusejp_4473_:
{
lean_object* v___x_4476_; 
if (v_isShared_4461_ == 0)
{
lean_ctor_set(v___x_4460_, 1, v___x_4474_);
v___x_4476_ = v___x_4460_;
goto v_reusejp_4475_;
}
else
{
lean_object* v_reuseFailAlloc_4481_; 
v_reuseFailAlloc_4481_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4481_, 0, v_fst_4458_);
lean_ctor_set(v_reuseFailAlloc_4481_, 1, v___x_4474_);
v___x_4476_ = v_reuseFailAlloc_4481_;
goto v_reusejp_4475_;
}
v_reusejp_4475_:
{
lean_object* v___x_4478_; 
if (v_isShared_4413_ == 0)
{
lean_ctor_set(v___x_4412_, 1, v___x_4476_);
lean_ctor_set(v___x_4412_, 0, v_snd_4467_);
v___x_4478_ = v___x_4412_;
goto v_reusejp_4477_;
}
else
{
lean_object* v_reuseFailAlloc_4480_; 
v_reuseFailAlloc_4480_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4480_, 0, v_snd_4467_);
lean_ctor_set(v_reuseFailAlloc_4480_, 1, v___x_4476_);
v___x_4478_ = v_reuseFailAlloc_4480_;
goto v_reusejp_4477_;
}
v_reusejp_4477_:
{
v_a_4405_ = v___x_4478_;
goto _start;
}
}
}
}
}
}
}
}
else
{
lean_object* v_a_4489_; lean_object* v___x_4491_; uint8_t v_isShared_4492_; uint8_t v_isSharedCheck_4496_; 
lean_dec(v___x_4444_);
lean_del_object(v___x_4412_);
lean_dec_ref(v_allowed_4403_);
v_a_4489_ = lean_ctor_get(v___x_4454_, 0);
v_isSharedCheck_4496_ = !lean_is_exclusive(v___x_4454_);
if (v_isSharedCheck_4496_ == 0)
{
v___x_4491_ = v___x_4454_;
v_isShared_4492_ = v_isSharedCheck_4496_;
goto v_resetjp_4490_;
}
else
{
lean_inc(v_a_4489_);
lean_dec(v___x_4454_);
v___x_4491_ = lean_box(0);
v_isShared_4492_ = v_isSharedCheck_4496_;
goto v_resetjp_4490_;
}
v_resetjp_4490_:
{
lean_object* v___x_4494_; 
if (v_isShared_4492_ == 0)
{
v___x_4494_ = v___x_4491_;
goto v_reusejp_4493_;
}
else
{
lean_object* v_reuseFailAlloc_4495_; 
v_reuseFailAlloc_4495_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v_reuseFailAlloc_4495_, 0, v_a_4489_);
v___x_4494_ = v_reuseFailAlloc_4495_;
goto v_reusejp_4493_;
}
v_reusejp_4493_:
{
return v___x_4494_;
}
}
}
}
}
}
}
}
}
}
}
}
}
LEAN_EXPORT lean_object* l___private_Init_While_0__repeatM_erased___at___00Legal_USTax_Hunt_Basis_search_spec__8___redArg___boxed(lean_object* v_allowed_4507_, lean_object* v_cfg_4508_, lean_object* v_a_4509_, lean_object* v___y_4510_){
_start:
{
lean_object* v_res_4511_; 
v_res_4511_ = l___private_Init_While_0__repeatM_erased___at___00Legal_USTax_Hunt_Basis_search_spec__8___redArg(v_allowed_4507_, v_cfg_4508_, v_a_4509_);
lean_dec_ref(v_cfg_4508_);
return v_res_4511_;
}
}
LEAN_EXPORT lean_object* l_IO_print___at___00IO_println___at___00Legal_USTax_Hunt_Basis_search_spec__0_spec__0(lean_object* v_s_4512_){
_start:
{
lean_object* v___x_4514_; lean_object* v_putStr_4515_; lean_object* v___x_4516_; 
v___x_4514_ = lean_get_stdout();
v_putStr_4515_ = lean_ctor_get(v___x_4514_, 4);
lean_inc_ref(v_putStr_4515_);
lean_dec_ref(v___x_4514_);
v___x_4516_ = lean_apply_2(v_putStr_4515_, v_s_4512_, lean_box(0));
return v___x_4516_;
}
}
LEAN_EXPORT lean_object* l_IO_print___at___00IO_println___at___00Legal_USTax_Hunt_Basis_search_spec__0_spec__0___boxed(lean_object* v_s_4517_, lean_object* v_a_4518_){
_start:
{
lean_object* v_res_4519_; 
v_res_4519_ = l_IO_print___at___00IO_println___at___00Legal_USTax_Hunt_Basis_search_spec__0_spec__0(v_s_4517_);
return v_res_4519_;
}
}
LEAN_EXPORT lean_object* l_IO_println___at___00Legal_USTax_Hunt_Basis_search_spec__0(lean_object* v_s_4520_){
_start:
{
uint32_t v___x_4522_; lean_object* v___x_4523_; lean_object* v___x_4524_; 
v___x_4522_ = 10;
v___x_4523_ = lean_string_push(v_s_4520_, v___x_4522_);
v___x_4524_ = l_IO_print___at___00IO_println___at___00Legal_USTax_Hunt_Basis_search_spec__0_spec__0(v___x_4523_);
return v___x_4524_;
}
}
LEAN_EXPORT lean_object* l_IO_println___at___00Legal_USTax_Hunt_Basis_search_spec__0___boxed(lean_object* v_s_4525_, lean_object* v_a_4526_){
_start:
{
lean_object* v_res_4527_; 
v_res_4527_ = l_IO_println___at___00Legal_USTax_Hunt_Basis_search_spec__0(v_s_4525_);
return v_res_4527_;
}
}
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg(lean_object* v_as_x27_4533_, lean_object* v_b_4534_){
_start:
{
if (lean_obj_tag(v_as_x27_4533_) == 0)
{
lean_object* v___x_4536_; 
v___x_4536_ = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(v___x_4536_, 0, v_b_4534_);
return v___x_4536_;
}
else
{
lean_object* v_head_4537_; lean_object* v_fst_4538_; lean_object* v_tail_4539_; lean_object* v_snd_4540_; uint8_t v_kind_4541_; uint8_t v_owner_4542_; lean_object* v_fmv_4543_; lean_object* v_basis_4544_; lean_object* v_held_4545_; lean_object* v___x_4546_; lean_object* v___x_4547_; lean_object* v___x_4548_; lean_object* v___x_4549_; lean_object* v___x_4550_; lean_object* v___x_4551_; lean_object* v___x_4552_; lean_object* v___x_4553_; lean_object* v___x_4554_; lean_object* v___x_4555_; lean_object* v___x_4556_; lean_object* v___x_4557_; lean_object* v___x_4558_; lean_object* v___x_4559_; lean_object* v___x_4560_; lean_object* v___x_4561_; lean_object* v___x_4562_; lean_object* v___x_4563_; lean_object* v___x_4564_; lean_object* v___x_4565_; lean_object* v___x_4566_; lean_object* v___x_4567_; lean_object* v___x_4568_; lean_object* v___x_4569_; lean_object* v___x_4570_; lean_object* v___x_4571_; lean_object* v___x_4572_; 
v_head_4537_ = lean_ctor_get(v_as_x27_4533_, 0);
v_fst_4538_ = lean_ctor_get(v_head_4537_, 0);
v_tail_4539_ = lean_ctor_get(v_as_x27_4533_, 1);
v_snd_4540_ = lean_ctor_get(v_head_4537_, 1);
v_kind_4541_ = lean_ctor_get_uint8(v_fst_4538_, sizeof(void*)*8);
v_owner_4542_ = lean_ctor_get_uint8(v_fst_4538_, sizeof(void*)*8 + 1);
v_fmv_4543_ = lean_ctor_get(v_fst_4538_, 0);
v_basis_4544_ = lean_ctor_get(v_fst_4538_, 1);
v_held_4545_ = lean_ctor_get(v_fst_4538_, 3);
v___x_4546_ = lean_box(0);
v___x_4547_ = ((lean_object*)(l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__0));
lean_inc(v_snd_4540_);
v___x_4548_ = l_Nat_reprFast(v_snd_4540_);
v___x_4549_ = lean_string_append(v___x_4547_, v___x_4548_);
lean_dec_ref(v___x_4548_);
v___x_4550_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__1));
v___x_4551_ = lean_string_append(v___x_4549_, v___x_4550_);
v___x_4552_ = l_Legal_USTax_Hunt_Basis_kindName(v_kind_4541_);
v___x_4553_ = lean_string_append(v___x_4551_, v___x_4552_);
lean_dec_ref(v___x_4552_);
v___x_4554_ = ((lean_object*)(l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__1));
v___x_4555_ = lean_string_append(v___x_4553_, v___x_4554_);
v___x_4556_ = l_Legal_USTax_Hunt_Basis_Who_name(v_owner_4542_);
v___x_4557_ = lean_string_append(v___x_4555_, v___x_4556_);
lean_dec_ref(v___x_4556_);
v___x_4558_ = ((lean_object*)(l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__2));
v___x_4559_ = lean_string_append(v___x_4557_, v___x_4558_);
lean_inc(v_fmv_4543_);
v___x_4560_ = l_Nat_reprFast(v_fmv_4543_);
v___x_4561_ = lean_string_append(v___x_4559_, v___x_4560_);
lean_dec_ref(v___x_4560_);
v___x_4562_ = ((lean_object*)(l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__3));
v___x_4563_ = lean_string_append(v___x_4561_, v___x_4562_);
lean_inc(v_basis_4544_);
v___x_4564_ = l_Nat_reprFast(v_basis_4544_);
v___x_4565_ = lean_string_append(v___x_4563_, v___x_4564_);
lean_dec_ref(v___x_4564_);
v___x_4566_ = ((lean_object*)(l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___closed__4));
v___x_4567_ = lean_string_append(v___x_4565_, v___x_4566_);
lean_inc(v_held_4545_);
v___x_4568_ = l_Nat_reprFast(v_held_4545_);
v___x_4569_ = lean_string_append(v___x_4567_, v___x_4568_);
lean_dec_ref(v___x_4568_);
v___x_4570_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_describe___closed__0));
v___x_4571_ = lean_string_append(v___x_4569_, v___x_4570_);
v___x_4572_ = l_IO_println___at___00Legal_USTax_Hunt_Basis_search_spec__0(v___x_4571_);
if (lean_obj_tag(v___x_4572_) == 0)
{
lean_dec_ref_known(v___x_4572_, 1);
v_as_x27_4533_ = v_tail_4539_;
v_b_4534_ = v___x_4546_;
goto _start;
}
else
{
return v___x_4572_;
}
}
}
}
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg___boxed(lean_object* v_as_x27_4574_, lean_object* v_b_4575_, lean_object* v___y_4576_){
_start:
{
lean_object* v_res_4577_; 
v_res_4577_ = l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg(v_as_x27_4574_, v_b_4575_);
lean_dec(v_as_x27_4574_);
return v_res_4577_;
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_foldlMUnsafe_fold___at___00Legal_USTax_Hunt_Basis_search_spec__9(lean_object* v___x_4578_, lean_object* v_as_4579_, size_t v_i_4580_, size_t v_stop_4581_, lean_object* v_b_4582_){
_start:
{
lean_object* v___y_4584_; uint8_t v___x_4588_; 
v___x_4588_ = lean_usize_dec_eq(v_i_4580_, v_stop_4581_);
if (v___x_4588_ == 0)
{
lean_object* v___x_4589_; lean_object* v_snd_4590_; lean_object* v_tax_4591_; uint8_t v___x_4592_; 
v___x_4589_ = lean_array_uget_borrowed(v_as_4579_, v_i_4580_);
v_snd_4590_ = lean_ctor_get(v___x_4589_, 1);
v_tax_4591_ = lean_ctor_get(v_snd_4590_, 0);
v___x_4592_ = lean_nat_dec_eq(v_tax_4591_, v___x_4578_);
if (v___x_4592_ == 0)
{
v___y_4584_ = v_b_4582_;
goto v___jp_4583_;
}
else
{
lean_object* v___x_4593_; 
lean_inc(v___x_4589_);
v___x_4593_ = lean_array_push(v_b_4582_, v___x_4589_);
v___y_4584_ = v___x_4593_;
goto v___jp_4583_;
}
}
else
{
return v_b_4582_;
}
v___jp_4583_:
{
size_t v___x_4585_; size_t v___x_4586_; 
v___x_4585_ = ((size_t)1ULL);
v___x_4586_ = lean_usize_add(v_i_4580_, v___x_4585_);
v_i_4580_ = v___x_4586_;
v_b_4582_ = v___y_4584_;
goto _start;
}
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_foldlMUnsafe_fold___at___00Legal_USTax_Hunt_Basis_search_spec__9___boxed(lean_object* v___x_4594_, lean_object* v_as_4595_, lean_object* v_i_4596_, lean_object* v_stop_4597_, lean_object* v_b_4598_){
_start:
{
size_t v_i_boxed_4599_; size_t v_stop_boxed_4600_; lean_object* v_res_4601_; 
v_i_boxed_4599_ = lean_unbox_usize(v_i_4596_);
lean_dec(v_i_4596_);
v_stop_boxed_4600_ = lean_unbox_usize(v_stop_4597_);
lean_dec(v_stop_4597_);
v_res_4601_ = l___private_Init_Data_Array_Basic_0__Array_foldlMUnsafe_fold___at___00Legal_USTax_Hunt_Basis_search_spec__9(v___x_4594_, v_as_4595_, v_i_boxed_4599_, v_stop_boxed_4600_, v_b_4598_);
lean_dec_ref(v_as_4595_);
lean_dec(v___x_4594_);
return v_res_4601_;
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17(lean_object* v_top_4611_, lean_object* v___y_4612_, lean_object* v___y_4613_, lean_object* v_as_4614_, size_t v_sz_4615_, size_t v_i_4616_, lean_object* v_b_4617_){
_start:
{
lean_object* v_a_4620_; uint8_t v___x_4624_; 
v___x_4624_ = lean_usize_dec_lt(v_i_4616_, v_sz_4615_);
if (v___x_4624_ == 0)
{
lean_object* v___x_4625_; 
v___x_4625_ = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(v___x_4625_, 0, v_b_4617_);
return v___x_4625_;
}
else
{
lean_object* v_a_4626_; lean_object* v_fst_4627_; lean_object* v_snd_4628_; lean_object* v___x_4630_; uint8_t v_isShared_4631_; uint8_t v_isSharedCheck_4715_; 
v_a_4626_ = lean_array_uget(v_as_4614_, v_i_4616_);
v_fst_4627_ = lean_ctor_get(v_a_4626_, 0);
v_snd_4628_ = lean_ctor_get(v_a_4626_, 1);
v_isSharedCheck_4715_ = !lean_is_exclusive(v_a_4626_);
if (v_isSharedCheck_4715_ == 0)
{
v___x_4630_ = v_a_4626_;
v_isShared_4631_ = v_isSharedCheck_4715_;
goto v_resetjp_4629_;
}
else
{
lean_inc(v_snd_4628_);
lean_inc(v_fst_4627_);
lean_dec(v_a_4626_);
v___x_4630_ = lean_box(0);
v_isShared_4631_ = v_isSharedCheck_4715_;
goto v_resetjp_4629_;
}
v_resetjp_4629_:
{
lean_object* v_fst_4632_; lean_object* v_snd_4633_; lean_object* v___x_4635_; uint8_t v_isShared_4636_; uint8_t v_isSharedCheck_4714_; 
v_fst_4632_ = lean_ctor_get(v_b_4617_, 0);
v_snd_4633_ = lean_ctor_get(v_b_4617_, 1);
v_isSharedCheck_4714_ = !lean_is_exclusive(v_b_4617_);
if (v_isSharedCheck_4714_ == 0)
{
v___x_4635_ = v_b_4617_;
v_isShared_4636_ = v_isSharedCheck_4714_;
goto v_resetjp_4634_;
}
else
{
lean_inc(v_snd_4633_);
lean_inc(v_fst_4632_);
lean_dec(v_b_4617_);
v___x_4635_ = lean_box(0);
v_isShared_4636_ = v_isSharedCheck_4714_;
goto v_resetjp_4634_;
}
v_resetjp_4634_:
{
uint8_t v___x_4641_; 
v___x_4641_ = lean_nat_dec_lt(v_fst_4632_, v_top_4611_);
if (v___x_4641_ == 0)
{
lean_del_object(v___x_4630_);
lean_dec(v_snd_4628_);
lean_dec(v_fst_4627_);
goto v___jp_4637_;
}
else
{
lean_object* v_tax_4642_; lean_object* v_gifts_4643_; lean_object* v_cf_4644_; lean_object* v_path_4645_; uint8_t v___x_4646_; 
v_tax_4642_ = lean_ctor_get(v_snd_4628_, 0);
lean_inc(v_tax_4642_);
v_gifts_4643_ = lean_ctor_get(v_snd_4628_, 1);
lean_inc(v_gifts_4643_);
v_cf_4644_ = lean_ctor_get(v_snd_4628_, 2);
lean_inc(v_cf_4644_);
v_path_4645_ = lean_ctor_get(v_snd_4628_, 3);
lean_inc(v_path_4645_);
lean_dec(v_snd_4628_);
v___x_4646_ = lean_nat_dec_eq(v_tax_4642_, v_snd_4633_);
if (v___x_4646_ == 0)
{
lean_object* v___x_4647_; lean_object* v___x_4648_; lean_object* v___x_4649_; lean_object* v___y_4651_; lean_object* v___x_4704_; lean_object* v___x_4705_; uint8_t v___x_4706_; 
lean_del_object(v___x_4635_);
lean_dec(v_snd_4633_);
v___x_4647_ = lean_unsigned_to_nat(1u);
v___x_4648_ = lean_unsigned_to_nat(0u);
v___x_4649_ = lean_nat_add(v_fst_4632_, v___x_4647_);
lean_dec(v_fst_4632_);
v___x_4704_ = lean_array_get_size(v___y_4613_);
v___x_4705_ = ((lean_object*)(l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__7));
v___x_4706_ = lean_nat_dec_lt(v___x_4648_, v___x_4704_);
if (v___x_4706_ == 0)
{
v___y_4651_ = v___x_4705_;
goto v___jp_4650_;
}
else
{
uint8_t v___x_4707_; 
v___x_4707_ = lean_nat_dec_le(v___x_4704_, v___x_4704_);
if (v___x_4707_ == 0)
{
if (v___x_4706_ == 0)
{
v___y_4651_ = v___x_4705_;
goto v___jp_4650_;
}
else
{
size_t v___x_4708_; size_t v___x_4709_; lean_object* v___x_4710_; 
v___x_4708_ = ((size_t)0ULL);
v___x_4709_ = lean_usize_of_nat(v___x_4704_);
v___x_4710_ = l___private_Init_Data_Array_Basic_0__Array_foldlMUnsafe_fold___at___00Legal_USTax_Hunt_Basis_search_spec__9(v_tax_4642_, v___y_4613_, v___x_4708_, v___x_4709_, v___x_4705_);
v___y_4651_ = v___x_4710_;
goto v___jp_4650_;
}
}
else
{
size_t v___x_4711_; size_t v___x_4712_; lean_object* v___x_4713_; 
v___x_4711_ = ((size_t)0ULL);
v___x_4712_ = lean_usize_of_nat(v___x_4704_);
v___x_4713_ = l___private_Init_Data_Array_Basic_0__Array_foldlMUnsafe_fold___at___00Legal_USTax_Hunt_Basis_search_spec__9(v_tax_4642_, v___y_4613_, v___x_4711_, v___x_4712_, v___x_4705_);
v___y_4651_ = v___x_4713_;
goto v___jp_4650_;
}
}
v___jp_4650_:
{
lean_object* v___x_4652_; lean_object* v___x_4653_; lean_object* v___x_4654_; lean_object* v___x_4655_; lean_object* v___x_4656_; lean_object* v___x_4657_; lean_object* v___x_4658_; lean_object* v___x_4659_; lean_object* v___x_4660_; lean_object* v___x_4661_; lean_object* v___x_4662_; lean_object* v___x_4663_; lean_object* v___x_4664_; lean_object* v___x_4665_; lean_object* v___x_4666_; lean_object* v___x_4667_; lean_object* v___x_4668_; lean_object* v___x_4669_; lean_object* v___x_4670_; lean_object* v___x_4671_; lean_object* v___x_4672_; lean_object* v___x_4673_; lean_object* v___x_4674_; lean_object* v___x_4675_; lean_object* v___x_4676_; lean_object* v___x_4677_; lean_object* v___x_4678_; lean_object* v___x_4679_; 
v___x_4652_ = lean_array_get_size(v___y_4651_);
lean_dec_ref(v___y_4651_);
v___x_4653_ = ((lean_object*)(l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__0));
lean_inc_n(v_tax_4642_, 2);
v___x_4654_ = l_Nat_reprFast(v_tax_4642_);
v___x_4655_ = lean_string_append(v___x_4653_, v___x_4654_);
lean_dec_ref(v___x_4654_);
v___x_4656_ = ((lean_object*)(l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__1));
v___x_4657_ = lean_string_append(v___x_4655_, v___x_4656_);
v___x_4658_ = lean_nat_to_int(v_tax_4642_);
v___x_4659_ = lean_int_sub(v___y_4612_, v___x_4658_);
lean_dec(v___x_4658_);
v___x_4660_ = l_Int_repr(v___x_4659_);
lean_dec(v___x_4659_);
v___x_4661_ = lean_string_append(v___x_4657_, v___x_4660_);
lean_dec_ref(v___x_4660_);
v___x_4662_ = ((lean_object*)(l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__2));
v___x_4663_ = lean_string_append(v___x_4661_, v___x_4662_);
v___x_4664_ = l_Nat_reprFast(v_gifts_4643_);
v___x_4665_ = lean_string_append(v___x_4663_, v___x_4664_);
lean_dec_ref(v___x_4664_);
v___x_4666_ = ((lean_object*)(l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__3));
v___x_4667_ = lean_string_append(v___x_4665_, v___x_4666_);
v___x_4668_ = l_Nat_reprFast(v_cf_4644_);
v___x_4669_ = lean_string_append(v___x_4667_, v___x_4668_);
lean_dec_ref(v___x_4668_);
v___x_4670_ = ((lean_object*)(l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__4));
v___x_4671_ = lean_string_append(v___x_4669_, v___x_4670_);
v___x_4672_ = l_Nat_reprFast(v___x_4652_);
v___x_4673_ = lean_string_append(v___x_4671_, v___x_4672_);
lean_dec_ref(v___x_4672_);
v___x_4674_ = ((lean_object*)(l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__5));
v___x_4675_ = lean_string_append(v___x_4673_, v___x_4674_);
v___x_4676_ = lean_string_append(v___x_4675_, v_fst_4627_);
lean_dec(v_fst_4627_);
v___x_4677_ = ((lean_object*)(l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__4));
v___x_4678_ = lean_string_append(v___x_4676_, v___x_4677_);
v___x_4679_ = l_IO_println___at___00Legal_USTax_Hunt_Basis_search_spec__0(v___x_4678_);
if (lean_obj_tag(v___x_4679_) == 0)
{
lean_object* v___x_4680_; lean_object* v___x_4681_; lean_object* v___x_4682_; lean_object* v___x_4683_; lean_object* v___x_4684_; 
lean_dec_ref_known(v___x_4679_, 1);
v___x_4680_ = ((lean_object*)(l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__6));
v___x_4681_ = l_List_reverse___redArg(v_path_4645_);
v___x_4682_ = l_String_intercalate(v___x_4670_, v___x_4681_);
v___x_4683_ = lean_string_append(v___x_4680_, v___x_4682_);
lean_dec_ref(v___x_4682_);
v___x_4684_ = l_IO_println___at___00Legal_USTax_Hunt_Basis_search_spec__0(v___x_4683_);
if (lean_obj_tag(v___x_4684_) == 0)
{
lean_object* v___x_4686_; 
lean_dec_ref_known(v___x_4684_, 1);
if (v_isShared_4631_ == 0)
{
lean_ctor_set(v___x_4630_, 1, v_tax_4642_);
lean_ctor_set(v___x_4630_, 0, v___x_4649_);
v___x_4686_ = v___x_4630_;
goto v_reusejp_4685_;
}
else
{
lean_object* v_reuseFailAlloc_4687_; 
v_reuseFailAlloc_4687_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4687_, 0, v___x_4649_);
lean_ctor_set(v_reuseFailAlloc_4687_, 1, v_tax_4642_);
v___x_4686_ = v_reuseFailAlloc_4687_;
goto v_reusejp_4685_;
}
v_reusejp_4685_:
{
v_a_4620_ = v___x_4686_;
goto v___jp_4619_;
}
}
else
{
lean_object* v_a_4688_; lean_object* v___x_4690_; uint8_t v_isShared_4691_; uint8_t v_isSharedCheck_4695_; 
lean_dec(v___x_4649_);
lean_dec(v_tax_4642_);
lean_del_object(v___x_4630_);
v_a_4688_ = lean_ctor_get(v___x_4684_, 0);
v_isSharedCheck_4695_ = !lean_is_exclusive(v___x_4684_);
if (v_isSharedCheck_4695_ == 0)
{
v___x_4690_ = v___x_4684_;
v_isShared_4691_ = v_isSharedCheck_4695_;
goto v_resetjp_4689_;
}
else
{
lean_inc(v_a_4688_);
lean_dec(v___x_4684_);
v___x_4690_ = lean_box(0);
v_isShared_4691_ = v_isSharedCheck_4695_;
goto v_resetjp_4689_;
}
v_resetjp_4689_:
{
lean_object* v___x_4693_; 
if (v_isShared_4691_ == 0)
{
v___x_4693_ = v___x_4690_;
goto v_reusejp_4692_;
}
else
{
lean_object* v_reuseFailAlloc_4694_; 
v_reuseFailAlloc_4694_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v_reuseFailAlloc_4694_, 0, v_a_4688_);
v___x_4693_ = v_reuseFailAlloc_4694_;
goto v_reusejp_4692_;
}
v_reusejp_4692_:
{
return v___x_4693_;
}
}
}
}
else
{
lean_object* v_a_4696_; lean_object* v___x_4698_; uint8_t v_isShared_4699_; uint8_t v_isSharedCheck_4703_; 
lean_dec(v___x_4649_);
lean_dec(v_path_4645_);
lean_dec(v_tax_4642_);
lean_del_object(v___x_4630_);
v_a_4696_ = lean_ctor_get(v___x_4679_, 0);
v_isSharedCheck_4703_ = !lean_is_exclusive(v___x_4679_);
if (v_isSharedCheck_4703_ == 0)
{
v___x_4698_ = v___x_4679_;
v_isShared_4699_ = v_isSharedCheck_4703_;
goto v_resetjp_4697_;
}
else
{
lean_inc(v_a_4696_);
lean_dec(v___x_4679_);
v___x_4698_ = lean_box(0);
v_isShared_4699_ = v_isSharedCheck_4703_;
goto v_resetjp_4697_;
}
v_resetjp_4697_:
{
lean_object* v___x_4701_; 
if (v_isShared_4699_ == 0)
{
v___x_4701_ = v___x_4698_;
goto v_reusejp_4700_;
}
else
{
lean_object* v_reuseFailAlloc_4702_; 
v_reuseFailAlloc_4702_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v_reuseFailAlloc_4702_, 0, v_a_4696_);
v___x_4701_ = v_reuseFailAlloc_4702_;
goto v_reusejp_4700_;
}
v_reusejp_4700_:
{
return v___x_4701_;
}
}
}
}
}
else
{
lean_dec(v_path_4645_);
lean_dec(v_cf_4644_);
lean_dec(v_gifts_4643_);
lean_dec(v_tax_4642_);
lean_del_object(v___x_4630_);
lean_dec(v_fst_4627_);
goto v___jp_4637_;
}
}
v___jp_4637_:
{
lean_object* v___x_4639_; 
if (v_isShared_4636_ == 0)
{
v___x_4639_ = v___x_4635_;
goto v_reusejp_4638_;
}
else
{
lean_object* v_reuseFailAlloc_4640_; 
v_reuseFailAlloc_4640_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4640_, 0, v_fst_4632_);
lean_ctor_set(v_reuseFailAlloc_4640_, 1, v_snd_4633_);
v___x_4639_ = v_reuseFailAlloc_4640_;
goto v_reusejp_4638_;
}
v_reusejp_4638_:
{
v_a_4620_ = v___x_4639_;
goto v___jp_4619_;
}
}
}
}
}
v___jp_4619_:
{
size_t v___x_4621_; size_t v___x_4622_; 
v___x_4621_ = ((size_t)1ULL);
v___x_4622_ = lean_usize_add(v_i_4616_, v___x_4621_);
v_i_4616_ = v___x_4622_;
v_b_4617_ = v_a_4620_;
goto _start;
}
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___boxed(lean_object* v_top_4716_, lean_object* v___y_4717_, lean_object* v___y_4718_, lean_object* v_as_4719_, lean_object* v_sz_4720_, lean_object* v_i_4721_, lean_object* v_b_4722_, lean_object* v___y_4723_){
_start:
{
size_t v_sz_boxed_4724_; size_t v_i_boxed_4725_; lean_object* v_res_4726_; 
v_sz_boxed_4724_ = lean_unbox_usize(v_sz_4720_);
lean_dec(v_sz_4720_);
v_i_boxed_4725_ = lean_unbox_usize(v_i_4721_);
lean_dec(v_i_4721_);
v_res_4726_ = l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17(v_top_4716_, v___y_4717_, v___y_4718_, v_as_4719_, v_sz_boxed_4724_, v_i_boxed_4725_, v_b_4722_);
lean_dec_ref(v_as_4719_);
lean_dec_ref(v___y_4718_);
lean_dec(v___y_4717_);
lean_dec(v_top_4716_);
return v_res_4726_;
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10(lean_object* v_top_4727_, lean_object* v___y_4728_, lean_object* v___y_4729_, lean_object* v_as_4730_, size_t v_sz_4731_, size_t v_i_4732_, lean_object* v_b_4733_){
_start:
{
lean_object* v_a_4736_; uint8_t v___x_4740_; 
v___x_4740_ = lean_usize_dec_lt(v_i_4732_, v_sz_4731_);
if (v___x_4740_ == 0)
{
lean_object* v___x_4741_; 
v___x_4741_ = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(v___x_4741_, 0, v_b_4733_);
return v___x_4741_;
}
else
{
lean_object* v_a_4742_; lean_object* v_fst_4743_; lean_object* v_snd_4744_; lean_object* v___x_4746_; uint8_t v_isShared_4747_; uint8_t v_isSharedCheck_4831_; 
v_a_4742_ = lean_array_uget(v_as_4730_, v_i_4732_);
v_fst_4743_ = lean_ctor_get(v_a_4742_, 0);
v_snd_4744_ = lean_ctor_get(v_a_4742_, 1);
v_isSharedCheck_4831_ = !lean_is_exclusive(v_a_4742_);
if (v_isSharedCheck_4831_ == 0)
{
v___x_4746_ = v_a_4742_;
v_isShared_4747_ = v_isSharedCheck_4831_;
goto v_resetjp_4745_;
}
else
{
lean_inc(v_snd_4744_);
lean_inc(v_fst_4743_);
lean_dec(v_a_4742_);
v___x_4746_ = lean_box(0);
v_isShared_4747_ = v_isSharedCheck_4831_;
goto v_resetjp_4745_;
}
v_resetjp_4745_:
{
lean_object* v_fst_4748_; lean_object* v_snd_4749_; lean_object* v___x_4751_; uint8_t v_isShared_4752_; uint8_t v_isSharedCheck_4830_; 
v_fst_4748_ = lean_ctor_get(v_b_4733_, 0);
v_snd_4749_ = lean_ctor_get(v_b_4733_, 1);
v_isSharedCheck_4830_ = !lean_is_exclusive(v_b_4733_);
if (v_isSharedCheck_4830_ == 0)
{
v___x_4751_ = v_b_4733_;
v_isShared_4752_ = v_isSharedCheck_4830_;
goto v_resetjp_4750_;
}
else
{
lean_inc(v_snd_4749_);
lean_inc(v_fst_4748_);
lean_dec(v_b_4733_);
v___x_4751_ = lean_box(0);
v_isShared_4752_ = v_isSharedCheck_4830_;
goto v_resetjp_4750_;
}
v_resetjp_4750_:
{
uint8_t v___x_4757_; 
v___x_4757_ = lean_nat_dec_lt(v_fst_4748_, v_top_4727_);
if (v___x_4757_ == 0)
{
lean_del_object(v___x_4746_);
lean_dec(v_snd_4744_);
lean_dec(v_fst_4743_);
goto v___jp_4753_;
}
else
{
lean_object* v_tax_4758_; lean_object* v_gifts_4759_; lean_object* v_cf_4760_; lean_object* v_path_4761_; uint8_t v___x_4762_; 
v_tax_4758_ = lean_ctor_get(v_snd_4744_, 0);
lean_inc(v_tax_4758_);
v_gifts_4759_ = lean_ctor_get(v_snd_4744_, 1);
lean_inc(v_gifts_4759_);
v_cf_4760_ = lean_ctor_get(v_snd_4744_, 2);
lean_inc(v_cf_4760_);
v_path_4761_ = lean_ctor_get(v_snd_4744_, 3);
lean_inc(v_path_4761_);
lean_dec(v_snd_4744_);
v___x_4762_ = lean_nat_dec_eq(v_tax_4758_, v_snd_4749_);
if (v___x_4762_ == 0)
{
lean_object* v___x_4763_; lean_object* v___x_4764_; lean_object* v___x_4765_; lean_object* v___y_4767_; lean_object* v___x_4820_; lean_object* v___x_4821_; uint8_t v___x_4822_; 
lean_del_object(v___x_4751_);
lean_dec(v_snd_4749_);
v___x_4763_ = lean_unsigned_to_nat(1u);
v___x_4764_ = lean_unsigned_to_nat(0u);
v___x_4765_ = lean_nat_add(v_fst_4748_, v___x_4763_);
lean_dec(v_fst_4748_);
v___x_4820_ = lean_array_get_size(v___y_4729_);
v___x_4821_ = ((lean_object*)(l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__7));
v___x_4822_ = lean_nat_dec_lt(v___x_4764_, v___x_4820_);
if (v___x_4822_ == 0)
{
v___y_4767_ = v___x_4821_;
goto v___jp_4766_;
}
else
{
uint8_t v___x_4823_; 
v___x_4823_ = lean_nat_dec_le(v___x_4820_, v___x_4820_);
if (v___x_4823_ == 0)
{
if (v___x_4822_ == 0)
{
v___y_4767_ = v___x_4821_;
goto v___jp_4766_;
}
else
{
size_t v___x_4824_; size_t v___x_4825_; lean_object* v___x_4826_; 
v___x_4824_ = ((size_t)0ULL);
v___x_4825_ = lean_usize_of_nat(v___x_4820_);
v___x_4826_ = l___private_Init_Data_Array_Basic_0__Array_foldlMUnsafe_fold___at___00Legal_USTax_Hunt_Basis_search_spec__9(v_tax_4758_, v___y_4729_, v___x_4824_, v___x_4825_, v___x_4821_);
v___y_4767_ = v___x_4826_;
goto v___jp_4766_;
}
}
else
{
size_t v___x_4827_; size_t v___x_4828_; lean_object* v___x_4829_; 
v___x_4827_ = ((size_t)0ULL);
v___x_4828_ = lean_usize_of_nat(v___x_4820_);
v___x_4829_ = l___private_Init_Data_Array_Basic_0__Array_foldlMUnsafe_fold___at___00Legal_USTax_Hunt_Basis_search_spec__9(v_tax_4758_, v___y_4729_, v___x_4827_, v___x_4828_, v___x_4821_);
v___y_4767_ = v___x_4829_;
goto v___jp_4766_;
}
}
v___jp_4766_:
{
lean_object* v___x_4768_; lean_object* v___x_4769_; lean_object* v___x_4770_; lean_object* v___x_4771_; lean_object* v___x_4772_; lean_object* v___x_4773_; lean_object* v___x_4774_; lean_object* v___x_4775_; lean_object* v___x_4776_; lean_object* v___x_4777_; lean_object* v___x_4778_; lean_object* v___x_4779_; lean_object* v___x_4780_; lean_object* v___x_4781_; lean_object* v___x_4782_; lean_object* v___x_4783_; lean_object* v___x_4784_; lean_object* v___x_4785_; lean_object* v___x_4786_; lean_object* v___x_4787_; lean_object* v___x_4788_; lean_object* v___x_4789_; lean_object* v___x_4790_; lean_object* v___x_4791_; lean_object* v___x_4792_; lean_object* v___x_4793_; lean_object* v___x_4794_; lean_object* v___x_4795_; 
v___x_4768_ = lean_array_get_size(v___y_4767_);
lean_dec_ref(v___y_4767_);
v___x_4769_ = ((lean_object*)(l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__0));
lean_inc_n(v_tax_4758_, 2);
v___x_4770_ = l_Nat_reprFast(v_tax_4758_);
v___x_4771_ = lean_string_append(v___x_4769_, v___x_4770_);
lean_dec_ref(v___x_4770_);
v___x_4772_ = ((lean_object*)(l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__1));
v___x_4773_ = lean_string_append(v___x_4771_, v___x_4772_);
v___x_4774_ = lean_nat_to_int(v_tax_4758_);
v___x_4775_ = lean_int_sub(v___y_4728_, v___x_4774_);
lean_dec(v___x_4774_);
v___x_4776_ = l_Int_repr(v___x_4775_);
lean_dec(v___x_4775_);
v___x_4777_ = lean_string_append(v___x_4773_, v___x_4776_);
lean_dec_ref(v___x_4776_);
v___x_4778_ = ((lean_object*)(l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__2));
v___x_4779_ = lean_string_append(v___x_4777_, v___x_4778_);
v___x_4780_ = l_Nat_reprFast(v_gifts_4759_);
v___x_4781_ = lean_string_append(v___x_4779_, v___x_4780_);
lean_dec_ref(v___x_4780_);
v___x_4782_ = ((lean_object*)(l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__3));
v___x_4783_ = lean_string_append(v___x_4781_, v___x_4782_);
v___x_4784_ = l_Nat_reprFast(v_cf_4760_);
v___x_4785_ = lean_string_append(v___x_4783_, v___x_4784_);
lean_dec_ref(v___x_4784_);
v___x_4786_ = ((lean_object*)(l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__4));
v___x_4787_ = lean_string_append(v___x_4785_, v___x_4786_);
v___x_4788_ = l_Nat_reprFast(v___x_4768_);
v___x_4789_ = lean_string_append(v___x_4787_, v___x_4788_);
lean_dec_ref(v___x_4788_);
v___x_4790_ = ((lean_object*)(l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__5));
v___x_4791_ = lean_string_append(v___x_4789_, v___x_4790_);
v___x_4792_ = lean_string_append(v___x_4791_, v_fst_4743_);
lean_dec(v_fst_4743_);
v___x_4793_ = ((lean_object*)(l_List_repr___at___00Legal_USTax_Hunt_Basis_instReprSt_repr_spec__0___redArg___closed__4));
v___x_4794_ = lean_string_append(v___x_4792_, v___x_4793_);
v___x_4795_ = l_IO_println___at___00Legal_USTax_Hunt_Basis_search_spec__0(v___x_4794_);
if (lean_obj_tag(v___x_4795_) == 0)
{
lean_object* v___x_4796_; lean_object* v___x_4797_; lean_object* v___x_4798_; lean_object* v___x_4799_; lean_object* v___x_4800_; 
lean_dec_ref_known(v___x_4795_, 1);
v___x_4796_ = ((lean_object*)(l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17___closed__6));
v___x_4797_ = l_List_reverse___redArg(v_path_4761_);
v___x_4798_ = l_String_intercalate(v___x_4786_, v___x_4797_);
v___x_4799_ = lean_string_append(v___x_4796_, v___x_4798_);
lean_dec_ref(v___x_4798_);
v___x_4800_ = l_IO_println___at___00Legal_USTax_Hunt_Basis_search_spec__0(v___x_4799_);
if (lean_obj_tag(v___x_4800_) == 0)
{
lean_object* v___x_4802_; 
lean_dec_ref_known(v___x_4800_, 1);
if (v_isShared_4747_ == 0)
{
lean_ctor_set(v___x_4746_, 1, v_tax_4758_);
lean_ctor_set(v___x_4746_, 0, v___x_4765_);
v___x_4802_ = v___x_4746_;
goto v_reusejp_4801_;
}
else
{
lean_object* v_reuseFailAlloc_4803_; 
v_reuseFailAlloc_4803_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4803_, 0, v___x_4765_);
lean_ctor_set(v_reuseFailAlloc_4803_, 1, v_tax_4758_);
v___x_4802_ = v_reuseFailAlloc_4803_;
goto v_reusejp_4801_;
}
v_reusejp_4801_:
{
v_a_4736_ = v___x_4802_;
goto v___jp_4735_;
}
}
else
{
lean_object* v_a_4804_; lean_object* v___x_4806_; uint8_t v_isShared_4807_; uint8_t v_isSharedCheck_4811_; 
lean_dec(v___x_4765_);
lean_dec(v_tax_4758_);
lean_del_object(v___x_4746_);
v_a_4804_ = lean_ctor_get(v___x_4800_, 0);
v_isSharedCheck_4811_ = !lean_is_exclusive(v___x_4800_);
if (v_isSharedCheck_4811_ == 0)
{
v___x_4806_ = v___x_4800_;
v_isShared_4807_ = v_isSharedCheck_4811_;
goto v_resetjp_4805_;
}
else
{
lean_inc(v_a_4804_);
lean_dec(v___x_4800_);
v___x_4806_ = lean_box(0);
v_isShared_4807_ = v_isSharedCheck_4811_;
goto v_resetjp_4805_;
}
v_resetjp_4805_:
{
lean_object* v___x_4809_; 
if (v_isShared_4807_ == 0)
{
v___x_4809_ = v___x_4806_;
goto v_reusejp_4808_;
}
else
{
lean_object* v_reuseFailAlloc_4810_; 
v_reuseFailAlloc_4810_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v_reuseFailAlloc_4810_, 0, v_a_4804_);
v___x_4809_ = v_reuseFailAlloc_4810_;
goto v_reusejp_4808_;
}
v_reusejp_4808_:
{
return v___x_4809_;
}
}
}
}
else
{
lean_object* v_a_4812_; lean_object* v___x_4814_; uint8_t v_isShared_4815_; uint8_t v_isSharedCheck_4819_; 
lean_dec(v___x_4765_);
lean_dec(v_path_4761_);
lean_dec(v_tax_4758_);
lean_del_object(v___x_4746_);
v_a_4812_ = lean_ctor_get(v___x_4795_, 0);
v_isSharedCheck_4819_ = !lean_is_exclusive(v___x_4795_);
if (v_isSharedCheck_4819_ == 0)
{
v___x_4814_ = v___x_4795_;
v_isShared_4815_ = v_isSharedCheck_4819_;
goto v_resetjp_4813_;
}
else
{
lean_inc(v_a_4812_);
lean_dec(v___x_4795_);
v___x_4814_ = lean_box(0);
v_isShared_4815_ = v_isSharedCheck_4819_;
goto v_resetjp_4813_;
}
v_resetjp_4813_:
{
lean_object* v___x_4817_; 
if (v_isShared_4815_ == 0)
{
v___x_4817_ = v___x_4814_;
goto v_reusejp_4816_;
}
else
{
lean_object* v_reuseFailAlloc_4818_; 
v_reuseFailAlloc_4818_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v_reuseFailAlloc_4818_, 0, v_a_4812_);
v___x_4817_ = v_reuseFailAlloc_4818_;
goto v_reusejp_4816_;
}
v_reusejp_4816_:
{
return v___x_4817_;
}
}
}
}
}
else
{
lean_dec(v_path_4761_);
lean_dec(v_cf_4760_);
lean_dec(v_gifts_4759_);
lean_dec(v_tax_4758_);
lean_del_object(v___x_4746_);
lean_dec(v_fst_4743_);
goto v___jp_4753_;
}
}
v___jp_4753_:
{
lean_object* v___x_4755_; 
if (v_isShared_4752_ == 0)
{
v___x_4755_ = v___x_4751_;
goto v_reusejp_4754_;
}
else
{
lean_object* v_reuseFailAlloc_4756_; 
v_reuseFailAlloc_4756_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v_reuseFailAlloc_4756_, 0, v_fst_4748_);
lean_ctor_set(v_reuseFailAlloc_4756_, 1, v_snd_4749_);
v___x_4755_ = v_reuseFailAlloc_4756_;
goto v_reusejp_4754_;
}
v_reusejp_4754_:
{
v_a_4736_ = v___x_4755_;
goto v___jp_4735_;
}
}
}
}
}
v___jp_4735_:
{
size_t v___x_4737_; size_t v___x_4738_; lean_object* v___x_4739_; 
v___x_4737_ = ((size_t)1ULL);
v___x_4738_ = lean_usize_add(v_i_4732_, v___x_4737_);
v___x_4739_ = l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00__private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10_spec__17(v_top_4727_, v___y_4728_, v___y_4729_, v_as_4730_, v_sz_4731_, v___x_4738_, v_a_4736_);
return v___x_4739_;
}
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10___boxed(lean_object* v_top_4832_, lean_object* v___y_4833_, lean_object* v___y_4834_, lean_object* v_as_4835_, lean_object* v_sz_4836_, lean_object* v_i_4837_, lean_object* v_b_4838_, lean_object* v___y_4839_){
_start:
{
size_t v_sz_boxed_4840_; size_t v_i_boxed_4841_; lean_object* v_res_4842_; 
v_sz_boxed_4840_ = lean_unbox_usize(v_sz_4836_);
lean_dec(v_sz_4836_);
v_i_boxed_4841_ = lean_unbox_usize(v_i_4837_);
lean_dec(v_i_4837_);
v_res_4842_ = l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10(v_top_4832_, v___y_4833_, v___y_4834_, v_as_4835_, v_sz_boxed_4840_, v_i_boxed_4841_, v_b_4838_);
lean_dec_ref(v_as_4835_);
lean_dec_ref(v___y_4834_);
lean_dec(v___y_4833_);
lean_dec(v_top_4832_);
return v_res_4842_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_foldlM___at___00Legal_USTax_Hunt_Basis_search_spec__12(lean_object* v_x_4843_, lean_object* v_x_4844_){
_start:
{
if (lean_obj_tag(v_x_4844_) == 0)
{
return v_x_4843_;
}
else
{
lean_object* v_key_4845_; lean_object* v_value_4846_; lean_object* v_tail_4847_; lean_object* v___x_4848_; lean_object* v___x_4849_; 
v_key_4845_ = lean_ctor_get(v_x_4844_, 0);
v_value_4846_ = lean_ctor_get(v_x_4844_, 1);
v_tail_4847_ = lean_ctor_get(v_x_4844_, 2);
lean_inc(v_value_4846_);
lean_inc(v_key_4845_);
v___x_4848_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4848_, 0, v_key_4845_);
lean_ctor_set(v___x_4848_, 1, v_value_4846_);
v___x_4849_ = lean_array_push(v_x_4843_, v___x_4848_);
v_x_4843_ = v___x_4849_;
v_x_4844_ = v_tail_4847_;
goto _start;
}
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_foldlM___at___00Legal_USTax_Hunt_Basis_search_spec__12___boxed(lean_object* v_x_4851_, lean_object* v_x_4852_){
_start:
{
lean_object* v_res_4853_; 
v_res_4853_ = l_Std_DHashMap_Internal_AssocList_foldlM___at___00Legal_USTax_Hunt_Basis_search_spec__12(v_x_4851_, v_x_4852_);
lean_dec(v_x_4852_);
return v_res_4853_;
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_foldlMUnsafe_fold___at___00Legal_USTax_Hunt_Basis_search_spec__13(lean_object* v_as_4854_, size_t v_i_4855_, size_t v_stop_4856_, lean_object* v_b_4857_){
_start:
{
uint8_t v___x_4858_; 
v___x_4858_ = lean_usize_dec_eq(v_i_4855_, v_stop_4856_);
if (v___x_4858_ == 0)
{
lean_object* v___x_4859_; lean_object* v___x_4860_; size_t v___x_4861_; size_t v___x_4862_; 
v___x_4859_ = lean_array_uget_borrowed(v_as_4854_, v_i_4855_);
v___x_4860_ = l_Std_DHashMap_Internal_AssocList_foldlM___at___00Legal_USTax_Hunt_Basis_search_spec__12(v_b_4857_, v___x_4859_);
v___x_4861_ = ((size_t)1ULL);
v___x_4862_ = lean_usize_add(v_i_4855_, v___x_4861_);
v_i_4855_ = v___x_4862_;
v_b_4857_ = v___x_4860_;
goto _start;
}
else
{
return v_b_4857_;
}
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Array_Basic_0__Array_foldlMUnsafe_fold___at___00Legal_USTax_Hunt_Basis_search_spec__13___boxed(lean_object* v_as_4864_, lean_object* v_i_4865_, lean_object* v_stop_4866_, lean_object* v_b_4867_){
_start:
{
size_t v_i_boxed_4868_; size_t v_stop_boxed_4869_; lean_object* v_res_4870_; 
v_i_boxed_4868_ = lean_unbox_usize(v_i_4865_);
lean_dec(v_i_4865_);
v_stop_boxed_4869_ = lean_unbox_usize(v_stop_4866_);
lean_dec(v_stop_4866_);
v_res_4870_ = l___private_Init_Data_Array_Basic_0__Array_foldlMUnsafe_fold___at___00Legal_USTax_Hunt_Basis_search_spec__13(v_as_4864_, v_i_boxed_4868_, v_stop_boxed_4869_, v_b_4867_);
lean_dec_ref(v_as_4864_);
return v_res_4870_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_search___closed__2(void){
_start:
{
lean_object* v___x_4873_; lean_object* v___x_4874_; lean_object* v___x_4875_; 
v___x_4873_ = lean_cstr_to_nat("1000000000000");
v___x_4874_ = lean_unsigned_to_nat(0u);
v___x_4875_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4875_, 0, v___x_4874_);
lean_ctor_set(v___x_4875_, 1, v___x_4873_);
return v___x_4875_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_search___closed__6(void){
_start:
{
lean_object* v___x_4883_; lean_object* v___x_4884_; lean_object* v___x_4885_; 
v___x_4883_ = lean_box(0);
v___x_4884_ = lean_unsigned_to_nat(16u);
v___x_4885_ = lean_mk_array(v___x_4884_, v___x_4883_);
return v___x_4885_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_search___closed__7(void){
_start:
{
lean_object* v___x_4886_; lean_object* v___x_4887_; lean_object* v___x_4888_; 
v___x_4886_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_search___closed__6, &l_Legal_USTax_Hunt_Basis_search___closed__6_once, _init_l_Legal_USTax_Hunt_Basis_search___closed__6);
v___x_4887_ = lean_unsigned_to_nat(0u);
v___x_4888_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4888_, 0, v___x_4887_);
lean_ctor_set(v___x_4888_, 1, v___x_4886_);
return v___x_4888_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_search___closed__8(void){
_start:
{
lean_object* v___x_4889_; lean_object* v___x_4890_; lean_object* v___x_4891_; 
v___x_4889_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_ordTax___closed__0));
v___x_4890_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_search___closed__7, &l_Legal_USTax_Hunt_Basis_search___closed__7_once, _init_l_Legal_USTax_Hunt_Basis_search___closed__7);
v___x_4891_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4891_, 0, v___x_4890_);
lean_ctor_set(v___x_4891_, 1, v___x_4889_);
return v___x_4891_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_search___closed__9(void){
_start:
{
lean_object* v___x_4892_; lean_object* v___x_4893_; lean_object* v___x_4894_; 
v___x_4892_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_search___closed__8, &l_Legal_USTax_Hunt_Basis_search___closed__8_once, _init_l_Legal_USTax_Hunt_Basis_search___closed__8);
v___x_4893_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_search___closed__7, &l_Legal_USTax_Hunt_Basis_search___closed__7_once, _init_l_Legal_USTax_Hunt_Basis_search___closed__7);
v___x_4894_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4894_, 0, v___x_4893_);
lean_ctor_set(v___x_4894_, 1, v___x_4892_);
return v___x_4894_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_search(lean_object* v_title_4899_, lean_object* v_cfg_4900_, lean_object* v_s0_4901_, lean_object* v_allowed_4902_, lean_object* v_top_4903_){
_start:
{
lean_object* v___x_4905_; lean_object* v___x_4906_; lean_object* v___x_4907_; lean_object* v___x_4908_; lean_object* v___x_4909_; 
v___x_4905_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_search___closed__0));
v___x_4906_ = lean_string_append(v___x_4905_, v_title_4899_);
v___x_4907_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_search___closed__1));
v___x_4908_ = lean_string_append(v___x_4906_, v___x_4907_);
v___x_4909_ = l_IO_println___at___00Legal_USTax_Hunt_Basis_search_spec__0(v___x_4908_);
if (lean_obj_tag(v___x_4909_) == 0)
{
lean_object* v_lots_4910_; lean_object* v___x_4911_; lean_object* v___x_4912_; lean_object* v___x_4913_; lean_object* v___y_4915_; lean_object* v___y_4916_; lean_object* v___y_4938_; lean_object* v___y_4939_; lean_object* v___y_4940_; lean_object* v___y_4941_; lean_object* v___y_4942_; lean_object* v___y_4945_; lean_object* v___y_4946_; lean_object* v___y_4947_; lean_object* v___y_4948_; lean_object* v___y_4949_; lean_object* v___y_4952_; lean_object* v___y_4953_; lean_object* v___y_4954_; lean_object* v___x_4959_; 
lean_dec_ref_known(v___x_4909_, 1);
v_lots_4910_ = lean_ctor_get(v_s0_4901_, 0);
v___x_4911_ = lean_unsigned_to_nat(0u);
lean_inc(v_lots_4910_);
v___x_4912_ = l_List_zipIdxTR___redArg(v_lots_4910_, v___x_4911_);
v___x_4913_ = lean_box(0);
v___x_4959_ = l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg(v___x_4912_, v___x_4913_);
lean_dec(v___x_4912_);
if (lean_obj_tag(v___x_4959_) == 0)
{
lean_object* v___y_4961_; lean_object* v___x_5015_; 
lean_dec_ref_known(v___x_4959_, 1);
lean_inc_ref(v_s0_4901_);
v___x_5015_ = l_Legal_USTax_Hunt_Basis_baseline(v_cfg_4900_, v_s0_4901_);
if (lean_obj_tag(v___x_5015_) == 0)
{
lean_object* v___x_5016_; 
v___x_5016_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0, &l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0);
v___y_4961_ = v___x_5016_;
goto v___jp_4960_;
}
else
{
lean_object* v_val_5017_; lean_object* v_tax_5018_; lean_object* v___x_5019_; 
v_val_5017_ = lean_ctor_get(v___x_5015_, 0);
lean_inc(v_val_5017_);
lean_dec_ref_known(v___x_5015_, 1);
v_tax_5018_ = lean_ctor_get(v_val_5017_, 11);
lean_inc(v_tax_5018_);
lean_dec(v_val_5017_);
v___x_5019_ = lean_nat_to_int(v_tax_5018_);
v___y_4961_ = v___x_5019_;
goto v___jp_4960_;
}
v___jp_4960_:
{
lean_object* v___x_4962_; lean_object* v___x_4963_; lean_object* v___x_4964_; lean_object* v___x_4965_; 
v___x_4962_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_search___closed__3));
v___x_4963_ = l_Int_repr(v___y_4961_);
v___x_4964_ = lean_string_append(v___x_4962_, v___x_4963_);
lean_dec_ref(v___x_4963_);
v___x_4965_ = l_IO_println___at___00Legal_USTax_Hunt_Basis_search_spec__0(v___x_4964_);
if (lean_obj_tag(v___x_4965_) == 0)
{
lean_object* v___x_4966_; lean_object* v___x_4967_; lean_object* v___x_4968_; lean_object* v___x_4969_; lean_object* v___x_4970_; lean_object* v___x_4971_; lean_object* v___x_4972_; lean_object* v___x_4973_; 
lean_dec_ref_known(v___x_4965_, 1);
v___x_4966_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_search___closed__5));
v___x_4967_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4967_, 0, v_s0_4901_);
lean_ctor_set(v___x_4967_, 1, v___x_4966_);
v___x_4968_ = lean_unsigned_to_nat(1u);
v___x_4969_ = lean_mk_empty_array_with_capacity(v___x_4968_);
v___x_4970_ = lean_array_push(v___x_4969_, v___x_4967_);
v___x_4971_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_search___closed__9, &l_Legal_USTax_Hunt_Basis_search___closed__9_once, _init_l_Legal_USTax_Hunt_Basis_search___closed__9);
v___x_4972_ = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(v___x_4972_, 0, v___x_4970_);
lean_ctor_set(v___x_4972_, 1, v___x_4971_);
v___x_4973_ = l___private_Init_While_0__repeatM_erased___at___00Legal_USTax_Hunt_Basis_search_spec__8___redArg(v_allowed_4902_, v_cfg_4900_, v___x_4972_);
if (lean_obj_tag(v___x_4973_) == 0)
{
lean_object* v_a_4974_; lean_object* v_snd_4975_; lean_object* v_snd_4976_; lean_object* v_snd_4977_; lean_object* v_fst_4978_; lean_object* v_fst_4979_; lean_object* v_fst_4980_; lean_object* v_snd_4981_; lean_object* v_size_4982_; lean_object* v_size_4983_; lean_object* v_buckets_4984_; lean_object* v___x_4985_; lean_object* v___x_4986_; lean_object* v___x_4987_; lean_object* v___x_4988_; lean_object* v___x_4989_; lean_object* v___x_4990_; lean_object* v___x_4991_; lean_object* v___x_4992_; lean_object* v___x_4993_; lean_object* v___x_4994_; lean_object* v___x_4995_; lean_object* v___x_4996_; lean_object* v___x_4997_; lean_object* v___x_4998_; lean_object* v___x_4999_; lean_object* v___x_5000_; 
v_a_4974_ = lean_ctor_get(v___x_4973_, 0);
lean_inc(v_a_4974_);
lean_dec_ref_known(v___x_4973_, 1);
v_snd_4975_ = lean_ctor_get(v_a_4974_, 1);
lean_inc(v_snd_4975_);
lean_dec(v_a_4974_);
v_snd_4976_ = lean_ctor_get(v_snd_4975_, 1);
lean_inc(v_snd_4976_);
v_snd_4977_ = lean_ctor_get(v_snd_4976_, 1);
lean_inc(v_snd_4977_);
v_fst_4978_ = lean_ctor_get(v_snd_4975_, 0);
lean_inc(v_fst_4978_);
lean_dec(v_snd_4975_);
v_fst_4979_ = lean_ctor_get(v_snd_4976_, 0);
lean_inc(v_fst_4979_);
lean_dec(v_snd_4976_);
v_fst_4980_ = lean_ctor_get(v_snd_4977_, 0);
lean_inc(v_fst_4980_);
v_snd_4981_ = lean_ctor_get(v_snd_4977_, 1);
lean_inc(v_snd_4981_);
lean_dec(v_snd_4977_);
v_size_4982_ = lean_ctor_get(v_fst_4978_, 0);
lean_inc(v_size_4982_);
lean_dec(v_fst_4978_);
v_size_4983_ = lean_ctor_get(v_fst_4979_, 0);
lean_inc_n(v_size_4983_, 2);
v_buckets_4984_ = lean_ctor_get(v_fst_4979_, 1);
lean_inc_ref(v_buckets_4984_);
lean_dec(v_fst_4979_);
v___x_4985_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_search___closed__10));
v___x_4986_ = l_Nat_reprFast(v_size_4982_);
v___x_4987_ = lean_string_append(v___x_4985_, v___x_4986_);
lean_dec_ref(v___x_4986_);
v___x_4988_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_search___closed__11));
v___x_4989_ = lean_string_append(v___x_4987_, v___x_4988_);
v___x_4990_ = l_Nat_reprFast(v_fst_4980_);
v___x_4991_ = lean_string_append(v___x_4989_, v___x_4990_);
lean_dec_ref(v___x_4990_);
v___x_4992_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_search___closed__12));
v___x_4993_ = lean_string_append(v___x_4991_, v___x_4992_);
v___x_4994_ = l_Nat_reprFast(v_size_4983_);
v___x_4995_ = lean_string_append(v___x_4993_, v___x_4994_);
lean_dec_ref(v___x_4994_);
v___x_4996_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_search___closed__13));
v___x_4997_ = lean_string_append(v___x_4995_, v___x_4996_);
v___x_4998_ = l_Nat_reprFast(v_snd_4981_);
v___x_4999_ = lean_string_append(v___x_4997_, v___x_4998_);
lean_dec_ref(v___x_4998_);
v___x_5000_ = l_IO_println___at___00Legal_USTax_Hunt_Basis_search_spec__0(v___x_4999_);
if (lean_obj_tag(v___x_5000_) == 0)
{
lean_object* v___x_5001_; lean_object* v___x_5002_; uint8_t v___x_5003_; 
lean_dec_ref_known(v___x_5000_, 1);
v___x_5001_ = lean_mk_empty_array_with_capacity(v_size_4983_);
lean_dec(v_size_4983_);
v___x_5002_ = lean_array_get_size(v_buckets_4984_);
v___x_5003_ = lean_nat_dec_lt(v___x_4911_, v___x_5002_);
if (v___x_5003_ == 0)
{
lean_dec_ref(v_buckets_4984_);
v___y_4952_ = v___x_4968_;
v___y_4953_ = v___y_4961_;
v___y_4954_ = v___x_5001_;
goto v___jp_4951_;
}
else
{
size_t v___x_5004_; size_t v___x_5005_; lean_object* v___x_5006_; 
v___x_5004_ = ((size_t)0ULL);
v___x_5005_ = lean_usize_of_nat(v___x_5002_);
v___x_5006_ = l___private_Init_Data_Array_Basic_0__Array_foldlMUnsafe_fold___at___00Legal_USTax_Hunt_Basis_search_spec__13(v_buckets_4984_, v___x_5004_, v___x_5005_, v___x_5001_);
lean_dec_ref(v_buckets_4984_);
v___y_4952_ = v___x_4968_;
v___y_4953_ = v___y_4961_;
v___y_4954_ = v___x_5006_;
goto v___jp_4951_;
}
}
else
{
lean_dec_ref(v_buckets_4984_);
lean_dec(v_size_4983_);
lean_dec(v___y_4961_);
return v___x_5000_;
}
}
else
{
lean_object* v_a_5007_; lean_object* v___x_5009_; uint8_t v_isShared_5010_; uint8_t v_isSharedCheck_5014_; 
lean_dec(v___y_4961_);
v_a_5007_ = lean_ctor_get(v___x_4973_, 0);
v_isSharedCheck_5014_ = !lean_is_exclusive(v___x_4973_);
if (v_isSharedCheck_5014_ == 0)
{
v___x_5009_ = v___x_4973_;
v_isShared_5010_ = v_isSharedCheck_5014_;
goto v_resetjp_5008_;
}
else
{
lean_inc(v_a_5007_);
lean_dec(v___x_4973_);
v___x_5009_ = lean_box(0);
v_isShared_5010_ = v_isSharedCheck_5014_;
goto v_resetjp_5008_;
}
v_resetjp_5008_:
{
lean_object* v___x_5012_; 
if (v_isShared_5010_ == 0)
{
v___x_5012_ = v___x_5009_;
goto v_reusejp_5011_;
}
else
{
lean_object* v_reuseFailAlloc_5013_; 
v_reuseFailAlloc_5013_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v_reuseFailAlloc_5013_, 0, v_a_5007_);
v___x_5012_ = v_reuseFailAlloc_5013_;
goto v_reusejp_5011_;
}
v_reusejp_5011_:
{
return v___x_5012_;
}
}
}
}
else
{
lean_dec(v___y_4961_);
lean_dec_ref(v_allowed_4902_);
lean_dec_ref(v_s0_4901_);
return v___x_4965_;
}
}
}
else
{
lean_dec_ref(v_allowed_4902_);
lean_dec_ref(v_s0_4901_);
return v___x_4959_;
}
v___jp_4914_:
{
lean_object* v___x_4917_; size_t v_sz_4918_; size_t v___x_4919_; lean_object* v___x_4920_; 
v___x_4917_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_search___closed__2, &l_Legal_USTax_Hunt_Basis_search___closed__2_once, _init_l_Legal_USTax_Hunt_Basis_search___closed__2);
v_sz_4918_ = lean_array_size(v___y_4916_);
v___x_4919_ = ((size_t)0ULL);
v___x_4920_ = l___private_Init_Data_Array_Basic_0__Array_forIn_x27Unsafe_loop___at___00Legal_USTax_Hunt_Basis_search_spec__10(v_top_4903_, v___y_4915_, v___y_4916_, v___y_4916_, v_sz_4918_, v___x_4919_, v___x_4917_);
lean_dec_ref(v___y_4916_);
lean_dec(v___y_4915_);
if (lean_obj_tag(v___x_4920_) == 0)
{
lean_object* v___x_4922_; uint8_t v_isShared_4923_; uint8_t v_isSharedCheck_4927_; 
v_isSharedCheck_4927_ = !lean_is_exclusive(v___x_4920_);
if (v_isSharedCheck_4927_ == 0)
{
lean_object* v_unused_4928_; 
v_unused_4928_ = lean_ctor_get(v___x_4920_, 0);
lean_dec(v_unused_4928_);
v___x_4922_ = v___x_4920_;
v_isShared_4923_ = v_isSharedCheck_4927_;
goto v_resetjp_4921_;
}
else
{
lean_dec(v___x_4920_);
v___x_4922_ = lean_box(0);
v_isShared_4923_ = v_isSharedCheck_4927_;
goto v_resetjp_4921_;
}
v_resetjp_4921_:
{
lean_object* v___x_4925_; 
if (v_isShared_4923_ == 0)
{
lean_ctor_set(v___x_4922_, 0, v___x_4913_);
v___x_4925_ = v___x_4922_;
goto v_reusejp_4924_;
}
else
{
lean_object* v_reuseFailAlloc_4926_; 
v_reuseFailAlloc_4926_ = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(v_reuseFailAlloc_4926_, 0, v___x_4913_);
v___x_4925_ = v_reuseFailAlloc_4926_;
goto v_reusejp_4924_;
}
v_reusejp_4924_:
{
return v___x_4925_;
}
}
}
else
{
lean_object* v_a_4929_; lean_object* v___x_4931_; uint8_t v_isShared_4932_; uint8_t v_isSharedCheck_4936_; 
v_a_4929_ = lean_ctor_get(v___x_4920_, 0);
v_isSharedCheck_4936_ = !lean_is_exclusive(v___x_4920_);
if (v_isSharedCheck_4936_ == 0)
{
v___x_4931_ = v___x_4920_;
v_isShared_4932_ = v_isSharedCheck_4936_;
goto v_resetjp_4930_;
}
else
{
lean_inc(v_a_4929_);
lean_dec(v___x_4920_);
v___x_4931_ = lean_box(0);
v_isShared_4932_ = v_isSharedCheck_4936_;
goto v_resetjp_4930_;
}
v_resetjp_4930_:
{
lean_object* v___x_4934_; 
if (v_isShared_4932_ == 0)
{
v___x_4934_ = v___x_4931_;
goto v_reusejp_4933_;
}
else
{
lean_object* v_reuseFailAlloc_4935_; 
v_reuseFailAlloc_4935_ = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(v_reuseFailAlloc_4935_, 0, v_a_4929_);
v___x_4934_ = v_reuseFailAlloc_4935_;
goto v_reusejp_4933_;
}
v_reusejp_4933_:
{
return v___x_4934_;
}
}
}
}
v___jp_4937_:
{
lean_object* v___x_4943_; 
v___x_4943_ = l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11___redArg(v___y_4939_, v___y_4938_, v___y_4941_, v___y_4942_);
lean_dec(v___y_4942_);
lean_dec(v___y_4939_);
v___y_4915_ = v___y_4940_;
v___y_4916_ = v___x_4943_;
goto v___jp_4914_;
}
v___jp_4944_:
{
uint8_t v___x_4950_; 
v___x_4950_ = lean_nat_dec_le(v___y_4949_, v___y_4946_);
if (v___x_4950_ == 0)
{
lean_dec(v___y_4946_);
lean_inc(v___y_4949_);
v___y_4938_ = v___y_4945_;
v___y_4939_ = v___y_4947_;
v___y_4940_ = v___y_4948_;
v___y_4941_ = v___y_4949_;
v___y_4942_ = v___y_4949_;
goto v___jp_4937_;
}
else
{
v___y_4938_ = v___y_4945_;
v___y_4939_ = v___y_4947_;
v___y_4940_ = v___y_4948_;
v___y_4941_ = v___y_4949_;
v___y_4942_ = v___y_4946_;
goto v___jp_4937_;
}
}
v___jp_4951_:
{
lean_object* v___x_4955_; uint8_t v___x_4956_; 
v___x_4955_ = lean_array_get_size(v___y_4954_);
v___x_4956_ = lean_nat_dec_eq(v___x_4955_, v___x_4911_);
if (v___x_4956_ == 0)
{
lean_object* v___x_4957_; uint8_t v___x_4958_; 
v___x_4957_ = lean_nat_sub(v___x_4955_, v___y_4952_);
v___x_4958_ = lean_nat_dec_le(v___x_4911_, v___x_4957_);
if (v___x_4958_ == 0)
{
lean_inc(v___x_4957_);
v___y_4945_ = v___y_4954_;
v___y_4946_ = v___x_4957_;
v___y_4947_ = v___x_4955_;
v___y_4948_ = v___y_4953_;
v___y_4949_ = v___x_4957_;
goto v___jp_4944_;
}
else
{
v___y_4945_ = v___y_4954_;
v___y_4946_ = v___x_4957_;
v___y_4947_ = v___x_4955_;
v___y_4948_ = v___y_4953_;
v___y_4949_ = v___x_4911_;
goto v___jp_4944_;
}
}
else
{
v___y_4915_ = v___y_4953_;
v___y_4916_ = v___y_4954_;
goto v___jp_4914_;
}
}
}
else
{
lean_dec_ref(v_allowed_4902_);
lean_dec_ref(v_s0_4901_);
return v___x_4909_;
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_search___boxed(lean_object* v_title_5020_, lean_object* v_cfg_5021_, lean_object* v_s0_5022_, lean_object* v_allowed_5023_, lean_object* v_top_5024_, lean_object* v_a_5025_){
_start:
{
lean_object* v_res_5026_; 
v_res_5026_ = l_Legal_USTax_Hunt_Basis_search(v_title_5020_, v_cfg_5021_, v_s0_5022_, v_allowed_5023_, v_top_5024_);
lean_dec(v_top_5024_);
lean_dec_ref(v_cfg_5021_);
lean_dec_ref(v_title_5020_);
return v_res_5026_;
}
}
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1(lean_object* v_as_5027_, lean_object* v_as_x27_5028_, lean_object* v_b_5029_, lean_object* v_a_5030_){
_start:
{
lean_object* v___x_5032_; 
v___x_5032_ = l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___redArg(v_as_x27_5028_, v_b_5029_);
return v___x_5032_;
}
}
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1___boxed(lean_object* v_as_5033_, lean_object* v_as_x27_5034_, lean_object* v_b_5035_, lean_object* v_a_5036_, lean_object* v___y_5037_){
_start:
{
lean_object* v_res_5038_; 
v_res_5038_ = l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__1(v_as_5033_, v_as_x27_5034_, v_b_5035_, v_a_5036_);
lean_dec(v_as_x27_5034_);
lean_dec(v_as_5033_);
return v_res_5038_;
}
}
LEAN_EXPORT uint8_t l_Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2(lean_object* v_00_u03b2_5039_, lean_object* v_m_5040_, lean_object* v_a_5041_){
_start:
{
uint8_t v___x_5042_; 
v___x_5042_ = l_Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2___redArg(v_m_5040_, v_a_5041_);
return v___x_5042_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2___boxed(lean_object* v_00_u03b2_5043_, lean_object* v_m_5044_, lean_object* v_a_5045_){
_start:
{
uint8_t v_res_5046_; lean_object* v_r_5047_; 
v_res_5046_ = l_Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2(v_00_u03b2_5043_, v_m_5044_, v_a_5045_);
lean_dec_ref(v_a_5045_);
lean_dec_ref(v_m_5044_);
v_r_5047_ = lean_box(v_res_5046_);
return v_r_5047_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3(lean_object* v_00_u03b2_5048_, lean_object* v_m_5049_, lean_object* v_a_5050_, lean_object* v_b_5051_){
_start:
{
lean_object* v___x_5052_; 
v___x_5052_ = l_Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3___redArg(v_m_5049_, v_a_5050_, v_b_5051_);
return v___x_5052_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4(lean_object* v_00_u03b2_5053_, lean_object* v_m_5054_, lean_object* v_a_5055_, lean_object* v_b_5056_){
_start:
{
lean_object* v___x_5057_; 
v___x_5057_ = l_Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4___redArg(v_m_5054_, v_a_5055_, v_b_5056_);
return v___x_5057_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5(lean_object* v_00_u03b2_5058_, lean_object* v_m_5059_, lean_object* v_a_5060_){
_start:
{
lean_object* v___x_5061_; 
v___x_5061_ = l_Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5___redArg(v_m_5059_, v_a_5060_);
return v___x_5061_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5___boxed(lean_object* v_00_u03b2_5062_, lean_object* v_m_5063_, lean_object* v_a_5064_){
_start:
{
lean_object* v_res_5065_; 
v_res_5065_ = l_Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5(v_00_u03b2_5062_, v_m_5063_, v_a_5064_);
lean_dec_ref(v_a_5064_);
lean_dec_ref(v_m_5063_);
return v_res_5065_;
}
}
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__6(lean_object* v_allowed_5066_, lean_object* v_cfg_5067_, lean_object* v_fst_5068_, lean_object* v_snd_5069_, lean_object* v_fst_5070_, lean_object* v_fst_5071_, lean_object* v_as_5072_, lean_object* v_as_x27_5073_, lean_object* v_b_5074_, lean_object* v_a_5075_){
_start:
{
lean_object* v___x_5077_; 
v___x_5077_ = l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__6___redArg(v_allowed_5066_, v_cfg_5067_, v_fst_5068_, v_snd_5069_, v_fst_5070_, v_fst_5071_, v_as_x27_5073_, v_b_5074_);
return v___x_5077_;
}
}
LEAN_EXPORT lean_object* l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__6___boxed(lean_object* v_allowed_5078_, lean_object* v_cfg_5079_, lean_object* v_fst_5080_, lean_object* v_snd_5081_, lean_object* v_fst_5082_, lean_object* v_fst_5083_, lean_object* v_as_5084_, lean_object* v_as_x27_5085_, lean_object* v_b_5086_, lean_object* v_a_5087_, lean_object* v___y_5088_){
_start:
{
lean_object* v_res_5089_; 
v_res_5089_ = l_List_forIn_x27_loop___at___00Legal_USTax_Hunt_Basis_search_spec__6(v_allowed_5078_, v_cfg_5079_, v_fst_5080_, v_snd_5081_, v_fst_5082_, v_fst_5083_, v_as_5084_, v_as_x27_5085_, v_b_5086_, v_a_5087_);
lean_dec(v_as_x27_5085_);
lean_dec(v_as_5084_);
lean_dec(v_snd_5081_);
lean_dec_ref(v_cfg_5079_);
return v_res_5089_;
}
}
LEAN_EXPORT lean_object* l___private_Init_While_0__repeatM_erased___at___00Legal_USTax_Hunt_Basis_search_spec__8(lean_object* v_allowed_5090_, lean_object* v_cfg_5091_, lean_object* v_inst_5092_, lean_object* v_a_5093_){
_start:
{
lean_object* v___x_5095_; 
v___x_5095_ = l___private_Init_While_0__repeatM_erased___at___00Legal_USTax_Hunt_Basis_search_spec__8___redArg(v_allowed_5090_, v_cfg_5091_, v_a_5093_);
return v___x_5095_;
}
}
LEAN_EXPORT lean_object* l___private_Init_While_0__repeatM_erased___at___00Legal_USTax_Hunt_Basis_search_spec__8___boxed(lean_object* v_allowed_5096_, lean_object* v_cfg_5097_, lean_object* v_inst_5098_, lean_object* v_a_5099_, lean_object* v___y_5100_){
_start:
{
lean_object* v_res_5101_; 
v_res_5101_ = l___private_Init_While_0__repeatM_erased___at___00Legal_USTax_Hunt_Basis_search_spec__8(v_allowed_5096_, v_cfg_5097_, v_inst_5098_, v_a_5099_);
lean_dec_ref(v_cfg_5097_);
return v_res_5101_;
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11(lean_object* v_n_5102_, lean_object* v_as_5103_, lean_object* v_lo_5104_, lean_object* v_hi_5105_, lean_object* v_w_5106_, lean_object* v_hlo_5107_, lean_object* v_hhi_5108_){
_start:
{
lean_object* v___x_5109_; 
v___x_5109_ = l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11___redArg(v_n_5102_, v_as_5103_, v_lo_5104_, v_hi_5105_);
return v___x_5109_;
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11___boxed(lean_object* v_n_5110_, lean_object* v_as_5111_, lean_object* v_lo_5112_, lean_object* v_hi_5113_, lean_object* v_w_5114_, lean_object* v_hlo_5115_, lean_object* v_hhi_5116_){
_start:
{
lean_object* v_res_5117_; 
v_res_5117_ = l___private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11(v_n_5110_, v_as_5111_, v_lo_5112_, v_hi_5113_, v_w_5114_, v_hlo_5115_, v_hhi_5116_);
lean_dec(v_hi_5113_);
lean_dec(v_n_5110_);
return v_res_5117_;
}
}
LEAN_EXPORT uint8_t l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2_spec__3(lean_object* v_00_u03b2_5118_, lean_object* v_a_5119_, lean_object* v_x_5120_){
_start:
{
uint8_t v___x_5121_; 
v___x_5121_ = l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2_spec__3___redArg(v_a_5119_, v_x_5120_);
return v___x_5121_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2_spec__3___boxed(lean_object* v_00_u03b2_5122_, lean_object* v_a_5123_, lean_object* v_x_5124_){
_start:
{
uint8_t v_res_5125_; lean_object* v_r_5126_; 
v_res_5125_ = l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_contains___at___00Legal_USTax_Hunt_Basis_search_spec__2_spec__3(v_00_u03b2_5122_, v_a_5123_, v_x_5124_);
lean_dec(v_x_5124_);
lean_dec_ref(v_a_5123_);
v_r_5126_ = lean_box(v_res_5125_);
return v_r_5126_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3_spec__5(lean_object* v_00_u03b2_5127_, lean_object* v_data_5128_){
_start:
{
lean_object* v___x_5129_; 
v___x_5129_ = l_Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3_spec__5___redArg(v_data_5128_);
return v___x_5129_;
}
}
LEAN_EXPORT uint8_t l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__7(lean_object* v_00_u03b2_5130_, lean_object* v_a_5131_, lean_object* v_x_5132_){
_start:
{
uint8_t v___x_5133_; 
v___x_5133_ = l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__7___redArg(v_a_5131_, v_x_5132_);
return v___x_5133_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__7___boxed(lean_object* v_00_u03b2_5134_, lean_object* v_a_5135_, lean_object* v_x_5136_){
_start:
{
uint8_t v_res_5137_; lean_object* v_r_5138_; 
v_res_5137_ = l_Std_DHashMap_Internal_AssocList_contains___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__7(v_00_u03b2_5134_, v_a_5135_, v_x_5136_);
lean_dec(v_x_5136_);
lean_dec_ref(v_a_5135_);
v_r_5138_ = lean_box(v_res_5137_);
return v_r_5138_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__8(lean_object* v_00_u03b2_5139_, lean_object* v_data_5140_){
_start:
{
lean_object* v___x_5141_; 
v___x_5141_ = l_Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__8___redArg(v_data_5140_);
return v___x_5141_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_replace___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__9(lean_object* v_00_u03b2_5142_, lean_object* v_a_5143_, lean_object* v_b_5144_, lean_object* v_x_5145_){
_start:
{
lean_object* v___x_5146_; 
v___x_5146_ = l_Std_DHashMap_Internal_AssocList_replace___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__9___redArg(v_a_5143_, v_b_5144_, v_x_5145_);
return v___x_5146_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_get_x3f___at___00Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5_spec__11(lean_object* v_00_u03b2_5147_, lean_object* v_a_5148_, lean_object* v_x_5149_){
_start:
{
lean_object* v___x_5150_; 
v___x_5150_ = l_Std_DHashMap_Internal_AssocList_get_x3f___at___00Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5_spec__11___redArg(v_a_5148_, v_x_5149_);
return v___x_5150_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_get_x3f___at___00Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5_spec__11___boxed(lean_object* v_00_u03b2_5151_, lean_object* v_a_5152_, lean_object* v_x_5153_){
_start:
{
lean_object* v_res_5154_; 
v_res_5154_ = l_Std_DHashMap_Internal_AssocList_get_x3f___at___00Std_DHashMap_Internal_Raw_u2080_Const_get_x3f___at___00Legal_USTax_Hunt_Basis_search_spec__5_spec__11(v_00_u03b2_5151_, v_a_5152_, v_x_5153_);
lean_dec(v_x_5153_);
lean_dec_ref(v_a_5152_);
return v_res_5154_;
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Array_QSort_Basic_0__Array_qpartition_loop___at___00__private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11_spec__19(lean_object* v_n_5155_, lean_object* v_lo_5156_, lean_object* v_hi_5157_, lean_object* v_hhi_5158_, lean_object* v_pivot_5159_, lean_object* v_as_5160_, lean_object* v_i_5161_, lean_object* v_k_5162_, lean_object* v_ilo_5163_, lean_object* v_ik_5164_, lean_object* v_w_5165_){
_start:
{
lean_object* v___x_5166_; 
v___x_5166_ = l___private_Init_Data_Array_QSort_Basic_0__Array_qpartition_loop___at___00__private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11_spec__19___redArg(v_hi_5157_, v_pivot_5159_, v_as_5160_, v_i_5161_, v_k_5162_);
return v___x_5166_;
}
}
LEAN_EXPORT lean_object* l___private_Init_Data_Array_QSort_Basic_0__Array_qpartition_loop___at___00__private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11_spec__19___boxed(lean_object* v_n_5167_, lean_object* v_lo_5168_, lean_object* v_hi_5169_, lean_object* v_hhi_5170_, lean_object* v_pivot_5171_, lean_object* v_as_5172_, lean_object* v_i_5173_, lean_object* v_k_5174_, lean_object* v_ilo_5175_, lean_object* v_ik_5176_, lean_object* v_w_5177_){
_start:
{
lean_object* v_res_5178_; 
v_res_5178_ = l___private_Init_Data_Array_QSort_Basic_0__Array_qpartition_loop___at___00__private_Init_Data_Array_QSort_Basic_0__Array_qsort_sort___at___00Legal_USTax_Hunt_Basis_search_spec__11_spec__19(v_n_5167_, v_lo_5168_, v_hi_5169_, v_hhi_5170_, v_pivot_5171_, v_as_5172_, v_i_5173_, v_k_5174_, v_ilo_5175_, v_ik_5176_, v_w_5177_);
lean_dec_ref(v_pivot_5171_);
lean_dec(v_hi_5169_);
lean_dec(v_lo_5168_);
lean_dec(v_n_5167_);
return v_res_5178_;
}
}
LEAN_EXPORT lean_object* l___private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3_spec__5_spec__6(lean_object* v_00_u03b2_5179_, lean_object* v_i_5180_, lean_object* v_source_5181_, lean_object* v_target_5182_){
_start:
{
lean_object* v___x_5183_; 
v___x_5183_ = l___private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3_spec__5_spec__6___redArg(v_i_5180_, v_source_5181_, v_target_5182_);
return v___x_5183_;
}
}
LEAN_EXPORT lean_object* l___private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__8_spec__10(lean_object* v_00_u03b2_5184_, lean_object* v_i_5185_, lean_object* v_source_5186_, lean_object* v_target_5187_){
_start:
{
lean_object* v___x_5188_; 
v___x_5188_ = l___private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__8_spec__10___redArg(v_i_5185_, v_source_5186_, v_target_5187_);
return v___x_5188_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_foldlM___at___00__private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3_spec__5_spec__6_spec__17(lean_object* v_00_u03b2_5189_, lean_object* v_x_5190_, lean_object* v_x_5191_){
_start:
{
lean_object* v___x_5192_; 
v___x_5192_ = l_Std_DHashMap_Internal_AssocList_foldlM___at___00__private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insertIfNew___at___00Legal_USTax_Hunt_Basis_search_spec__3_spec__5_spec__6_spec__17___redArg(v_x_5190_, v_x_5191_);
return v___x_5192_;
}
}
LEAN_EXPORT lean_object* l_Std_DHashMap_Internal_AssocList_foldlM___at___00__private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__8_spec__10_spec__21(lean_object* v_00_u03b2_5193_, lean_object* v_x_5194_, lean_object* v_x_5195_){
_start:
{
lean_object* v___x_5196_; 
v___x_5196_ = l_Std_DHashMap_Internal_AssocList_foldlM___at___00__private_Std_Data_DHashMap_Internal_Defs_0__Std_DHashMap_Internal_Raw_u2080_expand_go___at___00Std_DHashMap_Internal_Raw_u2080_expand___at___00Std_DHashMap_Internal_Raw_u2080_insert___at___00Legal_USTax_Hunt_Basis_search_spec__4_spec__8_spec__10_spec__21___redArg(v_x_5194_, v_x_5195_);
return v___x_5196_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_lot(uint8_t v_k_5197_, uint8_t v_o_5198_, lean_object* v_fmv_5199_, lean_object* v_basis_5200_, lean_object* v_held_5201_){
_start:
{
lean_object* v___y_5203_; uint8_t v___x_5209_; uint8_t v___x_5210_; 
v___x_5209_ = 2;
v___x_5210_ = l_Legal_USTax_Hunt_Basis_instBEqKind_beq(v_k_5197_, v___x_5209_);
if (v___x_5210_ == 0)
{
lean_object* v___x_5211_; 
v___x_5211_ = lean_unsigned_to_nat(0u);
v___y_5203_ = v___x_5211_;
goto v___jp_5202_;
}
else
{
lean_object* v___x_5212_; 
v___x_5212_ = lean_unsigned_to_nat(2u);
v___y_5203_ = v___x_5212_;
goto v___jp_5202_;
}
v___jp_5202_:
{
lean_object* v___x_5204_; lean_object* v___x_5205_; lean_object* v___x_5206_; uint8_t v___x_5207_; lean_object* v___x_5208_; 
v___x_5204_ = lean_unsigned_to_nat(0u);
v___x_5205_ = lean_box(0);
v___x_5206_ = lean_unsigned_to_nat(1u);
v___x_5207_ = 0;
lean_inc(v_basis_5200_);
v___x_5208_ = lean_alloc_ctor(0, 8, 4);
lean_ctor_set(v___x_5208_, 0, v_fmv_5199_);
lean_ctor_set(v___x_5208_, 1, v_basis_5200_);
lean_ctor_set(v___x_5208_, 2, v_basis_5200_);
lean_ctor_set(v___x_5208_, 3, v_held_5201_);
lean_ctor_set(v___x_5208_, 4, v___y_5203_);
lean_ctor_set(v___x_5208_, 5, v___x_5204_);
lean_ctor_set(v___x_5208_, 6, v___x_5205_);
lean_ctor_set(v___x_5208_, 7, v___x_5206_);
lean_ctor_set_uint8(v___x_5208_, sizeof(void*)*8, v_k_5197_);
lean_ctor_set_uint8(v___x_5208_, sizeof(void*)*8 + 1, v_o_5198_);
lean_ctor_set_uint8(v___x_5208_, sizeof(void*)*8 + 2, v___x_5207_);
lean_ctor_set_uint8(v___x_5208_, sizeof(void*)*8 + 3, v___x_5207_);
return v___x_5208_;
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_lot___boxed(lean_object* v_k_5213_, lean_object* v_o_5214_, lean_object* v_fmv_5215_, lean_object* v_basis_5216_, lean_object* v_held_5217_){
_start:
{
uint8_t v_k_boxed_5218_; uint8_t v_o_boxed_5219_; lean_object* v_res_5220_; 
v_k_boxed_5218_ = lean_unbox(v_k_5213_);
v_o_boxed_5219_ = lean_unbox(v_o_5214_);
v_res_5220_ = l_Legal_USTax_Hunt_Basis_lot(v_k_boxed_5218_, v_o_boxed_5219_, v_fmv_5215_, v_basis_5216_, v_held_5217_);
return v_res_5220_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_mk(lean_object* v_lots_5221_, lean_object* v_pledge_5222_, lean_object* v_rP_5223_){
_start:
{
lean_object* v___x_5224_; uint8_t v___x_5225_; uint8_t v___x_5226_; lean_object* v___x_5227_; lean_object* v___x_5228_; 
v___x_5224_ = lean_unsigned_to_nat(0u);
v___x_5225_ = 1;
v___x_5226_ = 0;
v___x_5227_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0, &l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0);
v___x_5228_ = lean_alloc_ctor(0, 12, 2);
lean_ctor_set(v___x_5228_, 0, v_lots_5221_);
lean_ctor_set(v___x_5228_, 1, v___x_5224_);
lean_ctor_set(v___x_5228_, 2, v___x_5224_);
lean_ctor_set(v___x_5228_, 3, v___x_5227_);
lean_ctor_set(v___x_5228_, 4, v___x_5227_);
lean_ctor_set(v___x_5228_, 5, v___x_5227_);
lean_ctor_set(v___x_5228_, 6, v_rP_5223_);
lean_ctor_set(v___x_5228_, 7, v___x_5224_);
lean_ctor_set(v___x_5228_, 8, v___x_5224_);
lean_ctor_set(v___x_5228_, 9, v___x_5224_);
lean_ctor_set(v___x_5228_, 10, v_pledge_5222_);
lean_ctor_set(v___x_5228_, 11, v___x_5224_);
lean_ctor_set_uint8(v___x_5228_, sizeof(void*)*12, v___x_5225_);
lean_ctor_set_uint8(v___x_5228_, sizeof(void*)*12 + 1, v___x_5226_);
return v___x_5228_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc1___closed__0(void){
_start:
{
lean_object* v___x_5250_; lean_object* v___x_5251_; lean_object* v___x_5252_; uint8_t v___x_5253_; uint8_t v___x_5254_; lean_object* v___x_5255_; 
v___x_5250_ = lean_unsigned_to_nat(3u);
v___x_5251_ = lean_unsigned_to_nat(6000u);
v___x_5252_ = lean_unsigned_to_nat(30000u);
v___x_5253_ = 0;
v___x_5254_ = 0;
v___x_5255_ = l_Legal_USTax_Hunt_Basis_lot(v___x_5254_, v___x_5253_, v___x_5252_, v___x_5251_, v___x_5250_);
return v___x_5255_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc1___closed__1(void){
_start:
{
lean_object* v___x_5256_; lean_object* v___x_5257_; lean_object* v___x_5258_; uint8_t v___x_5259_; uint8_t v___x_5260_; lean_object* v___x_5261_; 
v___x_5256_ = lean_unsigned_to_nat(0u);
v___x_5257_ = lean_unsigned_to_nat(10000u);
v___x_5258_ = lean_unsigned_to_nat(30000u);
v___x_5259_ = 0;
v___x_5260_ = 0;
v___x_5261_ = l_Legal_USTax_Hunt_Basis_lot(v___x_5260_, v___x_5259_, v___x_5258_, v___x_5257_, v___x_5256_);
return v___x_5261_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc1___closed__2(void){
_start:
{
lean_object* v___x_5262_; lean_object* v___x_5263_; lean_object* v___x_5264_; uint8_t v___x_5265_; uint8_t v___x_5266_; lean_object* v___x_5267_; 
v___x_5262_ = lean_unsigned_to_nat(3u);
v___x_5263_ = lean_unsigned_to_nat(50000u);
v___x_5264_ = lean_unsigned_to_nat(20000u);
v___x_5265_ = 0;
v___x_5266_ = 0;
v___x_5267_ = l_Legal_USTax_Hunt_Basis_lot(v___x_5266_, v___x_5265_, v___x_5264_, v___x_5263_, v___x_5262_);
return v___x_5267_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc1___closed__3(void){
_start:
{
lean_object* v___x_5268_; lean_object* v___x_5269_; lean_object* v___x_5270_; 
v___x_5268_ = lean_box(0);
v___x_5269_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc1___closed__2, &l_Legal_USTax_Hunt_Basis_sc1___closed__2_once, _init_l_Legal_USTax_Hunt_Basis_sc1___closed__2);
v___x_5270_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_5270_, 0, v___x_5269_);
lean_ctor_set(v___x_5270_, 1, v___x_5268_);
return v___x_5270_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc1___closed__4(void){
_start:
{
lean_object* v___x_5271_; lean_object* v___x_5272_; lean_object* v___x_5273_; 
v___x_5271_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc1___closed__3, &l_Legal_USTax_Hunt_Basis_sc1___closed__3_once, _init_l_Legal_USTax_Hunt_Basis_sc1___closed__3);
v___x_5272_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc1___closed__1, &l_Legal_USTax_Hunt_Basis_sc1___closed__1_once, _init_l_Legal_USTax_Hunt_Basis_sc1___closed__1);
v___x_5273_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_5273_, 0, v___x_5272_);
lean_ctor_set(v___x_5273_, 1, v___x_5271_);
return v___x_5273_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc1___closed__5(void){
_start:
{
lean_object* v___x_5274_; lean_object* v___x_5275_; lean_object* v___x_5276_; 
v___x_5274_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc1___closed__4, &l_Legal_USTax_Hunt_Basis_sc1___closed__4_once, _init_l_Legal_USTax_Hunt_Basis_sc1___closed__4);
v___x_5275_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc1___closed__0, &l_Legal_USTax_Hunt_Basis_sc1___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_sc1___closed__0);
v___x_5276_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_5276_, 0, v___x_5275_);
lean_ctor_set(v___x_5276_, 1, v___x_5274_);
return v___x_5276_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc1___closed__6(void){
_start:
{
lean_object* v___x_5277_; lean_object* v___x_5278_; lean_object* v___x_5279_; lean_object* v___x_5280_; 
v___x_5277_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0, &l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0);
v___x_5278_ = lean_unsigned_to_nat(30000u);
v___x_5279_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc1___closed__5, &l_Legal_USTax_Hunt_Basis_sc1___closed__5_once, _init_l_Legal_USTax_Hunt_Basis_sc1___closed__5);
v___x_5280_ = l_Legal_USTax_Hunt_Basis_mk(v___x_5279_, v___x_5278_, v___x_5277_);
return v___x_5280_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc1(void){
_start:
{
lean_object* v___x_5281_; 
v___x_5281_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc1___closed__6, &l_Legal_USTax_Hunt_Basis_sc1___closed__6_once, _init_l_Legal_USTax_Hunt_Basis_sc1___closed__6);
return v___x_5281_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc2___closed__0(void){
_start:
{
lean_object* v___x_5282_; lean_object* v___x_5283_; lean_object* v___x_5284_; uint8_t v___x_5285_; uint8_t v___x_5286_; lean_object* v___x_5287_; 
v___x_5282_ = lean_unsigned_to_nat(3u);
v___x_5283_ = lean_unsigned_to_nat(10000u);
v___x_5284_ = lean_unsigned_to_nat(60000u);
v___x_5285_ = 0;
v___x_5286_ = 0;
v___x_5287_ = l_Legal_USTax_Hunt_Basis_lot(v___x_5286_, v___x_5285_, v___x_5284_, v___x_5283_, v___x_5282_);
return v___x_5287_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc2___closed__1(void){
_start:
{
lean_object* v___x_5288_; lean_object* v___x_5289_; lean_object* v___x_5290_; uint8_t v___x_5291_; uint8_t v___x_5292_; lean_object* v___x_5293_; 
v___x_5288_ = lean_unsigned_to_nat(3u);
v___x_5289_ = lean_unsigned_to_nat(10000u);
v___x_5290_ = lean_unsigned_to_nat(60000u);
v___x_5291_ = 4;
v___x_5292_ = 0;
v___x_5293_ = l_Legal_USTax_Hunt_Basis_lot(v___x_5292_, v___x_5291_, v___x_5290_, v___x_5289_, v___x_5288_);
return v___x_5293_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc2___closed__2(void){
_start:
{
lean_object* v___x_5294_; lean_object* v___x_5295_; lean_object* v___x_5296_; uint8_t v___x_5297_; uint8_t v___x_5298_; lean_object* v___x_5299_; 
v___x_5294_ = lean_unsigned_to_nat(3u);
v___x_5295_ = lean_unsigned_to_nat(60000u);
v___x_5296_ = lean_unsigned_to_nat(20000u);
v___x_5297_ = 4;
v___x_5298_ = 0;
v___x_5299_ = l_Legal_USTax_Hunt_Basis_lot(v___x_5298_, v___x_5297_, v___x_5296_, v___x_5295_, v___x_5294_);
return v___x_5299_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc2___closed__3(void){
_start:
{
lean_object* v___x_5300_; lean_object* v___x_5301_; lean_object* v___x_5302_; 
v___x_5300_ = lean_box(0);
v___x_5301_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc2___closed__2, &l_Legal_USTax_Hunt_Basis_sc2___closed__2_once, _init_l_Legal_USTax_Hunt_Basis_sc2___closed__2);
v___x_5302_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_5302_, 0, v___x_5301_);
lean_ctor_set(v___x_5302_, 1, v___x_5300_);
return v___x_5302_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc2___closed__4(void){
_start:
{
lean_object* v___x_5303_; lean_object* v___x_5304_; lean_object* v___x_5305_; 
v___x_5303_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc2___closed__3, &l_Legal_USTax_Hunt_Basis_sc2___closed__3_once, _init_l_Legal_USTax_Hunt_Basis_sc2___closed__3);
v___x_5304_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc2___closed__1, &l_Legal_USTax_Hunt_Basis_sc2___closed__1_once, _init_l_Legal_USTax_Hunt_Basis_sc2___closed__1);
v___x_5305_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_5305_, 0, v___x_5304_);
lean_ctor_set(v___x_5305_, 1, v___x_5303_);
return v___x_5305_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc2___closed__5(void){
_start:
{
lean_object* v___x_5306_; lean_object* v___x_5307_; lean_object* v___x_5308_; 
v___x_5306_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc2___closed__4, &l_Legal_USTax_Hunt_Basis_sc2___closed__4_once, _init_l_Legal_USTax_Hunt_Basis_sc2___closed__4);
v___x_5307_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc2___closed__0, &l_Legal_USTax_Hunt_Basis_sc2___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_sc2___closed__0);
v___x_5308_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_5308_, 0, v___x_5307_);
lean_ctor_set(v___x_5308_, 1, v___x_5306_);
return v___x_5308_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc2___closed__6(void){
_start:
{
lean_object* v___x_5309_; lean_object* v___x_5310_; lean_object* v___x_5311_; lean_object* v___x_5312_; 
v___x_5309_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0, &l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0);
v___x_5310_ = lean_unsigned_to_nat(0u);
v___x_5311_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc2___closed__5, &l_Legal_USTax_Hunt_Basis_sc2___closed__5_once, _init_l_Legal_USTax_Hunt_Basis_sc2___closed__5);
v___x_5312_ = l_Legal_USTax_Hunt_Basis_mk(v___x_5311_, v___x_5310_, v___x_5309_);
return v___x_5312_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc2(void){
_start:
{
lean_object* v___x_5313_; 
v___x_5313_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc2___closed__6, &l_Legal_USTax_Hunt_Basis_sc2___closed__6_once, _init_l_Legal_USTax_Hunt_Basis_sc2___closed__6);
return v___x_5313_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc3___closed__0(void){
_start:
{
lean_object* v___x_5314_; lean_object* v___x_5315_; lean_object* v___x_5316_; 
v___x_5314_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc1___closed__3, &l_Legal_USTax_Hunt_Basis_sc1___closed__3_once, _init_l_Legal_USTax_Hunt_Basis_sc1___closed__3);
v___x_5315_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc1___closed__0, &l_Legal_USTax_Hunt_Basis_sc1___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_sc1___closed__0);
v___x_5316_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_5316_, 0, v___x_5315_);
lean_ctor_set(v___x_5316_, 1, v___x_5314_);
return v___x_5316_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc3___closed__1(void){
_start:
{
lean_object* v___x_5317_; lean_object* v___x_5318_; lean_object* v___x_5319_; lean_object* v___x_5320_; 
v___x_5317_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0, &l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0);
v___x_5318_ = lean_unsigned_to_nat(0u);
v___x_5319_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc3___closed__0, &l_Legal_USTax_Hunt_Basis_sc3___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_sc3___closed__0);
v___x_5320_ = l_Legal_USTax_Hunt_Basis_mk(v___x_5319_, v___x_5318_, v___x_5317_);
return v___x_5320_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc3(void){
_start:
{
lean_object* v___x_5321_; 
v___x_5321_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc3___closed__1, &l_Legal_USTax_Hunt_Basis_sc3___closed__1_once, _init_l_Legal_USTax_Hunt_Basis_sc3___closed__1);
return v___x_5321_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc4___closed__0(void){
_start:
{
lean_object* v___x_5322_; lean_object* v___x_5323_; lean_object* v___x_5324_; uint8_t v___x_5325_; uint8_t v___x_5326_; lean_object* v___x_5327_; 
v___x_5322_ = lean_unsigned_to_nat(2u);
v___x_5323_ = lean_unsigned_to_nat(0u);
v___x_5324_ = lean_unsigned_to_nat(12000000u);
v___x_5325_ = 0;
v___x_5326_ = 1;
v___x_5327_ = l_Legal_USTax_Hunt_Basis_lot(v___x_5326_, v___x_5325_, v___x_5324_, v___x_5323_, v___x_5322_);
return v___x_5327_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_sc4(lean_object* v_n_5328_){
_start:
{
lean_object* v___x_5329_; lean_object* v___x_5330_; lean_object* v___x_5331_; lean_object* v___x_5332_; lean_object* v___x_5333_; 
v___x_5329_ = lean_unsigned_to_nat(0u);
v___x_5330_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc4___closed__0, &l_Legal_USTax_Hunt_Basis_sc4___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_sc4___closed__0);
v___x_5331_ = l_List_replicateTR___redArg(v_n_5328_, v___x_5330_);
v___x_5332_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0, &l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0);
v___x_5333_ = l_Legal_USTax_Hunt_Basis_mk(v___x_5331_, v___x_5329_, v___x_5332_);
return v___x_5333_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc5___closed__0(void){
_start:
{
lean_object* v___x_5334_; lean_object* v___x_5335_; lean_object* v___x_5336_; uint8_t v___x_5337_; uint8_t v___x_5338_; lean_object* v___x_5339_; 
v___x_5334_ = lean_unsigned_to_nat(3u);
v___x_5335_ = lean_unsigned_to_nat(100000u);
v___x_5336_ = lean_unsigned_to_nat(500000u);
v___x_5337_ = 0;
v___x_5338_ = 2;
v___x_5339_ = l_Legal_USTax_Hunt_Basis_lot(v___x_5338_, v___x_5337_, v___x_5336_, v___x_5335_, v___x_5334_);
return v___x_5339_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_sc5(lean_object* v_n_5340_){
_start:
{
lean_object* v___x_5341_; lean_object* v___x_5342_; lean_object* v___x_5343_; lean_object* v___x_5344_; lean_object* v___x_5345_; 
v___x_5341_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc5___closed__0, &l_Legal_USTax_Hunt_Basis_sc5___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_sc5___closed__0);
v___x_5342_ = l_List_replicateTR___redArg(v_n_5340_, v___x_5341_);
v___x_5343_ = lean_unsigned_to_nat(0u);
v___x_5344_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0, &l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0);
v___x_5345_ = l_Legal_USTax_Hunt_Basis_mk(v___x_5342_, v___x_5343_, v___x_5344_);
return v___x_5345_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc6___closed__0(void){
_start:
{
lean_object* v___x_5346_; lean_object* v___x_5347_; lean_object* v___x_5348_; 
v___x_5346_ = lean_box(0);
v___x_5347_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc2___closed__1, &l_Legal_USTax_Hunt_Basis_sc2___closed__1_once, _init_l_Legal_USTax_Hunt_Basis_sc2___closed__1);
v___x_5348_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_5348_, 0, v___x_5347_);
lean_ctor_set(v___x_5348_, 1, v___x_5346_);
return v___x_5348_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc6___closed__1(void){
_start:
{
lean_object* v___x_5349_; lean_object* v___x_5350_; lean_object* v___x_5351_; 
v___x_5349_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc6___closed__0, &l_Legal_USTax_Hunt_Basis_sc6___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_sc6___closed__0);
v___x_5350_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc1___closed__2, &l_Legal_USTax_Hunt_Basis_sc1___closed__2_once, _init_l_Legal_USTax_Hunt_Basis_sc1___closed__2);
v___x_5351_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_5351_, 0, v___x_5350_);
lean_ctor_set(v___x_5351_, 1, v___x_5349_);
return v___x_5351_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc6___closed__2(void){
_start:
{
lean_object* v___x_5352_; lean_object* v___x_5353_; lean_object* v___x_5354_; 
v___x_5352_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc6___closed__1, &l_Legal_USTax_Hunt_Basis_sc6___closed__1_once, _init_l_Legal_USTax_Hunt_Basis_sc6___closed__1);
v___x_5353_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc1___closed__1, &l_Legal_USTax_Hunt_Basis_sc1___closed__1_once, _init_l_Legal_USTax_Hunt_Basis_sc1___closed__1);
v___x_5354_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_5354_, 0, v___x_5353_);
lean_ctor_set(v___x_5354_, 1, v___x_5352_);
return v___x_5354_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc6___closed__3(void){
_start:
{
lean_object* v___x_5355_; lean_object* v___x_5356_; lean_object* v___x_5357_; 
v___x_5355_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc6___closed__2, &l_Legal_USTax_Hunt_Basis_sc6___closed__2_once, _init_l_Legal_USTax_Hunt_Basis_sc6___closed__2);
v___x_5356_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc2___closed__0, &l_Legal_USTax_Hunt_Basis_sc2___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_sc2___closed__0);
v___x_5357_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_5357_, 0, v___x_5356_);
lean_ctor_set(v___x_5357_, 1, v___x_5355_);
return v___x_5357_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc6___closed__4(void){
_start:
{
lean_object* v___x_5358_; lean_object* v___x_5359_; lean_object* v___x_5360_; lean_object* v___x_5361_; 
v___x_5358_ = lean_unsigned_to_nat(40000u);
v___x_5359_ = lean_unsigned_to_nat(0u);
v___x_5360_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0, &l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_instHashableRet_hash___closed__0);
v___x_5361_ = lean_alloc_ctor(0, 7, 0);
lean_ctor_set(v___x_5361_, 0, v___x_5360_);
lean_ctor_set(v___x_5361_, 1, v___x_5360_);
lean_ctor_set(v___x_5361_, 2, v___x_5359_);
lean_ctor_set(v___x_5361_, 3, v___x_5359_);
lean_ctor_set(v___x_5361_, 4, v___x_5358_);
lean_ctor_set(v___x_5361_, 5, v___x_5359_);
lean_ctor_set(v___x_5361_, 6, v___x_5359_);
return v___x_5361_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc6___closed__5(void){
_start:
{
lean_object* v___x_5362_; lean_object* v___x_5363_; lean_object* v___x_5364_; lean_object* v___x_5365_; 
v___x_5362_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc6___closed__4, &l_Legal_USTax_Hunt_Basis_sc6___closed__4_once, _init_l_Legal_USTax_Hunt_Basis_sc6___closed__4);
v___x_5363_ = lean_unsigned_to_nat(30000u);
v___x_5364_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc6___closed__3, &l_Legal_USTax_Hunt_Basis_sc6___closed__3_once, _init_l_Legal_USTax_Hunt_Basis_sc6___closed__3);
v___x_5365_ = l_Legal_USTax_Hunt_Basis_mk(v___x_5364_, v___x_5363_, v___x_5362_);
return v___x_5365_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_sc6(void){
_start:
{
lean_object* v___x_5366_; 
v___x_5366_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc6___closed__5, &l_Legal_USTax_Hunt_Basis_sc6___closed__5_once, _init_l_Legal_USTax_Hunt_Basis_sc6___closed__5);
return v___x_5366_;
}
}
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_all___redArg(){
_start:
{
uint8_t v___x_5368_; 
v___x_5368_ = 1;
return v___x_5368_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_all___redArg___boxed(lean_object* v___dummy_5369_){
_start:
{
uint8_t v_res_5370_; lean_object* v_r_5371_; 
v_res_5370_ = l_Legal_USTax_Hunt_Basis_all___redArg();
v_r_5371_ = lean_box(v_res_5370_);
return v_r_5371_;
}
}
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_all(lean_object* v_x_5372_){
_start:
{
uint8_t v___x_5373_; 
v___x_5373_ = 1;
return v___x_5373_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_all___boxed(lean_object* v_x_5374_){
_start:
{
uint8_t v_res_5375_; lean_object* v_r_5376_; 
v_res_5375_ = l_Legal_USTax_Hunt_Basis_all(v_x_5374_);
lean_dec(v_x_5374_);
v_r_5376_ = lean_box(v_res_5375_);
return v_r_5376_;
}
}
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_small___lam__0(lean_object* v___y_5377_){
_start:
{
uint8_t v___x_5378_; 
v___x_5378_ = 1;
return v___x_5378_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_small___lam__0___boxed(lean_object* v___y_5379_){
_start:
{
uint8_t v_res_5380_; lean_object* v_r_5381_; 
v_res_5380_ = l_Legal_USTax_Hunt_Basis_small___lam__0(v___y_5379_);
lean_dec(v___y_5379_);
v_r_5381_ = lean_box(v_res_5380_);
return v_r_5381_;
}
}
LEAN_EXPORT uint8_t l_Legal_USTax_Hunt_Basis_small___lam__1(uint8_t v___x_5382_, lean_object* v_x_5383_){
_start:
{
if (lean_obj_tag(v_x_5383_) == 5)
{
uint8_t v_heir_5384_; 
v_heir_5384_ = lean_ctor_get_uint8(v_x_5383_, 0);
switch(v_heir_5384_)
{
case 3:
{
uint8_t v___x_5385_; 
v___x_5385_ = 0;
return v___x_5385_;
}
case 2:
{
uint8_t v___x_5386_; 
v___x_5386_ = 0;
return v___x_5386_;
}
default: 
{
return v___x_5382_;
}
}
}
else
{
return v___x_5382_;
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_small___lam__1___boxed(lean_object* v___x_5387_, lean_object* v_x_5388_){
_start:
{
uint8_t v___x_345__boxed_5389_; uint8_t v_res_5390_; lean_object* v_r_5391_; 
v___x_345__boxed_5389_ = lean_unbox(v___x_5387_);
v_res_5390_ = l_Legal_USTax_Hunt_Basis_small___lam__1(v___x_345__boxed_5389_, v_x_5388_);
lean_dec(v_x_5388_);
v_r_5391_ = lean_box(v_res_5390_);
return v_r_5391_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_small___closed__7(void){
_start:
{
lean_object* v___x_5402_; lean_object* v___x_5403_; 
v___x_5402_ = lean_unsigned_to_nat(2u);
v___x_5403_ = l_Legal_USTax_Hunt_Basis_sc4(v___x_5402_);
return v___x_5403_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_small___closed__9(void){
_start:
{
lean_object* v___x_5405_; lean_object* v___x_5406_; lean_object* v___x_5407_; 
v___x_5405_ = lean_box(0);
v___x_5406_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_sc2___closed__0, &l_Legal_USTax_Hunt_Basis_sc2___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_sc2___closed__0);
v___x_5407_ = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(v___x_5407_, 0, v___x_5406_);
lean_ctor_set(v___x_5407_, 1, v___x_5405_);
return v___x_5407_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_small___closed__10(void){
_start:
{
lean_object* v___x_5408_; lean_object* v___x_5409_; lean_object* v___x_5410_; lean_object* v___x_5411_; 
v___x_5408_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0, &l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0_once, _init_l_Legal_USTax_Hunt_Basis_instInhabitedRet_default___closed__0);
v___x_5409_ = lean_unsigned_to_nat(0u);
v___x_5410_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_small___closed__9, &l_Legal_USTax_Hunt_Basis_small___closed__9_once, _init_l_Legal_USTax_Hunt_Basis_small___closed__9);
v___x_5411_ = l_Legal_USTax_Hunt_Basis_mk(v___x_5410_, v___x_5409_, v___x_5408_);
return v___x_5411_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_small(){
_start:
{
lean_object* v___f_5413_; lean_object* v___x_5414_; lean_object* v___x_5415_; lean_object* v___x_5416_; lean_object* v___x_5417_; lean_object* v___x_5418_; 
v___f_5413_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_small___closed__0));
v___x_5414_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_small___closed__1));
v___x_5415_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_cfg0));
v___x_5416_ = l_Legal_USTax_Hunt_Basis_sc1;
v___x_5417_ = lean_unsigned_to_nat(14u);
v___x_5418_ = l_Legal_USTax_Hunt_Basis_search(v___x_5414_, v___x_5415_, v___x_5416_, v___f_5413_, v___x_5417_);
if (lean_obj_tag(v___x_5418_) == 0)
{
lean_object* v_wJ_5419_; lean_object* v_wA_5420_; lean_object* v_wP_5421_; lean_object* v_horizon_5422_; lean_object* v_users_5423_; uint8_t v___x_5424_; lean_object* v___x_5425_; lean_object* v___x_5426_; lean_object* v___x_5427_; lean_object* v___x_5428_; lean_object* v___x_5429_; lean_object* v___x_5430_; 
lean_dec_ref_known(v___x_5418_, 1);
v_wJ_5419_ = lean_ctor_get(v___x_5415_, 0);
v_wA_5420_ = lean_ctor_get(v___x_5415_, 1);
v_wP_5421_ = lean_ctor_get(v___x_5415_, 2);
v_horizon_5422_ = lean_ctor_get(v___x_5415_, 4);
v_users_5423_ = lean_ctor_get(v___x_5415_, 5);
v___x_5424_ = 0;
v___x_5425_ = lean_box(0);
v___x_5426_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_small___closed__2));
v___x_5427_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_small___closed__3));
lean_inc(v_users_5423_);
lean_inc(v_horizon_5422_);
lean_inc(v_wP_5421_);
lean_inc(v_wA_5420_);
lean_inc(v_wJ_5419_);
v___x_5428_ = lean_alloc_ctor(0, 6, 1);
lean_ctor_set(v___x_5428_, 0, v_wJ_5419_);
lean_ctor_set(v___x_5428_, 1, v_wA_5420_);
lean_ctor_set(v___x_5428_, 2, v_wP_5421_);
lean_ctor_set(v___x_5428_, 3, v___x_5427_);
lean_ctor_set(v___x_5428_, 4, v_horizon_5422_);
lean_ctor_set(v___x_5428_, 5, v_users_5423_);
lean_ctor_set_uint8(v___x_5428_, sizeof(void*)*6, v___x_5424_);
v___x_5429_ = l_Legal_USTax_Hunt_Basis_sc2;
v___x_5430_ = l_Legal_USTax_Hunt_Basis_search(v___x_5426_, v___x_5428_, v___x_5429_, v___f_5413_, v___x_5417_);
if (lean_obj_tag(v___x_5430_) == 0)
{
lean_object* v___x_5431_; uint8_t v___x_5432_; lean_object* v___f_5433_; lean_object* v___x_5434_; lean_object* v___x_5435_; lean_object* v___x_5436_; 
lean_dec_ref_known(v___x_5430_, 1);
v___x_5431_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_small___closed__4));
v___x_5432_ = 1;
v___f_5433_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_small___closed__5));
lean_inc(v_users_5423_);
lean_inc(v_horizon_5422_);
lean_inc(v_wP_5421_);
lean_inc(v_wA_5420_);
lean_inc(v_wJ_5419_);
v___x_5434_ = lean_alloc_ctor(0, 6, 1);
lean_ctor_set(v___x_5434_, 0, v_wJ_5419_);
lean_ctor_set(v___x_5434_, 1, v_wA_5420_);
lean_ctor_set(v___x_5434_, 2, v_wP_5421_);
lean_ctor_set(v___x_5434_, 3, v___x_5425_);
lean_ctor_set(v___x_5434_, 4, v_horizon_5422_);
lean_ctor_set(v___x_5434_, 5, v_users_5423_);
lean_ctor_set_uint8(v___x_5434_, sizeof(void*)*6, v___x_5432_);
v___x_5435_ = l_Legal_USTax_Hunt_Basis_sc3;
v___x_5436_ = l_Legal_USTax_Hunt_Basis_search(v___x_5431_, v___x_5434_, v___x_5435_, v___f_5413_, v___x_5417_);
lean_dec_ref_known(v___x_5434_, 6);
if (lean_obj_tag(v___x_5436_) == 0)
{
lean_object* v___x_5437_; lean_object* v___x_5438_; lean_object* v___x_5439_; lean_object* v___x_5440_; lean_object* v___x_5441_; lean_object* v___x_5442_; 
lean_dec_ref_known(v___x_5436_, 1);
v___x_5437_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_small___closed__6));
v___x_5438_ = lean_unsigned_to_nat(4u);
lean_inc(v_users_5423_);
lean_inc(v_wP_5421_);
lean_inc(v_wA_5420_);
lean_inc(v_wJ_5419_);
v___x_5439_ = lean_alloc_ctor(0, 6, 1);
lean_ctor_set(v___x_5439_, 0, v_wJ_5419_);
lean_ctor_set(v___x_5439_, 1, v_wA_5420_);
lean_ctor_set(v___x_5439_, 2, v_wP_5421_);
lean_ctor_set(v___x_5439_, 3, v___x_5425_);
lean_ctor_set(v___x_5439_, 4, v___x_5438_);
lean_ctor_set(v___x_5439_, 5, v_users_5423_);
lean_ctor_set_uint8(v___x_5439_, sizeof(void*)*6, v___x_5424_);
v___x_5440_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_small___closed__7, &l_Legal_USTax_Hunt_Basis_small___closed__7_once, _init_l_Legal_USTax_Hunt_Basis_small___closed__7);
v___x_5441_ = lean_unsigned_to_nat(8u);
v___x_5442_ = l_Legal_USTax_Hunt_Basis_search(v___x_5437_, v___x_5439_, v___x_5440_, v___f_5413_, v___x_5441_);
lean_dec_ref_known(v___x_5439_, 6);
if (lean_obj_tag(v___x_5442_) == 0)
{
lean_object* v___x_5443_; lean_object* v___x_5444_; lean_object* v___x_5445_; lean_object* v___x_5446_; 
lean_dec_ref_known(v___x_5442_, 1);
v___x_5443_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_small___closed__8));
v___x_5444_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_small___closed__10, &l_Legal_USTax_Hunt_Basis_small___closed__10_once, _init_l_Legal_USTax_Hunt_Basis_small___closed__10);
v___x_5445_ = lean_unsigned_to_nat(6u);
v___x_5446_ = l_Legal_USTax_Hunt_Basis_search(v___x_5443_, v___x_5428_, v___x_5444_, v___f_5433_, v___x_5445_);
lean_dec_ref_known(v___x_5428_, 6);
return v___x_5446_;
}
else
{
lean_dec_ref_known(v___x_5428_, 6);
return v___x_5442_;
}
}
else
{
lean_dec_ref_known(v___x_5428_, 6);
return v___x_5436_;
}
}
else
{
lean_dec_ref_known(v___x_5428_, 6);
return v___x_5430_;
}
}
else
{
return v___x_5418_;
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_small___boxed(lean_object* v_a_5447_){
_start:
{
lean_object* v_res_5448_; 
v_res_5448_ = l_Legal_USTax_Hunt_Basis_small();
return v_res_5448_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_wide___closed__3(void){
_start:
{
lean_object* v___x_5453_; lean_object* v___x_5454_; 
v___x_5453_ = lean_unsigned_to_nat(3u);
v___x_5454_ = l_Legal_USTax_Hunt_Basis_sc4(v___x_5453_);
return v___x_5454_;
}
}
static lean_object* _init_l_Legal_USTax_Hunt_Basis_wide___closed__5(void){
_start:
{
lean_object* v___x_5456_; lean_object* v___x_5457_; 
v___x_5456_ = lean_unsigned_to_nat(3u);
v___x_5457_ = l_Legal_USTax_Hunt_Basis_sc5(v___x_5456_);
return v___x_5457_;
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_wide(){
_start:
{
lean_object* v___x_5461_; lean_object* v_wJ_5462_; lean_object* v_wA_5463_; lean_object* v_wP_5464_; lean_object* v_horizon_5465_; lean_object* v_users_5466_; uint8_t v___x_5467_; lean_object* v___x_5468_; lean_object* v___f_5469_; lean_object* v___x_5470_; lean_object* v___x_5471_; lean_object* v___x_5472_; lean_object* v___x_5473_; lean_object* v___x_5474_; lean_object* v___x_5475_; 
v___x_5461_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_cfg0));
v_wJ_5462_ = lean_ctor_get(v___x_5461_, 0);
v_wA_5463_ = lean_ctor_get(v___x_5461_, 1);
v_wP_5464_ = lean_ctor_get(v___x_5461_, 2);
v_horizon_5465_ = lean_ctor_get(v___x_5461_, 4);
v_users_5466_ = lean_ctor_get(v___x_5461_, 5);
v___x_5467_ = 0;
v___x_5468_ = lean_box(0);
v___f_5469_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_small___closed__0));
v___x_5470_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_wide___closed__0));
v___x_5471_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_wide___closed__1));
lean_inc(v_users_5466_);
lean_inc(v_horizon_5465_);
lean_inc(v_wP_5464_);
lean_inc(v_wA_5463_);
lean_inc(v_wJ_5462_);
v___x_5472_ = lean_alloc_ctor(0, 6, 1);
lean_ctor_set(v___x_5472_, 0, v_wJ_5462_);
lean_ctor_set(v___x_5472_, 1, v_wA_5463_);
lean_ctor_set(v___x_5472_, 2, v_wP_5464_);
lean_ctor_set(v___x_5472_, 3, v___x_5471_);
lean_ctor_set(v___x_5472_, 4, v_horizon_5465_);
lean_ctor_set(v___x_5472_, 5, v_users_5466_);
lean_ctor_set_uint8(v___x_5472_, sizeof(void*)*6, v___x_5467_);
v___x_5473_ = l_Legal_USTax_Hunt_Basis_sc2;
v___x_5474_ = lean_unsigned_to_nat(14u);
v___x_5475_ = l_Legal_USTax_Hunt_Basis_search(v___x_5470_, v___x_5472_, v___x_5473_, v___f_5469_, v___x_5474_);
if (lean_obj_tag(v___x_5475_) == 0)
{
lean_object* v___x_5476_; lean_object* v___x_5477_; lean_object* v___x_5478_; lean_object* v___x_5479_; lean_object* v___x_5480_; lean_object* v___x_5481_; lean_object* v___x_5482_; 
lean_dec_ref_known(v___x_5475_, 1);
v___x_5476_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_wide___closed__2));
v___x_5477_ = lean_unsigned_to_nat(4u);
lean_inc(v_users_5466_);
lean_inc(v_wP_5464_);
lean_inc(v_wA_5463_);
lean_inc(v_wJ_5462_);
v___x_5478_ = lean_alloc_ctor(0, 6, 1);
lean_ctor_set(v___x_5478_, 0, v_wJ_5462_);
lean_ctor_set(v___x_5478_, 1, v_wA_5463_);
lean_ctor_set(v___x_5478_, 2, v_wP_5464_);
lean_ctor_set(v___x_5478_, 3, v___x_5471_);
lean_ctor_set(v___x_5478_, 4, v___x_5477_);
lean_ctor_set(v___x_5478_, 5, v_users_5466_);
lean_ctor_set_uint8(v___x_5478_, sizeof(void*)*6, v___x_5467_);
v___x_5479_ = lean_unsigned_to_nat(3u);
v___x_5480_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_wide___closed__3, &l_Legal_USTax_Hunt_Basis_wide___closed__3_once, _init_l_Legal_USTax_Hunt_Basis_wide___closed__3);
v___x_5481_ = lean_unsigned_to_nat(10u);
v___x_5482_ = l_Legal_USTax_Hunt_Basis_search(v___x_5476_, v___x_5478_, v___x_5480_, v___f_5469_, v___x_5481_);
lean_dec_ref_known(v___x_5478_, 6);
if (lean_obj_tag(v___x_5482_) == 0)
{
lean_object* v___x_5483_; lean_object* v___x_5484_; lean_object* v___x_5485_; lean_object* v___x_5486_; 
lean_dec_ref_known(v___x_5482_, 1);
v___x_5483_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_wide___closed__4));
lean_inc(v_users_5466_);
lean_inc(v_wP_5464_);
lean_inc(v_wA_5463_);
lean_inc(v_wJ_5462_);
v___x_5484_ = lean_alloc_ctor(0, 6, 1);
lean_ctor_set(v___x_5484_, 0, v_wJ_5462_);
lean_ctor_set(v___x_5484_, 1, v_wA_5463_);
lean_ctor_set(v___x_5484_, 2, v_wP_5464_);
lean_ctor_set(v___x_5484_, 3, v___x_5468_);
lean_ctor_set(v___x_5484_, 4, v___x_5479_);
lean_ctor_set(v___x_5484_, 5, v_users_5466_);
lean_ctor_set_uint8(v___x_5484_, sizeof(void*)*6, v___x_5467_);
v___x_5485_ = lean_obj_once(&l_Legal_USTax_Hunt_Basis_wide___closed__5, &l_Legal_USTax_Hunt_Basis_wide___closed__5_once, _init_l_Legal_USTax_Hunt_Basis_wide___closed__5);
v___x_5486_ = l_Legal_USTax_Hunt_Basis_search(v___x_5483_, v___x_5484_, v___x_5485_, v___f_5469_, v___x_5481_);
lean_dec_ref_known(v___x_5484_, 6);
if (lean_obj_tag(v___x_5486_) == 0)
{
lean_object* v___x_5487_; lean_object* v___x_5488_; lean_object* v___x_5489_; lean_object* v___x_5490_; 
lean_dec_ref_known(v___x_5486_, 1);
v___x_5487_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_wide___closed__6));
v___x_5488_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_small___closed__3));
lean_inc(v_users_5466_);
lean_inc(v_wP_5464_);
lean_inc(v_wA_5463_);
lean_inc(v_wJ_5462_);
v___x_5489_ = lean_alloc_ctor(0, 6, 1);
lean_ctor_set(v___x_5489_, 0, v_wJ_5462_);
lean_ctor_set(v___x_5489_, 1, v_wA_5463_);
lean_ctor_set(v___x_5489_, 2, v_wP_5464_);
lean_ctor_set(v___x_5489_, 3, v___x_5488_);
lean_ctor_set(v___x_5489_, 4, v___x_5479_);
lean_ctor_set(v___x_5489_, 5, v_users_5466_);
lean_ctor_set_uint8(v___x_5489_, sizeof(void*)*6, v___x_5467_);
v___x_5490_ = l_Legal_USTax_Hunt_Basis_search(v___x_5487_, v___x_5489_, v___x_5485_, v___f_5469_, v___x_5481_);
lean_dec_ref_known(v___x_5489_, 6);
if (lean_obj_tag(v___x_5490_) == 0)
{
lean_object* v___x_5491_; lean_object* v___x_5492_; lean_object* v___x_5493_; lean_object* v___x_5494_; 
lean_dec_ref_known(v___x_5490_, 1);
v___x_5491_ = ((lean_object*)(l_Legal_USTax_Hunt_Basis_wide___closed__7));
v___x_5492_ = l_Legal_USTax_Hunt_Basis_sc6;
v___x_5493_ = lean_unsigned_to_nat(16u);
v___x_5494_ = l_Legal_USTax_Hunt_Basis_search(v___x_5491_, v___x_5472_, v___x_5492_, v___f_5469_, v___x_5493_);
lean_dec_ref_known(v___x_5472_, 6);
return v___x_5494_;
}
else
{
lean_dec_ref_known(v___x_5472_, 6);
return v___x_5490_;
}
}
else
{
lean_dec_ref_known(v___x_5472_, 6);
return v___x_5486_;
}
}
else
{
lean_dec_ref_known(v___x_5472_, 6);
return v___x_5482_;
}
}
else
{
lean_dec_ref_known(v___x_5472_, 6);
return v___x_5475_;
}
}
}
LEAN_EXPORT lean_object* l_Legal_USTax_Hunt_Basis_wide___boxed(lean_object* v_a_5495_){
_start:
{
lean_object* v_res_5496_; 
v_res_5496_ = l_Legal_USTax_Hunt_Basis_wide();
return v_res_5496_;
}
}
LEAN_EXPORT uint8_t l_List_elem___at___00main_spec__0(lean_object* v_a_5497_, lean_object* v_x_5498_){
_start:
{
if (lean_obj_tag(v_x_5498_) == 0)
{
uint8_t v___x_5499_; 
v___x_5499_ = 0;
return v___x_5499_;
}
else
{
lean_object* v_head_5500_; lean_object* v_tail_5501_; uint8_t v___x_5502_; 
v_head_5500_ = lean_ctor_get(v_x_5498_, 0);
v_tail_5501_ = lean_ctor_get(v_x_5498_, 1);
v___x_5502_ = lean_string_dec_eq(v_a_5497_, v_head_5500_);
if (v___x_5502_ == 0)
{
v_x_5498_ = v_tail_5501_;
goto _start;
}
else
{
return v___x_5502_;
}
}
}
}
LEAN_EXPORT lean_object* l_List_elem___at___00main_spec__0___boxed(lean_object* v_a_5504_, lean_object* v_x_5505_){
_start:
{
uint8_t v_res_5506_; lean_object* v_r_5507_; 
v_res_5506_ = l_List_elem___at___00main_spec__0(v_a_5504_, v_x_5505_);
lean_dec(v_x_5505_);
lean_dec_ref(v_a_5504_);
v_r_5507_ = lean_box(v_res_5506_);
return v_r_5507_;
}
}
LEAN_EXPORT lean_object* _lean_main(lean_object* v_args_5509_){
_start:
{
lean_object* v___x_5511_; uint8_t v___x_5512_; 
v___x_5511_ = ((lean_object*)(l_main___closed__0));
v___x_5512_ = l_List_elem___at___00main_spec__0(v___x_5511_, v_args_5509_);
lean_dec(v_args_5509_);
if (v___x_5512_ == 0)
{
lean_object* v___x_5513_; 
v___x_5513_ = l_Legal_USTax_Hunt_Basis_wide();
return v___x_5513_;
}
else
{
lean_object* v___x_5514_; 
v___x_5514_ = l_Legal_USTax_Hunt_Basis_small();
return v___x_5514_;
}
}
}
LEAN_EXPORT lean_object* l_main___boxed(lean_object* v_args_5515_, lean_object* v_a_5516_){
_start:
{
lean_object* v_res_5517_; 
v_res_5517_ = _lean_main(v_args_5515_);
return v_res_5517_;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_Std(uint8_t builtin);
void lean_initialize_runtime_module();
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_BasisMain(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
lean_initialize_runtime_module();
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_Std(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
l_Legal_USTax_Hunt_Basis_instInhabitedWho_default = _init_l_Legal_USTax_Hunt_Basis_instInhabitedWho_default();
l_Legal_USTax_Hunt_Basis_instInhabitedWho = _init_l_Legal_USTax_Hunt_Basis_instInhabitedWho();
l_Legal_USTax_Hunt_Basis_instInhabitedKind_default = _init_l_Legal_USTax_Hunt_Basis_instInhabitedKind_default();
l_Legal_USTax_Hunt_Basis_instInhabitedKind = _init_l_Legal_USTax_Hunt_Basis_instInhabitedKind();
l_Legal_USTax_Hunt_Basis_instInhabitedRet_default = _init_l_Legal_USTax_Hunt_Basis_instInhabitedRet_default();
lean_mark_persistent(l_Legal_USTax_Hunt_Basis_instInhabitedRet_default);
l_Legal_USTax_Hunt_Basis_instInhabitedRet = _init_l_Legal_USTax_Hunt_Basis_instInhabitedRet();
lean_mark_persistent(l_Legal_USTax_Hunt_Basis_instInhabitedRet);
l_Legal_USTax_Hunt_Basis_instInhabitedSt_default = _init_l_Legal_USTax_Hunt_Basis_instInhabitedSt_default();
lean_mark_persistent(l_Legal_USTax_Hunt_Basis_instInhabitedSt_default);
l_Legal_USTax_Hunt_Basis_instInhabitedSt = _init_l_Legal_USTax_Hunt_Basis_instInhabitedSt();
lean_mark_persistent(l_Legal_USTax_Hunt_Basis_instInhabitedSt);
l_Legal_USTax_Hunt_Basis_big = _init_l_Legal_USTax_Hunt_Basis_big();
lean_mark_persistent(l_Legal_USTax_Hunt_Basis_big);
l_Legal_USTax_Hunt_Basis_mfj = _init_l_Legal_USTax_Hunt_Basis_mfj();
lean_mark_persistent(l_Legal_USTax_Hunt_Basis_mfj);
l_Legal_USTax_Hunt_Basis_single = _init_l_Legal_USTax_Hunt_Basis_single();
lean_mark_persistent(l_Legal_USTax_Hunt_Basis_single);
l_Legal_USTax_Hunt_Basis_stdSingle = _init_l_Legal_USTax_Hunt_Basis_stdSingle();
lean_mark_persistent(l_Legal_USTax_Hunt_Basis_stdSingle);
l_Legal_USTax_Hunt_Basis_stdAged = _init_l_Legal_USTax_Hunt_Basis_stdAged();
lean_mark_persistent(l_Legal_USTax_Hunt_Basis_stdAged);
l_Legal_USTax_Hunt_Basis_seniorDed = _init_l_Legal_USTax_Hunt_Basis_seniorDed();
lean_mark_persistent(l_Legal_USTax_Hunt_Basis_seniorDed);
l_Legal_USTax_Hunt_Basis_stdDependent = _init_l_Legal_USTax_Hunt_Basis_stdDependent();
lean_mark_persistent(l_Legal_USTax_Hunt_Basis_stdDependent);
l_Legal_USTax_Hunt_Basis_giftExcl = _init_l_Legal_USTax_Hunt_Basis_giftExcl();
lean_mark_persistent(l_Legal_USTax_Hunt_Basis_giftExcl);
l_Legal_USTax_Hunt_Basis_qCap = _init_l_Legal_USTax_Hunt_Basis_qCap();
lean_mark_persistent(l_Legal_USTax_Hunt_Basis_qCap);
l_Legal_USTax_Hunt_Basis_top37 = _init_l_Legal_USTax_Hunt_Basis_top37();
lean_mark_persistent(l_Legal_USTax_Hunt_Basis_top37);
l_Legal_USTax_Hunt_Basis_sc1 = _init_l_Legal_USTax_Hunt_Basis_sc1();
lean_mark_persistent(l_Legal_USTax_Hunt_Basis_sc1);
l_Legal_USTax_Hunt_Basis_sc2 = _init_l_Legal_USTax_Hunt_Basis_sc2();
lean_mark_persistent(l_Legal_USTax_Hunt_Basis_sc2);
l_Legal_USTax_Hunt_Basis_sc3 = _init_l_Legal_USTax_Hunt_Basis_sc3();
lean_mark_persistent(l_Legal_USTax_Hunt_Basis_sc3);
l_Legal_USTax_Hunt_Basis_sc6 = _init_l_Legal_USTax_Hunt_Basis_sc6();
lean_mark_persistent(l_Legal_USTax_Hunt_Basis_sc6);
return lean_io_result_mk_ok(lean_box(0));
}
char ** lean_setup_args(int argc, char ** argv);
#if defined(WIN32) || defined(_WIN32)
#include <windows.h>
#endif
lean_object* run_main(int argc, char ** argv) {
    lean_object* in = lean_box(0);
    int i = argc;
    while (i > 1) {
      lean_object* n;
      i--;
      n = lean_alloc_ctor(1,2,0); lean_ctor_set(n, 0, lean_mk_string(argv[i])); lean_ctor_set(n, 1, in);
      in = n;
    }
    return _lean_main(in);
}
int main(int argc, char ** argv) {
#if defined(WIN32) || defined(_WIN32)
  SetErrorMode(SEM_FAILCRITICALERRORS);
  SetConsoleOutputCP(CP_UTF8);
#endif
  lean_object* res;
  argv = lean_setup_args(argc, argv);
  res = initialize_BasisMain(1 /* builtin */);
  lean_io_mark_end_initialization();
  if (lean_io_result_is_ok(res)) {
    lean_dec_ref(res);
    lean_init_task_manager();
    res = lean_run_main(&run_main, argc, argv);
  }
  lean_finalize_task_manager();
  if (lean_io_result_is_ok(res)) {
    int ret = 0;
    lean_dec_ref(res);
    return ret;
  } else {
    lean_io_result_show_error(res);
    lean_dec_ref(res);
    return 1;
  }
}
#ifdef __cplusplus
}
#endif
