# Michael Lawrence
# CSC 447-001
# 2/6/2020

import sys
import os
import hashlib

def main():
    # validate arguments
    try:
        if os.path.exists(sys.argv[1]):
            target_hashes = open(sys.argv[1], errors="ignore")
        else:
            print("Error: Argument 1 path does not exist.")
            sys.exit(0)
        if os.path.exists(sys.argv[2]):
            word_list = open(sys.argv[2], errors="ignore")
        else:
            print("Error: Argument 2 path does not exist.")
            sys.exit(0)
    except Exception as e:
        print("Script format: lawrencemj-pwcracker.py [target_hash text file] [word list for cracking]")
        print(e)
        sys.exit(0)

    # Start hash comparison
    for x in target_hashes:
        word_list.seek(0)     # reset file pointer to start of file
        target = x.split(":")
        print("=" * 90)
        print("Attempting to break", target[0], "with", target[1][:-1], "hashing algorithm ...\n")
        result = cracker(target[1][:-1], target[0], word_list)
        if result[0] is not "":
            print("password found:", result[0], "\nTarget Hash:   ", target[0], "\nComputed Hash: ", result[1], "\n")
        else:
            print("password not found: not in given word_list.\n")

    # Closing files
    word_list.close()
    target_hashes.close()

# function: give it the hash algorithm name, the hash, and the word_list to compare it to.
#           Returns: ["password", "hash of password"] (returns "" if password cannot be found)
def cracker(hash_name, byte_string, word_list):
    password = ""
    hash = b""
    if hash_name == "md5" or hash_name == "sha1" or hash_name == "sha512":
        # using exec() for python
        execute = "hashlib." + hash_name + "()"
        for plain in word_list:
            hasher = eval(execute)
            hasher.update(plain[:-1].encode())

            if byte_string == hasher.hexdigest():
                password = plain[:-1]
                hash = hasher.hexdigest()
                break
    else:
        print("Hash Algorithm could not be found.")

    return [password, hash] # returns "" if not found

if __name__ == "__main__":
    main()