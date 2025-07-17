import random
import DataSet as ds
import DBScan as db
import PatternComplexo as pc

def MAI_DAI():
    for k in range(1, 6):
        n = "00"+str(k)
        num_linhas = random.randint(1000, 9999)
        ds.main(n,num_linhas)
        n = "00"+str(k)+".csv"
        num_patterns = 3
        repetitions = 3
        pattern_size = 3
        pc.generate_random_patterns(n, n, num_patterns, repetitions, pattern_size)
        eps = None
        db.main(n, repetitions, eps)

if __name__ == "__main__":
    MAI_DAI()
