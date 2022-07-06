import sys

RECURSIVE_CALLS = 0
class CSP():

    def __init__(self, csp):
        self.csp = csp
        self.domains = {}

        for var in self.csp.variables:
            self.domains[var] = self.csp.words.copy()

    def revise(self, x, y):
        '''
        Perform revision against each pair of (Xi, Xj) where both words matched and have an overlapping
        '''
        i, j = self.csp.intersects[x, y]
        is_revised = False
        for first_word in self.domains[x].copy():
            is_matched = False
            for second_word in self.domains[y]:
                if len(first_word) > i and len(second_word) > j and first_word[i] == second_word[j] and first_word != second_word:
                    is_matched = True
                    break
            if is_matched == False:
                self.domains[x].remove(first_word)
                is_revised = True
        return is_revised

    def get_all_arcs_csp(self):
        arcs = []
        for first_variable, second_variable in self.csp.intersects:
            if self.csp.intersects[first_variable, second_variable] is not None:
                arcs.append((first_variable, second_variable))
        return arcs

    def arc_consistency_ac3(self, arcs=None):
        while not arcs:
            # Get a queue that contains all arcs in CSP
            arcs = self.get_all_arcs_csp()
                 
        for i, j in arcs:
            is_revised = self.revise(i ,j)
            if is_revised:
                if len(self.domains[i]) == 0:
                    return False
        return True

    def select_unassigned_variable(self, assignment):
        '''
        Check for the most constrained variable based on a word. Then check for most constraining variable if 
        exists a ties between variables within the most constrained set
        '''
        fewest_legal_moves_set = set()
        most_constrainted_variable = len(self.csp.words)
        for word in self.csp.variables:
            if word not in assignment:
                if len(self.domains[word]) <= most_constrainted_variable:
                    fewest_legal_moves_set.add(word)
                    most_constrainted_variable = len(self.domains[word])
                elif len(self.domains[word]) == most_constrainted_variable:
                    fewest_legal_moves_set.add(word)

        most_neighbors = 0
        most_constraining_variable = set()

        for word in fewest_legal_moves_set:
            current_neighbors = len(self.csp.get_neighbors(word))
            if current_neighbors > most_neighbors:
                most_constraining_variable.add(word)
                most_neighbors = current_neighbors
            elif current_neighbors == most_neighbors:
                most_constraining_variable.add(word)
        
        if len(fewest_legal_moves_set) == 1:
            return fewest_legal_moves_set.pop()
        else:
            return most_constraining_variable.pop()
        
    
    def is_consistent(self, assignment):
        if len(assignment) != len(set(assignment.values())):
            return False
        for var in assignment:
            if var.length != len(assignment[var]):
                return False      
        for var in assignment:
            first_word = assignment[var]
            current_neighbors = self.csp.get_neighbors(var)
            for var2 in current_neighbors:
                if var2 in assignment:
                    second_word = assignment[var2]
                    i, j = self.csp.intersects[var, var2]
                    # check if 2 words have same letter at the overlaping index
                    if first_word[i] != second_word[j] or first_word == second_word:
                        return False
        return True
    
    def order_domain_values(self, var, assignment):
        result = {}
        for word1 in self.domains[var]:
            heuristic_value = 0
            for variable in self.csp.variables:
                # Check if variable in domains matches with variable existed in variables. If not, get the the intersection between them
                if variable != var:
                    intersected_index = self.csp.intersects[var, variable]
                    if variable not in assignment and intersected_index != None:
                        # If such intersection and variable is not in assignment, check if these two words are the same. If it is, lower its priority
                        for word2 in self.domains[variable]:
                            if len(word1) > intersected_index[0] and len(word2) > intersected_index[1]:
                                if word1[intersected_index[0]] != word2[intersected_index[1]]:
                                    heuristic_value += 1
                            else:
                                break
            result[word1] = heuristic_value
        return sorted(result, key=result.get)

    def display_grid(self, height, width, assignment):
        # Construct an empty 2D grid
        empty_grid = []
        for _ in range(height):
            curr_grid = []
            for _ in range(width):
                curr_grid.append('_')
            empty_grid.append(curr_grid)
        
        for variable, word in assignment.items():
            direction = variable.curr_move
            for k in range(len(word)):
                i = variable.row + (k if direction == GridCoordinate.MOVE_DOWN else 0)
                j = variable.column + (k if direction == GridCoordinate.MOVE_ACROSS else 0)
                empty_grid[i][j] = word[k]

        for i in range(height):
            for j in range(width):
                if self.csp.domain[i][j]:
                    print(empty_grid[i][j], end="")
                else:
                    print(" ", end="")
            print()

    def backtracking_search(self, assignment={}):
        global RECURSIVE_CALLS
        if len(assignment) == len(self.csp.variables):
            sys.stdout.write(f'SUCCESS! Solution found after {RECURSIVE_CALLS} recursive calls to search\n')
            return assignment
            
        var = self.select_unassigned_variable(assignment)
        domain = self.order_domain_values(var, assignment)

        solution = None  
        for word in domain:
            assignment[var] = word
            if self.is_consistent(assignment):
                RECURSIVE_CALLS += 1
                solution = self.backtracking_search(assignment)

            if solution is not None:
                break
        
        return solution


