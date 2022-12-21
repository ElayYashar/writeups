s = "abcdefghijklmnopqrstuvwxyz"
shift=0
encrypted="hcjqnnsotrrwnqc"

# Enter one char
k = input("Input a single word key :")
if len(k) > 1:
        print("Something bad happened!")
        exit(-1)

# {
#   The ord() function returns an integer representing the Unicode character.
#   res = ord('A')
#   print(res)
#   output 65
# }

# Gets decimal value of the char we entered on line 6
i = ord(k)

# Replaces in the abcd the char we entered with blank 
s = s.replace(k, '')

# Adds the abcd to the char we entered
s = k + s

# {
#    k = 'f'
#    abcdefghijklmnopqrstuvwxyz
#    22 abcdeghijklmnopqrstuvwxyz
#    34 fabcdeghijklmnopqrstuvwxyz
# }

# Takes another input a string
t = input("Enter the string to Encrypt here:")

# Gets the length of the string we entered and goes into a loop while the length
# isn't equal to 0
li = len(t)
print("Encrypted message is:", end="")


while li != 0:
        # for char in string (we entered, line 35)
        for n in t:
                # Gets the decimal of the first char
                j = ord(n)
                if j == ord('a'):
                        j = i
                        print(chr(j), end="")
                        li = li - 1

                elif n > 'a' and n <= k:
                        j = j - 1
                        print(chr(j), end="")
                        li = li - 1

                elif n > k:
                        print(n, end="")
                        li = li - 1

                elif ord(n) == 32:
                        print(chr(32), end="")
                        li = li - 1

                elif j >= 48 and j <= 57:
                        print(chr(j), end="")
                        li = li - 1

                elif j >= 33 and j <= 47:
                        print(chr(j), end="")
                        li = li - 1

                elif j >= 58 and j <= 64:
                        print(chr(j), end="")
                        li = li - 1

                elif j >= 91 and j <= 96:
                        print(chr(j), end="")
                        li = li - 1

                elif j >= 123 and j <= 126:
                        print(chr(j), end="")
                        li = li - 1
