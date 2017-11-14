from __future__ import division
import itertools
import sys


def ruleFinding(s, c, datapath):
    '''
    Finds all rules in dataset with support > s and confidence > c.
        @param s: float (0<=s<=1) containing the support of the returned rules
        @param c: float (0<=s<=1) containing the confidence of the returned rules
        @param datapath: string containing path to file containing baskets data
        @return: (rules, rule_support, confidence)
            rules: list containing 2-tuples (X,Y) with rule X->Y with confidence >c and support >s
            rule_support: list containing for each rule the support level of such rule
            confidence: list containing for each rule the confidence level of such rule 
    '''
    print "Finding association rules"
    #First we find all frequent item sets with support > s
    freq, sup = frequentItemSets(s, datapath)
    rules = []
    rule_support = []
    confidence = []
    #Each frequent item set (S=X U Y) is a candidate for a rule.
    for i in range(len(freq)):
        #We skip item sets with 1 element
        if(len(freq[i])>1):
            #For each set S, we find all subsets X of all lengths
            #Since X is in S, sup(X)>=sup(S)>s and therefore X is in the 
            #large itemset (and we already computed it's support)
            for k in range(1,len(freq[i])):
                subsets = list(itertools.combinations(freq[i],k))
                #For each X candidate, we check if confidence is > c (sup(S)/sup(X)=sup(X U Y)/sup(X)>c)
                for X in subsets:
                    X=set(X)
                    idx = freq.index(X)
                    if(sup[i]/sup[idx]>c):
                        #Y = S\X
                        rules.append((X,freq[i]-X))
                        rule_support.append(sup[i])
                        confidence.append(sup[i]/sup[idx])
    
    print "Finished finding association rules"
    return rules, rule_support, confidence



def generateCk(L1, Lk_1):
    '''
    Generates all candidates of sets of size k using sets of size k-1 with support >s. Due to 
    the monotonicity of the support function, all k-sets with support >s must have all subsets
    of size k-1 with support >s too.
        @param L1: list of 1-dimensional sets with support >s (singletons with support >s)
        @param Lk_1: list of (k-1)-dimensional sets with support >s
        @return: list of all potential candidates of k-dimensional sets with support >s
    '''
    #C_{k+1}
    Ckp1=[]
    #for every k-1 size set, we add one element of L1 (which they all have support >s) to
    #generate all k set candidates with support >s
    for kset in Lk_1:
        #in each k-1 set we only need to add elements of higher value than the ones
        #in set, to avoid repeating k sets, since sets are unordered
        maxinSet = max(kset)
        for item in L1:
            item = next(iter(item))
            if (item>maxinSet):
                kp1Set = set(kset)
                kp1Set.add(item)
                Ckp1.append(kp1Set)
    return Ckp1

def generateAllkSets(line, k):
    '''
    From a line containing a basket information (set of items), return
    all possible subsets of size k for this basket.
        @param line: string containing a list of integers separated by space
        @param k: size of subsets to generate
        @return: list of all subsets of size k generated by elements in basket (line)
    '''
    basketStrings = line.split()
    basketItems = [int(it) for it in basketStrings]
    return list(itertools.combinations(basketItems,k))

def computeL1(s, data, frequent_items, freqit_support):
    '''
    Computes the list of single items with support >s.
        @param s: support threshold for items.
        @param data: file containing in each line a basket of items
        @param frequent_items: empty list to append single items to.
            The list intends to contain all frequent items with support >s.
        @param freqit_support: empty list to append support of items added in frequent_items
        @return: L1, total_baskets
            L1: single sets that have support >s
            total_baskets: total number of baskets in data
    '''
    max_item = 0
    #initial item size guess (should catch if there is overflow and resize array)
    counts = [0]*1000
    total_baskets = 0
    for line in data:
        basketItems = line.split()
        #for each element seen in the baskets increment its counter
        for item in basketItems:
            counts[int(item)] += 1
            if item > max_item:
                max_item = item
        total_baskets += 1
    
    L1 = []
    #Once we have all counts check which ones have support >s
    for i in range(int(max_item)+1):
        if counts[i]/total_baskets > s:
            L1.append({i})
            frequent_items.append({i})
            freqit_support.append(counts[i]/total_baskets)
            
    return L1, total_baskets

def frequentItemSets(s, datapath):
    '''
    Computes a list of all basket sets that have support >s
        @param s: support threshold
        @param datapath: string containing file path to data
            (each line in file should be a list of integers, where each integer is an item)
        @return: frequent_items, freqit_support
            frequent_items: list of all item sets that have support >s 
            freqit_support: support of each item set in frequent_items
    
    '''
    print "Computing frequent item sets with support higher than " + str(s) + " in dataset " + datapath
    data = open(datapath)
    
    frequent_items = []
    freqit_support = []
    print "Frequent items iteration 1" 
    L1, total_baskets = computeL1(s, data, frequent_items, freqit_support)
    print "Number of 1-sets with support > " +str(s)+": " + str(len(L1))
    Lk_1 = L1
    k = 2
    #at each iteration (with k) we are looking for the item sets of size k with support >s
    while True:
        print "Frequent items iteration " +  str(k)
        data.seek(0)
        #generate all candidate pairs from sets of size k-1 (we do this since all sets of
        #size k with support >s need to have all its subsets of support >s too (so we use
        #sets from previous iteration)
        Ck = generateCk(L1, Lk_1)
        print "Number of candidate " + str(k) + "-sets: " + str(len(Ck))

        #once there are no candidates we can stop our search for item sets
        n = len(Ck)
        if(n==0):
            break
        
        #for all candidate sets, we will count how many times they appear in data
        #to compute their support
        counts = [0]*n
        for line in data:
            #we look at all subsets of size k in each basket
            basketkSets = generateAllkSets(line, k)
            for kset in basketkSets:
                kset = set(kset)
                #we only consider sets that are in the candidate list, since the 
                #rest we know for sure they won't have support >s
                if kset in Ck:
                    idx = Ck.index(kset)
                    counts[idx] += 1
        
        #with the counts for each candidate, we can compute support and keep the
        #sets with support >s
        Lk_1 = []  
        for i in range(n):
            if counts[i]/total_baskets > s:
                Lk_1.append(Ck[i])
                frequent_items.append(Ck[i])
                freqit_support.append(counts[i]/total_baskets)
        
        print "Number of " + str(k) + "-sets with support > "+str(s)+": " + str(len(Lk_1))
        k += 1
    
    data.close()
    print "Finished computing frequent item sets"
    print "Large itemset: "
    print frequent_items
    print "With support (>s): "
    print freqit_support
    return frequent_items, freqit_support


def main(s=0.4,c=0.5,datapath="test.dat"):
    print "Finding rules with support higher than " + str(s) + " and confidence higher than " + str(c) + " in dataset " + datapath
    rules, support, confidence = ruleFinding(s,c,datapath)
    print "All rules found: "
    for i in range(len(rules)):     
        print "Rule: " + str(rules[i][0]) + " -> " + str(rules[i][1]) + " with support " + str(support[i]) + " and confidence " + str(confidence[i])


try:
    main(float(sys.argv[1]),float(sys.argv[2]),sys.argv[3])
except:
    main()

    
    