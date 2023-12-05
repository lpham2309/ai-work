from turtle import update
import numpy as np
import sys
import re

global edict
class ProbDist:
    def __init__(self, var_name='?', freq=None):
        self.prob = {}
        self.var_name = var_name
        self.values = []
        if freq:
            for (v, p) in freq.items():
                self[v] = p
            self.normalize()

    def __getitem__(self, val):
        return self.prob[val]

    def __setitem__(self, val, p):
        if val not in self.values:
            self.values.append(val)
        self.prob[val] = p

    def normalize(self):
        total = sum(self.prob.values())
        if not np.isclose(total, 1.0):
            for val in self.prob:
                self.prob[val] /= total
        return self

class Node:
    def __init__(self, X, parents, conditional_probability):
        if isinstance(parents, str):
            parents = parents.split()
        if isinstance(conditional_probability, (float, int)):
            conditional_probability = {(): conditional_probability}
        elif isinstance(conditional_probability, dict):
            if conditional_probability and isinstance(list(conditional_probability.keys())[0], bool):
                conditional_probability = {(v,): p for v, p in conditional_probability.items()}

        self.variable = X
        self.parents = parents
        self.conditional_probability = conditional_probability
        self.children = []

    def calculate_probability(self, value, event):
        if isinstance(event, tuple) and len(event) == len(self.parents):
            cond_prob = event
        else:
            cond_prob= tuple([event[var] for var in self.parents])
        
        update_index_val = int(value) - 1
        if isinstance(self.conditional_probability, list):
            if int(value) >= 4:
                new_val = 1 - sum(self.conditional_probability)
                self.conditional_probability.append(new_val)
                ptrue = self.conditional_probability[update_index_val]
            else:
                ptrue = self.conditional_probability[update_index_val]
        elif isinstance(self.conditional_probability[cond_prob], list):
            ptrue = self.conditional_probability[cond_prob][update_index_val]
        else:
            ptrue = self.conditional_probability[cond_prob]
                
        return ptrue if value else 1 - ptrue

class BayesNetwork:

    def __init__(self, node_properties=None):
        self.nodes = []
        self.variables = []
        node_properties = node_properties or []
        for prop in node_properties:
            self.add_node(prop)
    
    def add_node(self, node_prop):
        node = Node(*node_prop)
        self.nodes.append(node)
        self.variables.append(node.variable)
        for parent in node.parents:
            if self.curr_node(parent).children:
                self.curr_node(parent).children.append(node)

    def curr_node(self, variable):
        for node in self.nodes:
            if node.variable == variable:
                return node

    def domain_values(self, var):
        if var in ['Quality', 'Kindness', 'Recommendation']:
            return ['1', '2', '3', '4', '5']
        else:
            return [True, False]

def enumeration_ask(X, e, bayes_net):
    Q = ProbDist(X)
    for idx in bayes_net.domain_values(X):
        Q[idx] = enumerate_all(bayes_net.variables, {**e, X: idx}, bayes_net)
    return Q.normalize()

def enumerate_all(variables, e, bayes_net):
    if not variables:
        return 1.0
    V = variables[0]
    curr_node = bayes_net.curr_node(V)
    if V in e:
        return curr_node.calculate_probability(e[V], e) * enumerate_all(variables[1:], e, bayes_net)
    else:
        return sum(curr_node.calculate_probability(y, e) * enumerate_all(variables[1:], {**e, V: y}, bayes_net)
                   for y in bayes_net.domain_values(V))


def parse_data_from_input(filename):
    bayes_net = {}
    with open(filename) as bayes_file:
        lines = bayes_file.readlines()
    results = []
    for idx, line in enumerate(lines):
        line = line.rstrip('\n')
        results.append(line)
    
    variables, tables, prob = [], [], []
    if '# Parents' in results:
        parent_idx = results.index('# Parents')
        variables = results[:parent_idx]
        for variable in variables:
            curr_value = variable.split(" ")
            bayes_net[curr_value[0]] = {
                'domains': curr_value[1:] if curr_value[1:] else []
            }
    if '# Tables' in results and '# Parents' in results:
        table_idx = results.index('# Tables')
        parent_idx = results.index('# Parents')
        tables = results[parent_idx+1:table_idx]
        for table in tables:
            curr_value = table.split(" ")
            bayes_net[curr_value[0]].update({
                'parents': curr_value[1:] if curr_value[1:] else [],
                'conditional_prob': {},
                'prob': -1
            })
    if '# Tables' in results:
        table_idx = results.index('# Tables')
        prob = results[table_idx+1:]
        curr_key = ''
        for i in range(len(prob)):
            for val in bayes_net.keys():
                if prob[i] == val:
                    curr_key = prob[i]
                    if prob[i+1] != prob[i] and \
                    ('T' or 'F') not in prob[i+1]:
                        if ' ' not in prob[i+1]:
                            bayes_net[prob[i]]['prob'] = float(prob[i+1])
                        else:
                            prob_to_list = prob[i+1].split(' ')
                            prob_to_list = [float(x) for x in prob_to_list]
                            bayes_net[prob[i]] = {
                                'prob': prob_to_list
                            }
    
                elif curr_key != prob[i]:
                    curr_condition = prob[i].split(' ')
                    if len(curr_condition) == 1:
                        curr_value = curr_condition[0]
                        if curr_value in bayes_net.keys():
                            continue
                    if 'parents' in bayes_net[curr_key]:
                        last_index = len(bayes_net[curr_key]['parents'])
                    if 'conditional_prob' in bayes_net[curr_key]:
                        if len(curr_condition[last_index:]) > 1:
                            stringify_value = [float(x) for x in curr_condition[last_index:]]
                            temp = []
                            temp.append(1.0 - sum(stringify_value))
                            stringify_value += temp
                        else:
                            stringify_value = float(''.join(str(x) for x in curr_condition[last_index:]))
                        bayes_net[curr_key]['conditional_prob'].update({
                            tuple(curr_condition[:last_index]): stringify_value
                        })
    return bayes_net

