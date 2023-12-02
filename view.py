import streamlit as st


st.set_page_config(
    page_title="Application Simplexe Groupe 3",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="auto", 
)

st.sidebar.title("Simplexe: Groupe3 GEI INSTI 23-24")
if 'variable_number' not in st.session_state:
    st.session_state.variable_number = 3
    
if 'constraint_number' not in st.session_state:
    st.session_state.constraint_number = 3

constraint_number=st.sidebar.number_input("Nombre de contraintes: ", step=1, min_value=2, max_value=50, value= st.session_state.constraint_number)
variable_number=st.sidebar.number_input("Nombre de variables: " ,step=1, min_value=2, max_value=50, value= st.session_state.variable_number)
st.info("Entrez les coefficients de la fonction objectif :")

st.session_state.variable_number = variable_number
st.session_state.constraint_number = constraint_number

colonne_variable=[None] * (variable_number+2)
x=[None] *  (variable_number)
i=0
with st.container():
    colonne_variable= st.columns(variable_number+2)
       # st.write(colonne_variable[i])
    for i in range(0, variable_number):
        with colonne_variable[i] :
            x[i]=st.text_input(f"x{i+1}",value=None, max_chars=9)
    with colonne_variable[-2] :
        st.markdown("<center><h1> → </h1></center>", unsafe_allow_html=True) 
    with colonne_variable[-1] :
        probleme = st.selectbox("Opération", {"max", "min"})    
   

st.info("Entrez les valeurs du système de contraintes :")

A=[ [None]*(variable_number)for _ in range(constraint_number) ]
i=0
colonne_variable=[None] * (variable_number+2)

colonne_variable= st.columns(variable_number+2)
for k in range(0, constraint_number):
    with st.container():
        # st.write(colonne_variable[i])
        for i in range(0, variable_number):
            with colonne_variable[i] :
                key = f"x{k}_{i}"
                A[k][i]=st.text_input(f"x{i+1}",value=None, max_chars=9, key=key)
        with colonne_variable[-2] :
            key__ = f"MaxMin{k}"
            A[k].append(st.selectbox("Opération", {"<=", "=", ">="}, key=key__))
        with colonne_variable[-1] :
            key____ = f"Res{k}"
            A[k].append(st.text_input("Resultat", key=key____))    

lancerAlgorithmeDeSimplex=st.button("Resoudre")

if lancerAlgorithmeDeSimplex:
    from simplex_function import simplexe
    simplexe(x, A, probleme)
