import numpy as np
import pandas as pd

def beta(i1,j1,i2,j2,df_prices, df_strikes):
    return (df_prices.iloc[i1,j1]-df_prices.iloc[i2,j2])/(df_strikes.iloc[i1,j1]-df_strikes.iloc[i2,j2])

def S_f(i1,j1,i2,j2,df_prices,df_strikes):
    if df_strikes.iloc[i1,j1] > df_strikes.iloc[i2,j2]:
        return -beta(i1,j1,i2,j2,df_prices,df_strikes)
    elif df_strikes.iloc[i1,j1] == df_strikes.iloc[i2,j2]:
        return df_prices.iloc[i2,j2] - df_prices.iloc[i1,j1]
    else:
        raise ValueError('Invalid strikes')
    
def v_1(df_prices):
    return np.sum(df_prices.iloc[:,-1:] < 0).values[0]

def v_2(df_prices, df_strikes):
    df_prices_shift=df_prices.shift(-1,axis=1)
    df_strikes_shift=df_strikes.shift(-1,axis=1)
    arb_1=(df_prices-df_prices_shift)/(df_strikes-df_strikes_shift)

    return np.sum(np.sum(arb_1.iloc[:,1:]>0.01)) + np.sum(arb_1.iloc[:,0]<-1.01)

def v_3(df_prices,df_strikes):
    df1 = (df_prices.shift(-1,axis=1)-df_prices)/(df_strikes.shift(-1,axis=1)-df_strikes)
    df2 = -(df_prices.shift(1,axis=1)-df_prices)/(df_strikes.shift(1,axis=1)-df_strikes)
    df3 = df1 + df2
    return np.sum(np.sum(df3 < -0.001))

def v_4(df_prices,df_strikes):
    
    number_of_violations=0
    for i in range(len(df_prices)-1):
        for j in range(len(df_prices.columns)):
            mask= (df_prices.iloc[i+1, j]< df_prices.iloc[i,j])
            number_of_violations+=mask
      
    return number_of_violations
    

def create_index_dictionaryI(df_strikes):
    index_dict = {}
    m, n = df_strikes.shape

    for i_star in range(m):
        for j_star in range(1, n):
            key = (i_star, j_star)
            strikes_i_star_j_star = df_strikes.iloc[i_star, j_star - 1]
            strikes_i_star_j_star_plus_1 = df_strikes.iloc[i_star, j_star]


            mask = (df_strikes.iloc[i_star+1:, :] > strikes_i_star_j_star) & (df_strikes.iloc[i_star+1:, :] < strikes_i_star_j_star_plus_1)

            indices = list(zip(*np.where(mask)))
            indices=[(i+i_star+1,j) for (i,j) in indices]
            index_dict[key] = indices

    return index_dict


def create_index_dictionaryI2(df_strikes):
    index_dict = {}
    m, n = df_strikes.shape

    for i_star in range(m):

        key = (i_star, n-1)
        strikes_i_star_n = df_strikes.iloc[i_star, n-1]
        mask = (df_strikes.iloc[i_star+1:, :] > strikes_i_star_n)
        indices = list(zip(*np.where(mask)))
        indices=[(i+i_star+1,j) for (i,j) in indices]

        index_dict[key] = indices

    return index_dict

def create_index_dictionaryI3(df_strikes):
    index_dict = {}
    m, n = df_strikes.shape

    for i_star in range(m):
        for j_star in range(n-1):
            key = (i_star, j_star)
            strikes_i_star_j_star = df_strikes.iloc[i_star, j_star ]
            strikes_i_star_j_star_plus_1 = df_strikes.iloc[i_star, j_star+1]


            mask = (df_strikes.iloc[i_star+1:, :] > strikes_i_star_j_star) & (df_strikes.iloc[i_star+1:, :] < strikes_i_star_j_star_plus_1)

            indices = list(zip(*np.where(mask)))
            indices=[(i+i_star+1,j) for (i,j) in indices]
            index_dict[key] = indices


    return index_dict

def create_index_dictionaryI4(df_strikes):
    index_dict = {}
    m, n = df_strikes.shape

    for i_star in range(m):

        key = (i_star, n-1)
        strikes_i_star_n = df_strikes.iloc[i_star, n-1]
        strikes_i_star_n_minus_1 = df_strikes.iloc[i_star, n-2]

        mask = (df_strikes.iloc[i_star+1:, :] > strikes_i_star_n_minus_1) & (df_strikes.iloc[i_star+1:, :] < strikes_i_star_n)

        indices = list(zip(*np.where(mask)))
        indices=[(i+i_star+1,j) for (i,j) in indices]


        index_dict[key] = indices

    return index_dict

def v_5(df_prices,df_strikes):
    dictio=create_index_dictionaryI(df_strikes)
    number_of_violations=0
    for key in dictio.keys():
        kis_js=df_strikes.iloc[key]
        cis_js=df_prices.iloc[key]
        for elem2 in dictio[key]:
            ki_j=df_strikes.iloc[elem2]
            ci_j=df_prices.iloc[elem2]
            if -(cis_js - ci_j)/(kis_js- ki_j)<-0.0001:
                number_of_violations+=1 
    return number_of_violations

