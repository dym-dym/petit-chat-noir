# TODO: Regarder mieux la forme des données pour les nettoyer correctement
# concerne tous les parsing de string
def parse_node_type(line: str) -> tuple[str, str]:
    line_split = line.split(";")
    line_split = [word for word in line_split]

    type_id = str(line_split[1])  # str(line_split.pop(0))
    # str(line_split.pop(0))
    type_name = str(line_split[2])[1:len(line_split[2]) - 1]
    return (type_id, type_name)


def parse_node(line: str) -> tuple[str, str, str, str]:

    line_split = line.split(";")
    line_split = [word for word in line_split]

    node_id = str(line_split[1])
    name = str(line_split[2])[1:len(line_split[2]) - 1]

    node_type = str(line_split[3])
    weight = str(line_split[4])
    return (node_id, name, node_type, weight)


def parse_relation_type(line: str) -> tuple[str, str, str, str]:
    line_split = line.split(";")
    line_split = [word for word in line_split]

    r_type_id = str(line_split[1])  # str(line_split.pop(0))
    r_type_name = str(line_split[2])[1:len(
        line_split[2]) - 1]  # str(line_split.pop(0))
    trgpname = str(line_split[3])[1:len(
        line_split[3]) - 1]  # str(line_split.pop(0))
    r_type_help = str(line_split[4])  # str(line_split.pop(0))
    return (r_type_id, r_type_name, trgpname, r_type_help)


def parse_relation(line: str) -> tuple[str, str, str, str, str]:
    line_split = line.split(";")
    line_split.pop(0)
    rid = str(line_split.pop(0))
    out_node = str(line_split.pop(0))
    in_node = str(line_split.pop(0))
    r_type = str(line_split.pop(0))
    weight = str(line_split.pop(0))
    return (rid, out_node, in_node, r_type, weight)
