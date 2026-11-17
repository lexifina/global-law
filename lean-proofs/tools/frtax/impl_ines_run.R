# INES (Insee-Drees-Cnaf microsimulation model, R, CeCILL 2.1): run its income-tax chain (07_impot_revenus.R:
# calcule_rbg -> calcule_charges -> calcule_part -> calcule_eligible_prelev_forf -> calcule_prelev_forf ->
# calcule_deduc -> calcule_impot_du) on our 2042-box returns, bypassing the ERFS survey data.
# usage: Rscript impl_ines_run.R <ines checkout> <in.json> <out.json>
#   in.json: [{id, year (income year), boxes:{BOX: value}}]; out.json: [{id, ...INES foyer variables}]
# Tables built here, as INES builds them from the ERFS (03_init_cases_fiscales.R, 06_evol_revenus.R):
#   erfs_foyer_fiscaux_an       one row per return: idfoyer, annee (= income year), annee_impot (= annee + 1), sif_*
#   erfs_foyer_cf_indivi_an     long table of personal boxes: idfoyer, coldec (1, 2, 3.. = declarant, spouse, dependants)
#   erfs_foyer_cf_non_indivi_an long table of household boxes
# Box labels (detail_contenu) come from INES's own dictionary (parametres/dictionnaire_cases_fiscales_rev2021.xlsx).
args <- commandArgs(TRUE)
ines <- normalizePath(args[1]); inp <- normalizePath(args[2]); outp <- file.path(normalizePath(dirname(args[3])), basename(args[3]))
suppressMessages({library(dplyr); library(tidyr); library(collapse); library(jsonlite); library(readxl)})
setwd(ines)
source("R/fonctions_utiles.R")
# 07_impot_revenus.R is used unchanged except that calcule_impot_du also returns its intermediate figures (tax after
# the QF cap, décote, tax after décote, CEHR) for comparison: the select() of its return gains columns.
src07 <- paste(readLines("R/07_impot_revenus.R", warn = FALSE), collapse = "\n")
patched <- sub("select(idfoyer, annee, credit, cred_impetr, impot_du,",
               paste("select(idfoyer, annee, credit, cred_impetr, impot1, impotssqf, impot2, decote1, impot3, impot4,",
                     "impot5, impot6, impot9, impot10, cehr, impot_du,"), src07, fixed = TRUE)
stopifnot(patched != src07)
eval(parse(text = patched))
options(warn = -1)

p_m <- list(anleg = 2025, anref = 2023)
profondeur_historique <- 6
# as 01_initialisation.R: legislation years (annee = year the tax is paid) 2019-2025, NA -> 0, names prefixed pm_
param <- rbind(import_param("param_prelev", c("IR", "TH", "cotis", "Imput", "smic", "ISF"), annee = 2025, profondeur = 6),
               import_param("param_baseERFS", "base", annee = 2025, paramanleg = FALSE, profondeur = 6),
               import_param("derive_revenu", "param_derive", 2023, paramanleg = FALSE, profondeur = 4))
param <- rbind(param, param |> filter(nom %in% c("smich", "tpstra")) |> arrange(annee) |> group_by(annee) |>
                 summarise(valeur = prod(valeur) * 52 / 12) |> mutate(nom = "smic_brut"))
param <- param |> mutate(valeur = replace_na(valeur, 0), nom = paste0("pm_", nom)) |> distinct(nom, annee, .keep_all = TRUE)

# INES's own dictionary for every form year (maj_dico_cases_fiscales, 03_init_cases_fiscales.R: the 2021 dictionary
# carried forward by its yearly passage functions; 'annee' = income year), built once and cached.
dico_cache <- file.path(Sys.getenv("HOME"), "fr/runs/impl/ines/dico_years.rds")
if (!file.exists(dico_cache)) {
  source("R/03_init_cases_fiscales.R"); chemin <- list(param = "parametres/")
  saveRDS(maj_dico_cases_fiscales(list(anleg = 2025, anref = 2023))$dico_cases_fiscales, dico_cache)
}
dico <- readRDS(dico_cache) |> mutate(annee = as.numeric(annee))
labs07_all <- gsub('"', "", unique(regmatches(src07, gregexpr('"(2042[^"]*)"', src07))[[1]]))
# Which of our boxes the tax chain reads, per income year: a box counts only if its label for that year occurs in 07
if (length(args) > 3 && args[4] == "--used-boxes") {
  write_json(dico |> filter(detail_contenu %in% labs07_all) |> distinct(annee, case_fiscale, concerne, detail_contenu), outp, auto_unbox = TRUE)
  quit(save = "no")
}
# Labels created after the 2021 form (INES adds them with its yearly passage functions, maj_dico_cases_fiscales):
# every label the tax chain asks for is added so that its existence checks pass; no box of ours maps to them.
labels07 <- unique(regmatches(src07, gregexpr('"(2042[^"]*)"', src07))[[1]])
labels07 <- gsub('"', "", labels07)
dico_cases_fiscales <- bind_rows(dico, tibble(detail_contenu = setdiff(labels07, dico$detail_contenu)))
lab <- dico |> distinct(annee, case_fiscale, concerne, detail_contenu)

