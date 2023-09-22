import os,optparse,csv

if __name__ == "__main__":

    parser = optparse.OptionParser(usage='usage: %prog <format>', version='%prog 1.0')
    parser.add_option(       '--datafile' , type='string'       , default='data/authorlist.csv' , help='use this alternative input file (expect CSV)')
    (options, args) = parser.parse_args()

    if len(args)<1:
        print("Need to give the format as argument. Supported formats are:\n")
        print("POSlatex [default]")
        exit(1)

    outformat = args[0]

    data = []
    with open(options.datafile, newline='') as csvfile:
        # initially the delimiter was "|" and "," aregular char in the institute. I changed it to make the table nicely appearing in the web
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if len(row)<1 or row[0].startswith("#"):
                continue
            key = (row[0],row[1],row[2])
            data.append([key, row[3:]])


    # sort in alphabetical order of second name
    # sorted_data = sorted(data, key=lambda x: x[0][2], reverse=False)
    sorted_data = data
    
    affiliations = []
    aff_with_keys = {}
    charkey = ord('a')
    for author in sorted_data:
        auth_institutes = author[1][1:]
        for i in auth_institutes:
            if i.strip() not in affiliations:
                affiliations.append(i.strip())
                aff_with_keys[i.strip()]=chr(charkey)
                charkey = charkey + 1

    if outformat=="POSlatex":
        # formats
        auth_fmt = "\\author[{instkeys}]{{{author_fullname}}}"
        affiliation_fmt = "\\affiliation[{instkey}]{{{inst_fullname}}}"

        outfile_name = "cygno_authors_pos.tex"
        fout = open(outfile_name,"w")
        
        authors = []
        fout.write("% CYGNO blessed authors. Add undergraduate students if their thesis work is contained in this paper\n")
        for author in sorted_data:
            auth_fullname = author[0]
            firsts  = auth_fullname[0].strip().split(" ")
            middles = auth_fullname[1].strip().split(" ")
            lasts   = auth_fullname[2].strip().split(" ")
            authname = ".".join([first[0] for first in firsts]) + "." + ".".join([middle[0] for middle in middles if len(middle)])
            if len(middles[-1]):
                authname = authname + "."
            authname = authname + "~" + " ".join(lasts)
            auth_inst_keys = [aff_with_keys[i.strip()] for i in author[1][1:]]

            formatted_author = auth_fmt.format(instkeys=','.join(auth_inst_keys),author_fullname=authname) + "\n"
            fout.write(formatted_author)
            authors.append(formatted_author)

        fout.write("\n\n%CYGNO institutions\n")
        affiliations = []
        for inst,k in aff_with_keys.items():
            formatted_inst = affiliation_fmt.format(instkey=k,inst_fullname=inst.replace(";",",")) + "\n"
            fout.write(formatted_inst)
            affiliations.append(formatted_inst)
            
        fout.close()

        print("Output written in ",outfile_name,". Please check contents carefully.")
        
        # print ("===> AUTHORS <===")
        # print (authors)
        
        # print ("===> INSTITUTES <===")
        # print (affiliations)
    else:
        print ("Format ",outformat," not yet implemented. Nothing written. ")
    
            
