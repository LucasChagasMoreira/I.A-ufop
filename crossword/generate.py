import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        # Initialize the crossword puzzle and set up the domains for each variable.
        # The domain of each variable is initially the set of all words.
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        # Create a 2D grid representing the crossword structure.
        # Initialize all cells to None (empty).
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        # Fill in the grid with the words from the assignment.
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                # Calculate the position of each letter in the grid based on the direction.
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        # Convert the assignment to a letter grid and print it.
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    # Print the letter if the cell is part of the crossword structure.
                    print(letters[i][j] or " ", end="")
                else:
                    # Print a block character for cells that are not part of the structure.
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        # Define the size of each cell and the border.
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas for the crossword image.
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    # Draw a white rectangle for cells that are part of the structure.
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        # Calculate the position to center the letter in the cell.
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        # Save the image to the specified filename.
        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        # First, enforce node consistency to remove invalid words from domains.
        self.enforce_node_consistency()
        # Then, enforce arc consistency to further reduce the domains.
        self.ac3()
        # Finally, use backtracking search to find a solution.
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # Iterate over each variable and its domain.
        for var in self.domains:
            for word in set(self.domains[var]):
                # Remove words that do not match the variable's length.
                if len(word) != var.length:
                    self.domains[var].remove(word)
        

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False

        # Get the overlap between variables x and y.
        overlap = self.crossword.overlaps[x,y]

        if overlap is None:
            return False
        
        i, j = overlap

        # Check each word in the domain of x.
        for word_x in set(self.domains[x]):
            match = False
            # Check if there is a word in the domain of y that matches the overlap.
            for word_y in self.domains[y]:
                if word_x[i] == word_y[j]:
                    match = True
                    break
            
            # If no matching word is found, remove the word from the domain of x.
            if match == False:
                self.domains[x].remove(word_x)
                revised = True

        return revised 
    
    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = []
            # Initialize the list of arcs with all pairs of neighboring variables.
            for x in self.crossword.variables:
                for y in self.crossword.neighbors(x):
                    arcs.append((x,y))
        
        fila = list(arcs)

        while len(fila) > 0:
            x, y = fila.pop(0)

            # Revise the domain of x based on y.
            if self.revise(x,y) == True:
                if len(self.domains[x]) == 0:
                    return False
                
                # If x's domain was revised, add arcs involving x's neighbors.
                for z in self.crossword.neighbors(x):
                    if z != y:
                        fila.append((z,x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # Check if all variables have been assigned a value.
        for variable in self.crossword.variables:
            if variable not in assignment:
                return False
        
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # Check that each word in the assignment matches the variable's length.
        for variable in assignment:
            word = assignment[variable]
            if len(word) != variable.length:
                return False
        
            # Check that no two variables are assigned the same word.
            for var2 in assignment:
                if var2 != variable and word == assignment[var2]:
                    return False
                
            # Check that the assignment is consistent with overlapping variables.
            for nb in self.crossword.neighbors(variable):
                if nb in assignment:
                    overlap = self.crossword.overlaps.get((variable, nb))
                    if overlap is not None:
                        x,y = overlap
                        if word[x] != assignment[nb][y]:
                            return False
                        
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        conf = []

        # For each word in the domain of var, count how many words it rules out in neighboring domains.
        for val in self.domains[var]:
            confcount = 0

            for nb in self.crossword.neighbors(var):
                if nb not in assignment:
                    overlap = self.crossword.overlaps.get((var, nb))
                    if overlap is not None:
                        x, y = overlap
                        for word in self.domains[nb]:
                            if word[y] != val[x]:
                                confcount += 1

            conf.append((val, confcount))

        # Sort the words by the number of conflicts they cause.
        conf.sort(key=lambda x:x[1])

        return [val for val, _ in conf]
    
    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        bestvar = None
        minval = float("inf")
        max = float("-inf")

        # Iterate over all variables to find the one with the smallest domain.
        for var in self.crossword.variables:
            if var not in assignment:
                remain = len(self.domains[var])
                degree = len(self.crossword.neighbors(var))

                if remain < minval:
                    bestvar = var
                    minval = remain
                    max = degree
                
                elif remain == minval:
                    if degree > max:
                        bestvar = var
                        max = degree

        
        return bestvar
            

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # If the assignment is complete, return it.
        if self.assignment_complete(assignment):
            return assignment
        
        # Select an unassigned variable.
        var = self.select_unassigned_variable(assignment)

        # Try each value in the domain of the selected variable.
        for value in self.order_domain_values(var,assignment):
            newa = assignment.copy()
            newa[var] = value

            # If the new assignment is consistent, continue searching.
            if self.consistent(newa):
                result = self.backtrack(newa)

                if result is not None:
                    return result
                
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()