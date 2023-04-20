import numpy as np                               
import sympy
import openpyxl
import pandas as pd
import datetime
from tqdm.auto import tqdm
import copy

'''Funcion para validar ingreso'''
def validacion_float(ingreso):
    while True:
        valor = input(ingreso)
        try:
            valor=float(valor)
            return valor
        except:
            print("\n¡VALOR INGRESADO NO VALIDO!\n")

#Funcion validar ingreso proxima
def validar_dato(a,b,texto):
    while True:
        try:
            valor = int(input(f"\nINGRESE {texto}: "))
            if valor>=a and valor<=b:
                break
            else:
                print(f"\n¡ERROR! INTERVALO VALIDO: [{texto}]\n")
        except ValueError:
            print(f"\n¡ERROR! EL VALOR DEBE SER ENTERO\n")
    return valor

"Funcion para el ingreso de datos de ensayo"
def ingreso_datos_ensayo(Array_Date):
    print("\n\n","INGRESE LOS DATOS DE ENSAYO Y FACTORES DE AJUSTE".center(100))
    temp_list = []
    for i in range(2):
        for e in range(1, 4):
            if i == 0:
                temp_list.append(validacion_float("* Modulo Elástico (E{}): ".format(e)))
            else:
                temp_list.append(validacion_float('* Deformacion Correlativa, idc{}{}: '.format(e, e - 1 if e == 3 else e + 1)))
        print()
    temp_list.extend([validacion_float('\n* Valor promedio de ancho (L1): '), validacion_float('* Factor de Ajuste incremental (λ): '), validacion_float('* Modulo Tracción (Et): '), validacion_float('* Resistencia Tracción (Ft): '),1,1,float(temp_list[0]/(2*(1+temp_list[3]))),float(temp_list[0]/(2*(1+temp_list[4]))),float(temp_list[1]/2/(1+temp_list[5]))])
    Array_Date.extend(temp_list) #L1 = 1; T = 1; G12; G13; G23

"Funcion de barra de carga"
def barra_carga():
    print("\n\n","CARGANDO...","\n\n")
    for i in tqdm(range(4000)):
        print("", end=("\r"))

'''Funcion para añadir datos al excel'''
def Agregar_datos_excel(Data_frame,nombre_hoja,H_Excel,Fec):
    H_Excel = pd.ExcelWriter(Fec,mode='a')
    Data_frame.to_excel(H_Excel, sheet_name=nombre_hoja, index=False)
    H_Excel.close()

'''Funcion de Matriz de Elementos'''
def M_E(x, y):
    M_elementos=[[x for x in range(1,x+1)]]
    for j in range(2, y+1):
        l_c=[]
        for i in range(M_elementos[-1][-1]+1, M_elementos[-1][-1]+x+1):
            l_c.append(i)
        M_elementos.append(l_c)
    M_elementos=np.array(M_elementos)
    return M_elementos

'''Funcion de String fecha'''
def fecha():
    T_de_M=datetime.datetime.now()
    T_de_Mstr=str(T_de_M.day)+"-"+str(T_de_M.month)+"-"+str(T_de_M.year)+" "+str(T_de_M.hour)+";"+str(T_de_M.minute)+";"+str(T_de_M.second)+".xlsx"
    return T_de_Mstr

'''Funcion de Matriz de Nodos'''
def M_N(x, y):
    M_Nodos=[[x for x in range(1,x+2)]]
    for j in range(2, y+2):
        l_c=[]
        for i in range(M_Nodos[-1][-1]+1, M_Nodos[-1][-1]+x+2):
            l_c.append(i)
        M_Nodos.append(l_c)
    M_Nodos=np.array(M_Nodos)
    return M_Nodos

'''Funcion de Tabla de Conectividad'''
def T_C(x,y,M_El,M_No):
    C_G_L={}
    for j in range(y):
        for i in range(x):
            C_G_L[M_El[j][i]]=[[M_No[j][i],M_No[j][i+1],M_No[j+1][i+1],M_No[j+1][i]],[(2*(M_No[j][i])-1),(2*(M_No[j][i])),(2*(M_No[j][i+1])-1),(2*(M_No[j][i+1])),(2*(M_No[j+1][i+1])-1),(2*(M_No[j+1][i+1])),(2*(M_No[j+1][i])-1),(2*(M_No[j+1][i]))]]
    return C_G_L

