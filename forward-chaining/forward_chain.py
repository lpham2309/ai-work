import sys
import re

def display_clauses_symbols(variable, clauses):
    output_variables = []
    for clause in clauses:
        if variable == 'clauses':
            if len(clause) > 2:
                output_variables.append(clause)
        elif variable == 'symbols':
            if len(clause) == 2:
                output_variables.append(clause)
    return output_variables

def get_user_input_perform_forward_chaining(clauses):
    '''
    Prompt messages asking users
    '''
    query_input = ''
    while query_input != 'end':
        query_input = input("Query symbol (or end): ")
        if query_input == 'end':
            sys.exit("Goodbye.\n")
        else:
            solution = pl_fc_entails(clauses, query_input)
            if solution:
                sys.stdout.write(f'Yes! {query_input} is entailed by our knowledge-base\n')
            else:
                sys.stdout.write(f'No. {query_input} is not entailed by our knowledge-base\n')
    
def get_symbol_count(knowledge_base):
    symbols_count = {}
    for x in knowledge_base:
        if x not in symbols_count:
            premise = x.split('THEN')[0]
            symbols_count[x] = len(re.findall(r'p[0-9]+', premise))
    return symbols_count

def initialize_inferred_table(knowledge_base, query):
    inferred = {}
    symbols = set()

    if query:
        inferred[query] = False
    for x in knowledge_base:
        curr_symbols = re.findall(r'p[0-9]+', x)
        for symbol in curr_symbols:
            symbols.add(symbol)

    for symbol in symbols:
        if symbol not in inferred:
            inferred[symbol] = False
    return inferred

def get_all_symbols(knowledge_base):
    symbols = []
    for x in knowledge_base:
        if len(x) == 2:
            symbols.append(x)
    return symbols

def get_symbol_premise(kb, symbols):
    symbol_premise = {}
    symbol_conclusion = {}
    for symbol in symbols:
        for clause in kb:
            premise = clause.split('THEN')[0]
            conclusion = clause.split('THEN')[1]
            if premise not in symbol_premise and symbol in premise:
                symbol_premise[symbol] = premise
                symbol_conclusion[premise] = conclusion
    return symbol_premise

def pl_fc_entails(kb, query):
    '''
    Forward-Chaining Algorithm
    '''
    count = get_symbol_count(kb)
    inferred = initialize_inferred_table(kb, query)
    agenda = get_all_symbols(kb)
    while agenda != []:
        p = agenda.pop()
        if p == query:
            return True
        if inferred[p] == False:
            inferred[p] = True
            for clause in kb:
                if 'THEN' in clause:
                    curr_premise = clause.split('THEN')[0][:-1]
                    curr_conclusion = clause.split('THEN')[1][1:]
                    if p in curr_premise:
                        count[clause] -= 1
                        if count[clause] == 0:
                            agenda.append(curr_conclusion)
    return False

def main():
    PROPOSITIONAL_CLAUSES = 0
    CONDITIONAL_CLAUSES = 0
    kb_file = sys.argv[1]
    clauses = []
    with open(kb_file) as f:
        lines = f.readlines()
        for line in lines:
            if len(line) > 2:
                CONDITIONAL_CLAUSES += 1
            else:
                PROPOSITIONAL_CLAUSES += 1
            clauses.append(line.rstrip('\n'))
    sys.stdout.write(f'KB has {CONDITIONAL_CLAUSES} conditional clauses and {PROPOSITIONAL_CLAUSES} propositional symbols.\n')
    
    sys.stdout.write('Clauses: \n')
    all_clauses = display_clauses_symbols('clauses', clauses)
    if all_clauses != []:
        sys.stdout.write(str(all_clauses) + '\n')
    else:
        sys.stdout.write('NONE\n')

    sys.stdout.write('Symbols: \n')
    symbols = display_clauses_symbols('symbols', clauses)
    if symbols != []:
        sys.stdout.write(str(symbols) + '\n')
    else:
        sys.stdout.write('NONE\n')
    get_user_input_perform_forward_chaining(clauses)
    
main()