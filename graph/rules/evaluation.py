from dataclasses import dataclass


@dataclass
class Rule:
    head: list[str]
    body: list[str]
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
            if pattern[3] == "EX":
                for entity in pattern:
                    if entity[0] == "$" and entity not in body_variables:
                        body_variables.append(entity)

        for head_pattern in self.head:
            for head_entity in head_pattern:
                if head_entity[0] == "$":
                    if head_entity in body_variables and head_entity not in frontier:
                        frontier.append(head_entity)
        return body_variables


def parse_rules(rule_file) -> list[Rule]:
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