class GridCoordinate():

    MOVE_ACROSS = "-"
    MOVE_DOWN = "|"

    def __init__(self, row, column, curr_move, length):
        self.row = row
        self.column = column
        self.curr_move = curr_move
        self.length = length
        self.grid = []
        for k in range(self.length):
            self.grid.append(
                (self.row + (k if self.curr_move == GridCoordinate.MOVE_DOWN else 0),
                 self.column + (k if self.curr_move == GridCoordinate.MOVE_ACROSS else 0))
            )

def parse_grid_info(file_name, header=False):
    with open(file_name) as f:
        if header:
            grid = f.readlines()[0].rstrip().split(' ')
            return grid[1], grid[2]
        else:
            lines = f.readlines()[1:]
            return [line.rstrip('\n').lstrip(' ').split() for line in lines]

def parse_words_data(file_name):
    words = []
    with open(file_name) as f:
        lines = f.readlines()
        for line in lines:
            words.append(line.rstrip())
        return set(words)

class CrosswordGrid():

    GRID_HEIGHT = 0
    GRID_WIDTH = 0

    def __init__(self, grid, words):
        '''
        Setup domains, variable and overlapped words for the entire grid
        '''
        self.grid = grid
        self.words = words
        self.domain = []
        self.variables = set()
        self.intersects = dict()

        global GRID_HEIGHT, GRID_WIDTH
        GRID_HEIGHT = len(grid)
        GRID_WIDTH = len(grid[0])

    def construct_overlapping_words(self):
        for first_word in self.variables:
            for second_word in self.variables:
                if first_word == second_word:
                    continue
                cells1 = first_word.grid
                cells2 = second_word.grid
                intersection = set(cells1).intersection(cells2)
                if not intersection:
                    self.intersects[first_word, second_word] = None
                else:
                    intersection = intersection.pop()
                    self.intersects[first_word, second_word] = (
                        cells1.index(intersection),
                        cells2.index(intersection)
                    )
        return self.intersects

    def construct_all_variables(self):
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                # Check all words in vertical direction
                vertical_word = (
                    self.domain[i][j] and (i == 0 or not self.domain[i - 1][j])
                )

                if vertical_word:
                    max_vertical_length = 1
                    for k in range(i + 1, GRID_HEIGHT):
                        if self.domain[k][j]:
                            max_vertical_length += 1
                        else:
                            break
                    if max_vertical_length > 1:
                        self.variables.add(
                            GridCoordinate(
                                row=i, column=j,
                                curr_move=GridCoordinate.MOVE_DOWN,
                                length=max_vertical_length
                            ))

                # Check all words in across direction
                across_word = (
                    self.domain[i][j]
                    and (j == 0 or not self.domain[i][j - 1])
                )
                if across_word:
                    max_across_length = 1
                    for k in range(j + 1, GRID_WIDTH):
                        if self.domain[i][k]:
                            max_across_length += 1
                        else:
                            break
                    if max_across_length > 1:
                        self.variables.add(GridCoordinate(
                            row=i, column=j,
                            curr_move=GridCoordinate.MOVE_ACROSS,
                            length=max_across_length
                        ))
        return self.variables

    def construct_domains(self, grid):
        for i in range(GRID_HEIGHT):
            row = []
            for j in range(GRID_WIDTH):
                if j >= len(grid[i]):
                    row.append(False)
                elif grid[i][j] != "X":
                    row.append(True)
                else:
                    row.append(False)
            self.domain.append(row)
        return self.domain

    def get_neighbors(self, var):
        all_neighbors = set()
        for variable in self.variables:
            if var != variable and self.intersects[var, variable]:
                all_neighbors.add(variable)
        return all_neighbors

def count_number_of_variables(grid):
    MAX_VARIABLES = 0
    for row in range(len(grid)):
        for col in range(len(grid)):
            if grid[row][col] == '_' or grid[row][col] == 'X':
                pass
            else:
                if int(grid[row][col]) > MAX_VARIABLES:
                    MAX_VARIABLES = int(grid[row][col]) + 1
    return MAX_VARIABLES

def main():
    pre_processing = None
    if len(sys.argv) > 3:
        grid_file = sys.argv[1]
        dictionary_file = sys.argv[2]
        pre_processing = sys.argv[3]
    else:
        grid_file = sys.argv[1]
        dictionary_file = sys.argv[2]

    # Parse grid file into a 2D array
    grid_data = parse_grid_info(grid_file)
    height = len(grid_data)
    width = len(grid_data[0])

    # Parse words in dictionary file and store in a set
    words = parse_words_data(dictionary_file)

    variable_num = count_number_of_variables(grid_data)
    sys.stdout.write(f'Current number of variables: {variable_num}\n')
    
    cross_word = CrosswordGrid(grid_data, words)
    cross_word.domain = cross_word.construct_domains(grid_data)
    cross_word.variables = cross_word.construct_all_variables()
    cross_word.intersects = cross_word.construct_overlapping_words()

    csp = CSP(cross_word)

    if pre_processing and pre_processing in ['true', '1', 'bananagram']:
        csp.arc_consistency_ac3()
    
    sys.stdout.write('Initial assignment and domain size: \n')
    curr_index = 1
    map_direction = {
        '|': 'down',
        '-': 'across'
    }
    for variable in cross_word.variables:
        sys.stdout.write(f'{curr_index}-{map_direction[variable.curr_move]} = NO VALUES ({variable_num} possible values)\n')
        curr_index += 1
    solution = csp.backtracking_search()

    if solution:
        csp.display_grid(height, width, solution)
    else:
        sys.stdout.write("No solution found!\n")
main()