import os,optparse,json


def getAirtableRecords():
    # write the API command
    apistring = 'curl "https://api.airtable.com/v0/app2N9vfJjQQCWp7K/papers?maxRecords=1000&view=Grid%20view" -H "Authorization: Bearer keyl5bKwb92iLsi0R"'
    apilist = 'getlist.sh'
    apish = open(apilist,'w')
    apish.write(apistring)
    apish.close()

    query_result = 'records.js'
    os.system('source {cmd} > {outf}'.format(cmd=apilist,outf=query_result))

    with open(query_result) as json_file:
        records = json.load(json_file)
    os.system('rm '+apilist)
    os.system('rm '+query_result)
    return records

def getRecordHash(paper):
    data = getAirtableRecords()

    rcdHash = None
    for rcd in data['records']:
        if rcd['fields']['Paper ID']==paper:
            rcdHash=rcd['id']
            break
    print("===> Hash for Paper ID ",paper," = ",rcdHash)
    return rcdHash
    
        
    
def writeAirtableAPI(shfile,paper,version):

    # first get the id of the record corresponding to the paper ID
    hashrcd = getRecordHash(paper)
    
    apistring = '''curl -v -X PATCH https://api.airtable.com/v0/app2N9vfJjQQCWp7K/papers \
    -H "Authorization: Bearer keyl5bKwb92iLsi0R" \
    -H "Content-Type: application/json" \
    --data '{{ "records": [
    {{
    "id": "{HASH}",
    "fields": {{
    "Paper ID": "{PAPER}",
    "git url": "https://github.com/CYGNO-publications/{PAPER}/tree/{VERSION}",
    "Latest version": "https://github.com/CYGNO-publications/{PAPER}/blob/{VERSION}/{PAPER}-{VERSION}.pdf"
    }}
    }}
    ]
    }}'
    '''.format(HASH=hashrcd,
               PAPER=paper,
               VERSION=version)
    sh = open('api.sh','w')
    sh.write(apistring)
    sh.close()
    

def uploadFromGit(paper,version):
    print("Uploading version ",version," from GITHUB to AIRTABLE")
    gitfile = 'git.sh'
    src = open(gitfile,'w')
    src.write('mkdir tmp-{paper}\n'.format(paper=paper))
    src.write('cd tmp-{paper}\n'.format(paper=paper))
    src.write('git clone git@github.com:CYGNO-publications/{paper}.git\n'.format(paper=paper))
    src.write('cd {paper}\n'.format(paper=paper))
    src.write('pdflatex {paper}\n'.format(paper=paper))
    src.write('bibtex {paper}\n'.format(paper=paper))
    src.write('pdflatex {paper}\n'.format(paper=paper))
    src.write('pdflatex {paper}\n'.format(paper=paper))
    src.write('mv {paper}.pdf {paper}-{version}.pdf\n'.format(paper=paper,version=version))
    src.write('git add {paper}-{version}.pdf\n'.format(paper=paper,version=version))
    src.write('git commit -m "adding compiled paper version {version}" {paper}-{version}.pdf\n'.format(paper=paper,version=version))
    src.write('git tag -a {version} -m "git version {version}"\n'.format(version=version))
    src.write('git push origin {version}\n'.format(version=version))
    src.write('cd ../../\n')
    src.write('rm -rf tmp-{paper}\n'.format(paper=paper))
    src.close()
    os.system('source '+gitfile)
    os.system('rm '+gitfile)

    shfile = 'api.sh'
    api = open(shfile,'w')
    writeAirtableAPI(shfile,paper,version)
    os.system('source '+shfile)
    os.system('rm '+shfile)
    print ("DONE. Airtable database updated with {paper} version {version}".format(paper=paper,version=version))
    
if __name__ == "__main__":

    parser = optparse.OptionParser(usage='usage: %prog PAPERID [opts]', version='%prog 1.0')
    parser.add_option('-v', '--vrs' , type='string'       , default='v1' , help='upload this tagged version')
    parser.add_option(      '--make' ,    type='string'       , default='v1' , help='upload from git')
    (options, args) = parser.parse_args()
    
    if len(args)<1:
        print("Need to give at least the PAPERID (eg LEMON-20-001)")
        exit(1)

    paperid = args[0]
    version = options.vrs
    
    print("Considering paper with ID = ",paperid)

    if options.make=='upgit':
        uploadFromGit(paperid,options.vrs)
        
