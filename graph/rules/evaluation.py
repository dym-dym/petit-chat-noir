from dataclasses import dataclass
from sqlite3 import Cursor, IntegrityError
from database.insertion import insert_relation_type
from graph.insertion import insert_sen_node
from graph.text.parsing import get_lowest_available_id, get_sen_node_id

from jdm.inference import get_reltype_id


@dataclass
class Rule:
    body: list[tuple[str, str, str, str]]
    head: list[tuple[str, str, str, str]]
    morphisms: list[str]

    def is_morphism_new(self, morph):
        return not (morph in self.morphisms)

    def add_morphism(self, morph):
        self.morphisms.append(morph)

    def get_existential_variables(self):
        body_variables = []
        existential = []
        for pattern in self.body:
            if pattern[3] == "EX":
                for entity in pattern:
                    if entity[0] == "$":
                        body_variables.append(entity)

        for head_pattern in self.head:
            if head_pattern[3] == "EX":
                for head_entity in head_pattern:
                    if head_entity[0] == "$":
                        if head_entity not in body_variables and head_entity not in existential:
                            existential.append(head_entity)
        return existential

    def get_frontier(self):
        body_variables = []
        frontier = []
        for pattern in self.body:
            # if pattern[3] == "EX":
            for entity in pattern:
                if entity[0] == "$" and entity not in body_variables:
                    body_variables.append(entity)

        for head_pattern in self.head:
            for head_entity in head_pattern:
                if head_entity[0] == "$":
                    if head_entity in body_variables and head_entity not in frontier:
                        frontier.append(head_entity)
        return body_variables


def build_query(cursor: Cursor, rule: Rule) -> str:
    body_variables = rule.get_frontier()
    select_variables = ", ".join(
        [f'{var[1:]}.id' for var in body_variables])

    select_statement = f'SELECT {select_variables}'

    from_statement = f'FROM {", ".join([f"sentence_graph_node as {var[1:]}" for var in body_variables])}\nWHERE'

    # operators = {">", "<", "<=", ">="}

    where_clauses = []

    for pattern in rule.body:

        pattern_variables = []
        pattern_constants = []
        pattern_filters = []

        if pattern[0] in body_variables:
            pattern_variables.append(pattern[0][1:])
        else:

            pattern_constants.append(pattern[0])
            pattern_filters.append(
                f"out_node='{get_sen_node_id(cursor, pattern[0])}'")
        if pattern[1] in body_variables:
            pattern_variables.append(pattern[1][1:])
        else:
            if pattern[1] != '!rgx':

                pattern_constants.append(pattern[1])
                rel_id = get_reltype_id(cursor, pattern[1])
                pattern_filters.append(f"type='{rel_id}'")
        if pattern[2] in body_variables:
            pattern_variables.append(pattern[2][1:])
        else:
            pattern_constants.append(pattern[2])
            if pattern[1] == '!rgx':

                split_pattern = pattern[2].replace(
                    "^(", "").replace(")", "").replace("$", "").split("|")
                or_clause = "("

                for elem in split_pattern:
                    or_clause += f"'{get_sen_node_id(cursor, elem)}', "

                or_clause = or_clause[:-2] + ")"
                pattern_filters.append(or_clause)

            else:

                pattern_filters.append(
                    f"in_node='{get_sen_node_id(cursor, pattern[2])}'")

        subselect_variables = f'{"out_node, " if pattern[0][1:] in pattern_variables else ""}{"type, " if pattern[1][1:] in pattern_variables else ""}{"in_node, " if pattern[2][1:] in pattern_variables else ""}'
        subselect_filters = " AND ".join(pattern_filters)

        subselect = f'(SELECT {subselect_variables[:-2]} FROM sentence_graph_relation WHERE {subselect_filters})' if pattern[1] != '!rgx' else f"{subselect_filters}"
        pattern_string = f'({", ".join(map(lambda s: f"{s}.id", pattern_variables))}) {"NOT " if pattern[3]=="NOT" else ""}IN {subselect}'

        where_clauses.append(pattern_string)

    clause = "\nAND ".join(where_clauses)

    query = f'{select_statement}\n{from_statement}\n{clause}'

    return query


def build_and_apply_rules(db, cursor: Cursor, stratas: list[list[Rule]], DEBUG=False):

    strata_morphisms = []
    for strata in stratas:
        # print("=======================New Strata=======================")
        rule_applications_res = None
        rule_applications_res_old = None

        while rule_applications_res is None or rule_applications_res != rule_applications_res_old:

            rule_applications_res_old = rule_applications_res

            rule_applications_res = loop_over_strata(db, cursor, strata, DEBUG)

            if rule_applications_res is not None:
                strata_morphisms += rule_applications_res
                print("app res : ", rule_applications_res)
                print("app res old : ", rule_applications_res_old)
    # print(strata_morphisms)


