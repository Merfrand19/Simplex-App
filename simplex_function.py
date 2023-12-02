import streamlit as st
def simplexe(fonction_objectif: list, contraintes: list, type_probleme="max"):
  from sympy import symbols, Q, oo, zoo, Rational
  import pandas as pd

  for i in range(len(fonction_objectif)):
    fonction_objectif[i] = Rational(fonction_objectif[i]).limit_denominator(10**12)
  for contrainte in contraintes:
     contrainte[:-2] = [Rational(x).limit_denominator(10**12) for x in contrainte[:-2]]
     contrainte[-1] = Rational(contrainte[-1]).limit_denominator(10**12)
  for contrainte in contraintes:
    if contrainte[-1] < 0:
      contrainte[:-2] = [-x for x in contrainte[:-2]]
      contrainte[-1] = - contrainte[-1]
      if contrainte[-2] == "<=":
        contrainte[-2] = ">="
      elif contrainte[-2] == ">=":
        contrainte[-2] = "<="

  colonnes = []
  contenu = []
  var_de_bases = []
  bases_coef = {} #Variable pour renseigner sur les contraintes et les variables artificielles et/ou d'écart qu'elles engendrent
# Définition de la taille du tableau des variables d'écarts et initialisation du nombre de variable d'activités (x1, x2, etc)
  for i in range(len(contraintes)):
    var_de_bases.append(i)
    bases_coef[i] = [] #Initialisation de la variable avec des valeurs "tableau vide" pour chaque contrainte
  nbr_variables_activites = len(fonction_objectif)
  nbr_var_ecart = 0
# Initialisation des en-têtes des variables d'activités dans les cases de la colonne
  for i in range(nbr_variables_activites):
    colonnes.append(f"x{i+1}")