# Coordenadas Locales
def coord_loc(c_g_l,d_gn):
    c_l = []
    for i in c_g_l.keys():
        print("\nElemento N°{}: \nCoordenadas Globales: {} \nCoordenadas Locales: {} \nDistancias en X: {} \nDistancias en Y: {}".format(i,c_g_l[i][0],c_g_l[i][1],d_gn[i][0],d_gn[i][1]))
        for e in c_g_l[i][1]:
            c_l.append(e)
    return c_l

'''Distancias generales'''
def D_G(x,y,a,l):
    D_G_d = {}
    L_x = []
    L_y = []
    for j in range(1,y+1):
        for i in range(1,x+1):
            L_x.append([a*(i-1),a*i,a*i,a*(i-1)])
            L_y.append([l*(j-1),l*(j-1),l*j,l*j])
    for i in range(1,(x*y)+1):
        D_G_d[i]=[L_x[i-1],L_y[i-1]]
    return D_G_d
            
'''Transformacion Isoparametrica'''
def T_I(N_L,D_G, Xi, ita):
    d = {}
    for i in D_G.keys():
        xf = (D_G[i][0][0])*(N_L[0])+(D_G[i][0][1])*(N_L[1])+(D_G[i][0][2])*(N_L[2])+(D_G[i][0][3])*(N_L[3])
        yf = (D_G[i][1][0])*(N_L[0])+(D_G[i][1][1])*(N_L[1])+(D_G[i][1][2])*(N_L[2])+(D_G[i][1][3])*(N_L[3])
        dXfdXi= xf.diff(Xi)
        dXfdita= xf.diff(ita)
        dYfdXi= yf.diff(Xi)
        dYfdita= yf.diff(ita)

        d[i] = [xf,yf,dXfdXi,dXfdita,dYfdXi,dYfdita]
    return d

'''Jacobianos e inversas'''
def J_I_D(T_I):
    j_i_d = {}
    for i in T_I.keys():
        J=np.array([[float(2*(T_I[i][2])),float(2*(T_I[i][4]))],[float(2*(T_I[i][3])),float(2*(T_I[i][5]))]])
        Inv_J=np.linalg.inv(J)
        Det_J = np.linalg.det(J)
        j_i_d[i]=[J,Inv_J,Det_J]
    return j_i_d

'''Matrices A'''
def M_A(j_i_d):
    a = {}
    for i in j_i_d.keys():
        A = (1/j_i_d[i][2])*(np.array([[j_i_d[i][0][1,1],(-1)*(j_i_d[i][0][0,1]),0,0],[0,0,(-1)*(j_i_d[i][0][1,0]),j_i_d[i][0][0,0]],[(-1)*(j_i_d[i][0][1,0]),j_i_d[i][0][0,0],j_i_d[i][0][1,1],(-1)*(j_i_d[i][0][0,1])]]))
        a[i] = [A]
    return a

'''Matriz G'''
def M_G(x, y):
    G=(1/4)*(np.array([[(-1)*(1-y),0,(1-y),0,(1+y),0,(-1)*(1+y),0],[(-1)*(1-x),0,(-1)*(1+x),0,(1+x),0,(1-x),0],[0,(-1)*(1-y),0,(1-y),0,(1+y),0,(-1)*(1+y)],[0,(-1)*(1-x),0,(-1)*(1+x),0,(1+x),0,(1-x)]]))
    return G

'''Matrices B'''
def M_B(m_a,m_g, bt):
    b = {}
    for i in m_a.keys():
        m = np.array(np.dot(m_a[i],m_g))
        b[i] = m[0]
        bt[i]= np.transpose(m[0])
    return b

'''Matriz D'''
def M_D(D):
    matr_D= np.array([[D[2]/(1-D[4]*D[4]),D[4]*D[2]/(1-D[4]*D[4]),0],[D[4]*D[0]/(1-D[3]*D[3]),D[0]/(1-D[5]*D[3]),0],[0,0,(D[0]/(2*(1+D[3])))]])
    return matr_D

