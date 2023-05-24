from DiscordDataNinja import DiscordDataNinja
import os

ddn = DiscordDataNinja()

print("""Discord Data Ninja development stage testing interface (v0.1)

""")
print("""--- This program is purely for testing and might not support all the functions of Discord Data Ninja.
Full predictable operation of this program is NOT guranteed! Use at your own risk! Don't use for critical
and/or important files! ---""")

agreed = str(input("Please type (Y)es if you understand: ")).lower()
if agreed == "yes" or agreed == "y":
    pass
else:
    exit()
while True:                                                           
    os.system("cls")
    print("""Discord Data Ninja development stage testing interface (v0.1)

    """)
    print("""Options:

    1) Split file
    2) Assemble chunks

    """)
    choice = str(input(":"))

    if choice == "1":
        os.system("cls")
        filePath = str(input("Please drag and frop the file: "))
        if filePath[0] == '"' and filePath[-1] == '"':
            filePath = filePath[1:-1]

        ddn.createChunks(filePath)

    elif choice == "2":
        os.system("cls")
        print("""Please drag and drop each of the chunk files one by one, pressing enter after each. Type 'c' and enter when done.
    Files can be input at any order.""")
        chunkList = []
        while True:
            chunkPath = input("Please drag and drop the file").lower()
            if chunkPath == "c":
                break
            else:
                chunkList.append(chunkPath)

        ddn.assembleChunks(chunkList)

    else:
        print("Option not valid!")

print("Press any key...")