
EMPTY_LETTER = None

class RIGHT:
    '''Move to the right'''
    pass
class LEFT:
    '''Move to the lefft'''
    pass
class NOWHERE:
    '''Don't move anywhere'''
    pass

class State:
    __number = 0
    def __init__(self):
        self.__number = State.__number
        State.__number += 1

    def __str__(self):
        return f"q{self.__number}"


def d_to_l(direction):
    return 'R' if direction is RIGHT else 'L' if direction is LEFT else 'N'


class Command:
    def __init__(self, start_state, input_letter, output_letter, direction, end_state):
        '''Initialize command
        Parameters:
            start_state: State
            input_letter: str or EMPTY_LETTER
            output_letter: str or EMPTY_LETTER
            direction: RIGHT, LEFT, NOWHERE
            end_state: State
        command is:
            start_state input_letter -> output_letter direction end_state
            example: q1 A -> B R q2
        '''

        self.start_state = start_state
        self.input_letter = input_letter
        self.output_letter = output_letter
        self.direction = direction
        self.end_state = end_state

    def output(self) -> tuple:
        '''Return right side of the command as a tuple'''
        return (self.output_letter, self.direction, self.end_state)

    def __str__(self):
        return f'{self.input_string()} -> {self.output_string()}'

    def output_string(self):
        '''String representing right side of the command'''
        return f'{self.output_letter} {d_to_l(self.direction)} {self.end_state}'

    def input_string(self):
        '''String representing left side of the command'''
        return f'{self.start_state} {self.input_letter}'

#

class Cell:
    __number = 0
    def __init__(self, item=None, left=None, right=None):
        self.letter = item  #
        self.left = left  #
        self.right = right  #
        self.__number = Cell.__number
        Cell.__number += 1

    @staticmethod
    def connect(Cell1, Cell2):
        '''Connect 2 consecutive cells'''
        Cell2.left = Cell1
        Cell1.right = Cell2

    def __str__(self):
        return f'Cell {self.__number} <{self.letter}>'

    def __eq__(self, other):
        return isinstance(other, Cell) and self.__number == other.__number


class Tape:
    '''Memory of the Turing machine'''
    def __init__(self):
        self.clear()

    def write(self, word):
        for i in word:
            self.append_end(i)

    def clear(self):
        self.start = Cell()
        self.end = Cell()
        Cell.connect(self.start, self.end)

    def __iter__(self):
        cell = self.start
        while cell.right is not self.end:
            cell = cell.right
            yield cell

    def append_start(self, thing=EMPTY_LETTER):
        '''Add a cell at the beginning of the tape'''
        cell = Cell(thing)
        Cell.connect(cell, self.start.right)
        Cell.connect(self.start, cell)
        return cell

    def append_end(self, thing=EMPTY_LETTER):
        '''Add a cell at the end of the tape'''
        cell = Cell(thing)
        Cell.connect(self.end.left, cell)
        Cell.connect(cell, self.end)
        return cell

    def right(self, head):
        '''Return the cell to the right of the given one,
           if there is no cell, creates a new one with EMPTY_LETTER'''
        if head.right is self.end:
            return self.append_end()
        return head.right

    def left(self, head):
        '''Return the cell to the left of the given one,
           if there is no cell, creates a new one with EMPTY_LETTER'''
        if head.left is self.start:
            return self.append_start()
        return head.left

    def __str__(self):
        return ' '.join([str(i.letter) for i in list(self)])

    def string(self, N=10):
        return '|'.join([str(i.letter).center(N) for i in list(self)])

