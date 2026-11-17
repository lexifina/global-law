(* Batch driver for the Catala impot_revenu module (catala-examples 9e251b9, Catala 1.3.2, OCaml backend).

   Reads one return per line on stdin, `id;year;BOX=VAL,BOX=VAL,...` (the 2042 box format of the Lean runner),
   and prints `id;KEY=VAL;...` with what the Catala code computes:
     NBPT, ABAT196B                        scope NombreDeParts
     TS_RBG, TS_DEF, RENTES                scope TraitementsSalairesFoyerFiscal (salaries, pensions, annuities)
     TSB_<p>, DFP_<p>, ABP_<p>, RBD_<p>    per person p in V C P1..P4: salaries after art. 81 quater/PPV,
                                           professional-expense deduction, pension allowance, net income
     BIC_RBG, BIC_DEFPRO, BIC_DEFNP, BIC_DEFLM, BIC_VL   scope BénéficesIndustrielsCommerciauxFoyerFiscal
     BNC_RBG, BNC_DEFPRO, BNC_DEFNP, BNC_VL              scope BénéficesNonCommerciauxFoyerFiscal
     RBG, DEFGLOB  our aggregation (the Catala code has no household-level revenu brut global):
                   TS_RBG + BIC_RBG + BNC_RBG - TS_DEF - BIC_DEFPRO - BNC_DEFPRO, split into RBG >= 0 and a
                   global deficit.
   A return the Catala code rejects prints `id;ERR=<kind>@<file>:<line>`.
   Usage: catala_ir [-time N]   (with -time, every return is evaluated N times and the mean time printed) *)

open Catala_runtime
open Impot_revenu

let boxes : (string, int) Hashtbl.t = Hashtbl.create 64
let g b = try Hashtbl.find boxes b with Not_found -> 0
let has b = g b <> 0
let m b = money_of_units_int (g b)
let mz = money_of_units_int 0
let used : (string, unit) Hashtbl.t = Hashtbl.create 256
let u b = Hashtbl.replace used b (); b
let gm b = m (u b)

(* ---- salaries, pensions: one column per person ---- *)
let persons = [| "V"; "C"; "P1"; "P2"; "P3"; "P4" |]
let col1 = [| 'A'; 'B'; 'C'; 'D'; 'E'; 'F' |]      (* 1AJ 1BJ 1CJ 1DJ 1EJ 1FJ *)
let colG = [| 'G'; 'H'; 'I'; 'J'; 'K'; 'L' |]      (* 1GB 1HB 1IB ... 1GH 1HH ... *)
let r1 i c = Printf.sprintf "1%c%c" col1.(i) c
let rG i c = Printf.sprintf "1%c%c" colG.(i) c
let opt2 i a b = if i = 0 then u a else if i = 1 then u b else "-"
let pourb = [| "1PB"; "1PC"; "1PD"; "1PE"; "-"; "-" |]

let decl_ts year i : DeclarationTraitementsSalaires.t =
  let k = r1 i 'K' in
  ignore year;
  { revenu_assistants_maternels_familiaux = gm (r1 i 'A');
    revenus_associes_gerants = gm (rG i 'B');
    droits_dauteurs_fonctionnaires_chercheurs = gm (rG i 'F');
    heures_supplementaires_et_rtt_exonerees = gm (rG i 'H');
    frais_reels = (if has (u k) then FraisReels.Oui (m k) else FraisReels.Non);
    pensions_retraites_rentes = gm (r1 i 'S');
    pensions_retraites_en_capital_7_5pct = gm (r1 i 'T');
    pensions_en_capital_plans_epargne_retraite = gm (r1 i 'I');
    pensions_invalidite = gm (r1 i 'Z');
    pensions_alimentaires_percues = gm (r1 i 'O');
    traitements_salaires = gm (r1 i 'J');
    pourboires_exoneres = (if pourb.(i) = "-" then mz else gm pourb.(i));
    prime_partage_valeur_exoneree = gm (r1 i 'D');
    majoration_seuil_exoneration = has (u (r1 i 'V'));
    autres_revenus_imposables_chomage_preretraite = gm (r1 i 'P');
    rabais_excedentaire_options_sur_titres = gm (opt2 i "1TP" "1UP");
    gains_de_levee_doptions = gm (opt2 i "1TT" "1UT");
    salaires_imposables_agent_assurance = gm (rG i 'G');
    indemnites_prejudice_moral_fraction_superieure_million = gm (opt2 i "1PM" "1QM");
    gains_et_distributions_carried_interest = gm (opt2 i "1NX" "1OX");
    gains_et_distributions_carried_interest_soumis_contribution_salariale = gm (opt2 i "1NY" "1OY");
    revenus_exceptionnels_ou_differes = [||];
    salaires_etrangers_impot_impute = gm (r1 i 'F');
    pensions_etrangeres_impots_impute = gm (r1 i 'L');
    autre_salaires_imposables_source_etrangere = gm (r1 i 'G');
    autre_pensions_imposables_source_etrangere = gm (r1 i 'M');
  }

