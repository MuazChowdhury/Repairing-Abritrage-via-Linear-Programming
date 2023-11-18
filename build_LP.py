import numpy as np
import pandas as pd
import constraints as cs

def build_Ab_1(m, n, N):
    A1=np.zeros((m,N))
    for i in range(m):
        A1[i,(i+1)*n -1 ]=1
    b1=np.zeros((m,1))
    return A1, b1

def build_Ab_2(strikes_norm, m, n, N):
    A2=np.zeros((N,N))
    np.fill_diagonal(A2, 1)
    np.fill_diagonal(A2[:, 1:], -1)
    A2 = np.delete(A2, [n*(i+1)-1 for i in range(m)], axis=0)
    b2=np.zeros((N-m,1))

    A2bis=np.zeros((m,N))
    b2bis=np.zeros((m,1))
    for i in range(m):
        A2bis[i,n*i]=1 
        b2bis[i]=1-strikes_norm.iloc[i,1]

    return A2bis, b2bis

def build_Ab_3(strikes_norm, m, n, N):
    A3=np.zeros((N-2*m,N))

    count=0
    for i in range(m):
        for j in range(1,n-1):
            coeff_j_minus_1=1/(strikes_norm.iloc[i,j] - strikes_norm.iloc[i,j-1])
            coeff_j_plus_1=1/(strikes_norm.iloc[i,j] - strikes_norm.iloc[i,j+1])
            A3[count][i*n+j-1]=coeff_j_minus_1
            A3[count][i*n+j]=coeff_j_plus_1 -coeff_j_minus_1        
            A3[count][i*n+j+1]=-coeff_j_plus_1   
            count+=1
    b3=np.zeros((N-2*m,1))

    return A3, b3

def build_A_4(): 
    pass

def build_Ab_5(strikes_norm, n, N):
    dictioI5= cs.create_index_dictionaryI(strikes_norm)
    s=sum(len(dictioI5[key]) for key in dictioI5.keys()) 
    A5=np.zeros((s,N))
    b5=np.zeros((s,1))
    count=0
    for key in dictioI5.keys():
        list_strikes=dictioI5[key]
        for x in list_strikes:
            A5[count,key[0]*n+ key[1]]=-1
            A5[count,x[0]*n+ x[1]]=1 
            count+=1 
    
    return A5, b5

def build_Ab_6_a(strikes_norm, n, N, dictio6a1, dictio6a2):
    sa1=sum(len(dictio6a1[key]) for key in dictio6a1.keys() if key[1]!=n-1) 
    A6a1=np.zeros((sa1,N))
    count=0
    for key in dictio6a1.keys():
        if key[1]!=n-1:
            list_strikes=dictio6a1[key]
            for x in list_strikes:
                den_i_j=1/(strikes_norm.iloc[key]-strikes_norm.iloc[x])
                den_is_js_p1=1/(strikes_norm.iloc[key[0],key[1]+1]-strikes_norm.iloc[key])
                A6a1[count,key[0]*n+ key[1]]=-(den_i_j + den_is_js_p1)
                A6a1[count,x[0]*n+ x[1]]=den_i_j
                A6a1[count,key[0]*n+ key[1]+1]=den_is_js_p1 
                count+=1 
    sa2=sum(len(dictio6a1[key]) for key in dictio6a1.keys() if key[1]>1) 
    A6a2=np.zeros((sa2,N))
    count=0
    for key in dictio6a1.keys():
        if key[1]>1:
            list_strikes=dictio6a1[key]
            for x in list_strikes:
                den_is_js_m1=1/(strikes_norm.iloc[key[0],key[1]-1]-strikes_norm.iloc[x])
                den_is_js_m2=1/(strikes_norm.iloc[key[0],key[1]-1]-strikes_norm.iloc[key[0],key[1]-2])
                A6a2[count,key[0]*n+ key[1]-1]=den_is_js_m1 - den_is_js_m2
                A6a2[count,key[0]*n+ key[1]-2]=den_is_js_m2 
                A6a2[count,x[0]*n+ x[1]]=-den_is_js_m1
                count+=1 
    sa3=sum(len(dictio6a2[key]) for key in dictio6a2.keys()) 
    A6a3=np.zeros((sa3,N))
    count=0
    for key in dictio6a2.keys():

        list_strikes=dictio6a2[key]
        for x in list_strikes:
            den_i_j=1/(strikes_norm.iloc[key[0],key[1]-1]-strikes_norm.iloc[key])
            den_is_js_m1=1/(strikes_norm.iloc[key]-strikes_norm.iloc[x])
            A6a3[count,key[0]*n+ key[1]-1]=den_i_j + den_is_js_p1
            A6a3[count,key[0]*n+ key[1]-2]=-den_i_j 
            A6a3[count,x[0]*n+ x[1]]=-den_is_js_p1
            count+=1 
    b6a1=np.zeros((sa1,1))
    b6a2=np.zeros((sa2,1))
    b6a3=np.zeros((sa3,1))

    return A6a1, A6a2, A6a3, b6a1, b6a2, b6a3

