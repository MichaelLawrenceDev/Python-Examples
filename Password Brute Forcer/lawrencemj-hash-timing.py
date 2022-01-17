# Michael Lawrence
# CSC 447.001
# 2/5/2020

import timeit
import hashlib
import functools
import os
import sys
from argon2 import PasswordHasher


def main():
    
    # Github copy of rockyou.txt, I do not have Kali Linux installed yet.
    # Utilizing 1000 passwords from rockyou for testing
    if os.path.exists("/usr/share/wordlist/rockyou.txt"):
        file = open("/usr/share/wordlist/rockyou.txt", errors="ignore")
    elif os.path.exists("rockyou.txt"):
        file = open("rockyou.txt", errors="ignore")
    else:
        print("Could not find file rockyou file.")
        sys.exit(0)
    rockyou = []

    for x in range(0, 500):
        rockyou.append(str(file.readline())[:-1])
    print("Done copying", len(rockyou), "passwords from rockyou.txt\n")

    hash_names = {"md5", "sha1", "sha512", "argon2"}
    for hash_name in hash_names:

        print("Starting timer for", hash_name, "hashing", len(rockyou),"passwords...")
        # using hashcode string, calculate average
        t = timeit.Timer(functools.partial(start_hash, hash_name, rockyou))
        hash_per_sec = len(rockyou) / t.timeit(1)
        print(hash_name, "hashing algorithm's calculated speed:% .2f hashes per second\n" %(hash_per_sec))

# encrypts plain txt, stores it in temp, and restarts.
def start_hash(hash_name, rockyou):
    if hash_name == "md5" or hash_name == "sha1" or hash_name == "sha512":
        # using exec() for python
        execute = "hashlib." + hash_name + "()"
        for plain in rockyou:
            hash = eval(execute)
            hash.update(plain.encode())
            temp = hash.hexdigest()
    elif hash_name == "argon2":
        for plain in rockyou:
            argon = PasswordHasher()
            temp = argon.hash(plain)
    else:
        print("error")


if __name__ == "__main__":
    main()