def loop_over_strata(db, cursor: Cursor, strata: list[Rule], DEBUG=False):

    morphisms = set()

    for rule in strata:

        morphisms = set()
        variables = rule.get_frontier()

        triggers_query = build_query(cursor, rule)

        cursor.execute(triggers_query)

        triggers = cursor.fetchall()

        for trigger in triggers:
            morphisms.add(tuple(zip(variables, trigger)))

        if len(morphisms) != 0:
            for morphism in morphisms:

                # print("morphisms : ", dict(morphism))

                for atom in rule.head:
                    morphism_dict = dict(morphism)

                    if atom[3] == "DEL":
                        cursor.execute(build_delete_query(
                            cursor, morphism_dict, atom))

                    if atom[3] == "EX":
                        try:
                            query = build_insert_query(
                                cursor, morphism_dict, atom)
                            # print(query)
                            cursor.execute(query)
                        except IntegrityError:
                            pass

                    db.commit()
    return morphisms


def build_delete_query(cursor: Cursor, morphism: dict[str, int], triplet: tuple[str, str, str, str]) -> str:

    res = "DELETE FROM sentence_graph_relation\nWHERE "

    res += f"out_node = '{morphism[triplet[0]]}'"
    if (rel := triplet[1]) != "!all":
        res += f"\nAND type = '{get_reltype_id(cursor, rel)}'"
    if (var2 := triplet[2]) != "!all":
        res += f"\nAND in_node = '{get_sen_node_id(cursor, var2)}'"

    return res


def build_insert_query(cursor: Cursor, morphism: dict[str, int], triplet: tuple[str, str, str, str]) -> str:

    object = triplet[2]
    # print("object : ", object)
    obj_id = object
    if object.startswith("$"):
        if object in morphism.keys():
            obj_id = morphism[object]
        else:
            pass

    else:
        obj_id = get_sen_node_id(cursor, object)
        if obj_id == "-1":
            obj_id = get_lowest_available_id(cursor)

            insert_sen_node(cursor, obj_id, object)

    if get_reltype_id(cursor, triplet[1]) == "-1":
        insert_relation_type(
            cursor, "100000" + str(get_lowest_available_id(cursor)), triplet[1], "", "", False)

    res = "INSERT INTO sentence_graph_relation\n(id, out_node, type, in_node, weight)\nVALUES("

    res += f"'{get_lowest_available_id(cursor)}', '{morphism[triplet[0]] if triplet[0] in morphism.keys() else -1}', "
    res += f"'{get_reltype_id(cursor, triplet[1])}', "
    res += f"'{obj_id}', 1)"

    return res


def parse_rules(rule_file) -> list[list[Rule]]:
    rules = []
    strata = None
    with open(rule_file, 'r') as f:
        for rule_line in f.readlines():
            if rule_line[:7] == "@STRATA":
                if strata is not None and len(strata) > 0:
                    rules.append(list(strata))
                strata = []
                continue
            if rule_line != "" and (not rule_line.isspace()) and not rule_line[0] == "#":
                body, head = rule_line.split("=>")
                body_patterns = body.split("&&")
                body_triples = []
                for pattern in body_patterns:
                    triple = pattern.split()
                    if len(triple) == 3:
                        body_triples.append(
                            (triple[0], triple[1], triple[2], "EX"))
                    elif len(triple) == 4:
                        if triple[0] == "!not":
                            body_triples.append(
                                (triple[1], triple[2], triple[3], "NOT"))
                        else:
                            raise ValueError("Malformed pattern")
                    else:
                        raise ValueError("Body patterns must be triples")

                head_patterns = head.split("&&")
                head_triples = []
                for pattern in head_patterns:
                    triple = pattern.split()
                    if len(triple) == 3:
                        head_triples.append(
                            (triple[0], triple[1], triple[2], "EX"))
                    elif len(triple) == 4:
                        if triple[0] == "!del":
                            head_triples.append(
                                (triple[1], triple[2], triple[3], "DEL"))
                        else:
                            raise ValueError("Malformed pattern")
                    else:
                        raise ValueError("Body patterns must be triples")

                strata.append(Rule(body_triples, head_triples, []))
    if strata is not None and len(strata) > 0:
        rules.append(list(strata))
    return rules