'''Matrices K'''
def M_K(b,bt,d,x,y,j_i_d,T,c_g_l):
    k = {}
    K = " "
    for t in b.keys():
        if t == 1:
            b_d=np.array(np.dot(d,b[t]))
            b_bt_d=np.array(np.dot(bt[t],b_d))
            M_p_k = []
            for j in range(8):
                L_x = []
                for i in range(8):
                    I_x = sympy.integrate(sympy.integrate(b_bt_d[i][j] , (x,-1,1)),(y,-1,1))
                    L_x.append(float(I_x))
                M_p_k.append(L_x)
            K = ((np.array(M_p_k))*(j_i_d[t][2])*T)
        M_d_k = pd.DataFrame(list(zip(K[:,0],K[:,1],K[:,2],K[:,3],K[:,4],K[:,5],K[:,6],K[:,7])),c_g_l[t][1],c_g_l[t][1])
        M_O_K = (M_d_k.sort_index(axis=0)).sort_index(axis=1)
        k[t]= M_O_K
    return k

'''Funcion de ensamble A'''
def f_e_A(M1,M2):
    for e in M1.index:
        if(e==M2.index[e-1]):
            for i in M1.columns:
                if(i==M2.columns[i-1]):
                    M2[e][i]+=M1[e][i]

'''Funcion de ensamble B'''
def f_e_B(M_N,K,T_C_L):
    Matriz_E=pd.DataFrame(list(zip()),T_C_L,T_C_L)
    Matriz_E=Matriz_E.fillna(0)
    for e in K.keys():
        f_e_A(K[e],Matriz_E)
    return Matriz_E

'''Funcion de armado'''
def armado(Lista1,Lista2,dicc,e):#K,C_L,Ke,elemento
    Lista1c=Lista1.copy()
    for i in range(len(Lista1)): 
        Lista1c[i].insert(0,Lista2[e][i])
    Lista2[e].insert(0,'-')
    Lista1c.insert(0,Lista2[e])    
    dicc[e+1]=Lista1c
    return dicc

'''Sistema de carga'''
def S_C(C,m_n,T_C_L):
    sist_c = (pd.DataFrame(list(zip()),T_C_L,[1])).fillna(0)
    CargaN = C/(2*len(m_n[0])-2)
    C_s=[]
    for j in range(0,-2,-1):
        lista = []
        for e in range(len(m_n[j])):
            if (e==0 or e==len(m_n[j])-1) and j==0:
                lista.append(-CargaN)
            elif (e==0 or e==len(m_n[j])-1)==False and j==0:
                lista.append(-2*CargaN)
            elif (e==0 or e==len(m_n[j])-1) and j==(-1):
                lista.append(CargaN)
            elif (e==0 or e==len(m_n[j])-1)==False and j==(-1):
                lista.append(2*CargaN)
        c_sc = pd.DataFrame(list(zip(lista)),2*m_n[j]-1,[1])
        C_s.append(c_sc)
    
    C_SCarga=pd.concat([C_s[0],C_s[1]])
    sist_c=(C_SCarga+sist_c).fillna(0)

    return sist_c

'''Deformaciones especificas'''
def D_E(Despz, alto, cant_ey):
    Su = 0
    count = 0
    for i in range(1,(Despz.index[-1])+1):
        if (Despz.index[i-1])%2==0:
            Su+=abs(Despz[0][i])
            count+=1

    D_e = Su*2/((alto*cant_ey)*count)
    return D_e


def B_valores(cl, B, Xi, ita):
    b_num = copy.deepcopy(B)
    contador = 0
    for i in range(4):
        for j in range(3):
            for h in range(8):
                b_num[i+1][j][h] = (((b_num[i+1][j][h]).subs(Xi,cl[contador])).subs(ita,cl[contador+1])) 
        contador+=2
    return b_num  

def sep_por_elem(x,x1,c_l):
    cargas = []
    c = 0
    paso = []
    for i in (x.index):
        paso.append(x1[1][i])
        c+=1
        if(c==8):
            cargas.append(paso)
            paso = []
            c = 0
    return cargas