(* the six columns 1x.. of a person are "present" when any of their boxes is non-zero *)
let person_has i =
  let pre1 = Printf.sprintf "1%c" col1.(i) and preG = Printf.sprintf "1%c" colG.(i) in
  Hashtbl.fold (fun k v acc -> acc || (v <> 0 && String.length k = 3 &&
    (String.sub k 0 2 = pre1 || String.sub k 0 2 = preG))) boxes false

(* ---- BIC / BNC: three columns V, C, P ---- *)
let p3 i (a, b, c) = u (match i with 0 -> a | 1 -> b | _ -> c)
let m3 i t = m (p3 i t)

let bic_gen_pro i : DeclarationBeneficesIndustrielsCommerciauxGeneraux.t =
  { revenus_concession_brevets = m3 i ("5UI", "5VI", "5WI");
    plus_values_nettes_court_terme_micro = m3 i ("5KX", "5LX", "5MX");
    moins_values_nettes_court_terme_micro = m3 i ("5KJ", "5LJ", "5MJ");
    plus_values_nettes_long_terme_micro = m3 i ("5KQ", "5LQ", "5MQ");
    moins_values_nettes_long_terme_micro = m3 i ("5KR", "5LR", "5MR");
    plus_values_nettes_long_terme_reel = m3 i ("5KE", "5LE", "5ME");
    revenus_imposables_micro_marchandises = m3 i ("5KO", "5LO", "5MO");
    revenus_imposables_micro_services = m3 i ("5KP", "5LP", "5MP");
    revenus_imposables_reel = m3 i ("5KC", "5LC", "5MC");
    deficit_reel = m3 i ("5KF", "5LF", "5MF");
    revenus_imposables_reel_source_etrangere_imputes = m3 i ("5DF", "5EF", "5FF");
    revenus_exceptionnels_ou_differes = [||] }

let bic_gen_np i : DeclarationBeneficesIndustrielsCommerciauxGeneraux.t =
  { revenus_concession_brevets = m3 i ("5TF", "5UF", "5VF");
    plus_values_nettes_court_terme_micro = m3 i ("5NX", "5OX", "5PX");
    moins_values_nettes_court_terme_micro = m3 i ("5IU", "5RZ", "5SZ");
    plus_values_nettes_long_terme_micro = m3 i ("5NQ", "5OQ", "5PQ");
    moins_values_nettes_long_terme_micro = m3 i ("5NR", "5OR", "5PR");
    plus_values_nettes_long_terme_reel = m3 i ("5NE", "5OE", "5PE");
    revenus_imposables_micro_marchandises = m3 i ("5NO", "5OO", "5PO");
    revenus_imposables_micro_services = m3 i ("5NP", "5OP", "5PP");
    revenus_imposables_reel = m3 i ("5NC", "5OC", "5PC");
    deficit_reel = m3 i ("5NF", "5OF", "5PF");
    revenus_imposables_reel_source_etrangere_imputes = m3 i ("5UR", "5VR", "5WR");
    revenus_exceptionnels_ou_differes = [||] }