# Déclaration des variables d'écarts, initialisation de la variable nbr_var_ecart
  i = 0
  j = 0
  for contrainte in contraintes:
    if (contrainte[-2] == ">=") or (contrainte[-2] == "<=") :
      i = i + 1
      colonnes.append(f"e{i}")
      bases_coef[j].append(f"e{i}") #Enregistrement de la variable d'écart engendrée par la contrainte en position j
      if(contrainte[-2] == "<="):
        var_de_bases[j] = f"e{i}"
      nbr_var_ecart = nbr_var_ecart + 1
    j = j + 1
  i = 0
  j = 0
  for contrainte in contraintes:
    if (contrainte[-2] == ">=") or (contrainte[-2] == "="):
      i = i + 1
      colonnes.append(f"a{i}")
      var_de_bases[j] = f"a{i}"
      bases_coef[j].append(f"a{i}") #Enregistrement de la variable artificielle engendrée par la contrainte en position j
    j = j + 1
  colonnes.append("R")
  var_de_bases.append("Delta")


  for i in range(len(contraintes)):
    bases_coef[var_de_bases[i]] = bases_coef.pop(i, None) #remplacement des indices (servant de clés) par les variables de bases correspondantes

  position_contrainte = 0
  for contrainte in contraintes:
    ligne_contrainte = contrainte[:-2]
    for _ in range(len(colonnes) - len(ligne_contrainte) - 1):
      ligne_contrainte.append(0)
    ligne_contrainte.append(contrainte[-1])
    contenu.append(ligne_contrainte)
  ligne_objectif = fonction_objectif


  for _ in range(len(colonnes) - len(ligne_objectif) - 1):
      ligne_objectif.append(0)
  M = symbols("M", domain=Q.positive(oo))
  for i in range((nbr_variables_activites + nbr_var_ecart), len(ligne_objectif)):
    if(type_probleme == "max"):
      ligne_objectif[i] = -M
    elif(type_probleme == "min"):
      ligne_objectif[i] = M
  ligne_objectif.append(0)
  contenu.append(ligne_objectif)
  tableau_initial = pd.DataFrame(contenu, index=var_de_bases, columns=colonnes)
  for i in var_de_bases[:-1]:
    if len(bases_coef[i])==2:
      tableau_initial.loc[i, bases_coef[i][0]] = -1
      tableau_initial.loc[i, bases_coef[i][1]] = 1
    elif len(bases_coef[i])==1:
      tableau_initial.loc[i, bases_coef[i][0]] = 1

  print("---------------SIMPLEX SOLVER BY GROUPE N°3 GEI-IT INSTI---------------")
  if type_probleme == "max":
    probleme = "maximisation"
  elif type_probleme == "min":
    probleme = "minimisation"
  print(f"Problème de {probleme}________________\nTableau initial:")
  #print(tableau_initial)
  st.dataframe(tableau_initial)

  if any('a1' in col for col in tableau_initial.columns):
    st.markdown("## Existence de variable artificielle au sein du problème:")
    print("\nExistence de variable artificielle au sein du problème: \nTableau intermédiaire:\n")
    vecteur_colonne = []
    for i in tableau_initial.index[:-1]:
      vecteur_colonne.append(tableau_initial.loc["Delta",i])
    for colonne in tableau_initial.columns:
      somme_intermediaire=0
      colonne_active = tableau_initial.loc[:, colonne]
      for i in range(len(vecteur_colonne)):
         somme_intermediaire = somme_intermediaire + colonne_active.iloc[i] * vecteur_colonne[i]
      tableau_initial.loc["Delta", colonne] = tableau_initial.loc["Delta", colonne] - somme_intermediaire
    print(tableau_initial)
    st.dataframe(tableau_initial)


  copie = tableau_initial.iloc[-1, :-1].copy(deep=True)
  for i in range(len(copie)):
    if type(copie.iloc[i]).__name__=="Add" or  type(copie.iloc[i]).__name__=="Mul" or  type(copie.iloc[i]).__name__=="Symbol" :
      copie.iloc[i] = copie.iloc[i].subs(M, 1e100)
  copie = copie.astype(float)
  if type_probleme == 'max':
    col_pivot = copie.argmax()
  elif type_probleme == 'min':
    col_pivot = copie.argmin()
  continuer = False
  if type_probleme == 'max':
    continuer = any(copie > 0)
  elif type_probleme == 'min':
    continuer = any(copie < 0)

  n_iteration = 0
  programme_interrompu = False
  while continuer:
    try:
      n_iteration = n_iteration + 1
      l, c = tableau_initial.shape
      R = pd.Series(index=range(len(tableau_initial.iloc[:, col_pivot])), dtype='float64')
      for i in range(len(tableau_initial.iloc[:, col_pivot])):
        R.iloc[i] = tableau_initial.iloc[:, c - 1].iloc[i] / tableau_initial.iloc[:, col_pivot].iloc[i]
        if R.iloc[i] == zoo:
          R.iloc[i] = oo
      R = R.iloc[:-1]
      R_positif = R[R > 0]
      ligne_pivot = R[R == R_positif.min()].index[0]

      if (tableau_initial[tableau_initial.columns[col_pivot]][:-1] <=0).all():
        print(f"Problème à solution infinie. {tableau_initial.columns[col_pivot]} n'admet aucune limite sur sa valeur d'entrée!")
        st.write(f"Problème à solution infinie.{tableau_initial.columns[col_pivot]} n'admet aucune limite sur sa valeur d'entrée!")
        break

      #print(f"Variable entrante: {tableau_initial.columns[col_pivot]}")
      st.write(f"Variable entrante: {tableau_initial.columns[col_pivot]}")
      #print(f"Variable sortante: {tableau_initial.index[ligne_pivot]}")
      st.write(f"Variable sortante: {tableau_initial.index[ligne_pivot]}")
      #print(f"Pivot: {tableau_initial.iloc[ligne_pivot, col_pivot]}\n")
      st.write(f"Pivot: {tableau_initial.iloc[ligne_pivot, col_pivot]}\n")
      #print(f"Itération n°{n_iteration}")
      st.write(f"Itération n°{n_iteration}")
      for i in range(l):
          if i == ligne_pivot:
              continue
          o = tableau_initial.iloc[i, col_pivot]
          for j in range(c):
            tableau_initial.iloc[i, j] = tableau_initial.iloc[i, j] - (o / tableau_initial.iloc[ligne_pivot, col_pivot]) * tableau_initial.iloc[ligne_pivot, j]
      p = tableau_initial.iloc[ligne_pivot, col_pivot]

      tableau_initial.iloc[ligne_pivot, :] = tableau_initial.iloc[ligne_pivot, :] / p

      label_string_col = tableau_initial.columns[col_pivot]
      tableau_initial = tableau_initial.rename(index={tableau_initial.index[ligne_pivot]: label_string_col})

      colonnes_a_verifier = [col for col in tableau_initial.columns if col.startswith('a')]
      lignes_presentes = tableau_initial.index.tolist()
      colonnes_a_retirer = [col for col in colonnes_a_verifier if col not in lignes_presentes]
      tableau_initial = tableau_initial.drop(columns=colonnes_a_retirer)

      print(tableau_initial)
      st.dataframe(tableau_initial)

      copie = tableau_initial.iloc[-1, :-1].copy(deep=True)
      for i in range(len(copie)):
        if type(copie.iloc[i]).__name__=="Add" or  type(copie.iloc[i]).__name__=="Mul" or  type(copie.iloc[i]).__name__=="Symbol":
          copie.iloc[i] = copie.iloc[i].subs(M, 1e100)
      copie = copie.astype(float)
      if type_probleme == 'max':
        col_pivot = copie.argmax()
      elif type_probleme == 'min':
        col_pivot = copie.argmin()
      if type_probleme == 'max':
        continuer = any(copie > 0)
      elif type_probleme == 'min':
        continuer = any(copie < 0)
    except Exception as e:
      print(f"Exception : {e}")
      st.write("Exception : {e}")
      programme_interrompu = True
      st.write("Quelque chose s'est mal passé!!")
      print("Quelque chose s'est mal passé!!")
  else:
    if ~programme_interrompu:
      print(f"\nFin des itérations! Aucun problème rencontré\n  Solutions:")
      st.write(f"\nFin des itérations! Aucun problème rencontré\n  Solutions:")
      for variable in colonnes[:nbr_variables_activites]:
        try:
          print(f"    {variable} = {tableau_initial.loc[variable, 'R']}")
          st.markdown(f"### {variable} = {tableau_initial.loc[variable, 'R']}" )
        except KeyError:
          print(f"    {variable} = 0")
          st.markdown(f"###  {variable} = 0" )
      print(f"    Z {type_probleme} = {- tableau_initial.loc['Delta', 'R']}")
      st.markdown(f"### Z {type_probleme} = {- tableau_initial.loc['Delta', 'R']}" )