def v_6_a(df_prices,df_strikes):
    dictioI1=create_index_dictionaryI(df_strikes)
    dictioI2=create_index_dictionaryI2(df_strikes)
    n,m=df_strikes.shape
    number_of_violations=0
    for key in dictioI1.keys():
        if key[1]!=m-1:
            kis_js=df_strikes.iloc[key]
            cis_js=df_prices.iloc[key]
            kis_js1=df_strikes.iloc[(key[0],key[1]+1)]
            cis_js1=df_prices.iloc[(key[0],key[1]+1)]
            
            for elem2 in dictioI1[key]:
                ki_j=df_strikes.iloc[elem2]
                ci_j=df_prices.iloc[elem2]
                if -(cis_js - ci_j)/(kis_js- ki_j) + (cis_js1 - cis_js)/(kis_js1- kis_js) <-0.001:
                    number_of_violations+=1 
    for key in dictioI1.keys():
        if key[1]>1:
            kis_jsm1=df_strikes.iloc[(key[0],key[1]-1)]
            cis_jsm1=df_prices.iloc[(key[0],key[1]-1)]
            kis_jsm2=df_strikes.iloc[(key[0],key[1]-2)]
            cis_jsm2=df_prices.iloc[(key[0],key[1]-2)]
            
            for elem2 in dictioI1[key]:
                ki_j=df_strikes.iloc[elem2]
                ci_j=df_prices.iloc[elem2]
                if -(cis_jsm1 - cis_jsm2)/(kis_jsm1- kis_jsm2) + (cis_jsm1 - ci_j)/(kis_jsm1- ki_j) <-0.001:
                    number_of_violations+=1 
    for key in dictioI2.keys():

        kis_jsm1=df_strikes.iloc[key]
        cis_jsm1=df_prices.iloc[key]
        kis_jsm2=df_strikes.iloc[(key[0],key[1]-1)]
        cis_jsm2=df_prices.iloc[(key[0],key[1]-1)]

        for elem2 in dictioI2[key]:
            ki_j=df_strikes.iloc[elem2]
            ci_j=df_prices.iloc[elem2]
            if -(cis_jsm1 - cis_jsm2)/(kis_jsm1- kis_jsm2) + (cis_jsm1 - ci_j)/(kis_jsm1- ki_j) <-0.001:
                number_of_violations+=1 

    return number_of_violations

def v_6_b(df_prices,df_strikes):

    dictioI1=create_index_dictionaryI(df_strikes)
    dictioI2=create_index_dictionaryI2(df_strikes)
    dictioI3=create_index_dictionaryI3(df_strikes)
    dictioI4=create_index_dictionaryI4(df_strikes)

    n,m=df_strikes.shape
    number_of_violations=0
    for key in dictioI1.keys():
        if key[1]!=0 and key[1]!=m-1 :
            kis_js=df_strikes.iloc[key]
            cis_js=df_prices.iloc[key]
            for elem in dictioI1[key]:
                
                ki1_j1=df_strikes.iloc[elem]
                ci1_j1=df_prices.iloc[elem]

                for elem2 in dictioI3[key]:
                    ki2_j2=df_strikes.iloc[elem2]
                    ci2_j2=df_prices.iloc[elem2]
                    if -(cis_js - ci1_j1)/(kis_js- ki1_j1) + (cis_js - ci2_j2)/(kis_js- ki2_j2) <-0.0001:
                        number_of_violations+=1 

    for key in dictioI2.keys():

        kis_js=df_strikes.iloc[key]
        cis_js=df_prices.iloc[key]
        for elem in dictioI2[key]:

            ki1_j1=df_strikes.iloc[elem]
            ci1_j1=df_prices.iloc[elem]

            for elem2 in dictioI4[key]:
                ki2_j2=df_strikes.iloc[elem2]
                ci2_j2=df_prices.iloc[elem2]
                if -(cis_js - ci1_j1)/(kis_js- ki1_j1) + (cis_js - ci2_j2)/(kis_js- ki2_j2) <-0.0001:
                    number_of_violations+=1 

    return number_of_violations


def violation_count(df_prices,df_strikes):
    v1,v2,v3,v4,v5=v_1(df_prices),v_2(df_prices,df_strikes),v_3(df_prices,df_strikes),v_4(df_prices,df_strikes),v_5(df_prices,df_strikes)
    v6=v_6_a(df_prices,df_strikes)+v_6_b(df_prices,df_strikes)
    print("Number of outright violations: "+ str(v1))
    print("Number of vertical spread violations: "+ str(v2))
    print("Number of vertical butterfly violations: "+ str(v3))
    print("Number of calendar spread violations: "+ str(v4))
    print("Number of calendar vertical spread violations: "+ str(v5))
    print("Number of calendar butterfly violations: "+ str(v6))