let decl_bic i : DeclarationBeneficesIndustrielsCommerciaux.t =
  { professionnels = bic_gen_pro i;
    non_professionnels =
      { generaux = bic_gen_np i;
        locations_meublees_micro_general = m3 i ("5ND", "5OD", "5PD");
        locations_meublees_micro_hotes_classees = m3 i ("5NG", "5OG", "5PG");
        locations_meublees_micro_classees_rurales_speciales = m3 i ("5QS", "5RS", "5SS");
        locations_meublees_micro_cotisations_general = m3 i ("5NW", "5OW", "5PW");
        locations_meublees_micro_cotisations_hotes_classees = m3 i ("5NJ", "5OJ", "5PJ");
        (* the Catala interface forces this one to 0 € *)
        locations_meublees_micro_cotisations_classees_rurales_speciales = mz;
        locations_meublees_reel_general = m3 i ("5NA", "5OA", "5PA");
        locations_meublees_reel_source_etrangere = m3 i ("5EY", "5FY", "5GY");
        locations_meublees_reel_cotisations = m3 i ("5NM", "5OM", "5PM");
        locations_meublees_deficit_general = m3 i ("5NY", "5OY", "5PY");
        locations_meublees_deficit_cotisations = m3 i ("5WE", "5XE", "5YE") };
    (* the Catala interface forces these to 0 € *)
    chiffre_affaires_prelevement_liberatoire_marchandises_exonere_cotisations = mz;
    chiffre_affaires_prelevement_liberatoire_services_exonere_cotisations = mz }

let bnc_gen_pro i : DeclarationBeneficesNonCommerciauxGeneraux.t =
  { revenus_imposables_micro = m3 i ("5HQ", "5IQ", "5JQ");
    plus_values_nettes_court_terme_micro = m3 i ("5HV", "5IV", "5JV");
    moins_values_nettes_court_terme_micro = m3 i ("5KZ", "5LZ", "5MZ");
    plus_values_nettes_long_terme_micro = m3 i ("5HR", "5IR", "5JR");
    moins_values_nettes_long_terme_micro = m3 i ("5HS", "5IS", "5JS");
    plus_values_nettes_long_terme_reel = m3 i ("5QD", "5RD", "5SD");
    revenus_imposables = m3 i ("5QC", "5RC", "5SC");
    deficit_reel = m3 i ("5QE", "5RE", "5SE");
    revenus_imposables_source_etrangere_imputes = m3 i ("5XJ", "5YJ", "5ZJ");
    revenus_exceptionnels_ou_differes = [||] }

let bnc_gen_np i : DeclarationBeneficesNonCommerciauxGeneraux.t =
  { revenus_imposables_micro = m3 i ("5KU", "5LU", "5MU");
    plus_values_nettes_court_terme_micro = m3 i ("5KY", "5LY", "5MY");
    moins_values_nettes_court_terme_micro = m3 i ("5JU", "5LD", "5MD");
    plus_values_nettes_long_terme_micro = m3 i ("5KV", "5LV", "5MV");
    moins_values_nettes_long_terme_micro = m3 i ("5KW", "5LW", "5MW");
    plus_values_nettes_long_terme_reel = m3 i ("5SO", "5NT", "5OT");
    revenus_imposables = m3 i ("5JG", "5RF", "5SF");
    deficit_reel = m3 i ("5JJ", "5RG", "5SG");
    revenus_imposables_source_etrangere_imputes = m3 i ("5XS", "5YS", "5ZS");
    revenus_exceptionnels_ou_differes = [||] }

let decl_bnc i : DeclarationBeneficesNonCommerciaux.t =
  { professionnels = { generaux = bnc_gen_pro i;
                       produits_inventeurs_logiciel_taxables = mz;
                       produits_inventeurs_logiciel_taxables_soumis_cotisations = mz };
    non_professionnels = { generaux = bnc_gen_np i };
    recettes_prelevement_liberatoire_exonerees_cotisations = mz }

