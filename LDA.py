# The entire LDA algo is compiled in one Simple function 
## Enjoy!!!

import numpy  as np
import pandas as pd
from nltk.tokenize import RegexpTokenizer
from random import randint

def lda_tm(document = [], K = 2, alpha = 0.12, eta = 0.01, iterations = 5000, dtm_matrix = False, dtm_bin_matrix = False, dtm_tf_matrix = False, dtm_tfidf_matrix = False, co_occurrence_matrix = False, correl_matrix = False):
    tokenizer = RegexpTokenizer(r'\w+')
    result_list = []
   
    # Corpus
    corpus = []
    for i in document:
        tokens = tokenizer.tokenize(i.lower())
        corpus.append(tokens)
    
    # Corpus ID
    corpus_id = []
    for i in document:
        tokens = tokenizer.tokenize(i.lower())
        corpus_id.append(tokens)
    
    # Unique Words
    uniqueWords = []
    for j in range(0, len(corpus)): 
        for i in corpus[j]:
            if not i in uniqueWords:
                uniqueWords.append(i)
       
    # Corpus ID for Unique Words   
    for j in range(0, len(corpus)): 
        for i in range(0, len(uniqueWords)):
            for k in range(0, len(corpus[j])): 
                if uniqueWords[i] == corpus[j][k]:
                    corpus_id[j][k]  = i  
    
    # Topic Assignment
    topic_assignment = []
    for i in document:
        tokens = tokenizer.tokenize(i.lower())
        topic_assignment.append(tokens)
    
    # dtm
    if dtm_matrix == True or dtm_bin_matrix == True or dtm_tf_matrix == True or dtm_tfidf_matrix == True or co_occurrence_matrix == True or correl_matrix == True:
        dtm = np.zeros(shape = (len(corpus), len(uniqueWords)))   
        for j in range(0, len(corpus)): 
            for i in range(0, len(uniqueWords)):
                for k in range(0, len(corpus[j])): 
                    if uniqueWords[i] == corpus[j][k]:
                        dtm[j][i]  = dtm[j][i] + 1
        dtm_pd = pd.DataFrame(dtm, columns = uniqueWords)
    
    if dtm_matrix == True:
        result_list.append(dtm_pd)
    
    # dtm_bin
    if dtm_bin_matrix == True or co_occurrence_matrix == True or correl_matrix == True:
        dtm_bin = np.zeros(shape = (len(corpus), len(uniqueWords)))  
        for i in range(0, len(corpus)): 
            for j in range(0, len(uniqueWords)):
                if dtm[i,j] > 0:
                    dtm_bin[i,j] = 1
        dtm_bin_pd = pd.DataFrame(dtm_bin, columns = uniqueWords)
    
    if dtm_bin_matrix == True:
        result_list.append(dtm_bin_pd)
    
    # dtm_tf
    if dtm_tf_matrix == True:
        dtm_tf = np.zeros(shape = (len(corpus), len(uniqueWords))) 
        for i in range(0, len(corpus)): 
            for j in range(0, len(uniqueWords)):
                if dtm[i,j] > 0:
                    dtm_tf[i,j] = dtm[i,j]/dtm[i,].sum()
        dtm_tf_pd = pd.DataFrame(dtm_tf, columns = uniqueWords)
        result_list.append(dtm_tf_pd)
    
    # dtm_tfidf
    if dtm_tfidf_matrix == True:
        idf  = np.zeros(shape = (1, len(uniqueWords)))  
        for i in range(0, len(uniqueWords)):
            idf[0,i] = np.log10(dtm.shape[0]/(dtm[:,i]>0).sum())
        dtm_tfidf = np.zeros(shape = (len(corpus), len(uniqueWords)))
        for i in range(0, len(corpus)): 
            for j in range(0, len(uniqueWords)):
                dtm_tfidf[i,j] = dtm_tf[i,j]*idf[0,j]
        dtm_tfidf_pd = pd.DataFrame(dtm_tfidf, columns = uniqueWords)
        result_list.append(dtm_tfidf_pd)
    
    # Co-occurrence Matrix
    if co_occurrence_matrix == True:
        co_occurrence = np.dot(dtm_bin.T,dtm_bin)
        co_occurrence_pd = pd.DataFrame(co_occurrence, columns = uniqueWords, index = uniqueWords)
        result_list.append(co_occurrence_pd)
    
    # Correlation Matrix
    if correl_matrix == True:
        correl = np.zeros(shape = (len(uniqueWords), len(uniqueWords)))
        for i in range(0, correl.shape[0]): 
            for j in range(i, correl.shape[1]):
                correl[i,j] = np.corrcoef(dtm_bin[:,i], dtm_bin[:,j])[0,1]
        correl_pd = pd.DataFrame(correl, columns = uniqueWords, index = uniqueWords)
        result_list.append(correl_pd) 
   
    # LDA Initialization
    for i in range(0, len(topic_assignment)): 
        for j in range(0, len(topic_assignment[i])): 
            topic_assignment[i][j]  = randint(0, K-1)
    
    cdt = np.zeros(shape = (len(topic_assignment), K))
    for i in range(0, len(topic_assignment)): 
        for j in range(0, len(topic_assignment[i])): 
            for m in range(0, K): 
                if topic_assignment[i][j] == m:
                    cdt[i][m]  = cdt[i][m] + 1
    
    cwt = np.zeros(shape = (K,  len(uniqueWords)))
    for i in range(0, len(corpus)): 
        for j in range(0, len(uniqueWords)):
            for m in range(0, len(corpus[i])):
                if uniqueWords[j] == corpus[i][m]:
                    for n in range(0, K):
                        if topic_assignment[i][m] == n:
                            cwt[n][j]  = cwt[n][j] + 1 
    
    # LDA Algorithm
    for i in range(0, iterations + 1): 
        for d in range(0, len(corpus)):
            for w in range(0, len(corpus[d])):
                initial_t = topic_assignment[d][w]
                word_num = corpus_id[d][w]
                cdt[d,initial_t] = cdt[d,initial_t] - 1 
                cwt[initial_t,word_num] = cwt[initial_t,word_num] - 1
                p_z = ((cwt[:,word_num] + eta) / (np.sum((cwt), axis = 1) + len(corpus) * eta)) * ((cdt[d,] + alpha) / (sum(cdt[d,]) + K * alpha )) 
                z = np.sum(p_z)
                p_z_ac = np.add.accumulate(p_z/z)   
                u = np.random.random_sample()
                for m in range(0, K):
                    if u <= p_z_ac[m]:
                        final_t = m
                        break
                topic_assignment[d][w] = final_t 
                cdt[d,final_t] = cdt[d,final_t] + 1 
                cwt[final_t,word_num] = cwt[final_t,word_num] + 1
        if i % 100 == 0:
            print('iteration:', i)
        
    theta = (cdt + alpha)
    for i in range(0, len(theta)): 
        for j in range(0, K):
            theta[i,j] = theta[i,j]/np.sum(theta, axis = 1)[i]
    
    result_list.append(theta)
        
    phi = (cwt + eta)
    d_phi = np.sum(phi, axis = 1)
    for i in range(0, K): 
        for j in range(0, len(phi.T)):
            phi[i,j] = phi[i,j]/d_phi[i]
     
    phi_pd = pd.DataFrame(phi.T, index = uniqueWords)
    result_list.append(phi_pd)
    
    return result_list

# I took some very simple examples and the terms are repeated out of context just to increase the score 
# As there are only 8 sentences

sen_1 = "Machine Learning technique data mining first favourite technique"
sen_2 = "Deep Learning technique data mining second favourite technique"
sen_3 = "Natural Language Processing technique third favourite technique"
sen_4 = "data mining technique fourth favourite technique"
sen_5 = "Sunday is chill day"
sen_6 = "Sunday is also free day"
sen_7 = "Sunday will play guitar"
sen_8 = "Natural technique is gruelling"
sen_9 = "Good indeed can thank"
sample = [sen_1, sen_2, sen_3, sen_4, sen_5, sen_6, sen_7, sen_8, sen_9]

# Call Function
lda = lda_tm(document = sample, K = 3, alpha = 0.12, eta = 0.01, iterations = 2500, co_occurrence_matrix = True)
print (lda)

# You can change parameters if you know how to. Good Luck!