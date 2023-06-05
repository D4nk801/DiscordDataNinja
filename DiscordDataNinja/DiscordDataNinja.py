#Discord Data Ninja core functions library (EXTENDED HEADER)
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


import os
import math
import hashlib


class DiscordDataNinja:
    __version__ = "1.0.0"
    __binver__ = ''.join(format(int(c), 'b').zfill(b) for c, b in zip(__version__.split('.'), [4, 5, 7])) #The version in a binary format (0000 00000 0000000)[major, minor, patch]

    def __init__(self, MAX_FILE_SIZE = 26214400, asmbFileOutputPath = "None", ddnFileOutputPath = "None"):
        self.MAX_FILE_SIZE = MAX_FILE_SIZE
        self.__MIN_HEADER_SIZE = 25 #The minimum header size is the size of the header without the input file extension added onto it.

        self.ddnFileOutputPath = ddnFileOutputPath
        self.asmbFileOutputPath = asmbFileOutputPath


    def createChunks(self, filePath):
        headerSize = self.__MIN_HEADER_SIZE + len( (os.path.splitext(filePath))[1][1:] )
        fileSize = os.path.getsize(filePath)
        fileChunkNumber = math.ceil( (fileSize + (headerSize * math.ceil( fileSize / self.MAX_FILE_SIZE ))) / self.MAX_FILE_SIZE )  
        outputPath = self.ddnFileOutputPath

        #A soft limit to prevent a user from dividing a really large file into too many files. This also disables the 65536 hard chunk limit caused due to
        #the way the header structure is designed.
        if fileChunkNumber > 255:
            raise RuntimeError("Woah! Your files are too powerful, even for a ninja.")

                   
        with open(filePath, "rb") as f:
            fileBytes = f.read()
            
            fileSHA256 = hashlib.sha256(fileBytes).hexdigest()
            fileShortSHA256 = fileSHA256[-16:]   #The last 8 bytes of the SHA256 hash of the file

            print(f"Your file will been seperated into {fileChunkNumber} pieces!")
            print(f"The SHA256 for the original file is: {fileSHA256} ShortSHA: {fileShortSHA256}")        

            headerBytes = [
                (bytes("ddn", encoding="utf-8")),
                (int(self.__binver__, 2).to_bytes(2, "big")),
                (int(headerSize).to_bytes(2, "big")),
                None,
                (int(fileShortSHA256, 16).to_bytes(8, "big")),
                None,
                #Bytes can be added ito the header (after the necessary bits and before the file extension) to extend functionality while keeping backwards compatibility. 
                #Change the "__MIN_HEADER_SIZE" variable to ensure that the program is aware of the additional bytes.
                #(int(0).to_bytes(16, "big")), 
                (bytes((os.path.splitext(filePath))[1][1:], encoding="utf-8"))
                ]

            for chunkNumber in range(fileChunkNumber):
                chunkBytes = fileBytes[(chunkNumber * (self.MAX_FILE_SIZE - headerSize)) : ((chunkNumber + 1) * (self.MAX_FILE_SIZE - headerSize))] 
                
                chunkSHA256 = hashlib.sha256(chunkBytes).hexdigest()
                chunkShortSHA256 = chunkSHA256[-16:] #The last 8 bytes of the SHA256 hash of the chunk

                print(f"The SHA256 for chunk {chunkNumber} is {chunkSHA256} ShortSHA: {chunkShortSHA256}")

                if outputPath == "None": outputPath = os.path.dirname(filePath)

                headerBytes[3] = int(chunkNumber).to_bytes(2, "big")
                headerBytes[5] = int(chunkShortSHA256, 16).to_bytes(8, "big")

                with open(f"{outputPath}/chunk{chunkNumber}.ddn", "wb") as outFile:

                    for i in headerBytes:
                        outFile.write(i)

                    outFile.write(chunkBytes)
                    outFile.close()
            
            f.close()
            
            return(True)
    

    #TODO: Check for hash to make sure the data is intact for the final file (chunk check is done)
    #This function is not super efficient. Could be improved in the future. I cannot be bothered right now. 
    def assembleChunks(self, inputFilePathsList):
        chunkList = []
        inFileHeaderLength = 0
        outFileExt = ""
        outFileName = ""
        outputPath = self.asmbFileOutputPath

        #Organise the files so it can be reconstructed correctly
        for chunkFile in inputFilePathsList:
            with open(chunkFile, "rb") as f:
                chunkBytes = f.read()
                chunkInfo = self.readHeader(chunkBytes)
                chunkList.insert(chunkInfo[2], chunkFile)

                inFileHeaderLength = chunkInfo[1]
                outFileExt = chunkInfo[5]
                outFileName = f"ddn_assembled.{outFileExt}"

                f.close()

        if outputPath == "None": outputPath = os.path.dirname(chunkList[0])
        
        with open(f"{outputPath}\{outFileName}", "wb") as outFile:
            for chunkFile in chunkList:
                chunkShortSHA256 = ''
                with open(chunkFile, "rb") as f:
                    chunkBytes = f.read()
                    chunkShortSHA256 = self.readHeader(chunkBytes)[4]
                    chunkHeaderSHA256 = int(hashlib.sha256(chunkBytes[inFileHeaderLength: ]).hexdigest()[-16:], 16)
                    
                    # Check the chunk's SHA256 to make sure the chunk has no errors
                    if chunkShortSHA256 == chunkHeaderSHA256:
                        outFile.write(chunkBytes[inFileHeaderLength: ])
                    else:
                        raise RuntimeError("The hash of the chunk didn't match. Cancelling")
            
            outFile.close()


    def readHeader(self, dataBytes): 
   
        if dataBytes[0:4].decode("ascii") == ".ddn":
            raise RuntimeError(f"Library version 1.0.0 and up are not compatible with this file")       
        elif dataBytes[0:3].decode("ascii") != "ddn":
            raise RuntimeError("Damaged header or Wrong file format")
        
        version = int.from_bytes(dataBytes[3:5], "big")
        headerLength = int.from_bytes(dataBytes[5:7], "big") 
        chunkIdx = int.from_bytes(dataBytes[7:9], "big")
        orgShortSHA256 = int.from_bytes(dataBytes[9:17], "big")
        chunkShortSHA256 = int.from_bytes(dataBytes[17:25], "big")
        orgFileExt = dataBytes[self.__MIN_HEADER_SIZE:headerLength].decode("utf-8")

        return [version, headerLength, chunkIdx, orgShortSHA256, chunkShortSHA256, orgFileExt]
                