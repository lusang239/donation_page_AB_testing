race_lookup = {
    "1": "American Indian or Alaska Native",
    "2": "Asian",
    "21": "Asian Indian",
    "22": "Chinese",
    "23": "Filipino",
    "24": "Japanese",
    "25": "Korean",
    "26": "Vietnamese",
    "27": "Other Asian",
    "3": "Black or African American",
    "4": "Native Hawaiian or Other Pacific Islander",
    "41": "Native Hawaiian",
    "42": "Guamanian or Chamorro",
    "43": "Samoan",
    "44": "Other Pacific Islander",
    "5": "White",
}

class Applicant:
    def __init__(self, age, race):
        self.age = age
        self.race = {race_lookup[r] for r in race if r in race_lookup}
  
    def __repr__(self):
        L = []
        for i in self.race:
            L.append(i)
        return f"Applicant({repr(self.age)}, {sorted(L)})"
    
    def lower_age(self):
        age = self.age.replace('<','')
        age = age.replace('>','')        
        age = age.split('-')
        return int(min(i for i in age))
    
    def __lt__(self, other):
        return self.lower_age() < other.lower_age()
    
class Loan:
    def __init__(self, values):
        self.loan_amount = float(values["loan_amount"]) if values["loan_amount"] not in ['NA','Exempt'] else -1
        self.property_value = float(values["property_value"]) if values["property_value"] not in ['NA','Exempt'] else -1
        self.interest_rate = float(values["interest_rate"]) if values["interest_rate"] not in ['NA','Exempt'] else -1
        self.applicants = list()
        r = []; co = []
        for i in range(1,6):
            r.append(values["applicant_race-" + str(i)])
            co.append(values["co-applicant_race-" + str(i)])
        
        if values["co-applicant_age"] != "9999":
            self.applicants.extend([Applicant(values["applicant_age"],r), Applicant(values["co-applicant_age"],co)])
        else:
            self.applicants.append(Applicant(values["applicant_age"],r))
            
    def __str__(self):
        return f"<Loan: {self.interest_rate}% on ${self.property_value} with {len(self.applicants)} applicant(s)>"
    
    def __repr__(self):
        return f"<Loan: {self.interest_rate}% on ${self.property_value} with {len(self.applicants)} applicant(s)>"
       
    def yearly_amounts(self, yearly_payment):
        if self.interest_rate > 0:
            amt = self.loan_amount
            while amt > 0:
                yield amt  
                amt = amt*(1+self.interest_rate/100)-yearly_payment 
                
from zipfile import ZipFile
from io import TextIOWrapper
import csv
import json

with open("banks.json","r") as f:
    obj = json.load(f) 
                
class Bank:
    def __init__(self, name):
        for i in range(len(obj)):
            if name == obj[i]["name"]:
                self.lei = obj[i]["lei"]
        
        self.loanlist = list()
        with ZipFile("wi.zip") as zf:
            with zf.open("wi.csv") as f:
                wi = csv.DictReader(TextIOWrapper(f))
                for row in wi:
                    if self.lei == row['lei']:
                        self.loanlist.append(Loan(row))

    def __getitem__(self, lookup):
        return self.loanlist[lookup]
    
    def __len__(self):
        return len(self.loanlist)
    
    

class Node():
    def __init__(self, key):
        self.key = key
        self.val = []
        self.left = None
        self.right = None
        
    def lookup(self, target):
        if target == self.key:
            return self.val

        if target < self.key and self.left != None:
            result = self.left.lookup(target)
            if result:
                return result
                              
        if target > self.key and self.right != None:
            result = self.right.lookup(target)
            if result:
                return result
            
        return []
    
    def height(self):
        if self.left:
            left_height = self.left.height()
        else:
            left_height = 0
            
        if self.right:
            right_height = self.right.height()
        else:
            right_height = 0
               
        return max(left_height, right_height)+1   
    
    def __len__(self):
        if self.key:
            size = 1
        if self.left:
            size += self.left.__len__()
        if self.right:
            size += self.right.__len__()
        return size
            
class BST():
    def __init__(self):
        self.root = None

    def add(self, key, val):
        if self.root == None:
            self.root = Node(key)
            
        curr = self.root
        while True:
            if key < curr.key:
                if curr.left == None:
                    curr.left = Node(key)
                curr = curr.left
            elif key > curr.key:
                if curr.right == None:
                    curr.right = Node(key)
                curr = curr.right
            else:
                assert curr.key == key
                break
        curr.val.append(val)
        
    def __dump(self, node):
        if node == None:
            return
        self.__dump(node.left)            
        print(node.key, ":", node.val)    
        self.__dump(node.right)             

    def dump(self):
        self.__dump(self.root)
    
    def __getitem__(self, target):
        return self.root.lookup(target)
    
 
        
    
    
    
    
    
 