def tens_m2(cx,cy,d,b_n,carg_pe):
    cant_recor = cx*cy ##cantidad de elementos
    dicc_ten = {}
    for i in range(cant_recor):
        dicc_ten_paso = {}
        for j in range(1,5):
            multp1 = np.dot(b_n[j],carg_pe[i]) #matriz B por las cargas del elemento
            multp2 = np.dot(multp1,d) #el resultado anteriror por D
            dicc_ten_paso[j] = multp2
        dicc_ten[i+1] = dicc_ten_paso
    return dicc_ten

def Tn(d,b,dz):
    pass

def deformac_tens(Dat_calc,i,matriz_nodos,matriz_ensablada,t_c_l,h_excel,fecha,coord_locales,alto,ancho,datos_ensayo,hx,vy,d,b_num):
    Carga = validacion_float("\nCarga (N): ")
    s_c = S_C(Carga,matriz_nodos,t_c_l)
    Agregar_datos_excel(s_c,"Sist. Q={}".format(Carga),h_excel,fecha)

    M_E_n = np.array(matriz_ensablada)
    M_E_ni = np.linalg.inv(M_E_n)

    Desplazamientos = pd.DataFrame(np.dot(M_E_ni,s_c),index=t_c_l)
    print(f"Desplazamientos sin ordenar Q {Carga}: \n{Desplazamientos}")

    D_e_o = pd.DataFrame([0.0 for i in range(len(coord_locales))],index=coord_locales)
    Sist_c_o = pd.DataFrame([0.0 for i in range(len(coord_locales))],index=coord_locales)

    for j in Desplazamientos.index:
        for e in D_e_o.index:
            if j == e:
                D_e_o[0][e] = Desplazamientos[0][e]
                Sist_c_o[0][e] = s_c[1][e] 

    Agregar_datos_excel(Sist_c_o,"Sist. ord. Q={}".format(Carga),h_excel,fecha)
    Agregar_datos_excel(D_e_o,"Desplaz. Q={}".format(Carga),h_excel,fecha)

    paso = D_e_o.copy() #Creo una copia del dataframe de desplzamientos
    Dat_calc['Desplazamientos'][i+1] = paso
    print(f"Desplazamientos ordenados Q {Carga}: \n{Dat_calc['Desplazamientos'][i+1]}")

    for h in range(1,(Desplazamientos.index[-1])+1):
        if h%2==0: 
            (D_e_o[0][h])/=alto
        else:
            (D_e_o[0][h])/=ancho

    paso2 = D_e_o.copy()
    Dat_calc['Desplazamientos_esp'][i+1] = paso2
    Agregar_datos_excel(Dat_calc['Desplazamientos_esp'][i+1],"Desplaz_esp. Q={}".format(Carga),h_excel,fecha)

    Dat_calc['tensiones_metodo1'][i+1] = paso2 = (D_e_o*datos_ensayo[0])
    Agregar_datos_excel(Dat_calc['tensiones_metodo1'][i+1],"tensiones. Q={}".format(Carga),h_excel,fecha)
    print(f"Tensiones Q {Carga}: \n{Dat_calc['tensiones_metodo1'][i+1]}")

    c_p_e = sep_por_elem(Sist_c_o,s_c,coord_locales)
    Dat_calc['cargas_por_elemento'][i+1] = c_p_e

    # Dat_calc['tensiones_metodo2'][i+1] = tens_m2(hx,vy,d,b_num,c_p_e) 

    D_especifica = D_E(Desplazamientos, alto, vy)
    print("\nLa Deformacion especifica es igual a: {}\n".format(D_especifica))

    # '''tensiones_m2 es un diccionario que como clave tiene el numero de todos los elementos
    # ej: un valor es 1, el otro 2 y asi hasta 100 que en este caso es nuestro ultimo elemento.
    # Cada uno de esas claves tiene otro diccionario como valor. Dicho diccionario contiene 4 pares
    # clave-valor, las claves son 1,2,3,4 (nodos) y como valor contienen una lista con las 3 tensiones'''