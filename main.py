from bs4 import BeautifulSoup
import request3


# Fetches relationnal data from jeuxdemots for
# a given word. Might fail
def fetch_word_data(word: str) -> str | None:

    try:
        r = request3.get(
            f"https://www.jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel={word}"
        )

        soup = BeautifulSoup(r.text, features="html.parser")

        return '\n'.join(
            filter(lambda x: x.startswith(('r', 'e', 'n')),
                   str(soup.find("code")).split('\n')))

    except request3.exceptions.RequestException as e:
        print("Couldn't reach url with reason: ", e)

        return None

class R_Relation:
    def __init__(self, rid: int, out_node: int, in_node: int, r_type: int, weight: int):
        self.rid = rid
        self.out_node = out_node 
        self.in_node = in_node
        self.r_type = r_type
        self.weight = weight

    def __str__(self):
        return f"Relation id : {self.rid}\nRelation origin: {self.out_node}\nRelation target: {self.in_node}\nRelation type: {self.r_type}\nRelation weight: {self.weight}\n"

def parse_relation(line: str) -> R_Relation:
    line_split = line.split(";")
    line_split.pop(0)
    rid = int(line_split.pop(0))
    out_node = int(line_split.pop(0))
    in_node = int(line_split.pop(0))
    r_type = int(line_split.pop(0))
    weight = int(line_split.pop(0))
    return R_Relation(rid, out_node, in_node, r_type, weight)

class Node_Type:
    def __init__(self, type_id: int, type_name: str):
        self.type_id = type_id 
        self.type_name = type_name 

    def __str__(self):
        return f"Node type id : {self.type_id}\nNode type name: {self.type_name}\n"

def parse_type(line: str) -> Node_Type:
    line_split = line.split(";")
    line_split.pop(0)
    type_id = int(line_split.pop(0))
    type_name = str(line_split.pop(0))
    return Node_Type(type_id, type_name)

class Relation_Type:
    def __init__(self, r_type_id: int, r_type_name: str, trgpname: str, r_type_help: str):
        self.r_type_id = r_type_id 
        self.r_type_name = r_type_name
        self.trgpname = trgpname
        self.r_type_help = r_type_help
    def __str__(self):
        return f"Relation type id : {self.r_type_id}\nRelation type name: {self.r_type_name}\nRelation trgpname\nRelation helper string: {self.r_type_help}\n"


def parse_relation_type(line: str) -> Relation_Type:
    line_split = line.split(";")
    line_split.pop(0)
    r_type_id = int(line_split.pop(0))
    r_type_name = str(line_split.pop(0))
    trgpname = str(line_split.pop(0))
    r_type_help = str(line_split.pop(0))
    return Relation_Type(r_type_id, r_type_name, trgpname, r_type_help)

relations = fetch_word_data("Noah")
if relations:

    relations_split = relations.split('\n')

    for elem in relations_split:
        if elem.startswith('nt;'):
            parse_type(elem)
        if elem.startswith('rt;'):
            print(parse_relation_type(elem))
        if elem.startswith('r;'):
            parse_relation(elem)