cases <- fromJSON(inp, simplifyVector = FALSE)
SIF_FLAGS <- c(L = "0AL", N = "0AN", P = "0AP", F = "0AF", W = "0AW", S = "0AS", G = "0AG", T = "0BT", Z = "0AZ")
foy <- list(); indiv <- list(); nonind <- list(); ind <- list()
unknown <- c()
for (i in seq_along(cases)) {
  c <- cases[[i]]; b <- c$boxes; y <- c$year
  g <- function(k) if (is.null(b[[k]])) 0 else as.numeric(b[[k]])
  mcdv <- if (g("0AM") > 0) "M" else if (g("0AO") > 0) "O" else if (g("0AV") > 0) "V" else if (g("0AD") > 0) "D" else "C"
  row <- list(idfoyer = i, annee = y, annee_impot = y + 1, sif_mcdv = mcdv,
              sif_nbf = g("0CF"), sif_nbg = g("0CG"), sif_nbr = g("0CR"), sif_nbj = g("0DJ"), sif_nbn = g("0DN"),
              sif_nbh = g("0CH"), sif_nbi = g("0CI"),
              aged = if (g("0DA") > 0) y - g("0DA") else 0, agec = if (g("0DB") > 0) y - g("0DB") else 0,
              anaisd = g("0DA"), anaisc = g("0DB"))
  for (f in names(SIF_FLAGS)) row[[paste0("sif_case", tolower(f))]] <- if (g(SIF_FLAGS[[f]]) > 0) f else "0"
  foy[[i]] <- row
  for (k in names(b)) {
    if (grepl("^0", k)) next
    cf <- paste0("c_", tolower(k)); l <- lab[lab$case_fiscale == cf & lab$annee == y, ]
    if (nrow(l) == 0) { unknown <- c(unknown, k); next }
    l <- l[1, ]
    v <- as.numeric(b[[k]])
    if (l$concerne == "Foyer") {
      nonind[[length(nonind) + 1]] <- list(idfoyer = i, annee = y, annee_impot = y + 1, case_fiscale = cf,
                                           detail_contenu = l$detail_contenu, value = v)
    } else {
      cd <- if (l$concerne == "Declarant 1") 1 else if (l$concerne == "Declarant 2") 2 else
        2 + as.integer(sub("\\D*", "", l$concerne))
      indiv[[length(indiv) + 1]] <- list(idfoyer = i, coldec = as.character(cd), annee = y, annee_impot = y + 1, case_fiscale = cf,
                                         detail_contenu = l$detail_contenu, value = v)
    }
  }
  for (cd in 1:10) {  # declarant, spouse, dependants 1..8 (rows with no box are all zero)
    ind[[length(ind) + 1]] <- list(idfoyer = i, coldec = as.character(cd), annee = y, annee_impot = y + 1, treff_comp = 0)
  }
}
erfs_foyer_fiscaux_an <- bind_rows(foy)
erfs_foyer_cf_indivi_an <- if (length(indiv)) bind_rows(indiv) else
  tibble(idfoyer = integer(), coldec = character(), annee = numeric(), annee_impot = numeric(), case_fiscale = character(),
         detail_contenu = character(), value = numeric())
erfs_foyer_cf_non_indivi_an <- if (length(nonind)) bind_rows(nonind) else
  tibble(idfoyer = integer(), annee = numeric(), annee_impot = numeric(), case_fiscale = character(),
         detail_contenu = character(), value = numeric())
erfs_individus_fiscaux_an <- bind_rows(ind)
erfs_individu_an <- erfs_individus_fiscaux_an
erfs_individus_fiscaux_an <- erfs_individus_fiscaux_an |> select(-treff_comp)

run_step <- function(fn) {
  a <- mget(names(formals(fn)), envir = globalenv(), inherits = TRUE)
  res <- do.call(fn, a)
  for (n in names(res)) assign(n, res[[n]], envir = globalenv())
}
t0 <- Sys.time()
for (fn in c("calcule_rbg", "calcule_charges", "calcule_part", "calcule_eligible_prelev_forf", "calcule_prelev_forf",
             "calcule_deduc", "calcule_impot_du")) {
  run_step(get(fn))
}
t1 <- Sys.time()
o <- erfs_foyer_fiscaux_an
o$id <- vapply(cases, function(c) c$id, "")[o$idfoyer]
keep <- intersect(c("id", "annee", "npart", "pfu_n", "prelev_forf", "pf_liberatoire", "credit", "cred_pfo", "ae_elipfl", "abat_spec", "exo_hsup", "decote1", "impot5", "impot6", "impot9", "impot10", "plaf_qf", "reduc_qf", "rbg", "rng", "rib", "rfr", "impot1", "impotssqf",
                    "decot", "impot2", "impot3", "impot4", "impot_du", "impot_brut", "ired", "cehr", "impot_du_revdisp",
                    "impot_brutciri_brutppe", "ci_ri_tot_plaf", "ci_ri_tot_horsplaf", "pfo", "pfl"), names(o))
out <- list(seconds = as.numeric(difftime(t1, t0, units = "secs")), unknown_boxes = unique(unknown),
            columns = names(o), rows = o[, keep])
write_json(out, outp, digits = NA, auto_unbox = TRUE)
