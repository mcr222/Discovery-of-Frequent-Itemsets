from __future__ import division
import itertools

# If a set has support of less than cs, then the support of any rule with items of the set can't be larger than s and
# the confidence be greater than c at the same time.
def ruleFinding(s, c, datapath):
    freq, sup = frequentItemSets(s, datapath)
    print "Large itemset"
    print freq
    rules = []
    for i in range(len(freq)):
        if(len(freq[i])>1):
            for k in range(1,len(freq[i])):
                subsets = list(itertools.combinations(freq[i],k))
                for X in subsets:
                    X=set(X)
                    idx = freq.index(X)
                    if(sup[i]/sup[idx]>c):
                        rules.append((X,freq[i]-X))
    
    return rules



def generateCk(L1, Lk_1):
    #C_{k+1}
    Ckp1=[]
    for kset in Lk_1:
        maxinSet = max(kset)
        for item in L1:
            item = next(iter(item))
            if (item>maxinSet):
                kp1Set = set(kset)
                kp1Set.add(item)
                Ckp1.append(kp1Set)
    return Ckp1

def generateAllkSets(line, k):
    basketStrings = line.split()
    basketItems = [int(it) for it in basketStrings]
    return list(itertools.combinations(basketItems,k))

def computeL1(s, data, frequent_items, freqit_support):
    max_item = 0
    #initial item size guess (should catch if there is overflow and resize array)
    counts = [0]*100
    total_baskets = 0
    for line in data:
        basketItems = line.split()
        for item in basketItems:
            counts[int(item)] += 1
            if item > max_item:
                max_item = item
        total_baskets += 1
        
    L1 = []
    for i in range(int(max_item)+1):
        if counts[i]/total_baskets > s:
            L1.append({i})
            frequent_items.append({i})
            freqit_support.append(counts[i]/total_baskets)
            
    return L1, total_baskets

def frequentItemSets(s, datapath):
    data = open(datapath)
    
    frequent_items = []
    freqit_support = []
    L1, total_baskets = computeL1(s, data, frequent_items, freqit_support)
    Lk_1 = L1
    k = 2
#     print "L1"
#     print L1
    while True:
        data.seek(0)
        #generate all candidate pairs from previous sets
        Ck = generateCk(L1, Lk_1)
#         print "Ck"
#         print Ck
        n = len(Ck)
        if(n==0):
            break
        
        counts = [0]*n
        for line in data:
            basketkSets = generateAllkSets(line, k)
            for kset in basketkSets:
                kset = set(kset)
                if kset in Ck:
                    idx = Ck.index(kset)
                    counts[idx] += 1
        
        Lk_1 = []  
        for i in range(n):
            if counts[i]/total_baskets > s:
                Lk_1.append(Ck[i])
                frequent_items.append(Ck[i])
                freqit_support.append(counts[i]/total_baskets)
#         print "Lk_1"
#         print Lk_1
        k += 1
    
    data.close()
    return frequent_items, freqit_support


def main():
#     print generateCk([{1},{2},{3},{4},{5}], [{3,2},{4,1}])
#     with open("test.dat") as data:
#         frequent_items = []
#         L1 = computeL1(0.2,data, frequent_items)
#         print L1
#         print frequent_items
#         print generateCk(L1, L1)
#     freq, sup = frequentItemSets(0.5, "test.dat")
#     print "Results: "
#     print freq
#     print sup

    rules = ruleFinding(0.5, 0.5, "test.dat")
    print "Results:"
    print rules
    
main() 
    
    