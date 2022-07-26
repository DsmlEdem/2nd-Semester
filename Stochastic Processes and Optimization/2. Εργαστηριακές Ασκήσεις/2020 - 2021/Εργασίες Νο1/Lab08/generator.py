import random
import string
from random import randint


characters = string.ascii_lowercase + "0" + "1" + "2" + "3" + "4" + "5" + "6" + "7" + "8" + "9" + "-"
print("characters to choose from",characters)
text_file = open("invalid.txt","w")

names_generated = set()
fqdns_without_dups = 0

while fqdns_without_dups < 800000:
    label_size = randint(10,30)
    label = ""
    for i in range(0,label_size):
        char = random.choice(characters)
        if i == 0:
            while char == "-":
                char = random.choice(characters)
        label = label + char
        fqdn = label
    if fqdn not in names_generated:
        names_generated.add(fqdn)
        fqdns_without_dups = fqdns_without_dups + 1
        text_file.write(fqdn + '\n')
