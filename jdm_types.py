
class Relation_Type:
    def __init__(self, r_type_id: int, r_type_name: str, trgpname: str,
                 r_type_help: str):
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


class R_Relation:
    def __init__(self, rid: int, out_node: int, in_node: int,
                 r_type: Relation_Type, weight: int):
        self.rid = rid
        self.out_node = out_node
        self.in_node = in_node
        self.r_type = r_type
        self.weight = weight

    def __str__(self):
        return f"Relation id : {self.rid}\nRelation origin: {self.out_node}\nRelation target: {self.in_node}\nRelation type: {self.r_type}\nRelation weight: {self.weight}\n"


def parse_relation(line: str, relation_types: list[Relation_Type]) -> R_Relation:
    line_split = line.split(";")
    line_split.pop(0)
    rid = int(line_split.pop(0))
    out_node = int(line_split.pop(0))
    in_node = int(line_split.pop(0))
    r_type_id = int(line_split.pop(0))
    weight = int(line_split.pop(0))
    r_type = filter(lambda x: x.r_type_id == r_type_id, relation_types).pop(0)

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


class Node:
    def __init__(self, node_id: int, name: str, node_type: Node_Type,
                 weight: int, formatted_name: str):
        self.node_id = node_id
        self.name = name
        self.node_type = node_type
        self.formatted_name = formatted_name

    def __str__(self):
        return f"Node id : {self.node_id}\nNode name: {self.name}\nNode type: {self.node_type}\nFormatted node name: {self.formatted_name}\n"


def parse_node(line: str) -> Node:
    line_split = line.split(";")
    line_split.pop(0)
    node_id = int(line_split.pop(0).strip("'"))
    name = str(line_split.pop(0).strip("'"))
    node_type = int(line_split.pop(0).strip("'").strip("&gt"))
    weight = int(line_split.pop(0).strip("'"))
    return Node(node_id, name, node_type, weight, "")
