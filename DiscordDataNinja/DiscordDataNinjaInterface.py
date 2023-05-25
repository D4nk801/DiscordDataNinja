#Discord Data Ninja development stage UI
#Copyright (C) 2023  Utku Turker

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <https://www.gnu.org/licenses/>.


from DiscordDataNinja import DiscordDataNinja
import os

#tkinter is used to open a file dialog
import tkinter.filedialog as tkfd

ddn = DiscordDataNinja()

print("""Discord Data Ninja development stage testing interface (v0.2)

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
        filePath = str(input("Please drag and frop the file (type f to open a file dialog): "))
        if filePath.lower() == 'f':
            filePath = tkfd.askopenfilename()

        if filePath[0] == '"' and filePath[-1] == '"':
            filePath = filePath[1:-1]

        ddn.createChunks(filePath)

    elif choice == "2":
        os.system("cls")
        print("""Please drag and drop each of the chunk files one by one, pressing enter after each. Type 'c' and enter when done.
    Files can be input at any order.""")
        chunkList = []
        while True:
            chunkPath = input("Please drag and drop the file (type f to open a file dialog): ").lower()
            if chunkPath == "c":
                break

            elif chunkPath == "f":
                chunkList = tkfd.askopenfilenames()
                break

            else:
                if chunkPath[0] == '"' and chunkPath[-1] == '"':
                    chunkList.append(chunkPath[1:-1])
                else:
                    chunkList.append(chunkPath)

        ddn.assembleChunks(chunkList)

    else:
        print("Option not valid!")

print("Press any key...")