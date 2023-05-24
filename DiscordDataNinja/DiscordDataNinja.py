import os
import math
import hashlib


class DiscordDataNinja:
    def __init__(self, MAX_FILE_SIZE = 26214400, MIN_HEADER_SIZE = 16, safeMode = True):
        self.MAX_FILE_SIZE = MAX_FILE_SIZE
        self.MIN_HEADER_SIZE = MIN_HEADER_SIZE

        #Disabling safe mode can cause the program to change constants, enable the program to act in a unpredicted or non user friendly manner. Some functionality may require 
        #safe mode to be turned off.
        self.safeMode = safeMode

    def createChunks(self, filePath):
        headerSize = self.MIN_HEADER_SIZE + len( (os.path.splitext(filePath))[1] )
        fileSize = os.path.getsize(filePath)
        fileChunkNumber = math.ceil( (fileSize + (headerSize * math.ceil( fileSize / self.MAX_FILE_SIZE ))) / self.MAX_FILE_SIZE )  

        #A soft limit to put in place to make sure the a really long file extension is not used. This can be disabled by initialising the class with safeMode = False.
        if headerSize > 255 and self.safeMode:
            raise RuntimeError("Woah! Something is wrong with your files! How long are your are your file extensions?!")

        #A soft limit to prevent a user from dividing a really large file into too many files. This also disables the 65536 hard chunk limit caused due to
        #the way the header structure is designed. This can be disabled by initialising the class with safeMode = False.
        if fileChunkNumber > 255 and self.safeMode:
            raise RuntimeError("Woah! Your files are too powerful, even for a ninja.")
        
        with open(filePath, "rb") as f:
            fileBytes = f.read()

            fileSHA256 = hashlib.sha256(fileBytes).hexdigest()
            fileShortSHA256 = fileSHA256[-8:]   #The last 4 bytes of the SHA256 hash of the file

            print(f"Your file will been seperated into {fileChunkNumber} pieces!")
            print(f"The SHA256 for the original file is: {fileSHA256}")        

            for chunkNumber in range(fileChunkNumber):
                chunkBytes = fileBytes[(chunkNumber * (self.MAX_FILE_SIZE - headerSize)) : ((chunkNumber + 1) * (self.MAX_FILE_SIZE - headerSize))] 
                
                chunkSHA256 = hashlib.sha256(chunkBytes).hexdigest()
                chunkShortSHA256 = chunkSHA256[-8:] #The last 4 bytes of the SHA256 hash of the chunk

                print(f"The SHA256 for chunk {chunkNumber} is {chunkSHA256}")

                chunkFileName = f"{os.path.dirname(filePath)}/chunk{chunkNumber}.ddn"

                headerBytes = [(bytes(".ddn", encoding="utf-8")),
                                (int(headerSize - 4).to_bytes(2, "big")),
                                (bytes((os.path.splitext(filePath))[1], encoding="utf-8")),
                                (int(chunkNumber).to_bytes(2, "big")),
                                (int(fileShortSHA256, 16).to_bytes(4, "big")),
                                (int(chunkShortSHA256, 16).to_bytes(4, "big"))]

                with open(chunkFileName, "wb") as outFile:
                    for i in headerBytes:
                        outFile.write(i)

                    outFile.write(chunkBytes)
                    outFile.close()
            
            f.close()
            
            return(True)
            #print("Operation Success")
    

    #TODO: Check for hash to make sure the data is intact for the final file (chunk check is done)
    #This function is not super efficient. Could be improved in the future. I cannot be bothered right now. 
    def assembleChunks(self, filePathsList):
        chunkList = []
        inFileHeaderLength = 0
        outFileExt = 0
        outFileName = ""

        #Organise the files so it can be reconstructed correctly
        for chunkFile in filePathsList:
            with open(chunkFile, "rb") as f:
                chunkBytes = f.read()
                chunkInfo = self.readHeader(chunkBytes)
                chunkList.insert(chunkInfo[2], chunkFile)

                inFileHeaderLength = chunkInfo[0]
                outFileExt = chunkInfo[1]
                outFileName = f"ddn_assembled{outFileExt}"

                f.close()
            
        with open(f"{(os.path.dirname(chunkList[0]))}\{outFileName}", "wb") as outFile:
            for chunkFile in chunkList:
                chunkShortSHA256 = ''
                with open(chunkFile, "rb") as f:
                    chunkBytes = f.read()
                    chunkShortSHA256 = self.readHeader(chunkBytes)[4]
                    chunkHeaderSHA256 = int(hashlib.sha256(chunkBytes[inFileHeaderLength + 4 : ]).hexdigest()[-8:], 16)
                    
                    # Check the chunk's SHA256 to make sure the chunk has no errors
                    if chunkShortSHA256 == chunkHeaderSHA256:
                        outFile.write(chunkBytes[inFileHeaderLength + 4 : ])
                    else:
                        raise RuntimeError("The hash of the chunk didn't match. Cancelling")
            
            outFile.close()



    def readHeader(self, dataBytes, searchHeader = False, maxSearchLength = 1000):
        HEADER_OFFSET = 0   #This is a constant that sometimes changes??? See below...

        #If "searchHeader" is True (and safeMode is False), the program will search for the header if it doesn't find it at byte 0. It can potentially take a lot of time to
        #find the header so it is not enabled by default. This is possibly useful if extra data is added before the header or for supporting future extended header versions. 
        if searchHeader and not self.safeMode:   
            for i in range(self.MAX_FILE_SIZE - self.MIN_HEADER_SIZE):
                if dataBytes[HEADER_OFFSET : HEADER_OFFSET + 4].decode("ascii") != ".ddn":
                    HEADER_OFFSET += 1
                    
                    #The following bit is to make sure the console printing process is not causing the program to slow down.
                    if i < maxSearchLength and i % math.ceil(maxSearchLength / 10) == 0:
                        print(f"Looking for header... Current offset:{HEADER_OFFSET}")
                    if i > maxSearchLength:
                        raise RuntimeError("Damaged header or Wrong file format")

                elif dataBytes[HEADER_OFFSET : HEADER_OFFSET + 4].decode("ascii") == ".ddn":
                    break

                else:
                    raise RuntimeError("Damaged header or Wrong file format")

   
        elif dataBytes[HEADER_OFFSET : HEADER_OFFSET + 4].decode("ascii") != ".ddn":
            raise RuntimeError("Damaged header or Wrong file format")

        print("Header detected. Reading...")

        headerLength = int.from_bytes(dataBytes[HEADER_OFFSET + 4 : HEADER_OFFSET + 6], "big")   
        orgFileExt = dataBytes[HEADER_OFFSET + 6 : HEADER_OFFSET + headerLength - 6].decode("utf-8")
        chunkIdx = int.from_bytes(dataBytes[HEADER_OFFSET + headerLength - 6 : HEADER_OFFSET + headerLength - 4], "big")
        orgShortSHA256 = int.from_bytes(dataBytes[HEADER_OFFSET + headerLength - 4 : HEADER_OFFSET + headerLength], "big")
        chunkShortSHA256 = int.from_bytes(dataBytes[HEADER_OFFSET + headerLength : HEADER_OFFSET + headerLength + 4], "big")

        return [headerLength, orgFileExt, chunkIdx, orgShortSHA256, chunkShortSHA256]
                