(* prior deficits: boxes listed oldest first; the last box is year - 1 *)
let prior year bxs : Oracles.DeficitAnterieur.t array =
  let n = List.length bxs in
  Array.of_list (List.concat (List.mapi (fun k b ->
    if has (u b) then [ { Oracles.DeficitAnterieur.annee = integer_of_int (year - n + k); valeur = m b } ] else [])
    bxs))

(* ---- family ---- *)
let foyer () : DescriptionFoyerFiscal.t =
  let married = has (u "0AM") and pacs = has (u "0AO") and div = has (u "0AD")
  and wid = has (u "0AV") and single = has (u "0AC") in
  { nombre_enfants_a_charge_mineurs_et_non_maries = integer_of_int (g (u "0CF"));
    nombre_enfants_a_charge_mineurs_et_non_maries_invalides = integer_of_int (g (u "0CG"));
    nombre_enfants_a_charge_residence_alternee = integer_of_int (g (u "0CH"));
    nombre_enfants_a_charge_residence_alternee_invalides = integer_of_int (g (u "0CI"));
    nombre_autres_personnes_invalides_vivant_sous_toit = integer_of_int (g (u "0CR"));
    nombre_enfants_majeurs_celibataires_sans_enfant = integer_of_int (g (u "0DJ"));
    nombre_enfants_majeurs_maries_ou_charges_famille = decimal_of_integer (integer_of_int (g (u "0DN")));
    mariees = married; pacsees = pacs; divorcee_separees = div; veuve = wid;
    (* the Catala interface: with no situation box ticked, the return is a single person's *)
    celibataire = single || not (married || pacs || div || wid);
    parent_isole = has (u "0BT");
    celibataire_divorce_veuf_sans_enfant = has (u "0AL");
    titulaire_carte_invalidite_CMI_invalidite_40_pourcent = has (u "0AP");
    conjoint_titulaire_carte_invalidite_CMI_invalidite_40_pourcent = has (u "0AF");
    pensionne_guerre_celibataire_veuf = has (u "0AW");
    pensionne_guerre_marie_pacse = has (u "0AS");
    pensionne_veuve_de_guerre = has (u "0AG") }

let money_s x = Printf.sprintf "%.2f" (money_to_float x)
let dec_s x = Printf.sprintf "%.2f" (decimal_to_float x)
let msum = List.fold_left (fun a x -> Oper.o_add_mon_mon a x) mz
let sumdef a = msum (Array.to_list (Array.map (fun (d : Oracles.DeficitAnterieur.t) -> d.valeur) a))

let err_s e locs =
  let where = match locs with
    | l :: _ -> Printf.sprintf "%s:%d" (Filename.basename l.filename) l.start_line
    | [] -> "?" in
  Printf.sprintf "%s@%s" (error_to_string e) where

let compute year =
  let yr = integer_of_int year in
  let out = Buffer.create 512 in
  let add k v = Buffer.add_string out (Printf.sprintf ";%s=%s" k v) in
  (* parts *)
  let np = nombre_de_parts { NombreDeParts_in.foyer_fiscal_in = foyer (); annee_revenus_in = yr } in
  add "NBPT" (dec_s np.nombre_de_parts);
  add "ABAT196B" (money_s np.abattement);
  (* salaries and pensions *)
  let couple = has "0AM" || has "0AO" in
  let deps = List.filter person_has [2; 3; 4; 5] in
  let ts = traitements_salaires_foyer_fiscal {
      TraitementsSalairesFoyerFiscal_in.declarant1_in = decl_ts year 0;
      declarant2_in = (if couple || person_has 1 then DeclarationTraitementsSalaires2.Declaration (decl_ts year 1)
                       else DeclarationTraitementsSalaires2.PasDeDeclaration);
      declarations_personnes_a_charge_in = Array.of_list (List.map (decl_ts year) deps);
      annee_revenus_in = yr;
      revenus_in = {
        rentes_percues_49moins_ans = gm "1AW"; rentes_percues_50_59ans = gm "1BW";
        rentes_percues_60_69ans = gm "1CW"; rentes_percues_70plus_ans = gm "1DW";
        rentes_etrangeres_imputables_percues_49moins_ans = gm "1AR";
        rentes_etrangeres_imputables_percues_50_59ans = gm "1BR";
        rentes_etrangeres_imputables_percues_60_69ans = gm "1CR";
        rentes_etrangeres_imputables_percues_70plus_ans = gm "1DR";
        revenus_exceptionnels_ou_differes = [||];
        acquisition_d_actions_gratuites_gain_imposable = gm "1TZ" } } in
  add "TS_RBG" (money_s ts.revenu_brut_global);
  add "TS_DEF" (money_s ts.deficit_brut_global);
  add "RENTES" (money_s ts.rentes_viageres_titre_onereux);
  let who = Array.of_list ([0] @ (if couple || person_has 1 then [1] else []) @ deps) in
  Array.iteri (fun k (r : TraitementsSalairesDeclarant.t) ->
      let p = persons.(who.(k)) in
      add ("TSB_" ^ p) (money_s r.traitements_salaires_avec_deduction_frais_professionnels);
      add ("DFP_" ^ p) (money_s r.deduction_frais_professionnels_traitements_salaires);
      add ("ABP_" ^ p) (money_s r.abattement_pensions_retraites_rentes);
      add ("RBD_" ^ p) (money_s r.revenu_brut_declarant_hors_quotient))
    ts.declarations_avec_resultats_traitements_salaires;
  (* BIC *)
  let bic = benefices_industriels_commerciaux_foyer_fiscal {
      BeneficesIndustrielsCommerciauxFoyerFiscal_in.annee_revenus_in = yr;
      revenus_in = [| decl_bic 0; decl_bic 1; decl_bic 2 |];
      deficits_reels_annees_anterieures_non_professionnels_in =
        prior year ["5RN"; "5RO"; "5RP"; "5RQ"; "5RR"; "5RW"];
      deficits_reels_annees_anterieures_non_professionnels_locations_meublees_in =
        prior year ["5GA"; "5GB"; "5GC"; "5GD"; "5GE"; "5GF"; "5GG"; "5GH"; "5GI"; "5GJ"] } in
  add "BIC_RBG" (money_s bic.revenu_brut_global);
  add "BIC_DEFPRO" (money_s bic.deficit_brut_global_professionnel);
  add "BIC_DEFNP" (money_s bic.deficit_brut_global_non_professionnel_hors_locations_meublees);
  add "BIC_DEFLM" (money_s bic.deficit_brut_global_non_professionnel_locations_meublees);
  add "BIC_DEFANT" (money_s (sumdef bic.deficits_reels_annees_anterieures_non_professionnels_mis_a_jour));
  add "BIC_DEFANTLM" (money_s (sumdef bic.deficits_reels_annees_anterieures_non_professionnels_locations_meublees_mis_a_jour));
  add "BIC_VL" (money_s (msum (Array.to_list (Array.map
      (fun (r : BeneficesIndustrielsCommerciauxDeclarant.t) -> r.prelevement_liberatoire_auto_entreprise)
      bic.resultats_liquidation_benefices_industriels_commerciaux))));
  (* BNC *)
  let bnc = benefices_non_commerciaux_foyer_fiscal {
      BeneficesNonCommerciauxFoyerFiscal_in.annee_revenus_in = yr;
      revenus_in = [| decl_bnc 0; decl_bnc 1; decl_bnc 2 |];
      deficits_reels_annees_anterieures_non_professionnels_in =
        prior year ["5HT"; "5IT"; "5JT"; "5KT"; "5LT"; "5MT"] } in
  add "BNC_RBG" (money_s bnc.revenu_brut_global);
  add "BNC_DEFPRO" (money_s bnc.deficit_brut_global_professionnel);
  add "BNC_DEFNP" (money_s bnc.deficit_brut_global_non_professionnel);
  add "BNC_DEFANT" (money_s (sumdef bnc.deficits_reels_annees_anterieures_non_professionnels_mis_a_jour));
  add "BNC_VL" (money_s (msum (Array.to_list (Array.map
      (fun (r : BeneficesNonCommerciauxDeclarant.t) -> r.prelevement_liberatoire_auto_entreprise)
      bnc.resultats_liquidation_benefices_non_commerciaux))));
  let tot = Oper.o_sub_mon_mon
      (msum [ts.revenu_brut_global; bic.revenu_brut_global; bnc.revenu_brut_global])
      (msum [ts.deficit_brut_global; bic.deficit_brut_global_professionnel; bnc.deficit_brut_global_professionnel]) in
  let t = money_to_float tot in
  add "RBG" (Printf.sprintf "%.2f" (if t > 0. then t else 0.));
  add "DEFGLOB" (Printf.sprintf "%.2f" (if t < 0. then -. t else 0.));
  Buffer.contents out

(* build every input record once, so that every box the mapping reads is marked as used, whatever the
   Catala code then does with the return *)
let mark year =
  for i = 0 to 5 do ignore (decl_ts year i) done;
  for i = 0 to 2 do ignore (decl_bic i); ignore (decl_bnc i) done;
  ignore (foyer ());
  List.iter (fun b -> ignore (u b))
    ["1AW"; "1BW"; "1CW"; "1DW"; "1AR"; "1BR"; "1CR"; "1DR"; "1TZ"; "0AC"];
  ignore (prior year ["5RN"; "5RO"; "5RP"; "5RQ"; "5RR"; "5RW"]);
  ignore (prior year ["5GA"; "5GB"; "5GC"; "5GD"; "5GE"; "5GF"; "5GG"; "5GH"; "5GI"; "5GJ"]);
  ignore (prior year ["5HT"; "5IT"; "5JT"; "5KT"; "5LT"; "5MT"])

let parse line =
  Hashtbl.reset boxes; Hashtbl.reset used;
  match String.split_on_char ';' line with
  | [id; y; bs] ->
    List.iter (fun kv -> match String.split_on_char '=' kv with
        | [k; v] -> (try Hashtbl.replace boxes (String.trim k) (int_of_string (String.trim v)) with _ -> ())
        | _ -> ()) (String.split_on_char ',' bs);
    Some (id, int_of_string (String.trim y))
  | _ -> None

let () =
  let reps = if Array.length Sys.argv > 2 && Sys.argv.(1) = "-time" then int_of_string Sys.argv.(2) else 0 in
  let total = ref 0. and n = ref 0 in
  (try while true do
       let line = String.trim (input_line stdin) in
       if line <> "" then
         match parse line with
         | None -> print_endline ("ERR;" ^ line)
         | Some (id, year) ->
           mark year;
           let res = (try compute year with
               | Error (e, locs, _) -> ";ERR=" ^ err_s e locs
               | Empty -> ";ERR=Empty"
               | ex -> ";ERR=" ^ Printexc.to_string ex) in
           let ignored = Hashtbl.fold (fun k v acc ->
               if v <> 0 && not (Hashtbl.mem used k) then k :: acc else acc) boxes [] in
           let ign = String.concat "," (List.sort Stdlib.compare
               (List.filter (fun k -> not (String.length k = 3 && k.[0] = '0' &&
                                           (k.[1] = 'F' || k.[1] = 'H' || k.[1] = 'J' || k.[1] = 'P'
                                            || (k.[1] = 'D' && (k.[2] = 'A' || k.[2] = 'B'))))) ignored)) in
           print_endline (id ^ res ^ (if ign = "" then "" else ";IGNORED=" ^ ign));
           if reps > 0 then begin
             let t0 = Unix.gettimeofday () in
             for _ = 1 to reps do ignore (try compute year with _ -> "") done;
             total := !total +. (Unix.gettimeofday () -. t0); n := !n + reps
           end
     done with End_of_file -> ());
  if reps > 0 then Printf.eprintf "TIME %d evaluations, %.3f us/household\n" !n (1e6 *. !total /. float !n)