class CommandTable:
    '''Table of commands of Turing machine'''
    def __init__(self, alphabet):
        self._table = {}
        self.alphabet = list(alphabet)

    def __getitem__(self, state):
        if state not in self._table:
            self._table[state] = {}
        return self._table[state]

    def add(self, command: Command):
        '''Add a command to the table'''
        if command.start_state in self and command.input_letter in self[command.start_state]:
            print('Warning: You overwrote an existing command!')
        self[command.start_state][command.input_letter] = command

    def remove(self, command: Command):
        '''Remove given command fro the table'''
        if not command.start_state in self:
            return
        if command.input_letter in self[command.start_state]:
            self[command.start_state].pop(command.input_letter)

    def __len__(self):
        return len(self._table)

    def __iter__(self):
        return iter(self._table)

    def __str__(self):
        W = 14
        string = ' '*(W-1)+'|'+'|'.join(list(map(lambda i: str(i).center(W), self.alphabet)))+'|'
        separator = '\n'+'-'*(len(string)-1+len(self))
        string += separator
        for i in self:
            string += '\n'+str(i).center(W-1)+'|'
            for j in self.alphabet:
                if j in self[i]:
                    string += str(self[i][j].output_string()).center(W)
                else:
                    string += '-'.center(W)
                string += '|'
        string += separator
        return string


class Machine:
    '''Turing machine'''
    def __init__(self, letters: list):
        ''' Initialize turing machine
        Parameters:
            letters: list of strings
        '''

        if not all(isinstance(i, str) for i in letters):
            raise ValueError('Alphabet can contain strings only')

        self.alphabet = letters+list(map(lambda x: x+"'", letters))+[EMPTY_LETTER]
        self.__command_table = CommandTable(self.alphabet)
        self.__start_state = State()
        self.__end_state = State()
        self.tape = Tape()

    def start_end_states(self):
        '''Return start and end states of the machine (q1, q0)'''
        return self.__start_state, self.__end_state

    def run(self, word):
        '''Process given word'''

        # Begin work
        current_state = self.__start_state
        self.tape.clear()  # clear tape
        self.tape.write(word)  # write word onto the tape
        tape = self.tape
        current_cell = tape.start.right  # start at the beginning of the tape

        while current_state is not self.__end_state:
            self.print_machine(current_state, current_cell)

            command = self.__command_table[current_state][current_cell.letter]
            current_cell.letter, shift, current_state = command.output()

            if shift == RIGHT:
                current_cell = tape.right(current_cell)  # move to the right
            elif shift == LEFT:
                current_cell = tape.left(current_cell)  # move to the left

        self.print_machine(current_state, current_cell)
        return tape

    def print_machine(self, state, head_cell):
        '''Print the machine in its current state'''
        N = max([len(str(i))+2 for i in self.alphabet])

        l, n = 0, 0
        for Cell in self.tape:
            if Cell == head_cell:
                break
            l += len(str(Cell.letter))
            n += 1

        print(self.tape.string(N))
        print(' '*(l*N+n), state)

    def add_command(self, command):
        '''Add command to the machine's table of commands'''

        if not command.input_letter in self.alphabet or \
               not command.output_letter in self.alphabet:
           raise ValueError("Invalid Command: command uses letters that aren't in the alphabet")
        self.__command_table.add(command)

    def remove_command(self, command):
        self.__command_table.remove(command)

    def table(self):
        return str(self.__command_table)



if __name__ == '__main__':
    word = '0120'
    # create a machine
    m = Machine(['0', '1', '2'])
    q1, q0 = m.start_end_states()
    # create states
    q2, q3, q4, q5 = State(), State(), State(), State()

    print('Input word:', word)

    # Adding commands
    m.add_command(Command(q1, '0', '0', RIGHT, q1))
    m.add_command(Command(q1, '1', '1', RIGHT, q1))
    m.add_command(Command(q1, '2', '1', RIGHT, q2))
    m.add_command(Command(q2, '0', '0', RIGHT, q2))
    m.add_command(Command(q2, EMPTY_LETTER, '2', RIGHT, q3))
    m.add_command(Command(q3, EMPTY_LETTER, '2', LEFT, q4))
    m.add_command(Command(q4, '2', '2', LEFT, q4))
    m.add_command(Command(q4, '1', '1', LEFT, q4))
    m.add_command(Command(q4, '0', '0', LEFT, q4))
    m.add_command(Command(q4, EMPTY_LETTER, '0', NOWHERE, q5))
    m.add_command(Command(q5, '0', EMPTY_LETTER, LEFT, q0))

    # print table of all commands of the machine
    print('\n',m.table(), '\n')

    print('\nResult: ', m.run(word), '\n\n')