def build_Ab_6_b(strikes_norm, n, N, dictio6a1, dictio6a2):
    dictioI3 = cs.create_index_dictionaryI3(strikes_norm)
    dictioI4 = cs.create_index_dictionaryI4(strikes_norm)
    sa4=sum(len(dictio6a1[key])*len(dictioI3[key]) for key in dictio6a1.keys() if key[1]!=n-1) 
    A6b1=np.zeros((sa4,N))
    count=0
    for key in dictio6a1.keys():
        if key[1]!=n-1:
            list_strikes1=dictio6a1[key]
            list_strikes2=dictioI3[key]
            for x in list_strikes1:
                for y in list_strikes2:
                    den_i1_j1=1/(strikes_norm.iloc[key]-strikes_norm.iloc[x])
                    den_i2_j2=1/(strikes_norm.iloc[key]-strikes_norm.iloc[y])
                    A6b1[count,key[0]*n+ key[1]]=-den_i1_j1 + den_i2_j2
                    A6b1[count,x[0]*n+ x[1]]=den_i1_j1
                    A6b1[count,y[0]*n+ y[1]]=-den_i2_j2
                    count+=1

    sa5=sum(len(dictio6a2[key])*len(dictioI4[key]) for key in dictio6a2.keys()) 
    A6b2=np.zeros((sa5,N))
    count=0
    for key in dictio6a2.keys():
        list_strikes1=dictio6a2[key]
        list_strikes2=dictioI4[key]
        for x in list_strikes1:
            for y in list_strikes2:
                den_i1_j1=1/(strikes_norm.iloc[x]-strikes_norm.iloc[key])
                den_i2_j2=1/(strikes_norm.iloc[key]-strikes_norm.iloc[y])
                A6b1[count,key[0]*n+ key[1]]=den_i1_j1 + den_i2_j2
                A6b1[count,x[0]*n+ x[1]]=-den_i1_j1
                A6b1[count,y[0]*n+ y[1]]=-den_i2_j2
                count+=1
                
    b6b1=np.zeros((sa4,1))
    b6b2=np.zeros((sa5,1))

    return A6b1, A6b2, b6b1, b6b2

def build_Ab_6(strikes_norm, m, n, N):
    dictio6a1 = cs.create_index_dictionaryI(strikes_norm)
    dictio6a2 = cs.create_index_dictionaryI2(strikes_norm)
    
    A6a1, A6a2, A6a3, b6a1, b6a2, b6a3 = build_Ab_6_a(strikes_norm, n, N, dictio6a1, dictio6a2)
    A6b1, A6b2, b6b1, b6b2 = build_Ab_6_b(strikes_norm, n, N, dictio6a1, dictio6a2)

    return A6a1, A6a2, A6a3, b6a1, b6a2, b6a3, A6b1, A6b2, b6b1, b6b2

def build_Abc(strikes_norm, option_prices_norm):
    m=len(strikes_norm.index)
    n=len(strikes_norm.columns)
    N=n*m

    A1, b1 = build_Ab_1(m, n, N)
    A2, b2 = build_Ab_2(strikes_norm, m, n, N)
    A3, b3 = build_Ab_3(strikes_norm, m, n, N)
    
    A5, b5 = build_Ab_5(strikes_norm, n, N)
    A6a1, A6a2, A6a3, b6a1, b6a2, b6a3, A6b1, A6b2, b6b1, b6b2 = build_Ab_6(strikes_norm, m, n, N)

    # Need to add A4 and b4 when fixed
    A_opt = np.vstack((A1, A2, A3, A5, A6a1,A6a2,A6b1,A6b2))
    b_opt= np.vstack((b1, b2, b3, b5, b6a1,b6a2,b6b1,b6b2))
    c = option_prices_norm.values.flatten()

    return A_opt, b_opt, c