def restructure_data_format(bh, is_book=False, inputs=dict()):
    result = []

    bool_parser = {
        'T': True,
        'F': False
    }

    if is_book:
        for key, val in inputs.items():
            total = 0.0
            if val not in bh[key]['prob']:
                for i in bh[key]['prob'].values():
                    total += float(i)
                bh[key]['prob'].update({
                    val: 1 - total
                }) 

    list_of_keys = bh.keys()

    for val in list_of_keys:
        curr_list = []
        curr_list.append(val)
        if 'parents' not in bh[val]:
            curr_list.append('')
        else:
            stringify_parents = ' '.join(str(x) for x in bh[val]['parents'])
            curr_list.append(stringify_parents)  
        if 'prob' in bh[val]:
            if bh[val]['prob'] != -1 and not isinstance(bh[val]['prob'], dict):
                curr_list.append(bh[val]['prob'])
            elif isinstance(bh[val]['prob'], dict):
                curr_prob = 0.0
                for k,v in inputs.items():
                    if curr_list[0] == k:
                        curr_prob = float(bh[k]['prob'][v])
                curr_list.append(curr_prob)
        if 'conditional_prob' in bh[val]:
            curr_prob_keys = bh[val]['conditional_prob'].keys()
            curr_prob_values = bh[val]['conditional_prob'].values()
            
            res = []
            if is_book == True:
                for prob in curr_prob_keys:
                    if len(prob) >= 3:
                        prob = list(prob)
                        temp = bool_parser[str(prob[0])]
                        prob[0] = temp
                        res.append(tuple(prob))
                curr_prob_keys = res
            else:
                curr_prob_keys = [tuple(bool_parser[i] for i in prob) for prob in curr_prob_keys]
            bh[val]['conditional_prob'] = dict(zip(curr_prob_keys, curr_prob_values))

            curr_list.append(bh[val]['conditional_prob'])
        
        result.append(tuple(curr_list))
    
    return result

def get_user_input(bayes_input):
    '''
    Prompt messages asking users
    '''
    bool_parser = {
        'T': True,
        'F': False
    }
    query_input = ''
    while query_input != 'quit':
        query_input = input("Enter your query: ")
        if query_input == 'quit':
            sys.exit("Goodbye.\n")
        else:
            match = re.match(r'(.*)\|(.*\=.*)', query_input)
            global edict

            if match:
                X = match.group(1).strip()
                e = match.group(2).strip().replace(' ', '')
                if ',' in e:
                    result = []
                    e_split = e.split(',')
                    for evidence in e_split:
                        e_split = evidence.split('=')
                        result += e_split
                    e = result
                else:
                    e = e.split('=')
                it = iter(e)
                edict = dict(zip(it, it))
                for k, v in edict.items():
                    if v == 'T' or v == 'F':
                        edict[k] = bool_parser[v]

            else:
                match = re.match(r'(.*)', query_input)
                if match:
                    X = match.group(1).strip()
                e = []
                edict = {}

            bayes_net = BayesNetwork(bayes_input)
            solution = enumeration_ask(X, edict, bayes_net)
            print(', '.join([('P({}): ' + '{:.3g}').format(v, p) for (v, p) in sorted(solution.prob.items())]))

def main():
    filename = sys.argv[1]
    is_book_file= None

    if 'books' in filename:
        is_book_file = 'true'
    else:
        is_book_file = 'false'

    bh = parse_data_from_input(filename)
    if is_book_file == 'true':
        bayes_input = restructure_data_format(bh, is_book=True)
    else:
        bayes_input = restructure_data_format(bh)

    get_user_input(bayes_input)

main()
