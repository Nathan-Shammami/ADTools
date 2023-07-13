import csv
import pyad.addomain
import pyad.adquery
import pyad.adcontainer
import pyad.adgroup
import pyad.adbase
import pyad.aduser
import pyad.adobject
import pwinput

class bcolors:
    Title = '\033[3;31;40m'
    Green = '\033[32m'
    Blue = '\033[0;34;40m'
    Reset = '\033[0m'
    
def Read_Data():
    Attributes={}
    groups = {}
    bats = {}
    buildings = {}
    extras={}
    with open("data\Dept assignment.csv") as file1:
        csv_reader1 = csv.reader(file1)
        next(csv_reader1)
        for row in csv_reader1:
            groups[row[0]] = row[1]
            bats[row[0]] = row[2]
    with open("data\Attributes.csv") as file2:
        csv_reader2 = csv.reader(file2)
        next(csv_reader2)
        for row in csv_reader2:
            Attributes[row[0]] = row[1]
    with open("data\Buildings.csv") as file3:
        csv_reader3 = csv.reader(file3)
        for row in csv_reader3:
            buildings[row[0]]=[row[1],row[2],row[3]]
    with open("data\Extras.csv") as file4:
        csv_reader4 = csv.reader(file4)
        next(csv_reader4)
        for row in csv_reader4:
            extras[row[0]]=row[1]
    return groups,bats,Attributes,buildings,extras

def ConnectAD(ad_server, domain_name, adminuser, adminpass):
    while (True):
        try:
            pyad.adbase.set_defaults(ldap_server=ad_server, ldap_domain=domain_name, username=adminuser, password=adminpass)
            break
        except:
            print(bcolors.Title+"Can't connect to AD")
            ad_server = input(bcolors.Blue+"Input IP for AD server")
            domain_name = input(bcolors.Blue+"Input domain for AD server")
            adminuser = input(bcolors.Blue+"Please enter your Admin account username: ")
            adminpass = pwinput.pwinput(prompt=bcolors.Blue+"Please enter your Admin Password: ", mask="*")

def Find_Group(description,groups,extras,username):
    group = next((groups[key] for key in groups if key in description.lower()), None)
    if group is None:
        print(bcolors.Title+"No group found for the given description.")
    else:
        print(bcolors.Green+"Assigned group:", group)
    try:
        group_dn = "CN="+group+",OU="+extras["ou"]+",DC="+extras["dc"]+",DC=com"
        name = pyad.aduser.ADUser.from_cn(username)
        dept_group = pyad.adgroup.ADGroup.from_dn(group_dn)
    except:
        group_dn = "CN="+group+",OU="+extras["dc2"]+",DC="+extras["dc"]+",DC=com"
        name = pyad.aduser.ADUser.from_cn(username)
        dept_group = pyad.adgroup.ADGroup.from_dn(group_dn)
    try:
        name.add_to_group(dept_group)
    except:
        print(bcolors.Title+"No group found")

def Find_Script(description,bats):
    script = next((bats[key] for key in bats if key in description.lower()), None)
    if script is None:
        print(bcolors.Title+"No script found for the given description.")
    else:
        print(bcolors.Green+"Assigned script:", script)
    return script

def main():
    while (True):
        groups,bats,Attributes,buildings,extras = Read_Data()
        print(bcolors.Title+"Welcome to Nathan Shammami's AD/Exchange account creator!")
        ad_server = extras["ad_server"]
        domain_name = extras["domain_name"]
        adminuser = input(bcolors.Blue+"Please enter your Admin account username: ")
        adminpass = pwinput.pwinput(prompt=bcolors.Blue+"Please enter your Admin Password: ", mask="*")
        ConnectAD(ad_server, domain_name, adminuser, adminpass)
        keys = ''
        templist = []
        username = input(bcolors.Blue+'Please enter name (with space) ')
        description= input(bcolors.Blue+"Please enter Department ")
        for key in buildings.keys():
            keys += key + ' ' 
        building = input(bcolors.Blue+"enter building name "+ keys[3:])
        user = username.replace(" ", '')
        l1 =[]
        l1 = username.split(" ")
        ou = pyad.adcontainer.ADContainer.from_dn("OU="+extras["ou"]+",DC="+extras["dc"]+",DC=com")
        new_user = pyad.aduser.ADUser.create(username,ou, password=Attributes['password'],upn_suffix=None)
        target= extras["targetaddress"]
        script = Find_Script(description, bats)
        templist = buildings[building.upper()]
        Attributes['postalCode']=templist[2]
        Attributes['l']=templist[1]
        Attributes['streetAddress']=templist[0]
        email = user+Attributes['UPN']
        Attributes['description']=description
        Attributes['department']=description
        Attributes['scriptPath']=script
        Attributes['userPrincipalName']=email
        Attributes['title']=input(bcolors.Blue+"Enter job Title: ")
        Attributes['mail']=email
        Attributes['displayName']=username
        Attributes['sAMAccountName']=user
        Attributes['givenName']=l1[0]
        Attributes['sn']=l1[1]
        Attributes['proxyAddresses']=[f"SMTP:{email}",f"smtp:{user}{target}"]
        Attributes['targetAddress']=[f"SMTP:{user}{target}"]
        Attributes['mailNickname']=user
        Find_Group(description,groups,extras,username)
        try:
            manager = input(bcolors.Blue+"Enter manager name (First Last): ")
            manager = "CN="+manager+",OU="+extras["ou"]+",DC="+extras["dc"]+",DC=com"
            Attributes['manager'] = manager
        except:
            print(bcolors.Title+"Manager Not Found")
        for i in Attributes:
            if (i!= "password" and i!='UPN'):
                try:
                    new_user.update_attribute(i, Attributes[i])
                except:
                    print(bcolors.Title+i,"failed value: ", Attributes[i])
        cont = input(bcolors.Reset+"Would you like to create another account [y/n]? ")
        if(cont.lower() != 'y'):
            break
if __name__=="__main__":
    main()